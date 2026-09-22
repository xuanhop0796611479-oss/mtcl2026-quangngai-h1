# -*- coding: utf-8 -*-
"""Chay boi GitHub Actions moi ngay 09:00 (gio VN): dang nhap sMartF, xuat
day.xlsx/month.xlsx, trich KPI va ghi data/kpi.json de Vercel doc.
"""
import os, sys, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import fetch_smartf          # noqa: E402
import build_outputs        # noqa: E402


def main():
    user = os.environ.get("SMARTF_USER")
    pw = os.environ.get("SMARTF_PASS")
    if not user or not pw:
        sys.exit("Thieu SMARTF_USER / SMARTF_PASS (dat trong GitHub Secrets).")

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    day = str(data_dir / "day.xlsx")
    month = str(data_dir / "month.xlsx")

    today = datetime.date.today()
    frm = "%d/1/%d" % (today.month, today.year)
    to = "%d/%d/%d" % (today.month, today.day, today.year)
    fetch_smartf.run(user, pw, day, month, frm, to)

    daily, monthly = build_outputs.extract_kpi(day, month)
    payload = {"daily": daily, "monthly": monthly, "updated": today.isoformat()}
    (data_dir / "kpi.json").write_text(
        json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
    print("[OK] da cap nhat data/kpi.json:", len(daily), "ngay.")


if __name__ == "__main__":
    main()
