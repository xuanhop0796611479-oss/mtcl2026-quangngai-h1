# -*- coding: utf-8 -*-
"""Tải sheet 'DS_MS online ngày' từ Google Sheets và thống kê mất sóng cho Quảng Ngãi."""
import subprocess, os, pandas as pd

SHEET_ID="1FHHw-pJSkyRSQ_qFM92ZQMF6vFbS4XfV0T3jKzcI1Lk"
GID="352339760"

def download_csv(path, sheet_url=None):
    if sheet_url:
        import re
        mid=re.search(r'/d/([\w-]+)', sheet_url); mg=re.search(r'gid=(\d+)', sheet_url)
        sid=mid.group(1) if mid else SHEET_ID; gid=mg.group(1) if mg else GID
    else:
        sid, gid = SHEET_ID, GID
    url="https://docs.google.com/spreadsheets/d/%s/export?format=csv&gid=%s"%(sid, gid)
    subprocess.run(["curl","-skL","-o",path,url], check=True)
    if not os.path.exists(path) or os.path.getsize(path)<1000:
        raise RuntimeError("Không tải được CSV từ Google Sheet (kiểm tra quyền chia sẻ / mạng).")
    return path

def analyze(csv_path, province_kw="Quảng Ngãi"):
    df=pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    cols=['PROVINCE','DISTRICT','SITE_ID','NETWORK','PRIORITY','START_TIME','EDATE_TIME','SO_PHUT','NN_CAP_1','NN_CAP_2','NN_CAP_3']
    qn=df[df['PROVINCE'].str.contains(province_kw, na=False)][cols].copy()
    qn=qn[qn['SITE_ID'].str.strip()!='']
    def tomin(x):
        x=str(x).strip().replace('.','').replace(',','.')
        try: return float(x)
        except: return 0.0
    qn['MIN']=qn['SO_PHUT'].apply(tomin)
    qn['ONGOING']=qn['EDATE_TIME'].str.strip()==''
    long=qn.sort_values('MIN', ascending=False).head(15)
    grp=qn.groupby('SITE_ID').agg(so_lan=('MIN','size'), tong_phut=('MIN','sum'), max_phut=('MIN','max'),
        district=('DISTRICT','first'), nets=('NETWORK', lambda s:'/'.join(sorted(set(s))))).reset_index()
    freq=grp.sort_values(['so_lan','tong_phut'], ascending=False).head(15)
    out={}
    out['summary']={'records':int(len(qn)),'total_min':round(float(qn['MIN'].sum()),1),
        'ongoing':int(qn['ONGOING'].sum()),'sites':int(qn['SITE_ID'].nunique()),
        'avg_min':round(float(qn['MIN'].mean()),1) if len(qn) else 0}
    out['longest']=[{'site':r.SITE_ID,'net':r.NETWORK,'district':r.DISTRICT,'min':round(r.MIN,1),
        'ongoing':bool(r.ONGOING),'start':r.START_TIME,'cause':r.NN_CAP_1} for _,r in long.iterrows()]
    out['freq']=[{'site':r.SITE_ID,'district':r.district,'nets':r.nets,'count':int(r.so_lan),
        'total':round(r.tong_phut,1),'max':round(r.max_phut,1)} for _,r in freq.iterrows()]
    out['cause']={k:int(v) for k,v in qn['NN_CAP_1'].replace('','Khác').value_counts().items()}
    out['net']={k:int(v) for k,v in qn['NETWORK'].value_counts().items()}
    out['ongoing_list']=[{'site':r.SITE_ID,'net':r.NETWORK,'district':r.DISTRICT,'min':round(r.MIN,1),
        'start':r.START_TIME,'cause':r.NN_CAP_1} for _,r in qn[qn['ONGOING']].sort_values('MIN',ascending=False).iterrows()]
    return out
