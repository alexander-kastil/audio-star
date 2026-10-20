CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE COLLATE NOCASE,
    size INTEGER NOT NULL,
    modified_ticks INTEGER NOT NULL,
    title TEXT NOT NULL,
    artist TEXT NULL,
    album_artist TEXT NULL,
    album TEXT NULL,
    genre TEXT NULL,
    track_number INTEGER NULL,
    disc_number INTEGER NULL,
    year INTEGER NULL,
    duration_ms INTEGER NOT NULL,
    has_cover INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_tracks_album ON tracks (album, album_artist);
CREATE INDEX IF NOT EXISTS ix_tracks_artist ON tracks (artist);
CREATE INDEX IF NOT EXISTS ix_tracks_genre ON tracks (genre);
