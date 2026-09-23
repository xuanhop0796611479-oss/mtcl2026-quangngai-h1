# Trien khai dashboard len Vercel

## Vi sao phai chia lam 2 phan

Vercel la nen tang **serverless / static** - KHONG chay tien trinh nen lien tuc
vo han, va rat kho chay Playwright (Chromium) trong ham serverless. Vi vay
ban khong the bung nguyen `run_service.py` (vong lap 24/7) len Vercel. Cach
dung dan la tach theo dung ban chat du lieu:

| Phan | Chay o dau | Tan suat |
|------|-----------|----------|
| **Mat song** (Google Sheet - nhe, chi la CSV) | Ham Vercel `api/index.py` | render **truc tiep moi khi mo trang**; trinh duyet tu tai lai 15 phut |
| **KPI ngay/thang** (sMartF - can trinh duyet Playwright) | **GitHub Actions** (cron) | **1 lan/ngay luc 09:00**, ket qua ghi vao `data/kpi.json` |

Ham Vercel doc `data/kpi.json` (do Actions cap nhat) + tai Sheet moi -> ghep lai
thanh dashboard. Ket qua: nhan vien mo 1 link, xem moi noi tren PC/dien thoai,
so lieu luon moi.

## Cau truc thu muc (day chinh la repo ban push len GitHub)

```
api/index.py                     <- ham render dashboard (Vercel)
vercel.json                      <- dinh tuyen moi request vao ham tren
requirements.txt                 <- pandas, openpyxl
lib/fetch_sheet.py               <- (co san) phan tich mat song
lib/fetch_smartf.py              <- (co san) lay sMartF - dung boi Actions
lib/build_outputs.py             <- (co san) dung dashboard
lib/dashboard_template.html      <- *** BAN PHAI THEM ***
lib/app_template.js              <- *** BAN PHAI THEM ***
lib/vendor/chart.umd.min.js      <- (tuy chon) de chay offline
data/kpi.json                    <- KPI do Actions cap nhat (da co ban rong)
scripts/build_kpi.py             <- Actions chay file nay moi sang
.github/workflows/smartf-daily.yml
```

> **Quan trong:** 3 file mau `dashboard_template.html`, `app_template.js`,
> `vendor/chart.umd.min.js` KHONG co trong goi nay (ban chua tai len). Phai chep
> chung vao thu muc `lib/` truoc khi deploy, neu khong ham se bao loi thieu file.

## Cac buoc thuc hien

### 1. Dua code len GitHub
```bash
cd vercel
git init
git add .
git commit -m "dashboard mtcl"
git branch -M main
git remote add origin https://github.com/<tai-khoan>/<ten-repo>.git
git push -u origin main
```

### 2. Khai bao secret cho GitHub Actions
Vao repo -> **Settings -> Secrets and variables -> Actions -> New repository secret**,
tao 2 secret:
- `SMARTF_USER` = tai khoan sMartF
- `SMARTF_PASS` = mat khau sMartF

Sau do vao tab **Actions**, chon workflow "sMartF daily KPI" va bam **Run workflow**
de chay thu ngay 1 lan (khong can doi den 9h sang). Kiem tra `data/kpi.json` da
duoc cap nhat.

### 3. Ket noi voi Vercel
1. Dang nhap https://vercel.com bang tai khoan GitHub.
2. **Add New -> Project -> Import** repo vua tao.
3. Framework Preset: **Other** (khong can build command). Vercel tu nhan
   `api/*.py` la Python Serverless Function nho `requirements.txt`.
4. (Tuy chon) o **Settings -> Environment Variables** them:
   - `SHEET_ID`, `SHEET_GID` neu Sheet khac mac dinh trong `fetch_sheet.py`.
   - `REFRESH_SEC` neu muon doi chu ky tu tai lai (mac dinh 900 giay = 15 phut).
5. Bam **Deploy**. Xong, ban co 1 link dang `https://<ten-du-an>.vercel.app`.

### 4. Chia se cho nhan vien
Gui link `https://<ten-du-an>.vercel.app` cho nhan vien. Mo tren trinh duyet
nao (PC hay dien thoai) cung xem duoc; trang tu tai lai moi 15 phut.

## Lich hoat dong sau khi deploy
- **Mat song:** cap nhat moi 15 phut (thuc te la moi khi tai lai trang, du lieu
  lay truc tiep tu Google Sheet, co cache CDN 5 phut cho nhe tai).
- **KPI ngay/thang:** GitHub Actions chay luc **02:00 UTC = 09:00 gio VN** moi
  ngay, commit `kpi.json` -> Vercel tu deploy lai -> trang co so lieu moi.

## Luu y gioi han Vercel
- Ham serverless co gioi han thoi gian (10s goi Hobby). Tai + phan tich Sheet
  thuong xong trong vai giay; neu Sheet qua lon co the can nang cap goi.
- Tong dung luong ham co pandas ~ vai chuc MB, van nam trong han muc Hobby.
- Neu khong muon dung GitHub Actions, ban co the chay `scripts/build_kpi.py`
  tren 1 may bat kem (cron 9h sang) roi commit/push `data/kpi.json` len repo -
  ket qua tuong duong.

## Cap nhat v2: them 2 tab moi

Dashboard nay da bo sung 2 tab:
- **Tab "Xa/phuong chua dat"**: danh sach xa/phuong KHONG DAT MTCL2026 cua
  ngay lien truoc (hom qua). Nguon: sMartF > MTCL > 2026_V2 > PHUONG_XA > NGAY,
  loc tinh Quang Ngai, Danh gia = KHONG DAT.
- **Tab "Cell 4G luu luong = 0"**: danh sach cell 4G co TRAFFIC_4G (MB) = 0.
  Nguon: sMartF > ran4g > EUTrancell > General, loc tinh Quang Ngai.

Hai bao cao nay do `scripts/build_kpi.py` tu dong lay them moi sang (goi
`fetch_smartf.run_extra(...)`) va ghi vao `data/kpi.json` (cac khoa
`xa_fail`, `xa_date`, `cell4g`, `cell4g_date`). Neu 1 trong 2 bao cao loi thi
pipeline VAN giu duoc KPI ngay/thang - tab tuong ung chi hien "chua lay duoc
du lieu" cho lan chay sau.

