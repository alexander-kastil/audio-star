# Audio Star v1 plan

Stack: WPF on .NET 10 (Windows), C# libraries kept UI-free so a later port (Avalonia) only replaces `AudioStar.Desktop`.
Solution: `src\audio-start\AudioStar.slnx`.

| Project | Owns |
|---|---|
| `AudioStar.Core` | Shared contract (interfaces, records), settings store, `AppPaths`, `NetworkInfo` |
| `AudioStar.Speakers` | Discovery (SSDP, mDNS, manual IP, cache), UPnP SOAP and `httpapi` clients, event subscriptions, playback, queue, presets, inputs |
| `AudioStar.Devices` | Multiroom groups, device settings |
| `AudioStar.Library` | My Music (scan, SQLite), media and stream-proxy HTTP server, DLNA server, Home Share, Recently played |
| `AudioStar.Sources` | YouTube and SoundCloud (yt-dlp), Spotify (Web API + Connect), Radio (radio-browser.info) |
| `AudioStar.Desktop` | WPF shell, pages, tray, single instance, sleep prevention |

## v1 features

From WiiM Home: speaker discovery and manual add; device dashboard with groups and volumes; named groups (save, activate, ungroup); now playing and mini bar with live updates; queue (view, jump, remove); presets (view, play, save, delete); recently played; device settings (device, network, sound, inputs, outputs, hardware, Bluetooth, voice, audio cast, sync delay); My Music with the PC as media server; PC DLNA server; Home Share; radio (WiiM Radio equivalent); tray, single instance, sleep prevention.

From the feature list: play YouTube playlists (library and pasted URLs), SoundCloud playlists and likes, Spotify playlists (through Spotify Connect).

## Status (2026-10-19)

Run: `src\audio-start\AudioStar.Desktop\bin\Debug\net10.0-windows\AudioStar.exe`. Tests: 302 pass (`dotnet test src\audio-start\AudioStar.slnx`).

Verified live on the WiiM Amp: discovery; dashboard; mini bar and now playing; a 200-track YouTube playlist through the PC stream proxy; next track; queue view; radio; a SoundCloud set (HLS converted to FLAC by ffmpeg); recently played; reading every device settings tab; My Music scan and the music file server (range requests, files outside the music folders refused).

Not verified live: Spotify playback (the in-popup app setup and the sign-in work; the Web API answers 403 without Premium, which the owner does not have), the YouTube library through browser cookies, groups (only one speaker), writing settings, presets (the Amp has none), DLNA server, Home Share, tray, single instance, sleep prevention.

Known behaviour: the Amp's firmware sends no UPnP events, so the app polls every 1 to 2 seconds. GPU rendering paints a white window on this PC, so the app renders in software; set `AUDIOSTAR_HARDWARE_RENDER=1` to try the GPU. Inbound needs the `tools\firewall.ps1` rules.

## Not in v1

- TIDAL and Qobuz catalog browsing: WiiM Home borrows the speaker's tokens and WiiM's own OAuth app registration for these; needs the owner's decision.
- WiiM Radio's LinkPlay backend, analytics, feedback upload, cloud device state, WinSparkle updates: they run on LinkPlay's private keys and feeds. Radio uses the public radio-browser.info directory instead.
- macOS.

## Open

- The log grows without bound when a page's XAML throws during layout. On 2026-10-19 the forward `BasedOn` of `NowPlayingAlbum` threw on every layout pass from 19:32 until the restart at 19:39; `App`'s unhandled-exception handler logged the full stack and showed a toast each time (about 575,000 times), and `%LOCALAPPDATA%\AudioStar\logs\audiostar-20261019.log` reached 2 GB. Not fixed: repeated identical exceptions are neither deduplicated nor capped, and the log file has no size limit.
