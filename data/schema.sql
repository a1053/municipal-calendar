CREATE TABLE IF NOT EXISTS matches (
  uid TEXT PRIMARY KEY,
  competition TEXT NOT NULL,
  season TEXT NOT NULL,
  round TEXT,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  start_utc TEXT,
  venue TEXT,
  city TEXT,
  status TEXT NOT NULL DEFAULT 'scheduled',
  home_score INTEGER,
  away_score INTEGER,
  source_url TEXT,
  source_name TEXT,
  source_updated_at TEXT,
  sequence INTEGER NOT NULL DEFAULT 0,
  last_changed_at TEXT,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS match_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT NOT NULL,
  changed_at TEXT NOT NULL,
  old_payload TEXT,
  new_payload TEXT,
  reason TEXT
);
CREATE TABLE IF NOT EXISTS sources (
  name TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  last_checked_at TEXT,
  last_success_at TEXT,
  last_error TEXT
);
