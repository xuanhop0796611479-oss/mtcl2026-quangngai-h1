# -*- coding: utf-8 -*-
"""Dang nhap sMartF va xuat cac bao cao MTCL2026_V2 - tinh Quang Ngai.

Bao cao lay duoc:
  - NGAY   : MTCL > 2026_V2 > TINH_THANH PHO > NGAY   (cap tinh, dau thang -> hom nay)
  - THANG  : MTCL > 2026_V2 > TINH_THANH PHO > THANG  (luy ke thang)
  - XA     : MTCL > 2026_V2 > PHUONG_XA > NGAY         (cap xa/phuong, mot ngay)
  - 4G     : ran4g > EUTrancell > General              (cap cell 4G, mot ngay)

Chay doc lap: python fetch_smartf.py  (doc cau hinh tu bien moi truong / .env)
"""
import os, sys, time
from playwright.sync_api import sync_playwright

LOGIN="https://smartf.mobifone.vn/auth/login"
REPORT="https://smartf.mobifone.vn/vienthong/hanhchinhhaicapchitiet"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# JS: chon tinh tren 1 dropdown cu the (giu tuong thich code cu)
SEL_PROV="s=>{for(const o of s.options){if(o.textContent.replace(/\\u00a0/g,' ').trim()=='%s'){s.value=o.value;s.dispatchEvent(new Event('change',{bubbles:true}));break;}}}"

# JS: chon tinh tren BAT KY dropdown nao co option khop (ben hon, khong phu thuoc chi so ctl)
SEL_PROV_ANY="""(prov)=>{
  let done=[];
  document.querySelectorAll("select[id*='ddValue']").forEach(s=>{
    for(const o of s.options){
      if(o.textContent.replace(/\\u00a0/g,' ').trim()==prov){
        s.value=o.value; s.dispatchEvent(new Event('change',{bubbles:true})); done.push(s.id); break;
      }
    }
  });
  return done;
}"""


def _click_leaf(p,label):
    loc=p.locator("a.bp3-menu-item:has-text('%s')"%label); n=loc.count()
    for i in range(n):
        el=loc.nth(i); cls=el.get_attribute("class") or ""
        if "dismiss" in cls and el.is_visible():
            el.click(); return True
    for i in range(n):
        el=loc.nth(i)
        if el.is_visible():
            el.click(); return True
    return False


def _hover_first(p, labels):
    for lb in labels:
        loc=p.locator("a.bp3-menu-item:has-text('%s')"%lb)
        if loc.count()>0:
            try:
                loc.first.hover(); return True
            except Exception:
                pass
    return False


def _wait_render(fr,to=120):
    for _ in range(to):
        aw=fr.query_selector("#ReportViewerControl_AsyncWait_Wait")
        st=aw.get_attribute("style") if aw else ""
        if aw is None or "none" in (st or ""): return True
        time.sleep(1)
    return False


def _open_mtcl_leaf(p, sub_labels, leaf):
    p.click("div.side-menu-button:has-text('MTCL')"); time.sleep(1.5)
    _hover_first(p, ["2026_V2"]); time.sleep(1.5)
    _hover_first(p, sub_labels); time.sleep(1.5)
    _click_leaf(p, leaf); time.sleep(14)
    ifr=p.query_selector("iframe[src*='ReportViewer.aspx']")
    return ifr.content_frame()


def _open_ran4g_general(p):
    for lb in ["ran4g", "RAN4G", "RAN 4G"]:
        btn=p.locator("div.side-menu-button:has-text('%s')"%lb)
        if btn.count()>0:
            btn.first.click(); break
    time.sleep(1.5)
    _hover_first(p, ["EUTrancell", "eUTrancell", "EUTRANCELL"]); time.sleep(1.5)
    _click_leaf(p, "General"); time.sleep(14)
    ifr=p.query_selector("iframe[src*='ReportViewer.aspx']")
    return ifr.content_frame()


def _set_date_range(fr, frm, to):
    ids=fr.eval_on_selector_all(
        "input[type=text][id*='txtValue']",
        "els=>els.filter(e=>e.offsetParent!==null).map(e=>e.id)")
    if len(ids)>=2:
        fr.fill('#'+ids[0], frm)
        fr.fill('#'+ids[1], to)
        return True
    return False


def _set_province_any(fr, province):
    try:
        return fr.evaluate(SEL_PROV_ANY, province)
    except Exception:
        return []


def _submit(fr):
    for sel in ["#ReportViewerControl_ctl04_ctl00",
                "input[id$='ctl04_ctl00']",
                "input[value*='Xem'], input[title*='Xem']"]:
        el=fr.query_selector(sel)
        if el:
            try:
                el.click(); return True
            except Exception:
                pass
    return False


def _export_excel(page, fr, out_path):
    with page.expect_download(timeout=90000) as di:
        fr.evaluate("()=>{$find('ReportViewerControl').exportReport('EXCELOPENXML');}")
    di.value.save_as(out_path)


def _goto_retry(p, url, tries=4, timeout=120000):
    """Mo trang co retry: sMartF doi khi tai rat cham tu server ngoai VN.
    Thu nhieu lan, noi long dieu kien cho tai (commit -> domcontentloaded -> load)."""
    waits = ["commit", "domcontentloaded", "load", "domcontentloaded"]
    last = None
    for i in range(tries):
        try:
            p.goto(url, timeout=timeout, wait_until=waits[i % len(waits)])
            return True
        except Exception as e:
            last = e
            print("[i] Thu mo lai trang (lan %d/%d): %s" % (i + 1, tries, url))
            time.sleep(5)
    raise RuntimeError(
        "Khong mo duoc trang sMartF sau %d lan thu (%s). "
        "Rat co the server GitHub khong truy cap duoc he thong sMartF noi bo MobiFone. "
        "Loi goc: %r" % (tries, url, last))


def _login(p, user, password):
    _goto_retry(p, LOGIN); time.sleep(4)
    p.fill("input[name=username]", user)
    p.fill("input[name=password]", password)
    p.click("button:has-text('\u0110\u0103ng nh\u1eadp')"); time.sleep(8)
    _goto_retry(p, REPORT); time.sleep(10)
    if "auth/login" in p.url and p.query_selector("input[name=username]"):
        raise RuntimeError("Dang nhap sMartF that bai - kiem tra tai khoan/mat khau.")


def run(user, password, out_day, out_month, from_date, to_date, province="Quang Ngai", headless=True):
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=headless, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx=b.new_context(viewport={"width":1680,"height":1050}, ignore_https_errors=True, accept_downloads=True, user_agent=UA)
        p=ctx.new_page()
        _login(p, user, password)
        fr=_open_mtcl_leaf(p, ["T\u1ec8NH_TH\u00c0NH PH\u1ed0","T\u1ec8NH_TH\u00c0NH"], "NG\u00c0Y"); time.sleep(2)
        fr.fill("#ReportViewerControl_ctl04_ctl03_txtValue", from_date)
        fr.fill("#ReportViewerControl_ctl04_ctl05_txtValue", to_date)
        fr.eval_on_selector("#ReportViewerControl_ctl04_ctl09_ddValue", SEL_PROV % province)
        fr.click("#ReportViewerControl_ctl04_ctl00"); time.sleep(6); _wait_render(fr); time.sleep(4)
        _export_excel(p, fr, out_day)
        print("[OK] da xuat bao cao NGAY:", out_day)
        _goto_retry(p, REPORT); time.sleep(10)
        fr=_open_mtcl_leaf(p, ["T\u1ec8NH_TH\u00c0NH PH\u1ed0","T\u1ec8NH_TH\u00c0NH"], "TH\u00c1NG"); time.sleep(2)
        fr.click("#ReportViewerControl_ctl04_ctl00"); time.sleep(6); _wait_render(fr); time.sleep(4)
        _export_excel(p, fr, out_month)
        print("[OK] da xuat bao cao THANG:", out_month)
        b.close()


def run_extra(user, password, out_xa, out_4g, xa_date, g4_date, province="Quang Ngai", headless=True):
    """Lay 2 bao cao moi: XA/PHUONG (1 ngay) + cell 4G General (1 ngay).
    xa_date / g4_date dang M/D/YYYY. Tra ve dict {'xa':bool,'g4':bool}."""
    got={"xa": False, "g4": False}
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=headless, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx=b.new_context(viewport={"width":1680,"height":1050}, ignore_https_errors=True, accept_downloads=True, user_agent=UA)
        p=ctx.new_page()
        _login(p, user, password)
        try:
            fr=_open_mtcl_leaf(p, ["PH\u01af\u1edcNG_X\u00c3","X\u00c3_PH\u01af\u1edcNG","X\u00c3/PH\u01af\u1edcNG","X\u00c3"], "NG\u00c0Y"); time.sleep(2)
            _set_date_range(fr, xa_date, xa_date)
            _set_province_any(fr, province); time.sleep(1)
            _submit(fr); time.sleep(6); _wait_render(fr); time.sleep(4)
            _export_excel(p, fr, out_xa)
            got["xa"]=True
            print("[OK] da xuat bao cao XA/PHUONG:", out_xa)
        except Exception as e:
            print("[!] Khong lay duoc bao cao XA/PHUONG:", repr(e))
        try:
            p.goto(REPORT, timeout=60000, wait_until="domcontentloaded"); time.sleep(10)
            fr=_open_ran4g_general(p); time.sleep(2)
            _set_date_range(fr, g4_date, g4_date)
            _set_province_any(fr, province); time.sleep(1)
            _submit(fr); time.sleep(6); _wait_render(fr); time.sleep(4)
            _export_excel(p, fr, out_4g)
            got["g4"]=True
            print("[OK] da xuat bao cao 4G EUTrancell:", out_4g)
        except Exception as e:
            print("[!] Khong lay duoc bao cao 4G:", repr(e))
        b.close()
    return got


if __name__=="__main__":
    import datetime
    u=os.environ.get("SMARTF_USER"); pw_=os.environ.get("SMARTF_PASS")
    if not u or not pw_:
        sys.exit("Thieu SMARTF_USER / SMARTF_PASS (dat trong .env hoac bien moi truong).")
    today=datetime.date.today()
    yday=today-datetime.timedelta(days=1)
    frm="%d/1/%d"%(today.month, today.year)
    to="%d/%d/%d"%(today.month, today.day, today.year)
    yd="%d/%d/%d"%(yday.month, yday.day, yday.year)
    run(u, pw_, "day.xlsx", "month.xlsx", frm, to)
    run_extra(u, pw_, "xa.xlsx", "cell4g.xlsx", yd, yd)
