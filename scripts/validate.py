from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'public/municipal.ics'
text=p.read_text(encoding='utf-8')
events=text.count('BEGIN:VEVENT')
uids=re.findall(r'^UID:(.+)$',text,re.M)
seqs=re.findall(r'^SEQUENCE:(\d+)$',text,re.M)
assert text.startswith('BEGIN:VCALENDAR') and text.strip().endswith('END:VCALENDAR'), 'Invalid VCALENDAR envelope'
assert events >= 22, f'Expected at least 22 events, got {events}'
assert len(uids)==events and len(set(uids))==events, 'UIDs must be unique'
assert len(seqs)==events, 'Every event needs SEQUENCE'
print(f'ICS OK: {events} events; {len(set(uids))} unique UIDs')
