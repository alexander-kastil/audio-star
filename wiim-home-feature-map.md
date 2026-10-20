# WiiM Home: reverse-engineered feature map

Target: WiiM Home 0.2.10.5 (release 2026-10-10), installed by its owner at `C:\Users\AlexanderKastil\AppData\Local\WiiMHome`. Analysed 2026-10-19, static only (nothing launched, no URL contacted).

Labels: **observed** = read in decompiled code, bytecode, QML or a bundled file at the cited place; **inferred** = from names or strings only. Path shorthands: `DEC\` = `evidence\decompiled\`, `OUT\` = `evidence\outline\` (`.dis.txt` is the authoritative bytecode listing where a `.py` is incomplete). Full per-feature reports with every citation: `evidence\reports\*.md`.

## 1. Target, method, evidence

| Item | Value |
|---|---|
| Packaging | PyInstaller onedir, Python 3.9 (`python39.dll`), PyQt6 Widgets plus QML (`Qml\` shipped as plain source) |
| Own code | 506 modules: `HOME` (UI, 297), `LPClientFramework` (core, 144), `LPCommonWidgets` (54), `LPPermission`, `LPGlobalUI`, `main` |
| Native code | None of WiiM's own. The only mypyc module (`81d243bd2c585b0f4821__mypyc.cp39-win_amd64.pyd`) belongs to `charset_normalizer`. No Ghidra pass needed. |
| Extraction | `evidence\pyinstaller\` (CArchive TOC, 2,481 PYZ modules as `.pyc`) |
| Decompiled | `evidence\decompiled\` (pycdc; 307 clean, 198 with a sibling `.py.err` = incomplete, mostly cut at try/except) |
| Bytecode outline | `evidence\outline\` (`.outline.txt` per module: defs, names, strings; `.dis.txt`: full disassembly, CPython 3.9) |
| Agent reports | `evidence\reports\` devices, groups-settings, playback, library, tidal, services, shell |
| Tools | `evidence\tools-build\pycdc` (built from zrax/pycdc `b4289760`), uv-managed CPython 3.9.25 |

## 2. Architecture

| Layer | What | Where |
|---|---|---|
| Shell | `main.py` > `LPApplication` > `WiiMHome.setupUI` > `LPStreamServiceMainWindow` (frameless QMainWindow) | `DEC\__main_script__.py`, `OUT\HOME\WiiMHome.dis.txt:11432-11628` (observed) |
| UI | Qt Widgets pages, with `QQuickWidget` islands for the device dashboard, discovery, presets, recently played, WiiM Radio, TIDAL, feedback; Python objects exposed by `setContextProperty`, no `qmlRegisterType` | `Qml\`, `DEC\HOME\DeviceDashboard\LPDeviceDashboardViewController.py:395-402` (observed) |
| Device model | `LPDevice` per speaker: UPnP SOAP plus HTTPS `httpapi.asp`, push via UPnP eventing | `OUT\LPClientFramework\LPDevice.dis.txt` |
| Local servers | cherrypy on `0.0.0.0`: media 22345, UPnP MediaServer 22346, OAuth callback 22347; UPnP event sink 22334; SSDP responder on UDP 1900 | `DEC\LPClientFramework\LPUtility.py:106-108`, `LPUPnPObserverManager.py:272` (observed) |
| Library | beets (in-process) over SQLite `userDataDir\beets\musiclibrary.db`, plus MusicBrainz, Discogs, Wikidata, Wikipedia | `LPBeetsWrapper`, `LPMusicDatabase.py:20-58` (observed) |
| Services | TIDAL and Qobuz (accounts live on the speaker), WiiM Radio (LinkPlay cloud), Radio Paradise 2 | `data\LPSupportedStreamServiceConfig.json` (observed) |
| Infra | WinSparkle updates, Freshdesk plus S3 feedback upload, LinkPlay analytics, crash dumps | `LPWinSparkleUpdater`, `LPFeedback\*`, `LPEventTrack` |

Third-party engines bundled: beets, musicbrainzngs, mutagen/mediafile, cherrypy/cheroot, zeroconf, requests, requests_cache, httpx, bs4/lxml, watchdog, smbprotocol, pycryptodome (`Crypto`), cryptography, PIL, psutil, pywin32, WinSparkle.dll.

## 3. Feature areas

### 3.1 Discovery and connection

Mechanism: three sources feed one `deviceCome(uuid, ip, port, origin)`: SSDP, mDNS and a JSON cache; each new speaker gets an `LPDevice`, an `init()` that pulls state, and three UPnP event subscriptions.

- SSDP M-SEARCH to `239.255.255.250:1900`, `MX: 3`, `USER-AGENT: mac/1.0 UPnP/1.1 upnpx/1.0`, `ST: ssdp:wiimudevice` (speakers) plus `ContentDirectory:1` / `MediaServer:1` (Home Share servers); every 2 s in fast mode, else 15 s. observed `OUT\LPClientFramework\LPDeviceDiscoverManager.outline.txt:33,147`, `.dis.txt:1796-1899`
- Speaker id: the USN uuid reduced to 24 hex (`uuid[:-len(first group)].replace('-','')`). observed `LPDeviceDiscoverManager.dis.txt:1704-1727`
- mDNS `_linkplay._tcp.local.`, TXT key `uuid`. observed `LPDeviceDiscoverManager.outline.txt:105`
- Cache `cacheDir\deviceCacheV2.json`, `mediaServerCacheV2.json` (rows `ip`, `port`, `name`, `gateway`); only rows on the current gateway are re-probed. observed `DEC\LPClientFramework\LPCache\LPDeviceFileCache.py:19`
- Manual IP: SOAP `GetControlDeviceInfo` to `http://<ip>:59152/upnp/control/rendercontrol1`, `Status` JSON `uuid`. observed `DEC\LPCommonWidgets\dialog\LPIPDiscoverDeviceDialog.py:147-166`
- `init()`: `GetInfoEx`, then `StreamServicesCapability` (JSON `version`, `streamServices`), then HTTPS `getModeRename` (input display names), then `GetControlDeviceInfo` (`Status` JSON: `uuid, DeviceName, project, capability, audioOutputModeVer, essid (hex), group, master_uuid, GroupName, ...`). observed `LPDevice.dis.txt:1184-1291`, `LPDevice.outline.txt:355-386`

Not traced: the SSDP record expiry value; who re-runs `refreshMultiroomState` and how often.

### 3.2 Control protocol (the core a new client needs)

Mechanism: two transports. UPnP SOAP over plain HTTP on port 59152 for transport, volume, queue, presets and accounts; HTTPS `httpapi.asp` commands for settings, groups and inputs.

SOAP (`UPnPTool.upnpPost`): `POST http://<ip>:59152/upnp/control/<endpoint>`, `Content-Type: text/xml; charset="utf-8"`, `SOAPACTION: "<urn>#<Action>"`; urn is `urn:schemas-wiimu-com:service:PlayQueue:1` for PlayQueue, else `urn:schemas-upnp-org:service:<svc>`; `LPDevice.upnpPost` adds `ControlSource=WiiMApp` to most actions. observed `OUT\LPClientFramework\UPnPTool.outline.txt:18-28`, `LPDevice.outline.txt:544-545`

| Endpoint | Actions (fixed args) |
|---|---|
| `rendertransport1` (AVTransport:1) | `Play` (InstanceID=0, Speed=1), `Pause`, `Next`, `Previous`, `Seek` (Unit=REL_TIME, Target=HH:MM:SS), `GetInfoEx` returns CurrentTransportState, TrackDuration, TrackMetaData, TrackURI, RelTime, LoopMode, CurrentVolume, TrackSource, PlayMedium |
| `rendercontrol1` (RenderingControl:1) | `SetVolume` (Channel=Master, DesiredVolume), `SetMute` (DesiredMute), `GetControlDeviceInfo`, `StreamServicesCapability` (AppVersion=1.0), `AirplayAutoSyncDelay` |
| `PlayQueue1` (wiimu PlayQueue:1) | `CreateQueue`, `AppendTracksInQueueEx`, `PlayQueueWithIndex`, `BrowseQueue`, `SkipQueue`, `GetQueueIndex`, `RemoveTracksInQueue`, `DeleteQueue`, `BackUpQueue`, `GetKeyMapping`, `SetKeyMapping`, `SetQueueLoopMode`, `GetUserInfo`, `GetBasicUserInfo`, `UserLogin`, `UserLogout` |

observed `OUT\LPClientFramework\LPDevice.dis.txt:4025-4940` (dispatch), `4137-4162` (GetInfoEx), `4403-4437` (Seek)

HTTPS: `GET https://<ip>/httpapi.asp?command=<cmd>` (command unencoded), `POST https://<ip>/httpapi.asp` with form body `command=<cmd>:<json>`; `verify=False`, a client certificate from `LPTLSTool`, timeout 15 s on GET. observed `LPDevice.dis.txt:5040-5099, 5419-5443`, `DEC\LPClientFramework\LPTLSTool.py:11-33`. Whether the speaker rejects requests without the client certificate: not established (inferred that it does on newer firmware, since the app ships one).

A third channel, raw TLS 1.2 to port 8893 with mutual certificates (`LPTLSTool.tlsCmd`), exists but has no caller beyond a wrapper. observed `LPTLSTool.py:37-71`

Push state: `SUBSCRIBE http://<ip>:<port>/upnp/event/{rendercontrol1,PlayQueue1,rendertransport1}`, `NT: upnp:event`, `CALLBACK: <http://<pc>:22334/Event>`, `TIMEOUT: Second-1800`, renew at 0.8 x timeout; NOTIFY bodies carry `LastChange` (TransportState, CurrentTrackMetaData DIDL, Volume, Mute, LoopMode, `lpmrm` group JSON, `Slave` add/rm). observed `DEC\LPClientFramework\LPUPnPObserverManager.py:262-272, 406-413`

Now-playing DIDL keys: `dc:title`, `upnp:artist`, `upnp:album`, `upnp:albumArtURI`, `song:id`, `song:quality`, `song:rate_hz`, `song:format_s` (bit depth), `song:bitrate`; badge text `'%d-bit · %.1f kHz'`. observed `LPDevice.dis.txt:5711-5931`, `OUT\HOME\PlayView\LPPlayViewController.dis.txt:2224-2300`

Not traced: whether there is any periodic `GetInfoEx` poll (none found; state is event-driven).

### 3.3 Queue, playback, presets, recently played

Mechanism: the PC never streams to the speaker directly; it hands the speaker a playlist XML (`CreateQueue`) whose tracks are URLs or service ids, then tells it which index to play.

- Queue XML: `<PlayList><ListName/><ListInfo><Radio>0</Radio><SourceName/><TrackNumber/><SearchUrl/><Quality>0</Quality><PicUrl/><StartPlayIndex/></ListInfo><Tracks><Track1><URL/><Source/><Id/><Metadata>escaped DIDL-Lite</Metadata></Track1>...</Tracks></PlayList>`; DIDL namespaces `song` = `www.linkplay.com/song/`, `custom` = `www.linkplay.com/custom/`. observed `DEC\LPClientFramework\LPPlayList\LPPlayList.py:89-124`
- Play a list at index i (`LPDevice.fastPlay`): `CreateQueue` with track i and i+1, `PlayQueueWithIndex(QueueName=<title>, Index=1)`, then `AppendTracksInQueueEx` in 200-track chunks, tail with `Direction=1`, head with `Direction=0`, max 500 extra tracks (250 head). observed `LPDevice.dis.txt:3371-3970`
- Queue read `BrowseQueue(QueueName=CurrentQueue)`; jump `PlayQueueWithIndex(CurrentQueue, row+1)`; delete `RemoveTracksInQueue(RangStart, RangEnd)` 1-based. observed `OUT\HOME\Queue\LPQueueListView.dis.txt:3142-3154`
- Shuffle/repeat: `SetQueueLoopMode(LoopMode)`, values listrepeat 0, singlerepeat 1, repeatshuffle 2, shuffle 3, default 4, singlerepeatshuffle 5. observed `OUT\LPClientFramework\LPMediaInfo.dis.txt:51-75`
- Presets: read `GetKeyMapping` (XML `KeyList` / `Key<n>` with `Name`, `Source`, `PicUrl`); play `httpapi MCUKeyShortClick:<n>`; save `BackUpQueue` then `SetKeyMapping`; delete writes `<RoutineId>Empty</RoutineId>`. observed `OUT\LPClientFramework\LPPresetManager.dis.txt:121-157`, `OUT\HOME\PresetQml\LPPresetQmlViewController.dis.txt:876-884`
- Recently played: rows in `LibMusicItem` of `musiclibrary.db` (`directoryName='recently'`), `detail` JSON `{playList, show, account}`; replay goes through `fastPlay`. observed `OUT\LPClientFramework\LPMusicLibrary\LPMusicLibraryDBManager.dis.txt:37-40`

Not traced: full-screen play view, `LPPlaybackLayoutPolicy`, the queue drag-and-drop reorder action.

### 3.4 Multiroom groups and device settings

Mechanism: named groups are stored on the master speaker as a JSON list and activated by id; membership is verified by polling the slave list; group volume is fanned out per member.

- `POST multiroom:savenamegrouplist` `{"grouplist":[{group_name, fullName, group_id, group_type, update_time, channel, slavelist:[{name, uuid, ipv4}]}]}`; activate `POST multiroom:setcurrentnamegroup` `{group_id, group_name, fullName, slavelist:[{uuid, ipv4}]}` (master not in slavelist), deactivate `{"group_id":"-1"}`; read `multiroom:getnamegrouplist`, verify `multiroom:getSlaveList` (`slave_list`); dissolve `multiroom:Ungroup`. observed `OUT\LPClientFramework\LPDeviceManager\LPDeviceGroupManager.dis.txt:586-843, 2061-2064`, `LPGroupManager.dis.txt:2464-2690`
- Leader/follower: `getStatusEx` `group == '1'` means slave. observed `LPDevice.dis.txt:2155-2190`
- Member volume: `httpapi multiroom:SlaveVolume:<slave ip>:<n>` on the master, else `SetVolume` with `Channel=Single`. observed `OUT\HOME\DeviceDashboard\LPGroupItemWrapper.dis.txt:2546-2740`
- Music follows a regroup: `BrowseQueue` on the old speaker, `fastPlay` on the new one; refused for line-in, optical, HDMI, Bluetooth, AirPlay and similar. observed `LPGroupManager.dis.txt:3008-3148`
- Settings are `httpapi` get/set pairs (complete table in `evidence\reports\groups-settings.md`): rename `setHexDeviceName:<utf8 hex>`; network `set{WlanBandConfig,NetworkPreferDNS,WlanRoamConfig,IPV6Enable}`; standby `setPowerModeTime:{"idleInterval":"n"}`; factory reset `restoreToDefault`; reboot `StartRebootTime:1`; sound `setMaxVolume`, `setVolumeControl`, `setChannelBalance:%.2f`, `SetFadeFeature`, `setDigitalFilterType`, `setSubLPF:{status|level|cross|phase|sub_delay}:n`, `setSoundCardOutputMode:<json>` / `setAudioOutputHardwareMode`; inputs `setPlayerCmd:switchmode:<mode>` (modes `wifi, line-in, optical, co-axial, HDMI, arc, bluetooth, phono, PCUSB, udisk, ...`), `PHONO_MODE_SWITCH_SET`; LEDs and buttons `LED_SWITCH_SET`, `Button_Enable_SET`; Bluetooth `startbtdiscovery`, `connectbta2dpsynk`, `getbthistory`; Alexa `setAlexaCountry`, `alexaSetLanguage`; cast-out `audio_cast:*`; sync delay `SetSyncPlayExtraDelay`. observed `OUT\HOME\DeviceSetting\*.dis.txt` (lines in the report)
- No EQ, preset EQ or DSP command exists in this app; only the DAC digital filter and the subwoofer LPF. observed (absence over all DeviceSetting modules, bounded search)

Not traced: getter reply shapes; a delete-named-group path (none found).

### 3.5 Local library and the PC media server

Mechanism: beets indexes music folders in place (no copy, no tag writes) into SQLite; a bundled beets plugin mirrors every change into a `wiim_upnpitems` table; the PC then serves files over HTTP and also acts as a DLNA MediaServer.

- Folders: `wiimhome-userconfig.json` key `mymusic-dir`. observed `DEC\LPClientFramework\LPUtility.py:278,305`
- beets config: `copy/write/move: no`, plugins `lyrics, fromfilename, lastgenre, lpbeetsplug`. observed `data\beets-config.yaml:6-22,163-168`
- Imports run in a staged copy (`cacheDir\beets-stage\task-<id>`) merged back in one transaction; folders watched by polling (watchdog). observed string `OUT\LPClientFramework\LPBeetsWrapper.dis.txt:608`; rest inferred
- Track URL handed to the speaker: `http://<pc ip>:22345/media/music/<hex(utf-8 absolute path)>`; cover `/media/cover/<hex>` (embedded art extracted to `cacheDir\cover\<md5>`); Range requests answered with 206; `Content-Type: audio/mpeg` for every file; no transcoding. observed `DEC\LPClientFramework\LPMediaHttpServer.py:12-45`, `.dis.txt:267-748`
- DLNA MediaServer: SSDP alive for `MediaServer:1` and `ContentDirectory:1`, description at `http://<pc>:22346/upnp/DeviceDescription.xml`, Browse/Search mapped to SQL over `wiim_upnpitems`; root containers `0$4` all music, `0$5` genre, `0$6` artist, `0$7` album, `0$14` folder, `0$F` playlist. observed `DEC\LPClientFramework\LPQTSSDPServer.py:74-153`, `data\LPUPnPServer.xml`; Browse internals inferred
- Artist pages: MusicBrainz, Discogs (`api.discogs.com/artists/<id>`), Wikidata, Wikipedia (`<lang>.wikipedia.org/w/api.php`). inferred from strings, `LPBeetsWrapper.outline.txt:1334-1376`
- Home Share: browses other LAN UPnP media servers found by SSDP. observed `DEC\HOME\HomeShare\LPHomeShareViewController.py:25-48`

Not traced: Browse/Search bodies (decompile cut), the Home Share remote-item play path.

### 3.6 Music services

Mechanism: service accounts live on the speaker. The PC opens the browser for OAuth, receives the code, encrypts it with the speaker's uuid and passes it to the speaker with `UserLogin`; it borrows the token back with `GetUserInfo` to browse the service API itself. To play, it sends the speaker a queue XML whose `SearchUrl` or track ids the speaker resolves.

- Offered list: exactly the four keys of `data\LPSupportedStreamServiceConfig.json` (RadioParadise2, Qobuz, Tidal, WiiMRadio), although a built-in table knows about 50 services. observed `LPDeviceStreamServiceManager.dis.txt:1018-1071`
- TIDAL login: speaker supplies `clientId` and `redirectUrl` (client id AES-decoded with the uuid prefix); browser `https://login.tidal.com/authorize?...&state=pc&restrictSignup=true`; return via `http://localhost:22347/tidal/wiimhome` or `wiim://callback?category=oauth&service=tidal&code=`. observed `OUT\LPClientFramework\LPMSManager\Tidal\LPTidalLoginManager.outline.txt:238-253`, `DEC\LPClientFramework\LPOAuthHttpServer.py:30-77`
- TIDAL API: `https://api.tidal.com/v1/...` with `Authorization: Bearer`; refresh is a new `GetUserInfo` 300 s before expiry; 401 retries once. Endpoints for home, search (`/v1/search/top-hits/`), albums, artists, playlists, mixes, genres, moods, videos, favorites and playlist edits are listed in `evidence\reports\tidal.md`. Images `https://resources.tidal.com/images/<uuid as path>/<WxH>.jpg`. observed `OUT\HOME\StreamService\Tidal\data\LPTidalDataProvider.outline.txt:766-1835`
- Qobuz: OAuth `https://www.qobuz.com/signin/oauth2` with redirect `https://auth.wiimhome.com/qobuz/wiimhome`; API `https://www.qobuz.com/api.json/0.2/` with Bearer token from the speaker (`accessToken` AES-decrypted with the uuid prefix); no request signing found. observed `OUT\LPClientFramework\LPNetworkClient\LPQobuz\LPQobuzRequester.outline.txt:50`, `LPQobuzLoginManager.outline.txt:43`
- WiiM Radio: `POST https://cloud-api.linkplay.com/prod/radio/station/list` (filters `countryCode, categories, tags, pageNo, pageSize, ...`), location `GET https://api.linkplay.com/apiv1/tool/location`; LinkPlay signature headers `accessKey, timestamp, nonce, sign, appId` (SHA-256). Favorites are local only. observed `DEC\HOME\StreamService\WiiMRadio\utils\LPWiiMRadioDataProvider.py:17-30`
- Radio Paradise 2: `https://api.radioparadise.com/api/list_chan?C_user_id=`, stream `.../api/gapless?C_user_id=&player_id=&chan=&bitrate=4` put into `SearchUrl`. observed `OUT\HOME\StreamService\RadioParadise2\LPRadioParadise2ViewController.outline.txt:120`
- Favorites cache per (source, user) as JSON, synced hourly with retries at 30, 120, 600 s. observed `DEC\LPClientFramework\LPFavoriteSyncCoordinator.py:18-21`

Not traced: how the speaker resolves `wiimu_search://` URLs and `SearchUrl` (firmware side).

### 3.7 App shell and infrastructure

- Single instance: `QLocalServer` named `wiim_singleton!#@`; second launch forwards `argv[1]` or `wiim://showApp`. URI schemes `wiim://` and `com.linkplay.wiimhome://` (`callback`, `active`, `showApp`). observed `DEC\LPClientFramework\LPSingletonAppManager.py:26-85`, `util\LPUriHandler.py:23-95`
- Config: `data\config.json` (version, sparkle feeds), `data\feature.yml` (`QUEUE_MOVE_DELETE`), user config `AppConfigLocation\com.linkplay.wiimhome\wiimhome-userconfig.json` (`mymusic-dir, pcId, pcName, userConfig.upnpserver{enable,name,lastUpdate}, otaSession`), window geometry in `QSettings('Linkplay','WiiMHome')`. observed
- Updates: WinSparkle with hard-coded feed `https://assets.wiimhome.com/appexe/appcast-beta-win-x86_64.xml`, automatic checks off; a hidden beta mode is unlocked by repeated taps on the friendly name in My Music settings. observed `OUT\LPClientFramework\LPWinSparkleUpdater.outline.txt:351, 375-391`, `LPUpdateCoordinator.outline.txt:899-932`
- Speaker firmware OTA: no update command found; the app only reads OTA status for telemetry. observed (bounded search)
- Analytics: `POST https://api.linkplay.com/apiv1/mp/collect`, batches of 10 or every 15 s, queue `cacheDir\event_track_queue.json`; events `app_open, screen_view, button_click, device_discovery_report, device_discovery_failure, network_context_snapshot, beets_import_result, ota, tidal_*, ss_wiimradio_*`. observed `DEC\LPClientFramework\LPEventTrack.py:26-53`
- Feedback: Freshdesk ticket `https://freshdesk.linkplay.com/apiv1/freshdesk/wiim/tickets`; speaker logs via `getsyslog` then `http://<ip>/data/sys.log`; app `.log` files AES-128-ECB encrypted into `feedback.zip`; STS `POST https://api.linkplay.com/datav3/log/feedbackUpload` (LKP1-HMAC-SHA256 signature) returns temporary S3 credentials; SigV4 `PUT https://<bucket>.s3.<region>.amazonaws.com/<key>`. observed `DEC\LPClientFramework\LPFeedback\LPFeedbackConfig.py:8-13`, `LPLkp1Signer.py:55-86`, `LPFeedbackS3Uploader.py:41-51`
- Crash: Python crashes to `cacheDir\crash\crash_<ts>.json`; native minidumps to `%APPDATA%\WiiMHome\crashes\`. observed
- Sleep prevention toggle (`preventSleepEnable`) via kernel32. observed `OUT\LPClientFramework\LPHibernation.outline.txt:48-63`
- Localisation: `en` only is selected at runtime (`zh.qm` ships). observed `OUT\HOME\WiiMHome.dis.txt:11476-11479`

## 4. Native pass

Not needed: all application logic is Python bytecode. The QML is plain source and also documents itself (`Qml\AGENTS.md`, `Qml\docs\*.md`, `Qml\Tidal\docs\*.md`, in Chinese).

## 5. Minimal client recipe (what audio-star would need)

1. Find speakers: M-SEARCH `ST: ssdp:wiimudevice` and/or mDNS `_linkplay._tcp.local.`.
2. Identify: SOAP `GetControlDeviceInfo` on `rendercontrol1`, parse `Status` JSON.
3. State: subscribe to the three event services with a local HTTP `/Event` sink; `GetInfoEx` once at start.
4. Control: AVTransport `Play/Pause/Next/Previous/Seek`, RenderingControl `SetVolume/SetMute`.
5. Play your own files: serve them over HTTP with Range support, build the PlayList XML with DIDL metadata, `CreateQueue` then `PlayQueueWithIndex`, `AppendTracksInQueueEx` for the rest.
6. Groups and settings: `httpapi.asp` commands over HTTPS (client certificate behaviour to be tested against a real speaker).

## 6. Coverage and open questions

- Decompile gaps: 198 modules are incomplete as source; facts there come from bytecode. Function bodies cut in both views: ContentDirectory Browse/Search, `LPUpnpAsyncDataModel` (exact `UserLogin` arguments), `LPBeetsWatchDog`.
- Unresolved: does the speaker require the client certificate on `httpapi.asp`; SSDP expiry threshold; `getStatusEx` and settings-getter reply shapes; speaker-side handling of `wiimu_search://` and `SearchUrl`; whether the MediaServer answers `event.xml` subscriptions.
- Untraced UI: full-screen play view, menu bar items, About dialog, Qobuz genre selector and artist biography, TIDAL quality/ReplayGain dialog keys.

## For your judgement

- A mutual-TLS client certificate, private key and CA for talking to speakers ship in `LPTLSTool.py:11-13` (base64 plus ROT13). Anyone with the app has them.
- LinkPlay cloud access and secret keys are hard-coded in `LPEventTrack.py:49-51`, `LPFeedbackConfig.py:10-16` (same values, Freshdesk), `LPCloudDeviceState.py:27-29` and `LPWiiMRadioDataProvider.py`; Discogs `DIS_C` / `DIS_S` in `LPBeetsWrapper`; `FEEDBACK_AES_KEY` in `LPFeedbackConfig`. Not reproduced here. Note: one reading agent's search printed the Freshdesk and analytics values into this session's transcript.
- Account secrets to speakers are protected by AES-CBC with a zero IV and the speaker's own uuid prefix as key (`util\aes.py:13-50`), and the uuid is broadcast by SSDP/mDNS.
- Every HTTPS call to speakers uses `verify=False`; the UPnP control port 59152 is plain HTTP without authentication.
- The PC servers bind `0.0.0.0` (22345 to 22347, 22334, SSDP 1900); the media server only serves files under tracked music folders or in the beets index.
- `musiclibrary.db` has `LibAccount.token` and `refreshToken` columns, and Recently Played `detail` can carry account fields.
