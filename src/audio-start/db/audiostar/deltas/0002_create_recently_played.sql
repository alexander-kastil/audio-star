CREATE TABLE IF NOT EXISTS recent_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT NULL,
    artwork_uri TEXT NULL,
    played_at INTEGER NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_recent_items_identity ON recent_items (kind, source_id, title);
CREATE INDEX IF NOT EXISTS ix_recent_items_played_at ON recent_items (played_at DESC);
