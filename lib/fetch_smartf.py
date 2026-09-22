# -*- coding: utf-8 -*-
"""Đăng nhập sMartF và xuất 2 báo cáo (NGÀY + THÁNG) MTCL2026_V2 - tỉnh Quảng Ngãi.
Chạy độc lập: python fetch_smartf.py  (đọc cấu hình từ biến môi trường / .env)
"""
import os, sys, time
from playwright.sync_api import sync_playwright

LOGIN="https://smartf.mobifone.vn/auth/login"
REPORT="https://smartf.mobifone.vn/vienthong/hanhchinhhaicapchitiet"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SEL_PROV="s=>{for(const o of s.options){if(o.textContent.replace(/\\u00a0/g,' ').trim()=='%s'){s.value=o.value;s.dispatchEvent(new Event('change',{bubbles:true}));break;}}}"

def _click_leaf(p,label):
    loc=p.locator("a.bp3-menu-item:has-text('%s')"%label); n=loc.count()
    for i in range(n):
        el=loc.nth(i); cls=el.get_attribute("class") or ""
        if "dismiss" in cls and el.is_visible():
            el.click(); return True
    return False

def _wait_render(fr,to=120):
    for _ in range(to):
        aw=fr.query_selector("#ReportViewerControl_AsyncWait_Wait")
        st=aw.get_attribute("style") if aw else ""
        if aw is None or "none" in (st or ""): return True
        time.sleep(1)
    return False

def _open_leaf(p, leaf):
    p.click("div.side-menu-button:has-text('MTCL')"); time.sleep(1.5)
    p.hover("a.bp3-menu-item:has-text('2026_V2')"); time.sleep(1.5)
    p.hover("a.bp3-menu-item:has-text('TỈNH_THÀNH PHỐ')"); time.sleep(1.5)
    _click_leaf(p, leaf); time.sleep(14)
    ifr=p.query_selector("iframe[src*='ReportViewer.aspx']")
    return ifr.content_frame()

def _export_excel(page, fr, out_path):
    with page.expect_download(timeout=90000) as di:
        fr.evaluate("()=>{$find('ReportViewerControl').exportReport('EXCELOPENXML');}")
    di.value.save_as(out_path)

def run(user, password, out_day, out_month, from_date, to_date, province="Quang Ngai", headless=True):
    """from_date/to_date dạng M/D/YYYY (ví dụ 9/1/2026)."""
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=headless, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx=b.new_context(viewport={"width":1680,"height":1050}, ignore_https_errors=True, accept_downloads=True, user_agent=UA)
        p=ctx.new_page()
        # login
        p.goto(LOGIN, timeout=60000, wait_until="domcontentloaded"); time.sleep(4)
        p.fill("input[name=username]", user)
        p.fill("input[name=password]", password)
        p.click("button:has-text('Đăng nhập')"); time.sleep(8)
        # go to report SPA
        p.goto(REPORT, timeout=60000, wait_until="domcontentloaded"); time.sleep(10)
        if "auth/login" in p.url and p.query_selector("input[name=username]"):
            raise RuntimeError("Đăng nhập sMartF thất bại - kiểm tra tài khoản/mật khẩu.")
        # ---- NGÀY ----
        fr=_open_leaf(p, "NGÀY"); time.sleep(2)
        fr.fill("#ReportViewerControl_ctl04_ctl03_txtValue", from_date)
        fr.fill("#ReportViewerControl_ctl04_ctl05_txtValue", to_date)
        fr.eval_on_selector("#ReportViewerControl_ctl04_ctl09_ddValue", SEL_PROV % province)
        fr.click("#ReportViewerControl_ctl04_ctl00"); time.sleep(6); _wait_render(fr); time.sleep(4)
        _export_excel(p, fr, out_day)
        print("[OK] đã xuất báo cáo NGÀY:", out_day)
        # reload report page for a clean THANG navigation
        p.goto(REPORT, timeout=60000, wait_until="domcontentloaded"); time.sleep(10)
        fr=_open_leaf(p, "THÁNG"); time.sleep(2)
        fr.click("#ReportViewerControl_ctl04_ctl00"); time.sleep(6); _wait_render(fr); time.sleep(4)
        _export_excel(p, fr, out_month)
        print("[OK] đã xuất báo cáo THÁNG:", out_month)
        b.close()

if __name__=="__main__":
    import datetime
    u=os.environ.get("SMARTF_USER"); pw_=os.environ.get("SMARTF_PASS")
    if not u or not pw_:
        sys.exit("Thiếu SMARTF_USER / SMARTF_PASS (đặt trong .env hoặc biến môi trường).")
    today=datetime.date.today()
    frm="%d/1/%d"%(today.month, today.year)
    to="%d/%d/%d"%(today.month, today.day, today.year)
    run(u, pw_, "day.xlsx", "month.xlsx", frm, to)
