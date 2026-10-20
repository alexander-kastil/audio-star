# audio-star feature list

Collected features, not yet planned or built.

## 1. Play my playlists on the WiiM speakers (YouTube, or Spotify / SoundCloud)

- Request: properly play my YouTube playlists (the list at https://www.youtube.com/feed/playlists). Spotify (https://open.spotify.com/) and SoundCloud would also be ok.
- First version: playing my lists is enough; adding tracks to the queue is not needed.
- Known so far:
  - WiiM Home plays none of the three itself. Its built-in service table names `YouTubeMusic`, `Spotify` and `SoundCloud` (icons only), and none of them is in the four services the app offers (`data\LPSupportedStreamServiceConfig.json`).
  - Spotify reaches the speaker as Spotify Connect: WiiM Home treats `MEDIATYPE_SPOTIFY` as a source it cannot queue into (`LPClientFramework.LPQueueManager`, `queueSpecialMediaType`).
  - `yt-dlp` and `ffmpeg` are installed (`C:\ProgramData\chocolatey\bin`).
  - The speaker plays any HTTP track list handed to it with UPnP `CreateQueue` (see `wiim-home-feature-map.md` 3.3 and 3.5), the same path WiiM Home uses for local music.
