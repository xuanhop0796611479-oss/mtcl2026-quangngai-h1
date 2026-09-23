# -*- coding: utf-8 -*-
"""Chay boi GitHub Actions moi ngay 09:00 (gio VN): dang nhap sMartF, xuat
day.xlsx/month.xlsx + xa.xlsx (cap xa/phuong) + cell4g.xlsx (cell 4G),
trich KPI va ghi data/kpi.json de Vercel doc.
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
    xa = str(data_dir / "xa.xlsx")
    g4 = str(data_dir / "cell4g.xlsx")

    today = datetime.date.today()
    yday = today - datetime.timedelta(days=1)
    frm = "%d/1/%d" % (today.month, today.year)
    to = "%d/%d/%d" % (today.month, today.day, today.year)
    yd = "%d/%d/%d" % (yday.month, yday.day, yday.year)   # ngay lien truoc (M/D/YYYY)

    # --- Bao cao chinh (NGAY + THANG) cap tinh ---
    fetch_smartf.run(user, pw, day, month, frm, to)
    daily, monthly = build_outputs.extract_kpi(day, month)

    # --- 2 bao cao bo sung: xa/phuong chua dat + cell 4G luu luong = 0 ---
    # Neu 1 phan loi thi van giu duoc du lieu chinh (khong lam sap pipeline).
    xa_fail, xa_date = [], ""
    cell4g, g4_date = {"list": [], "summary": {"total": 0, "zero": 0}}, ""
    try:
        got = fetch_smartf.run_extra(user, pw, xa, g4, yd, yd)
        if got.get("xa") and os.path.exists(xa):
            xa_fail, xa_date = build_outputs.extract_xa_fail(xa)
            print("[OK] xa/phuong chua dat:", len(xa_fail), "| ngay:", xa_date)
        if got.get("g4") and os.path.exists(g4):
            cell4g, g4_date = build_outputs.extract_4g_zero(g4)
            print("[OK] cell 4G luu luong=0:", cell4g["summary"], "| ngay:", g4_date)
    except Exception as e:
        print("[!] Loi khi lay 2 bao cao bo sung:", repr(e))

    payload = {
        "daily": daily,
        "monthly": monthly,
        "xa_fail": xa_fail,
        "xa_date": xa_date or yd,
        "cell4g": cell4g,
        "cell4g_date": g4_date or yd,
        "updated": today.isoformat(),
    }
    (data_dir / "kpi.json").write_text(
        json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
    print("[OK] da cap nhat data/kpi.json:", len(daily), "ngay.")


if __name__ == "__main__":
    main()
