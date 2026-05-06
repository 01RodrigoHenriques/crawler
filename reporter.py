"""
Geracao de relatorios em multiplos formatos (JSON, XML, HTML)
"""

import html
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import config
from logger_config import logger


class ReportGenerator:
    """Gera relatorios em multiplos formatos."""

    def __init__(self, results: Dict[str, Any]):
        self.results = results
        self.timestamp = datetime.now().isoformat()

    def _clean_results(self) -> Dict[str, Any]:
        """Limpa resultados para relatorio final."""
        return {
            "target": self.results.get("target"),
            "timestamp": self.results.get("timestamp"),
            "waf_detected": self.results.get("waf_detected"),
            "summary": {
                "open_ports": len(self.results.get("open_ports", [])),
                "subdomains_active": len(self.results.get("subdomains", [])),
                "directories_found": len(self.results.get("directories", [])),
                "technologies_detected": len(self.results.get("technologies", [])),
                "links_crawled": len(self.results.get("links", [])),
            },
            "open_ports": self.results.get("open_ports", []),
            "subdomains": self.results.get("subdomains", []),
            "directories": self.results.get("directories", []),
            "technologies": self.results.get("technologies", []),
            "links": list(set(self.results.get("links", [])))[:100],
        }

    def _ensure_output_dir(self, output_file: Path) -> Path:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        return output_file

    def _escape(self, value: Any) -> str:
        return html.escape(str(value or ""), quote=True)

    def _render_html_table(
        self,
        title: str,
        headers: list[str],
        rows: list[list[Any]],
        cell_classes: list[str] | None = None,
    ) -> str:
        if not rows:
            return ""

        cell_classes = cell_classes or [""] * len(headers)
        header_html = "".join(f"<th>{self._escape(header)}</th>" for header in headers)

        body_rows = []
        for row in rows:
            cells = []
            for value, class_name in zip(row, cell_classes, strict=False):
                class_attr = f" class='{class_name}'" if class_name else ""
                cells.append(f"<td{class_attr}>{self._escape(value)}</td>")
            body_rows.append("<tr>" + "".join(cells) + "</tr>")

        table_rows = "".join(body_rows)
        return f"<h2>{self._escape(title)}</h2><table><tr>{header_html}</tr>{table_rows}</table>"

    def _render_html_tags(self, title: str, values: list[Any]) -> str:
        if not values:
            return ""
        tags = "".join(f"<span class='tag'>{self._escape(value)}</span>" for value in values)
        return f"<h2>{self._escape(title)}</h2>{tags}"

    def to_json(self, output_file: Path | None = None) -> str:
        """Gera relatorio em JSON."""
        if output_file is None:
            output_file = config.OUTPUT_JSON

        try:
            output_file = self._ensure_output_dir(output_file)
            clean_data = self._clean_results()

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(clean_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Relatorio JSON salvo: {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Erro ao gerar relatorio JSON: {e}")
            return ""

    def to_xml(self, output_file: Path | None = None) -> str:
        """Gera relatorio em XML (estilo Nmap)."""
        if output_file is None:
            output_file = config.OUTPUT_XML

        try:
            output_file = self._ensure_output_dir(output_file)
            root = ET.Element("scanresult")
            root.set("version", "1.0")
            root.set("timestamp", self.timestamp)

            target_elem = ET.SubElement(root, "target")
            target_elem.set("url", self.results.get("target", ""))

            summary = ET.SubElement(root, "summary")
            for key, value in self.results.get("summary", {}).items():
                elem = ET.SubElement(summary, key)
                elem.text = str(value)

            if self.results.get("waf_detected"):
                waf_elem = ET.SubElement(root, "waf")
                waf_elem.text = self.results["waf_detected"]

            ports_elem = ET.SubElement(root, "ports")
            for port in self.results.get("open_ports", []):
                port_elem = ET.SubElement(ports_elem, "port")
                port_elem.set("number", str(port["port"]))
                port_elem.set("service", port.get("service", "unknown"))
                port_elem.set("status", port.get("status", "open"))
                if port.get("banner"):
                    banner_elem = ET.SubElement(port_elem, "banner")
                    banner_elem.text = port["banner"][:200]

            subdomains_elem = ET.SubElement(root, "subdomains")
            for subdomain in self.results.get("subdomains", []):
                sub_elem = ET.SubElement(subdomains_elem, "subdomain")
                sub_elem.set("name", subdomain.get("subdomain", ""))
                sub_elem.set("ip", subdomain.get("ip", ""))
                sub_elem.set("status", str(subdomain.get("status_code", "")))

            directories_elem = ET.SubElement(root, "directories")
            for directory in self.results.get("directories", []):
                dir_elem = ET.SubElement(directories_elem, "directory")
                dir_elem.set("path", directory.get("path", ""))
                dir_elem.set("status", str(directory.get("status", "")))

            technologies_elem = ET.SubElement(root, "technologies")
            for tech in self.results.get("technologies", []):
                tech_elem = ET.SubElement(technologies_elem, "technology")
                tech_elem.set("name", tech.get("name", ""))
                tech_elem.set("category", tech.get("category", ""))

            tree = ET.ElementTree(root)
            tree.write(output_file, encoding="utf-8", xml_declaration=True)

            logger.info(f"Relatorio XML salvo: {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Erro ao gerar relatorio XML: {e}")
            return ""

    def to_html(self, output_file: Path | None = None) -> str:
        """Gera relatorio em HTML."""
        if output_file is None:
            output_file = config.OUTPUT_HTML

        try:
            output_file = self._ensure_output_dir(output_file)
            clean_data = self._clean_results()

            target = self._escape(clean_data["target"])
            timestamp = self._escape(clean_data["timestamp"])
            waf_detected = self._escape(clean_data["waf_detected"]) if clean_data["waf_detected"] else ""

            open_ports_table = self._render_html_table(
                "Open Ports",
                ["Port", "Service", "Status"],
                [[port["port"], port.get("service", "unknown"), port.get("status", "open")] for port in clean_data["open_ports"]],
                ["", "", "status-open"],
            )
            subdomains_table = self._render_html_table(
                "Active Subdomains",
                ["Subdomain", "IP", "Status Code"],
                [[sub.get("subdomain"), sub.get("ip"), sub.get("status_code", "N/A")] for sub in clean_data["subdomains"]],
            )
            directories_table = self._render_html_table(
                "Discovered Directories",
                ["Path", "Status"],
                [[directory.get("path"), directory.get("status")] for directory in clean_data["directories"]],
            )
            technologies_tags = self._render_html_tags(
                "Technologies Detected",
                [technology["name"] for technology in clean_data["technologies"]],
            )

            content = f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Crawler Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #764ba2;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card h3 {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .summary-card .number {{
            font-size: 32px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        table td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        table tr:hover {{ background: #f5f5f5; }}
        .tag {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin: 2px;
        }}
        .status-open {{ color: #27ae60; font-weight: bold; }}
        .meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Web Crawler Reconnaissance Report</h1>
        <div class="meta">
            <strong>Target:</strong> {target}<br>
            <strong>Scan Date:</strong> {timestamp}<br>
            {"<strong>WAF Detected:</strong> " + waf_detected if waf_detected else ""}
        </div>

        <h2>Summary</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>Open Ports</h3>
                <div class="number">{clean_data["summary"]["open_ports"]}</div>
            </div>
            <div class="summary-card">
                <h3>Active Subdomains</h3>
                <div class="number">{clean_data["summary"]["subdomains_active"]}</div>
            </div>
            <div class="summary-card">
                <h3>Directories Found</h3>
                <div class="number">{clean_data["summary"]["directories_found"]}</div>
            </div>
            <div class="summary-card">
                <h3>Technologies</h3>
                <div class="number">{clean_data["summary"]["technologies_detected"]}</div>
            </div>
        </div>

        {open_ports_table}

        {subdomains_table}

        {directories_table}

        {technologies_tags}
    </div>
</body>
</html>"""

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Relatorio HTML salvo: {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Erro ao gerar relatorio HTML: {e}")
            return ""
