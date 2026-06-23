import argparse
import json
import os
import datetime
from html import escape

def generate_report(log_file, comp_file, output_file):
    try:
        with open(log_file, 'r') as f:
            attack_log = json.load(f)
    except FileNotFoundError:
        attack_log = []

    try:
        with open(comp_file, 'r') as f:
            comp_results = json.load(f)
    except FileNotFoundError:
        comp_results = {}

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode = os.environ.get("SENTINEL_MODE", "DEV").upper()
    
    total_attempts = len(attack_log)
    successful_exploits = sum(1 for a in attack_log if a.get('verdict', {}).get('exploit_succeeded'))
    max_severity = max((a.get('verdict', {}).get('severity', 0) for a in attack_log), default=0)
    unique_skills = set(a.get('skill_used') for a in attack_log if a.get('skill_used'))
    skills_triggered = len(unique_skills)

    # SVG Timeline Generation
    svg_width = 800
    svg_height = 200
    padding = 30
    graph_w = svg_width - 2 * padding
    graph_h = svg_height - 2 * padding
    
    points = []
    if total_attempts > 0:
        x_step = graph_w / max(1, total_attempts - 1)
        y_step = graph_h / 4  # Severities 1 to 5, range is 4

        for i, a in enumerate(attack_log):
            sev = a.get('verdict', {}).get('severity', 1)
            cx = padding + i * x_step
            cy = padding + graph_h - ((sev - 1) * y_step)
            is_exploit = a.get('verdict', {}).get('exploit_succeeded', False)
            
            if sev <= 2:
                color = "#2ea043" # green
            elif sev == 3:
                color = "#d29922" # yellow
            elif sev == 4:
                color = "#f85149" # orange
            else:
                color = "#da3633" # red

            points.append({
                "cx": cx, "cy": cy, "color": color, 
                "is_exploit": is_exploit, "attempt": i + 1, "sev": sev
            })

    svg_elements = []
    # Grid lines
    for sev in range(1, 6):
        y = padding + graph_h - ((sev - 1) * (graph_h / 4))
        svg_elements.append(f'<line x1="{padding}" y1="{y}" x2="{svg_width-padding}" y2="{y}" stroke="#30363d" stroke-width="1"/>')
        svg_elements.append(f'<text x="{padding-10}" y="{y+4}" fill="#8b949e" font-size="10" text-anchor="end">{sev}</text>')

    # Lines between points
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i+1]
        svg_elements.append(f'<line x1="{p1["cx"]}" y1="{p1["cy"]}" x2="{p2["cx"]}" y2="{p2["cy"]}" stroke="#8b949e" stroke-width="2"/>')

    # Points
    for p in points:
        if p["is_exploit"]:
            # Draw a star or distinct marker
            svg_elements.append(f'<path d="M {p["cx"]} {p["cy"]-8} L {p["cx"]+2} {p["cy"]-2} L {p["cx"]+8} {p["cy"]-2} L {p["cx"]+3} {p["cy"]+2} L {p["cx"]+5} {p["cy"]+8} L {p["cx"]} {p["cy"]+5} L {p["cx"]-5} {p["cy"]+8} L {p["cx"]-3} {p["cy"]+2} L {p["cx"]-8} {p["cy"]-2} L {p["cx"]-2} {p["cy"]-2} Z" fill="{p["color"]}" stroke="#fff" stroke-width="1"/>')
        else:
            svg_elements.append(f'<circle cx="{p["cx"]}" cy="{p["cy"]}" r="5" fill="{p["color"]}"/>')
        
        svg_elements.append(f'<text x="{p["cx"]}" y="{padding + graph_h + 8}" fill="#8b949e" font-size="10" text-anchor="middle">{p["attempt"]}</text>')

    svg_content = f'''<svg width="100%" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="{svg_width}" height="{svg_height}" fill="#0d1117" />
        {''.join(svg_elements)}
    </svg>'''

    # Table Generation
    all_configs = list(comp_results.keys())
    # Find all skills across configs
    all_skills = set()
    for conf_data in comp_results.values():
        all_skills.update(conf_data.get('success_rate_by_skill', {}).keys())
    all_skills = sorted(list(all_skills))

    is_empty_comp = not comp_results or all(c.get('total_attempts', 0) == 0 for c in comp_results.values())

    if is_empty_comp:
        table_html = "<p style='color: #8b949e; font-style: italic;'>No comparison data available — run compare_targets.py to populate.</p>"
    else:
        table_html = "<table><tr><th>Metric</th>"
        for c in all_configs:
            table_html += f"<th>{c.upper()}</th>"
        table_html += "</tr>"
    
        metrics = [
            ("Total Runs", "runs"),
            ("Total Attempts", "total_attempts"),
            ("Successful Exploits", "successful_exploits"),
            ("Max Severity", "max_severity")
        ]
        
        for label, key in metrics:
            table_html += f"<tr><td>{label}</td>"
            for c in all_configs:
                table_html += f"<td>{comp_results[c].get(key, 0)}</td>"
            table_html += "</tr>"
            
        for skill in all_skills:
            table_html += f"<tr><td>Skill: {skill}</td>"
            for c in all_configs:
                rate = comp_results[c].get('success_rate_by_skill', {}).get(skill, "—")
                table_html += f"<td>{rate}</td>"
            table_html += "</tr>"
            
        table_html += "</table>"

    # Attempt Log
    log_html = ""
    for i, a in enumerate(attack_log):
        verdict = a.get('verdict', {})
        sev = verdict.get('severity', 0)
        is_exploit = verdict.get('exploit_succeeded', False)
        skill = a.get('skill_used', 'unknown')
        payload = escape(a.get('payload', ''))
        response = escape(a.get('target_response', ''))
        tool_calls = a.get('target_tool_calls', [])
        tool_calls_str = escape(json.dumps(tool_calls)) if tool_calls else "None"
        reasoning = escape(verdict.get('reasoning', ''))

        if sev <= 2:
            badge_color = "#2ea043"
        elif sev == 3:
            badge_color = "#d29922"
        elif sev == 4:
            badge_color = "#f85149"
        else:
            badge_color = "#da3633"

        card_classes = "log-card"
        if is_exploit:
            card_classes += " exploit"
            
        critical_badge = '<span class="badge critical">CRITICAL</span>' if sev == 5 else ''
        exploit_badge = '<span class="badge exploit-badge">EXPLOIT</span>' if is_exploit else ''

        log_html += f'''
        <div class="{card_classes}">
            <div class="card-header">
                <div>
                    <strong>Attempt {i+1}</strong> | Skill: <code>{skill}</code> 
                    <span class="badge" style="background-color: {badge_color};">Sev {sev}</span>
                    {critical_badge}
                    {exploit_badge}
                </div>
            </div>
            <div class="card-body">
                <strong>Payload:</strong>
                <pre>{payload}</pre>
                
                <details>
                    <summary>Target Response</summary>
                    <pre>{response}</pre>
                </details>
                
                <strong>Tool Calls:</strong>
                <pre><code>{tool_calls_str}</code></pre>
                
                <strong>Judge Reasoning:</strong>
                <p>{reasoning}</p>
            </div>
        </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sentinel // Red-Team Report</title>
    <style>
        body {{
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #58a6ff;
            border-bottom: 1px solid #30363d;
            padding-bottom: 5px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 20px;
        }}
        .badges {{
            display: flex;
            gap: 10px;
        }}
        .badge {{
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            color: #ffffff;
            background-color: #30363d;
        }}
        .critical {{ background-color: #da3633; }}
        .exploit-badge {{ background-color: #8957e5; }}
        
        .summary-bar {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
            flex: 1;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        th, td {{
            border: 1px solid #30363d;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{ background-color: #161b22; }}
        
        .log-card {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        .log-card.exploit {{
            border-left: 4px solid #da3633;
        }}
        .card-header {{
            background-color: #21262d;
            padding: 10px 15px;
            border-bottom: 1px solid #30363d;
        }}
        .card-body {{
            padding: 15px;
        }}
        pre, code {{
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
            background-color: #0d1117;
            padding: 10px;
            border-radius: 6px;
            overflow-x: auto;
            color: #e6edf3;
            border: 1px solid #30363d;
            margin: 5px 0 15px 0;
        }}
        code {{ padding: 2px 4px; display: inline; border: none; }}
        details {{
            margin-bottom: 15px;
        }}
        summary {{
            cursor: pointer;
            font-weight: bold;
            color: #58a6ff;
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>Sentinel // Red-Team Report</h1>
        <div class="badges">
            <span class="badge" style="background-color: #1f6feb;">MODE: {mode}</span>
            <span class="badge">{timestamp}</span>
        </div>
    </div>

    <div class="summary-bar">
        <div class="stat-card">
            <div>Total Attempts</div>
            <div class="stat-value">{total_attempts}</div>
        </div>
        <div class="stat-card">
            <div>Successful Exploits</div>
            <div class="stat-value" style="color: {'#da3633' if successful_exploits > 0 else '#2ea043'}">{successful_exploits}</div>
        </div>
        <div class="stat-card">
            <div>Max Severity Reached</div>
            <div class="stat-value">{max_severity}/5</div>
        </div>
        <div class="stat-card">
            <div>Skills Triggered</div>
            <div class="stat-value">{skills_triggered}</div>
        </div>
    </div>

    <h2>Severity Timeline</h2>
    <div style="background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 10px; margin-bottom: 30px; text-align: center;">
        {svg_content}
    </div>

    <h2>Configuration Comparison</h2>
    {table_html}

    <h2>Attempt Log</h2>
    {log_html}

</body>
</html>'''

    with open(output_file, 'w') as f:
        f.write(html)
    print(f"Report generated successfully: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Sentinel HTML Report")
    parser.add_argument("--log", default="attack_log.json", help="Path to attack_log.json")
    parser.add_argument("--comparison", default="comparison_results.json", help="Path to comparison_results.json")
    parser.add_argument("--output", default="sentinel_report.html", help="Path for the output HTML file")
    args = parser.parse_args()

    generate_report(args.log, args.comparison, args.output)
