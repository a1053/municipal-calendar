from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from .db import connect

GT = ZoneInfo('America/Guatemala')
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public' / 'municipal.ics'

def esc(s):
    return str(s or '').replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')

def dt_ics(iso):
    if not iso:
        return None
    d = datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone(timezone.utc)
    return d.strftime('%Y%m%dT%H%M%SZ')

def generate():
    con = connect()
    rows = con.execute("SELECT * FROM matches WHERE status != 'cancelled' ORDER BY start_utc").fetchall()
    lines = [
      'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//CSD Municipal//Calendario Oficial//GT',
      'CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-CALNAME:CSD Municipal',
      'X-WR-TIMEZONE:America/Guatemala'
    ]
    now = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    for r in rows:
        lines += ['BEGIN:VEVENT', f'UID:{esc(r["uid"])}', f'SEQUENCE:{r["sequence"]}', f'DTSTAMP:{now}']
        if r['start_utc']:
            start = dt_ics(r['start_utc'])
            lines.append(f'DTSTART:{start}')
            # End is intentionally one hour after kickoff; can be customized later.
            d = datetime.fromisoformat(r['start_utc'].replace('Z','+00:00'))
            end = d.timestamp() + 3600
            lines.append('DTEND:' + datetime.fromtimestamp(end, timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        summary = f"{r['home_team']} vs {r['away_team']}"
        if r['status'] == 'postponed': summary = 'REPROGRAMADO — ' + summary
        if r['status'] == 'finished' and r['home_score'] is not None: summary += f" ({r['home_score']}-{r['away_score']})"
        lines.append(f'SUMMARY:{esc(summary)}')
        desc = f"{r['competition']} | {r['round'] or ''} | Estado: {r['status']}"
        if r['notes']: desc += f"\\n{r['notes']}"
        if r['source_url']: desc += f"\\nFuente: {r['source_url']}"
        lines.append(f'DESCRIPTION:{esc(desc)}')
        if r['venue']: lines.append(f'LOCATION:{esc(r["venue"] + (", " + r["city"] if r["city"] else ""))}')
        if r['source_url']: lines.append(f'URL:{r["source_url"]}')
        lines += ['BEGIN:VALARM','TRIGGER:-PT60M','ACTION:DISPLAY','DESCRIPTION:Partido de Municipal en 1 hora','END:VALARM','END:VEVENT']
    lines.append('END:VCALENDAR')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\r\n'.join(lines) + '\r\n', encoding='utf-8')
    return OUT
