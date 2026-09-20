from datetime import date, timedelta
import pandas as pd

def week_start(): return (date.today() - timedelta(days=date.today().weekday())).isoformat()
def csv_bytes(rows): return pd.DataFrame(rows).to_csv(index=False).encode()
def report_pdf(report):
    """Dependency-free, counselor-only PDF record using standard PDF text objects."""
    import textwrap
    lines = ["SafeBridge AI - Counselor Review", "AI recommendation only. Human review required.", ""]
    for key in ["id", "status", "category", "location", "severity", "priority", "incident_summary", "original_report"]:
        value = str(report.get(key, "")).replace("\n", " ")
        lines.extend(textwrap.wrap(f"{key.replace('_', ' ').title()}: {value}", width=92) or [""])
    # Cap to fit single printable letter page (~42 lines from 750pt down to 60pt)
    if len(lines) > 43:
        lines = lines[:42] + ["[Summary PDF limit reached. View SafeBridge portal for complete report and attachments.]"]
    # Latin-1 makes this deliberately conservative and avoids external font dependencies.
    def esc(value): return value.encode("latin-1", "replace").decode("latin-1").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = ["BT", "/F1 16 Tf", "48 750 Td", f"({esc(lines[0])}) Tj", "/F1 9 Tf", "0 -24 Td", f"({esc(lines[1])}) Tj", "/F1 10 Tf"]
    for line in lines[2:]: content.extend(["0 -15 Td", f"({esc(line)}) Tj"])
    content.append("ET"); stream = "\n".join(content).encode("latin-1")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf)); pdf.extend(f"{number} 0 obj\n".encode()); pdf.extend(obj); pdf.extend(b"\nendobj\n")
    xref = len(pdf); pdf.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]: pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(pdf)
