from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from .db import connect

app = FastAPI(title='CSD Municipal Calendar')
ROOT = Path(__file__).resolve().parents[1]
ICS = ROOT / 'public' / 'municipal.ics'

@app.get('/')
def home():
    return {'name':'CSD Municipal Calendar','feed':'/municipal.ics','status':'ok'}

@app.get('/municipal.ics')
def feed():
    if not ICS.exists():
        from .ics import generate
        generate()
    return FileResponse(ICS, media_type='text/calendar; charset=utf-8', filename='municipal.ics')

@app.get('/api/matches')
def matches():
    con = connect()
    rows = con.execute('SELECT * FROM matches ORDER BY start_utc').fetchall()
    return JSONResponse([dict(r) for r in rows])
