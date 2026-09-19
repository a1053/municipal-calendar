"""Sync official Liga Nacional calendar, apply official overrides, and optionally enrich results from ESPN."""
import json, re, sys, unicodedata
from pathlib import Path
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect
from app.ics import generate
ROOT=Path(__file__).resolve().parents[1]
OFFICIAL='https://ligagt.org/calendar/calendarioactual/'
HEADERS={'User-Agent':'MunicipalCalendarBot/1.0 (+calendar sync)'}

def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')

def uid(j,home,away): return f'mun-liga-2026-j{j}-{slug(home)}-{slug(away)}'

def source_record(name,url,ok,error=None):
    con=connect(); now=datetime.now(timezone.utc).isoformat()
    con.execute('''INSERT INTO sources(name,url,last_checked_at,last_success_at,last_error) VALUES(?,?,?,?,?)
                   ON CONFLICT(name) DO UPDATE SET last_checked_at=excluded.last_checked_at,last_success_at=excluded.last_success_at,last_error=excluded.last_error''',(name,url,now,now if ok else None,error)); con.commit(); con.close()

def official_rows():
    r=requests.get(OFFICIAL,timeout=30,headers=HEADERS); r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser'); out=[]
    for tr in soup.find_all('tr'):
        cells=tr.find_all(['td','th'])
        if len(cells)<6: continue
        text=[c.get_text(' ',strip=True) for c in cells]
        if 'Municipal' not in text[1]: continue
        a=cells[0].find('a'); m=re.search(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})', a.get_text(' ',strip=True) if a else text[0])
        if not m: continue
        dt=datetime.fromisoformat(m.group(1)+'T'+m.group(2)).replace(tzinfo=__import__('zoneinfo').ZoneInfo('America/Guatemala')).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
        match=text[1]; home,away=[x.strip() for x in re.split(r'\s+vs\s+',match,maxsplit=1)]
        round_=text[5]; result=text[2]; status='finished' if re.match(r'^\d+\s*-\s*\d+$',result) else 'scheduled'
        hs=aws=None
        if status=='finished': hs,aws=[int(x) for x in re.split(r'\s*-\s*',result)]
        j=re.search(r'(\d+)',round_); j=int(j.group(1)) if j else None
        if j: out.append((uid(j,home,away),j,home,away,dt,status,hs,aws,OFFICIAL))
    return out

def upsert_official(rows):
    con=connect(); now=datetime.now(timezone.utc).isoformat(); changed=0
    for u,j,home,away,start,status,hs,aws,url in rows:
        old=con.execute('SELECT * FROM matches WHERE uid=?',(u,)).fetchone()
        if not old:
            con.execute('''INSERT INTO matches(uid,competition,season,round,home_team,away_team,start_utc,status,home_score,away_score,source_url,source_name,source_updated_at,last_changed_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(u,'Liga Nacional - Apertura 2026','2026',f'Jornada {j}',home,away,start,status,hs,aws,url,'Liga Nacional',now,now)); changed+=1
        else:
            oldvals=tuple(old[k] for k in ['start_utc','status','home_score','away_score','home_team','away_team','round'])
            newvals=(start,status,hs,aws,home,away,f'Jornada {j}')
            if oldvals!=newvals:
                con.execute('''UPDATE matches SET start_utc=?,status=?,home_score=?,away_score=?,home_team=?,away_team=?,round=?,source_url=?,source_name=?,source_updated_at=?,sequence=sequence+1,last_changed_at=? WHERE uid=?''',(start,status,hs,aws,home,away,f'Jornada {j}',url,'Liga Nacional',now,now,u))
                con.execute('INSERT INTO match_history(uid,changed_at,old_payload,new_payload,reason) VALUES(?,?,?,?,?)',(u,now,str(oldvals),str(newvals),'Liga Nacional sync')); changed+=1
    con.commit(); con.close(); return changed

def apply_overrides():
    overrides=json.loads((ROOT/'data/overrides.json').read_text(encoding='utf-8')); con=connect(); now=datetime.now(timezone.utc).isoformat(); changed=0
    for u,p in overrides.items():
        row=con.execute('SELECT * FROM matches WHERE uid=?',(u,)).fetchone()
        if not row: continue
        fields=[]; vals=[]
        for k,v in p.items():
            fields.append(f'{k}=?'); vals.append(v)
        current={k:row[k] for k in p}
        if any(current[k]!=v for k,v in p.items()):
            con.execute(f"UPDATE matches SET {','.join(fields)},source_url=?,source_name=?,source_updated_at=?,sequence=sequence+1,last_changed_at=? WHERE uid=?",(*vals,'https://ligagt.org/iniciot/','Liga Nacional — comunicado oficial',now,now,u))
            con.execute('INSERT INTO match_history(uid,changed_at,old_payload,new_payload,reason) VALUES(?,?,?,?,?)',(u,now,str(current),str(p),'Official override')); changed+=1
    con.commit(); con.close(); return changed

try:
    n=upsert_official(official_rows()); print('Official sync:',n,'changes'); source_record('Liga Nacional',OFFICIAL,True)
except Exception as e:
    print('Official sync failed:',e); source_record('Liga Nacional',OFFICIAL,False,str(e))
print('Overrides:',apply_overrides())
print(generate())
