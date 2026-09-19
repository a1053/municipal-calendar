import json, sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/schedule.json').read_text(encoding='utf-8'))
con=connect()
for j,home,away,start,venue,city,status,hs,aws in data['fixtures']:
    uid=f"mun-liga-2026-j{j}-{home.lower().replace(' ','-').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')}-{away.lower().replace(' ','-').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')}"
    now=datetime.now(timezone.utc).isoformat()
    con.execute('''INSERT INTO matches(uid,competition,season,round,home_team,away_team,start_utc,venue,city,status,home_score,away_score,source_url,source_name,source_updated_at,last_changed_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(uid) DO UPDATE SET competition=excluded.competition,season=excluded.season,round=excluded.round,home_team=excluded.home_team,away_team=excluded.away_team,start_utc=excluded.start_utc,venue=excluded.venue,city=excluded.city,status=excluded.status,home_score=excluded.home_score,away_score=excluded.away_score,source_url=excluded.source_url,source_name=excluded.source_name,source_updated_at=excluded.source_updated_at''',
                (uid,'Liga Nacional - Apertura 2026','2026',f'Jornada {j}',home,away,start,venue,city,status,hs,aws,'https://ligagt.org/calendar/calendarioactual/','seed',now,now))
con.commit(); con.close(); print('Seeded',len(data['fixtures']),'Liga matches')
