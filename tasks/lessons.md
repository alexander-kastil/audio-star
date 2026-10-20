# audio-star lessons

## WiiM Home is a PyInstaller Python app, not a native one

**Pattern:** WiiM Home (AppData\Local\WiiMHome, not Program Files) is PyInstaller onedir, Python 3.9, PyQt6 Widgets plus plain-source QML. REA has no PyInstaller support and the only mypyc `.pyd` belongs to `charset_normalizer`, so Ghidra was never needed.
**Rule:** For WiiM Home use the windows-app-reverse-engineering skill's Python leaf (`references/python-pyinstaller.md`): extract the PYZ, outline with a uv-managed CPython 3.9, decompile with pycdc. Evidence lives in `evidence\decompiled`, `evidence\outline` (the `.dis.txt` is authoritative where a `.py.err` sibling exists) and `evidence\reports`.

## The WiiM Amp needs no client certificate and sends no UPnP events

**Pattern:** WiiM Home ships a mutual-TLS client certificate, but the Amp (192.168.0.67, Linkplay.5.2.830149) answers `https://<ip>/httpapi.asp` without it. SUBSCRIBE returns a SID, yet no NOTIFY ever arrives, not even after a volume change; WiiM Home's own log shows `first_notify_still_missing` for all three services.
**Rule:** Never ship WiiM's embedded certificate or LinkPlay cloud keys. Treat speaker state as polled (`GetInfoEx` every 1 to 2 s, group every 10 to 30 s); events are a bonus. `BrowseQueue`/`GetQueueIndex` HTTP 500 means an empty queue; `GetKeyMapping` with `MaxNumber 0` means the model has no presets.

## Prove PC reachability with a speaker fetch, not with events

**Pattern:** The missing NOTIFY looked like a firewall block, so a Windows rule and a Kaspersky trusted-network check followed, and the NOTIFY still never came. Asking the speaker to play `setPlayerCmd:play:http://<pc>:22545/tone.wav` showed it fetched from the PC at once.
**Rule:** Test inbound reachability by making the speaker fetch a URL from the PC (a 3 s quiet tone, then `setPlayerCmd:stop`). Inbound needs `src\audio-start\tools\firewall.ps1` run elevated (TCP 22534, 22545 and UDP 1900, LocalSubnet, Private) and the LAN marked trusted in Kaspersky.

## Hand the owner a script file, never a multi-line paste

**Pattern:** Two attempts at pasting firewall commands into an elevated terminal failed: a long line wrapped into two commands, then a splatted `$p` was lost because the lines ran out of order.
**Rule:** For anything the owner must run elevated, write a `.ps1` into the repo and give one short line: `pwsh -ExecutionPolicy Bypass -File <path>`.

## A feature request during feature collection is a list entry

**Pattern:** "play my YouTube playlists" started a build investigation; the owner said "right now we are collecting features".
**Rule:** While the owner is collecting features, record each one in `tasks\features.md` (request in their words plus known facts) and build nothing until they ask for a version.

## Fan-out builds: one project per area, the contract first, the integrator runs every suite

**Pattern:** Five dotnet-expert agents built Audio Star in parallel without a single build collision, because each owned one project, `AudioStar.Core` held a fixed contract, and every build used `-p:BuildProjectReferences=false`. They were told not to run tests, and the first integrated run found 11 failures: NSubstitute could not proxy `internal` interfaces, a fixture captured through a non-UTF-8 pipe was double-encoded, a test expected C# rounding where the code copies Python's `%.2f`, and the DLNA SOAP reply lacked the `u:` prefix.
**Rule:** Keep the project-per-area split and the fixed contract for parallel agents. Add `InternalsVisibleTo DynamicProxyGenAssembly2` to every library tested with NSubstitute. The integrator runs every test suite right after the fan-out, before any live test.

## Keep Audio Star's own yt-dlp

**Pattern:** The chocolatey yt-dlp (2025.06.09) returned zero entries for current YouTube playlists ("Unsupported lockup view model").
**Rule:** Audio Star downloads yt-dlp to `%LOCALAPPDATA%\AudioStar\tools` and self-updates it every two days (`YtDlpUpdater`); the PATH copy is only the fallback.

## Spotify Web API changes in 2026

**Pattern:** Since February 2026 playlist contents come from `/playlists/{id}/items` with the track under `item`; development-mode apps need a Premium owner and allow 5 users; the redirect must be `http://127.0.0.1:<port>/callback`, never `localhost`. On 2026-10-19 the Create app form showed **Web API** greyed out for the owner's account, and after the in-popup setup and sign-in succeeded, `GET /me` answered 403 forbidden: the owner has no Premium, so Spotify stays off for them.
**Rule:** Check developer.spotify.com before touching the Spotify source. With no client ID, Connect sets the app up inside the popup (see "Controls set up what they need" below); App settings still accepts a client ID. A 403 on `/me` right after a good sign-in means no Premium, not a bug in Audio Star.

## Restart Audio Star without asking

**Pattern:** A UI change was built to a scratch folder because the running app locked `bin`, and the owner had to ask for the restart.
**Rule:** The owner allows restarting Audio Star at any time (2026-10-19). After a change: stop `AudioStar.exe`, `dotnet build src\audio-start\AudioStar.Desktop`, start `bin\Debug\net10.0-windows\AudioStar.exe`.
`dotnet test AudioStar.slnx` is not that build: it left the Desktop `bin` on old code, so the first playlist-cache check ran the previous version. Since the setup project joined the solution it also publishes and builds the MSI. Run the four test projects one by one and build the Desktop csproj before every restart.

## The owner's look for Audio Star beats design-skill defaults

**Pattern:** Add stayed a plain button so the page kept one primary action (the ui-ux-pro-max primary-action rule), although the owner had called blue "our indicator for action"; the owner then asked again for every button in blue. Settled in the same round: no hint or cookie lines under a page title; title, connection state and buttons on one row; the URL box across the full width; playlist cards sharing the panel width; the playing track marked in blue.
**Rule:** Every text button takes the accent style (the implicit `Button` style in `Resources\Styles.xaml`, based on `AccentButton`, with no per-button padding); icon, transport and card buttons keep `IconButton`, `PlayButton` and `CardButton`. Blue (`AppAccentBrush`, `AppAccentSoftBrush`) marks actions and now playing. A design skill's default applies only where the owner has stated nothing.
**Settled later the same day:** text buttons share a 100 px minimum width (set in `AccentButton`, never on one button); the playing row is solid accent with white text and turns `AppAccentHoverBrush` on hover; dividers are 1 px hairlines (`HairlineSplitter`, also drawn through every row), never a 5 px bar; scrollbars are a 4 px accent bar that keeps its thickness on hover and only darkens over a faint rail; tooltips are one card style and appear on a cell only when its text is trimmed; the track list shows Title, Artist and Time with # hidden by default, toggled by right-click. Read the owner's shorthand against the screenshot arrows: "colors" meant columns, "a thin line between the rows" meant the column divider drawn through every row.

## Verify Audio Star through UI Automation, never the mouse

**Pattern:** A simulated double-click on a track went to the owner's terminal: the owner was typing, so `SetForegroundWindow` failed silently. `Process.MainWindowHandle` pointed at a tooltip popup, and a `CopyFromScreen` shot captured the terminal instead of the app.
**Rule:** Drive the app with UIA patterns only: sidebar buttons by Name, playlist cards by HelpText (the playlist title), the "Playlist URL" box by its automation name. Capture with `PrintWindow`. The global `dotnet-conventions` WPF leaf and its `wpf-uia-drive.ps1` carry the foreground guard and the `invoke` step; add `-Attach` to drive the running instance instead of starting a second one, which only hands off and exits. Screenshots are physical pixels at 150 percent: divide by 1.5 before comparing them with XAML sizes. The speaker reports the current track as the `GetPositionInfo` `TrackURI` (`http://<pc>:22545/stream/<source>/<id>`), which is how the track list finds the playing row.

## Fluent's ListViewItem paints over a row's Background

**Pattern:** The playing row set `Background` and `Foreground` from a DataTrigger in the item container style. The Fluent theme's ListViewItem template draws its own hover and selection fill on a template part, so on hover the row turned light grey under white text and became unreadable.
**Rule:** Track rows in `SourceView.xaml` carry their own ListViewItem `ControlTemplate` (a rounded Border bound to `Background`) with the triggers in order: hover, selected, playing, then playing plus hover. Restyle a Fluent list row through the template, never through a Background setter alone. The general trap and the column-grid recipe live in the global `dotnet-conventions` WPF leaf.

## Connection state lives in the provider row, known from the start

**Pattern:** The status went from text beside the page title, to a lamp there, to a lamp in the sidebar row, to a switch beside the lamp. The owner's corrections: a state that shows only once a provider page is opened is useless ("it influences where we click"); Reconnect and Disconnect belong on the provider row; lamp and switch side by side say the same thing twice. This replaces "title, connection state and buttons on one row" from the entry above.
**Rule:** Each music service row in the sidebar carries one switch that is the indicator and the action: green and on only when `Connected`, grey otherwise, never disabled (2026-10-19, see "Controls set up what they need"); right-click offers Connect or Reconnect and Disconnect. Connected services sort to the top of the group, the rest to the bottom. The source page has no connect buttons. `MainViewModel.Start` calls `IMusicSource.ConnectSilentlyAsync` for every service, which must never need the owner (Spotify and SoundCloud use only a stored token and never open the sign-in popup; source pages also call `ConnectSilentlyAsync` on load), so the rows are correct before the first click.

## Fold a field label into hint text

**Pattern:** The owner dropped the "Add playlist by URL" label for the same words as hint text inside the empty box, and asked for the row's buttons at one width, right-aligned to the URL box's Add.
**Rule:** A single input carries its label's words as hint text (overlay recipe in the global `dotnet-conventions` WPF leaf), and give the text buttons that share a page one `MinWidth` with their right edges aligned.

## A clean build says nothing about a XAML trigger

**Pattern:** The new switch built clean and stayed off for a connected YouTube: its `Tag` trigger compared a bound `bool` with the string "True". Only the screenshot after the restart showed it.
**Rule:** After every XAML change, restart and look at the result before reporting. Read the WPF leaf of `dotnet-conventions` before UI work; it carries the `Tag` trigger fix. `NavButton` and `IconToggleButton` still use `Value="True"` on `Tag`.

## SoundCloud signs in with the website's token, not the official API

**Pattern:** SoundCloud's API is OAuth 2.1 with PKCE, but every client counts as confidential (the client secret is required for the token and every refresh) and registering an app needs an Artist Pro subscription. The owner proposed an in-app browser popup instead.
**Rule:** Connect opens the WebView2 popup at `soundcloud.com/signin` and keeps the website's `oauth_token` cookie, DPAPI-encrypted in `%APPDATA%\AudioStar\soundcloud-token.bin` (`SoundCloudSession`). yt-dlp gets it as `--username oauth --password <token>` on every SoundCloud call, and `YtDlpRedaction` masks it in stderr before logging. The account comes from `api-v2.soundcloud.com/me` with `Authorization: OAuth <token>` and the web `client_id` scraped from soundcloud.com's scripts. A Profile URL in App settings still wins over the signed-in account's profile.

## One sign-in popup for every account a service has

**Pattern:** Asked whether the popup should cover all providers: Spotify moved from the system browser plus a loopback listener on 22547 to the popup, YouTube could not follow because Google blocks sign-in inside embedded browsers, and Radio has no account. At 520 px the popup cut soundcloud.com's sign-in card off; closing it from inside `NavigationStarting` disposed the WebView2 inside its own callback.
**Rule:** A service with an account signs in through `IWebSignIn` (Core) implemented by `Services/WebSignInService.cs` and `Views/WebSignInWindow.cs`: cookie mode for SoundCloud, redirect mode for Spotify (the popup cancels the navigation to `http://127.0.0.1:22547/callback`; nothing listens on the port), address mode for Spotify's app setup (`AddressPattern`, matched on `SourceChanged` and `HistoryChanged` too, because developer.spotify.com is a single-page app). `Instructions` and `CopyText` put a strip with a Copy button above the page. Only `ConnectAsync` may open it. YouTube stays on browser cookies. The general WebView2 recipe (sizing, deferred close, cookie timer, sign-out) is in the global `dotnet-conventions` WPF leaf.

## Never Disconnect a service during a live check

**Pattern:** The sidebar switch calls `DisconnectAsync` when it is on, and Spotify's Disconnect deletes the owner's stored refresh token; SoundCloud's deletes its token and the popup's cookies.
**Rule:** In a UIA check, invoke a service switch only while its Name is "Connect", dismiss the sign-in popup with `WindowPattern.Close`, and never type credentials: the owner signs in.

## Setup and brand screens are warm comic, never cold tech

**Pattern:** "Retro Icon but with AI crossover" was drafted as a dark synthwave star inside a neural-network constellation, with a terminal listing the install path and the firewall ports. The owner called it "too cold", then, seeing a warm comic layout that still listed paths and ports beside an empty picture slot, "cold and technical". Accepted: a full-window comic illustration of a slim, fit elderly woman in red headphones hugging a vinyl single from her childhood, on a cream ground with ink outlines and halftone, a speech bubble "Oh! That's my song!", and one card with a music headline, one sentence, the autostart checkbox and the buttons.
**Rule:** An Audio Star welcome, setup or brand screen leads with a warm comic scene of a person enjoying music (cream `#FFF1D6`, ink `#1E1A17`, brand gold `#FFC43D`; Luckiest Guy, Patrick Hand, Nunito) and talks about music, never mechanics: no paths, ports, firewall rules or version badges. Read "retro" as warm vintage (vinyl, comic print), not neon synthwave or circuits. Show the owner a draft only once the illustration is in it. The art lives in the design canvas https://claude.ai/artifact/4JfBepk3xpPmpEmopDxakg (asset store) and the Media Creator library (wide scene `01a15527-4b7e-7a91-afa3-a1d5b349225c`, portrait `01a15524-b339-7e28-8721-8996b6c862d6`).

## The MSI's pictures carry their copy

**Pattern:** Offered a custom setup.exe that would match the design exactly, the owner chose "Restyle the MSI": MSI screens show a bitmap plus native grey controls only. `StartDlg` replaced the Welcome and Options dialogs on a fresh install, with its headline, sentence and speech bubble painted into `Assets/start.bmp`; `ExitDialog` and `UserExit` got `Assets/exit.bmp` through `Strings.en-us.wxl`, because every WixUI dialog shares `WixUIDialogBmp`. Checking the screens, a `Win32_Product` query made Windows Installer reconfigure Python, Dapr and Office, and `PrintWindow` returned the bitmap blank.
**Rule:** A wording change on those screens is a re-render of the bitmap (`render-msi-bitmap.ps1` in the global `dotnet-conventions` skill, `-Scale 2`), never a `.wxs` text edit; the checkbox, Cancel and Install stay native in the grey strip. The render pages and fonts were scratch files of the 2026-10-19 session, so rebuild the page from the design canvas. Check MSI screens without installing, as the `dotnet-msi-wix` leaf of that skill describes.

## Restyling the other views: full width, equal margins, one control surface

**Pattern:** Applying the YouTube reference page to the other views took a chain of owner corrections in one session: "i prefere full width" (every fixed-width search box, server box and card), "check all left and right margins .... should be equal" then "right margins are the problem" (the scrollbar column plus the content's right inset made the right gap 10 DIP wider), "do we need double control chrome?" (Now playing repeated the player bar's buttons), "buttons are not nice" (Add folder stacked under Save, 10 DIP off its right edge) and "add folder goes here as icon ... make those blue".
**Rule:** Read `.claude/rules/view-reference.md` before restyling any view; its corrections table holds these. Group C pages (forms, Now playing) get a proposal first and no edit before the owner's answer. Measure margins in the PrintWindow shot (left and right gap in px to the outermost ink), never from the XAML numbers.

## One UI agent at a time builds and restarts Audio Star

**Pattern:** A margins agent and the Now playing implementer both needed `Styles.xaml` and a restart of `AudioStar.exe`, while a peer session built the same Desktop project for its sign-in work and restarted the app on its own. The peer also committed (`v1.1`) mid-run, and a `git diff --stat` progress probe dropped from 12 files to 6, which looked like lost work.
**Rule:** Run read-only proposal agents in parallel, but queue every agent that edits shared XAML, builds and restarts behind the running one. Brief it to re-read each file from disk right before editing, to use whatever instance is running if the PID changed, and to stop on a build error in a file it did not touch. Before reading a shrinking diff as a revert, check `git log`.

## A forward BasedOn crashes the page, not the build

**Pattern:** `NowPlayingAlbum` was declared above its base `Subtle` in `Styles.xaml`. The build was clean; opening Now playing threw "Cannot find resource" and the page failed to load.
**Rule:** Declare every keyed style below the style it is `BasedOn`, then open the page in the running app before reporting. The general trap is in the global `dotnet-conventions` WPF leaf.

## What UI Automation cannot reach

**Pattern:** `PlaylistSettingsWindow` opens only from a playlist card's right-click menu, and no UIA pattern opens a `ContextMenu`, so it was never captured. A narrow-window check worked by resizing the window through `TransformPattern` and restoring it afterwards. A driver script hung because `Start-Sleep 2500` waits 2500 seconds.
**Rule:** Name every right-click, hover and drag state as not seen in the report. UIA `InvokePattern` also bypasses mouse capture and hit testing, so a "the click does nothing" report cannot be reproduced through UIA: say the cause was found by reading the code, not observed. Check the one-column layouts at 1470 px (the window's minimum) through `TransformPattern.Resize`, then restore 1920x1230 at the old position. Use `Start-Sleep -Milliseconds`.

## Controls set up what they need, and say why when they cannot act

**Pattern:** "spotify connect does nothing": with no client ID, `SpotifySource.ConnectAsync` returned quietly, with no popup and no message. A toast naming the settings field fixed the silence and was still "not very user friendly". The owner picked setup inside the popup: Connect opens developer.spotify.com's Create app page in the sign-in popup, shows the redirect URI with a Copy button, reads the new client ID from the app page's address, saves it and goes on to the login. Then: "connect should be not only right click but also just toggle ... make the list dynamic ... move disabled to bottom". The switch had been disabled while connecting (`CanExecute`) and nested inside the row's nav button, while the menu's Connect had neither.
**Rule:** These are the owner's design principles for every control in Audio Star:
1. A control that cannot act says why (a toast with the reason); it never does nothing.
2. Better than saying why: set the missing prerequisite up in the same flow. Open the provider's page in the popup, show what the user must paste with a Copy button, capture the result from the page itself (address, cookie or redirect), save it and continue. Never send the user to a settings field to copy a value the app can read; the settings field stays as a fallback.
3. A switch does its whole job alone: the right-click menu only repeats it. Never disable it while the menu equivalent still works, and never nest it inside another button; place it beside the row button in a `Grid`.
4. A list of things that are on or off sorts live: on at the top, off at the bottom, the original order kept inside each part (`MainViewModel.SortServices`, `ObservableCollection.Move`).

## SoundCloud metadata comes from api-v2, not from yt-dlp's flat list

**Pattern:** SoundCloud showed no covers, an empty Artist and Time column, and the speaker no artist: `yt-dlp -J --flat-playlist` gives SoundCloud entries only id, url and title (its `_extract_set` passes album fields only), and no option changes that.
**Rule:** `SoundCloudSession` fills tracks from api-v2 with the scraped client id and the stored token: `/tracks?ids=` in batches of 50, artist `user.username`, `duration` in ms, `artwork_url` with `-large` rewritten to `-t500x500` and `user.avatar_url` as fallback. A set's cover is its `artwork_url`, else the first track's; Likes takes the newest liked track (`/resolve` the likes URL for the user id, then `/users/{id}/track_likes?limit=1`); History is `/me/play-history/tracks` and needs the token. Check api-v2 shapes in the owner's signed-in Chrome with `fetch` from the page and return derived fields only: the Chrome tool blanks any result that contains a query string, a cookie or a token.

## Transcoded streams go out as WAV with an exact length, so the speaker can seek

**Pattern:** SoundCloud serves HLS only (aac_160k, aac_96k, abr_sq; progressive MP3 went away at the end of 2025). The ffmpeg FLAC pipe had no length, so the speaker reported `totlen` 0, and the mini bar showed "Live", hid the seek slider and stopped ticking the position ("we have no forward control"). The speaker seeks with HTTP byte ranges (`DLNA.ORG_OP=01`, the flag WiiM Home writes too).
**Rule:** When the resolver knows the duration (yt-dlp `duration`, null when live), `StreamEndpoint` serves 44.1 kHz 16-bit stereo WAV with `Content-Length = 44 + round(seconds * 44100) * 4`, answers `Range` with 206 and starts ffmpeg at `-ss offset / 176400`, padding with silence when ffmpeg ends early. The FLAC pipe stays only for live or unknown durations. Verified live on 2026-10-19: `totlen` 4458703 ms, and a seek to 30:00 buffers about 10 s, then plays on. After any change to the stream path, check that `getPlayerStatusEx` reports `totlen` above 0 and that a `Seek` moves `curpos`.

## SoundCloud's account read can hang right after a restart

**Pattern:** Twice on 2026-10-19 the account read hung for the full 30 s HttpClient timeout at startup, both times while the speaker reconnected to a SoundCloud stream in the same seconds. The single try set Error, so Likes and the sets vanished and the switch stayed off ("soundcloud does not automatically connect"). curl and a fresh .NET HttpClient answered in under 0.3 s, and History (also api-v2) loaded during the hang.
**Rule:** Connect retries transient failures after 2, 5 and 10 s and logs each attempt as `attempt N of 4, GET <url>`. The cause is still open: when that line appears, start from the request it names, not from the network.

## The list/card toggle is a blue action button, and track cards carry the time

**Pattern:** The toggle went in as a neutral `IconButton`, per the house rule for icon buttons; the owner: "this should be a blue button (action)". The first track cards had no time: "to the cards add time information for the track".
**Rule:** An icon-only button that acts beside the text buttons (the toggle left of "Play all") takes the accent fill with a white glyph and the neighbours' height. Track cards show cover, title, artist and time, and the playing card is solid accent. The view mode is a session-wide static like `ShowArtist`, not saved.

## A same-version MSI leaves the old app installed

**Pattern:** On 2026-10-20 the owner reinstalled and still saw no covers. `Program Files\Audio Star` held DLLs from before the SoundCloud artwork code, and the `Uninstall` keys listed two "Audio Star 1.0.0" products: with `AppVersion` stuck at 1.0.0, `<MajorUpgrade>` skipped the installed product and Windows Installer kept the equal-version files. The coordinator then briefed `AllowSameVersionUpgrades` without looking for the owner's convention. The owner had already asked for semantic versioning like presenter-tools, bumped with each build, and that rule lived only in presenter-tools' auto-memory.
**Rule:** When the installed app lacks something the Debug build has, compare installed file dates and versions with `bin` and read the `Uninstall` keys before debugging code. Bump `<Version>` in `AudioStar.Desktop.csproj` and the wixproj `AppVersion` default together before every MSI build (fix patch, feature minor, breaking major), never with a `-p:AppVersion=` override. Before briefing a build, installer or other conventional fix, grep the global skills, the agent files and the owner's memories for a precedent; one found only in a memory moves into the global skill.

## WiiM Home's keys sit in evidence in four forms, and the history now starts at v1.1.0

**Pattern:** Before making the repo public, `evidence/` still carried WiiM Home's mutual-TLS certificate, key and CA (`LPTLSTool`), the LinkPlay cloud, Freshdesk and WiiM Radio app keys, the Discogs key and secret and `FEEDBACK_AES_KEY`, all since the first commit. Each value lived in the decompiled `.py`, the `.dis.txt`, the `.outline.txt` (which cuts long constants at about 300 characters, so a full-value match misses it) and the `.pyc`, plus zlib-compressed inside `evidence/pyinstaller/carchive/PYZ-00.pyz`, where a plain grep finds nothing. Audio Star uses none of them. On 2026-10-20 they were redacted (`<redacted>` in text, same-length `REDACTED` filler in `.pyc` and in each PYZ entry, so both still parse), `master` was rebuilt as one root commit `v1.1.0` from the 1.1.0 tree, and GitHub was force-pushed. The owner's "we can override history to 1.1.0" already meant GitHub too; stopping at the local rewrite and asking about the push drew an angry correction, and so did trying to push while the tree was not clean.
**Rule:** Any new evidence from WiiM Home gets the same scan before it is committed: derive the values from the decompiled constants, match full values and 20-character prefixes in every text form, and decompress every PYZ entry before searching it. Never print a value; report module and constant name. When the owner says to override the history, the force push is part of the job: get `git status` clean first, then fetch, push with `--force-with-lease=master:<fetched sha>` and check `git rev-list --count origin/master`. Other clones of the old history must re-clone, not pull.

## A readme screenshot is cropped to the window, corners included, and wired once the file exists

**Pattern:** On 2026-10-20 the owner asked for `agent-instructions/image.png` "perfectly cropped" in `readme.md`, above Prerequisites, and renamed. The readme line went in while the crop was still running, so the preview showed a broken image and the owner wrote "the screenshot has an err". The first crop found the window edges from the pixels (right: 2 px border plus a strip of the window behind; top: the border row) but left background pixels outside the rounded Windows 11 corners and called transparency "beyond the crop"; a magnified corner check on the main thread caught it.
**Rule:** A perfect crop of a window screenshot cuts inside the border and makes the pixels outside the rounded corners transparent (measure the radius, about 10 px for the inner curve at 150 percent, anti-alias it), then checks all four corners magnified on white and black before reporting. Readme images live in `assets/` under a descriptive name (`assets/audio-star.png`); a rename removes the source. Add the readme reference only after the file exists, or say up front that the preview stays broken until it lands. Captured globally: `optimize-images` `references/window-screenshot-crop.md` with `scripts/window-screenshot-crop.py`, and a rule in the `image-producer` agent.
