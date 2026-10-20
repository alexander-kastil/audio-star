# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Audio Star is a Windows desktop controller for WiiM/LinkPlay speakers (WPF on .NET 10). It replaces the WiiM Home app and plays YouTube, SoundCloud, Spotify, radio and local music on the speaker. The protocol it speaks was reverse engineered from WiiM Home; the result is `wiim-home-feature-map.md`, with raw evidence (decompiled sources, live speaker replies) under `evidence/`.

## Commands

All paths are relative to the repo root; the solution is `src/audio-start/AudioStar.slnx`.

| Task | Command |
| --- | --- |
| Build the app | `dotnet build src/audio-start/AudioStar.Desktop/AudioStar.Desktop.csproj` |
| Run the app | `src/audio-start/AudioStar.Desktop/bin/Debug/net10.0-windows/AudioStar.exe` (add `--autostart` to start hidden in the tray) |
| Test one project | `dotnet test src/audio-start/AudioStar.Sources.Tests/AudioStar.Sources.Tests.csproj` (also `Speakers`, `Devices`, `Library`) |
| Run a single test | `dotnet test <test csproj> --filter "FullyQualifiedName~PlaylistCacheTests"` |
| Build the installer | `dotnet build src/audio-start/AudioStar.Setup/AudioStar.Setup.wixproj -c Release` (WiX v6, writes `setup/AudioStar.msi`) |
| Open the firewall (elevated, once) | `pwsh -ExecutionPolicy Bypass -File src/audio-start/tools/firewall.ps1` |

- **Restart after a change:** the running `AudioStar.exe` locks `bin`, so stop it, build the Desktop csproj, then start it again.
- **Don't run `dotnet test AudioStar.slnx`:** it does not refresh the Desktop `bin`, and because the WiX project is in the solution it also publishes and builds the MSI. Run the four test projects one by one instead.
- **Tests:** xUnit, FluentAssertions 7.2.0 and NSubstitute. Libraries tested with NSubstitute need `InternalsVisibleTo DynamicProxyGenAssembly2`.

## Architecture

One project per area. `AudioStar.Core` holds the shared contract: interfaces and records such as `ISpeakerSession`, `ISpeakerController`, `IMusicSource`, `IMediaServer` and `IEditablePlaylistSource`, plus settings and `AppPaths`. All libraries are UI-free so a later port only replaces `AudioStar.Desktop`.

| Project | Owns |
| --- | --- |
| `AudioStar.Speakers` | Discovery (SSDP `ssdp:wiimudevice`, mDNS `_linkplay._tcp`, manual IP), UPnP SOAP and `httpapi` clients, playback, queue, presets |
| `AudioStar.Devices` | Multiroom groups, device settings |
| `AudioStar.Library` | My Music (scan, SQLite), the media and stream-proxy HTTP server, DLNA server, Home Share, recently played |
| `AudioStar.Sources` | YouTube and SoundCloud through yt-dlp, Spotify (Web API plus Connect), radio (radio-browser.info) |
| `AudioStar.Desktop` | WPF shell (Fluent theme, Generic Host, CommunityToolkit.Mvvm), pages, tray, autostart, single instance |
| `AudioStar.Setup` | WiX MSI: per-machine install, Start Menu shortcut, firewall rules, autostart option |

### Talking to the speaker

- **Control:** UPnP SOAP on port 59152 (`rendertransport1`, `rendercontrol1`, and `PlayQueue1` for the queue). `https://<ip>/httpapi.asp?command=` also works, with no client certificate and certificate checks off.
- **State is polled:** the WiiM Amp firmware sends no UPnP NOTIFY, so `SpeakerSession` polls `GetInfoEx` every 1 to 2 seconds. Events are a bonus.
- **Queueing a playlist** (`FastPlayPlanner`): `CreateQueue` with the first one or two tracks, start playback, then `AppendTracksInQueueEx` in chunks of 50 with a short delay and one retry. Larger chunks make the speaker drop the connection.
- **Queue SourceName:** never set it to a service the speaker has built in. "SoundCloud" makes the speaker blank the URLs, so the SoundCloud source uses "SoundCloud via Audio Star".

### How YouTube and SoundCloud reach the speaker

The speaker never sees YouTube or SoundCloud URLs. Each queued track points at the PC: `http://<pc>:22545/stream/<sourceId>/<trackId>`. When the speaker fetches it, the `IStreamResolver` for that source resolves the real stream with yt-dlp, and `MediaServer` proxies it. HLS (all of SoundCloud) is transcoded with ffmpeg: to WAV with an exact length whenever the duration is known, so the speaker shows the time and seeks by HTTP byte range; to a FLAC pipe only for live or unknown durations.

The same `TrackURI` comes back from `GetPositionInfo`, which is how the UI finds the playing row.

yt-dlp is a managed copy at `%LOCALAPPDATA%\AudioStar\tools\yt-dlp.exe`, self-updated by `YtDlpUpdater`; the copy on PATH is only a fallback. Playlists added by URL are cached as JSON (`JsonPlaylistCache`) and refreshed in the background. `PlayAsync` plays the exact list last shown, so the start index always matches the row the user clicked.

### Signing in to services

- **One popup:** SoundCloud and Spotify sign in through a WebView2 window (`IWebSignIn` in Core, `Services/WebSignInService.cs`). `ConnectAsync` may open it; `ConnectSilentlyAsync` (startup and opening a source page) never does.
- **SoundCloud:** keeps the website's `oauth_token` cookie, because the official API needs a client secret and an Artist Pro app. yt-dlp gets it as `--username oauth --password <token>`, masked in logs. yt-dlp's flat list has no covers, artist or time for SoundCloud, so `SoundCloudSession` fills them, the card covers and the History card from api-v2 with the same token and the client id scraped from soundcloud.com.
- **Spotify:** the popup catches the redirect. With no client ID, Connect first opens the popup on developer.spotify.com's Create app page (redirect URI with a Copy button) and reads the new app's client ID from the page address; App settings still accepts one. The Web API needs Premium since February 2026; the owner has none, so Spotify answers 403 for them.
- **YouTube:** stays on browser cookies, because Google blocks sign-in inside embedded browsers.

### Ports and data

| Item | Value |
| --- | --- |
| Media and stream proxy | TCP 22545 |
| UPnP event sink | TCP 22534 |
| Spotify redirect URI (caught by the sign-in popup, nothing listens) | `http://127.0.0.1:22547/callback` |
| Settings, SQLite library | `%APPDATA%\AudioStar\settings.json`, `audiostar.db` |
| Sign-in tokens (DPAPI, current user) | `%APPDATA%\AudioStar\spotify-token.bin`, `soundcloud-token.bin` |
| Logs, tools, playlist cache, speaker cache, sign-in popup profile (`WebView2`) | `%LOCALAPPDATA%\AudioStar\` |
| Autostart | HKCU Run value `AudioStar`, `"<exe>" --autostart` |

Schema changes are hand-written SQL delta scripts in `src/audio-start/db/audiostar/deltas/NNNN_name.sql`. They are embedded into `AudioStar.Library` and applied in version order at startup (`Data/Database.cs`); there are no EF migrations.

## UI conventions (owner's standing choices)

- **Rendering:** software by default, because GPU rendering paints a white window on the owner's PC. Set `AUDIOSTAR_HARDWARE_RENDER=1` to try the GPU.
- **Design tokens:** colours are the `App*Brush` resources set in `Services/ThemeService.cs` for light and dark. Never put raw colours in views.
- **Buttons:** every text button is blue. The implicit `Button` style in `Resources/Styles.xaml` is based on `AccentButton` (min width 100), so buttons take no per-button padding. Icon, transport and card buttons use `IconButton`, `PlayButton` and `CardButton`; an icon-only button that acts beside text buttons (the list/card toggle left of "Play all") is blue too, accent fill with a white glyph.
- **Blue means action and now playing:** the playing track row is solid accent with white text.
- **Shared styles:** dividers use `HairlineSplitter`. Scrollbars and tooltips have app-wide implicit styles in `Styles.xaml`.
- **Controls never fail silently:** a control that cannot act shows the reason in a toast. Better, it sets the missing prerequisite up in the same flow and captures the value itself instead of sending the owner to a settings field.
- **Sidebar service switches:** the switch alone connects and disconnects (the right-click menu only repeats it); it is never disabled while connecting and sits beside the row button, not inside it. Connected services sort to the top of the group, the rest to the bottom, live.
- **Source pages:** no hint lines under the page title.
- **Track list (`Views/SourceView.xaml`):** rows use their own `ListViewItem` template, because Fluent's template repaints hover over a row's `Background` and hid the white-on-blue playing row. Column widths are star `GridLength` properties on `SourceViewModel`, bound `TwoWay` by the header and `OneWay` by every row. Cells show a tooltip only when their text is trimmed (`Interaction.FullTextToolTip`). The toggle switches every source page to track cards (cover, title, artist, time) in `VirtualizingAdaptiveGrid`; the mode holds for the session, like the column options, and is not saved.

## Working rules for this repo

- **Verify the UI through UI Automation only:** never simulate mouse input, which can land in the owner's terminal. Capture the window with `PrintWindow`. Screenshots are physical pixels at 150 percent scaling.
- **The owner's speaker:** a WiiM Amp at 192.168.0.67. Restarting the app is always allowed; it interrupts what is playing.
- **WiiM Home secrets:** never copy WiiM Home's embedded TLS certificate and key, LinkPlay cloud keys or other secrets into Audio Star.
- **Planning and lessons:** see `tasks/features.md`, `tasks/v1-plan.md` (scope and what was verified live) and `tasks/lessons.md` (the reasons behind most of the rules above).
