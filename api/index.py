# -*- coding: utf-8 -*-
import os, sys, re, json, urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "lib"))

import fetch_sheet
import build_outputs

REFRESH_SEC = int(os.environ.get("REFRESH_SEC", "900"))   # 15 phut


def _load_kpi():
    p = ROOT / "data" / "kpi.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        return d.get("daily", []), d.get("monthly")
    return [], None


def _download_csv():
    sid = os.environ.get("SHEET_ID") or fetch_sheet.SHEET_ID
    gid = os.environ.get("SHEET_GID") or fetch_sheet.GID
    url = ("https://docs.google.com/spreadsheets/d/%s/export?format=csv&gid=%s"
           % (sid, gid))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    tmp = "/tmp/ds_ms.csv"
    with open(tmp, "wb") as f:
        f.write(data)
    if len(data) < 1000:
        raise RuntimeError("CSV tai ve qua nho - kiem tra quyen chia se cua Sheet.")
    return tmp


def _inject_head(html):
    if 'http-equiv="refresh"' in html or "http-equiv='refresh'" in html:
        return html
    inject = ('<meta http-equiv="refresh" content="%d">'
              '<meta name="viewport" content="width=device-width, initial-scale=1">'
              % REFRESH_SEC)
    m = re.search(r"<head[^>]*>", html, re.IGNORECASE)
    if m:
        return html[:m.end()] + inject + html[m.end():]
    m = re.search(r"<html[^>]*>", html, re.IGNORECASE)
    if m:
        return html[:m.end()] + "<head>" + inject + "</head>" + html[m.end():]
    return "<head>" + inject + "</head>" + html


def _render_html():
    csv = _download_csv()
    ms = fetch_sheet.analyze(csv)
    daily, monthly = _load_kpi()
    out = "/tmp/dashboard.html"
    build_outputs.build_dashboard(daily, monthly, ms, out)
    html = Path(out).read_text(encoding="utf-8")
    return _inject_head(html)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            body = _render_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=0, s-maxage=60")
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            import traceback
            msg = "Loi khi dung dashboard:\n%s\n\n%s" % (e, traceback.format_exc())
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))
