# -*- coding: utf-8 -*-
"""Lấy dữ liệu sMartF + sheet mất sóng rồi xuất 1 trang TĨNH public/index.html.
Trang tĩnh này tự chứa (nhúng sẵn biểu đồ + dữ liệu), ai mở cũng xem được,
không cần máy chủ chạy nền — hợp để host miễn phí trên GitHub Pages / Netlify.

Chạy trong CI (GitHub Actions) mỗi sáng. Đọc tài khoản từ biến môi trường:
  SMARTF_USER, SMARTF_PASS  (bắt buộc)
  PROVINCE                  (mặc định 'Quang Ngai')
  SHEET_URL                 (tùy chọn)
"""
import os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LIB  = os.path.join(HERE, 'lib')
OUT_DIR = os.path.join(HERE, 'public')
sys.path.insert(0, LIB)
os.makedirs(OUT_DIR, exist_ok=True)

import fetch_smartf, fetch_sheet, build_outputs

# nội suy Chart.js từ static/ (build_outputs đọc từ lib/vendor; ta chỉ định lại)
build_outputs.HERE = LIB  # để build_dashboard tìm template trong lib/

def _inline_chart_into(html):
    return html

def main():
    user = os.environ.get('SMARTF_USER'); pwd = os.environ.get('SMARTF_PASS')
    if not user or not pwd:
        sys.exit('[LỖI] Thiếu SMARTF_USER / SMARTF_PASS trong biến môi trường (GitHub Secrets).')
    province = os.environ.get('PROVINCE', 'Quang Ngai')
    sheet_url = os.environ.get('SHEET_URL', '')
    today = datetime.date.today()
    day_x  = os.path.join(OUT_DIR, 'raw_day.xlsx')
    month_x = os.path.join(OUT_DIR, 'raw_month.xlsx')
    csv_p  = os.path.join(OUT_DIR, 'ds_ms.csv')
    frm = '%d/1/%d' % (today.month, today.year)
    to  = '%d/%d/%d' % (today.month, today.day, today.year)

    print('==> [1/3] Đăng nhập sMartF & xuất báo cáo NGÀY + THÁNG')
    fetch_smartf.run(user, pwd, day_x, month_x, frm, to, province=province, headless=True)
    print('==> [2/3] Tải sheet mất sóng')
    if sheet_url:
        fetch_sheet.download_csv(csv_p, sheet_url)
    else:
        fetch_sheet.download_csv(csv_p)
    ms = fetch_sheet.analyze(csv_p)
    daily, monthly = build_outputs.extract_kpi(day_x, month_x)

    print('==> [3/3] Dựng trang tĩnh public/index.html')
    # vendor chart.js: build_outputs tìm lib/vendor/chart.umd.min.js -> copy từ static
    vend = os.path.join(LIB, 'vendor'); os.makedirs(vend, exist_ok=True)
    import shutil
    shutil.copy(os.path.join(HERE, 'static', 'chart.umd.min.js'), os.path.join(vend, 'chart.umd.min.js'))
    gen_ts = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime('%d/%m/%Y %H:%M') + ' (giờ VN)'
    out_html = os.path.join(OUT_DIR, 'index.html')
    build_outputs.build_dashboard(daily, monthly, ms, out_html, gen_ts=gen_ts)

    # đổi nút "Cập nhật" (vốn dành cho chat) thành nhãn thông báo tự động
    html = open(out_html, encoding='utf-8').read()
    btn_block = ('<div style="margin-top:14px">\n'
        '<button id="btnUpdate" style="background:#fff;color:#0b3d91;border:none;padding:10px 18px;'
        'border-radius:10px;font-size:14px;font-weight:800;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.18)">'
        '\U0001f504 Cập nhật dữ liệu</button>\n</div>')
    note = ('<div style="margin-top:14px"><span class="badge" style="background:rgba(255,255,255,.28)">'
        '\U0001f552 Dữ liệu tự động cập nhật mỗi sáng 9h (giờ VN)</span></div>')
    html = html.replace(btn_block, note)
    open(out_html, 'w', encoding='utf-8').write(html)

    # dọn file thô, chỉ giữ trang tĩnh để publish
    for f in (day_x, month_x, csv_p):
        try: os.remove(f)
        except OSError: pass
    print('\n\u2705 Xong: %s' % out_html)

if __name__ == '__main__':
    main()
