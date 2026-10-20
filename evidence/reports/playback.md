I could not verify everything in the brief from the decompiled source alone. `LPDevice.py` has no method bodies, and the `.py` files for the queue, playlist, media-info and recently modules are garbled by pycdc. Those facts come from the `.dis.txt` disassembly, and the report says so where it matters.

FACT REPORT: WiiM Home playback, queue, presets, recently played

Base paths: `D:\git-projects\audio-star\evidence\outline\` is abbreviated as `OUT\` below. The `.dis.txt` files are authoritative. `.py` line numbers are used only where the docstring is the evidence.

**Protocol base (shared by every block)**
- SOAP POST to `http://<ip>:59152/upnp/control/<endpoint>`. Endpoints: `rendercontrol1` (service `RenderingControl:1`), `rendertransport1` (`AVTransport:1`), `PlayQueue1` (`PlayQueue:1`). Source: `OUT\LPClientFramework\LPDevice.dis.txt:4038, 4120, 4144`.
- URN: `PlayQueue:1` uses `urn:schemas-wiimu-com:service:PlayQueue:1`. Other services use `urn:schemas-upnp-org:service:<svc>`. Source: `OUT\LPClientFramework\UPnPTool.dis.txt:63-73`.
- SOAPACTION header is `"<urn>#<Action>"`. Body is `<u:Action xmlns:u="<urn>"><Arg>value</Arg>...</u:Action>` inside an `s:Envelope`. Source: `OUT\LPClientFramework\UPnPTool.outline.txt:18-40`. Argument values are escaped (inferred from the `escape` import).
- Dispatch: `LPDevice.asyncUpnpPost(cmd, inParams, cb)` runs on a thread and calls `LPDevice.upnpPost(cmd, inParams, apiTimeout)`, which picks endpoint, service and default params per command, then calls `UPnPTool.upnpPost`. Source: `OUT\LPClientFramework\LPDevice.dis.txt:3982-4025` and `:4025-4939`.

---

**FEATURE: Transport (play, pause, next, previous, seek)**
- ENTRY: `LPMiniBarViewController` (`OUT\HOME\Minibar\LPMiniBarViewController.dis.txt:5083-5134`, `:5160-5201`). Also `LPPresetQmlViewController` (Play/Pause, `OUT\HOME\PresetQml\LPPresetQmlViewController.dis.txt:839, 869`), `LPRecentlyPlayedViewController` (`:6696-6708`), `LPMenuBarController` (`OUT\HOME\Menu\LPMenuBarController.dis.txt:355-373`).
- MODULES: `HOME.Minibar.LPMiniBarViewController`, `LPClientFramework.LPDevice`, `LPClientFramework.UPnPTool`.
- DATA: none persisted. Seek and volume update the local `mediaInfo` optimistically.
- MECHANISM: UI calls `asyncUpnpPost(command, inParams)`. `upnpPost` merges defaults under `inParams`.
- PROTOCOL (observed, `OUT\LPClientFramework\LPDevice.dis.txt`):
  - `Play`: `rendertransport1`, `AVTransport:1`, args `InstanceID=0, Speed=1, ControlSource=WiiMApp` (`:4240-4268`).
  - `Pause`: `InstanceID=0, ControlSource=WiiMApp` (`:4276-4303`).
  - `Next`, `Previous`: `InstanceID=0, ControlSource=WiiMApp` (`:4170-4232`).
  - `Seek`: `InstanceID=0, Unit=REL_TIME, Target=<HH:MM:SS>`. No ControlSource (`:4403-4437`). Target is built by `time.strftime('%H:%M:%S', time.gmtime(secs))` (`OUT\HOME\Minibar\LPMiniBarViewController.dis.txt:5163-5200`).
  - `SetVolume`: `rendercontrol1`, args `InstanceID=0, Channel=Master, DesiredVolume=<caller>` (`LPDevice.dis.txt:4311-4349`; caller `LPMiniBarViewController.dis.txt:5378-5380`).
  - `SetMute`: `rendercontrol1`, args `InstanceID=0, Channel=Master, DesiredMute=<caller>` (`LPDevice.dis.txt:4357-4395`; caller `:5500-5502`).
  - Reads: `GetInfoEx` on `rendertransport1` with out-list `CurrentTransportState, TrackDuration, TrackMetaData, TrackURI, RelTime, LoopMode, CurrentVolume, TrackSource, PlayMedium` (`LPDevice.dis.txt:4137-4162`). `GetControlDeviceInfo` on `rendercontrol1` (`:4079-4111`).
- EVIDENCE: all of the above are observed in the `.dis.txt` lines cited.
- UNKNOWNS: value type and range of `DesiredVolume` at the caller. Default `apiTimeout` for transport calls not traced.

**FEATURE: Shuffle and repeat**
- ENTRY: `LPShuffleManager.setShuffle` / `setNoShuffle` / `nextShuffleMode` / `nextLoopMode` (`OUT\LPClientFramework\LPShuffleManager.dis.txt:97-176, 192-251, 595-677, 679-`). Caller sites: `OUT\HOME\Queue\LPQueueDialog.dis.txt:1846, 1903`, `OUT\HOME\PlayView\LPPlayViewQueueSectionController.dis.txt:1551, 1608`.
- MODULES: `LPClientFramework.LPShuffleManager`, `LPClientFramework.LPMediaInfo` (`LPLoopMode`), `LPDevice`.
- DATA: none persisted.
- MECHANISM: compute next `LoopMode` int, then `LPGlobalUI.currentDevice.updateMediaInfo({'loopMode': n})` locally, then `asyncUpnpPost('SetQueueLoopMode', {'LoopMode': n}, callback)`. Callback re-applies the same value.
- PROTOCOL: `PlayQueue1`, `PlayQueue:1`, action `SetQueueLoopMode`, args `LoopMode=<int>` (no InstanceID). outParams `['Result']` (`LPDevice.dis.txt:4439-4465`).
- Enum wire values (`OUT\LPClientFramework\LPMediaInfo.dis.txt:51-75`): `listrepeat=0, singlerepeat=1, repeatshuffle=2, shuffle=3, default=4, singlerepeatshuffle=5`. The constants are 1-tuples, which IntEnum coerces to int (inferred).
- Transitions (observed from dis compare/store pairs):
  - `setShuffle`: singlerepeat→5, listrepeat→2, default→3. No-op if current is shuffle, repeatshuffle or singlerepeatshuffle.
  - `setNoShuffle`: singlerepeatshuffle→1, repeatshuffle→0, shuffle→4. No-op if current is default, singlerepeat or listrepeat.
  - `nextShuffleMode` (toggle): singlerepeat→5, listrepeat→2, shuffle→4, repeatshuffle→0, default→3, singlerepeatshuffle→1.
  - `nextLoopMode` (repeat cycle): singlerepeat→4, listrepeat→1, shuffle→2, repeatshuffle→5, default→0, singlerepeatshuffle→3. The fallback branch was not confirmed.
- Icons: `miniBar/repeat.png`, `miniBar/shuffle.png`, `miniBar/singlerepeat.png` (`OUT\LPClientFramework\LPShuffleManager.outline.txt:46-49`).
- UNKNOWNS: `nextLoopMode` fallback. Arguments passed by the two `LPQueueDialog` call sites.

**FEATURE: Now-playing metadata and cover art**
- ENTRY: `LPStreamServiceMainWindow.updateDeviceMediaInfo` calls `asyncFetchMediaInfo` (`OUT\HOME\WiiMHome.outline.txt:885-886`; `WiiMHome.dis.txt:8711`). UPnP NOTIFY path via `LPUPnPObserverManager`. UI: `LPPlayViewController`, `LPMiniBarViewController`.
- MODULES: `LPClientFramework.LPDevice` (`fetchMediaInfo`, `updateMediaInfo`), `LPClientFramework.LPMediaInfo`, `LPClientFramework.LPUPnPObserverManager`, `LPUtility` (`fetchUrlQPixmap`, `getCachedPixmapWithUrl`).
- DATA: no metadata file. Covers go through an `LPUtility` cache whose path was not traced.
- MECHANISM:
  1. Pull: `fetchMediaInfo` calls `upnpPostWithRetry('GetInfoEx', apiTimeout=5)` (`LPDevice.dis.txt:5592-5605`). Mapping (`:5630-5682`): `CurrentTransportState→playState, TrackDuration→duration, TrackURI→playUri, RelTime→progress, LoopMode→loopMode (int), CurrentVolume→volume (float), TrackSource→trackSource, PlayMedium→mediaType`.
  2. `TrackMetaData` is parsed as DIDL-Lite (`_parseMeta`, `:5711-5931`). Typed fields: `song:quality` (int), `song:actualQuality`, `song:rate_hz` (float → trackRateHz), `song:format_s` (float → trackFormat), `song:bitrate` (float → trackBitrate), `upnp:ratingURI`. Also `dc:title→trackName`, `song:id→trackId`, `custom:uuid→customUUID`, `song:singerid→artistId`, `upnp:artist→artist`, `song:albumid→albumId`, `upnp:album→album`, `upnp:albumArtURI→artworkUri`, `upnp:localAlbumArtURI→localArtworkUri`, `song:guibehavior→guiBehavior`.
  3. Push (event): subscription to `rendercontrol1`, `PlayQueue1`, `rendertransport1` (`OUT\LPClientFramework\LPUPnPObserverManager.dis.txt:1233`). SUBSCRIBE to `http://<ip>:<port>/upnp/event/<svc>` with `CALLBACK: <http://<localIP>:<port>/Event>` and `NT: upnp:event` (`:2225-2271`). Renewal uses `RENEW_RATIO`, `RETRY_INTERVAL`, `FIRST_NOTIFY_TIMEOUT` (`:1233-1246`). Notifications arrive at `POST /Event` and are parsed by `LPSimpleUPnPObserverHandler.do_NOTIFY`, which reads `SID`, `SEQ` and `LastChange` (`OUT\LPClientFramework\LPUPnPObserverManager.outline.txt:189-202`).
     - `LPRenderTransportParser` maps `TransportState→playState, CurrentTrackMetaData→metaData, CurrentTrackURI→playUri, CurrentTrack→lastPlayIndex, TrackSource→trackSource, PlaybackStorageMedium→mediaType, CurrentTrackDuration→duration` (outline lines 96-135).
     - `LPRenderControlParser`: `Volume, Mute, FixVolume, DeviceName, Slave` (lpmrm) (outline lines 50-75).
     - `LPPlayQueueParser`: `LoopMode/LoopMpde→loopMode, CurretPlayListName→info` (outline lines 161-172).
  4. Polling: no periodic `GetInfoEx` loop was found in the scanned modules. Pulls happen at device init (`LPDevice.dis.txt:1176-1190`), on `asyncFetchMediaInfo` (`:1308-1333`), and from the main-window hook above. The caller that triggers `updateDeviceMediaInfo` was not traced. Single-worker queue for mediaInfo refresh: `OUT\LPClientFramework\LPDeviceStreamServiceManager.outline.txt:23-25`.
  5. Cover URL resolution (docstrings, `LPMediaInfo.py:79-119`; logic garbled): prefer `localArtworkUri` when it starts with `http`, else `artworkUri`. A `127.0.0.1` host is replaced with the device IP, keeping the port. Fetch (`LPMediaInfo.py:122-149`): WiiMRadio uses `getCachedPixmapWithUrl` and retries at size 155. Plex and others use `fetchUrlQPixmap` with `privateDevice` and `forceFetch`. A 403 or 404 clears retry; other failures retry after 5 s, at most 2 automatic retries (`:152-192`).
  6. Quality badge (`OUT\HOME\PlayView\LPPlayViewController.dis.txt:2224-2300`): if `trackFormat==0` and `trackRateHz==0`, hide. Otherwise `'%d-bit · %.1f kHz' % (trackFormat, trackRateHz/1000)`, prefixed with `'%.0f kbps | ' % trackBitrate` when `trackBitrate>0`. Labels are not derived from `quality` or `actualQuality` in the traced code.
- PROTOCOL: `GetInfoEx` as above. Event services as above. DIDL keys as above.
- Device-to-PC media paths (not device control): `http://%s:%d/media/music/%s` and `http://%s:%d/media/cover/%s` served by the PC (`OUT\LPClientFramework\LPUPnPHttpServer.outline.txt:188-191`). Used when the device plays PC-local content (inferred).
- EVIDENCE: cited lines.
- UNKNOWNS: exact trigger of `updateDeviceMediaInfo`. Subscription port value (`record['port']`) not traced to a constant. Meaning of quality enum values. Full-screen view cover code path. `mediaInfoInterceptor`, `guardMediaInfoRollback`, `_expireMediaShield` (`LPDevice.dis.txt:7015-7180`) implement a direction-based rollback guard with a watchdog. Only names were read.

**FEATURE: Queue (read, build and send, jump, delete, add)**
- ENTRY: `LPQueueViewController` (`OUT\HOME\Queue\LPQueueViewController.outline.txt`), `LPQueueListView.itemDoubleClick` (`OUT\HOME\Queue\LPQueueListView.dis.txt:3110-3157`), `LPQueueDialog` (MiniBar queue button), `LPPlayViewQueueSectionController`. Build entry points: `LPMyMusicViewController.fastPlay` and similar. Append entries: `LPMyMusicTracksViewController` (context menu → `add_to_next`/`add_to_last`).
- MODULES: `LPClientFramework.LPQueueManager`, `LPClientFramework.LPPlayList.LPPlayList` (`LPPlayMusicList.generateXML`), `LPClientFramework.LPPlayList.LPLocalMusicPlayList`, `LPDevice` (`fastPlay`, `upnpPost`, `parseQueue`, `_resolveQueueTrackImage`).
- DATA: in memory only. `LPQueueManager.playList` and `version`.
- MECHANISM (build and send, `LPDevice.fastPlay`, `OUT\LPClientFramework\LPDevice.dis.txt:3371-3486`; `_asyncPlay` `:3488-3946`; `_chunks` `:3948-3970`). Recipe for a new client to play `list` starting at `index`:
  1. If `len(list)<=1`: `xml = generateXML(list)`. Else `nextIndex = index+1 if index < len-1 else 0`. `xml = generateXML([list[index]])` if `nextIndex==0`, else `generateXML([list[index], list[index+1]])`.
  2. `CreateQueue {QueueContext: xml}`. On `error`, finish(False) and stop. Device forces `QueuePolicy='0'` into the args (`upnpPost`, `:4466-4499`).
  3. `PlayQueueWithIndex {QueueName: header.headTitle, Index: 1}`.
  4. If `len>1`: `appendLimit=500`. `headNum=min(index, 250)`. `tailNum=len-index-2`. If `tailNum+headNum>500`: `tailNum=500-headNum`, else `headNum=min(index, 500-tailNum)`.
  5. Tail: `list[index+2 : index+2+tailNum]`, split into 200-track chunks in order. Each chunk: `AppendTracksInQueueEx {QueueContext: generateXML(chunk), Direction: '1', StartIndex: '0'}`.
  6. Head: `list[index-headNum : index]`, split into 200-track chunks, iterate chunks in reverse. Each chunk: `AppendTracksInQueueEx {QueueContext: generateXML(chunk), Direction: '0', StartIndex: '0'}`.
  7. finish(True).
- Append (`LPQueueManager.add_to_next` / `add_to_last`, `OUT\LPClientFramework\LPQueueManager.outline.txt:79-116`): if not playing a special source, or if playing WiFi content, the device gets `CreateQueue` with a one-track `LPLocalMusicPlayList` (header `MyMusic Track`, `generateXML([item], '1')`). Otherwise `AppendTracksInQueueEx {QueueContext: generateXML([item]), Direction: '1', StartIndex: str(index+1)}` (`add_to_last` uses `len(list)-1+1`). Replacing the queue on the first branch is inferred from the `CreateQueue` usage.
- Read (`requestQueue`, `OUT\LPClientFramework\LPQueueManager.outline.txt:65-78`): `asyncUpnpPost('BrowseQueue', {QueueName: 'CurrentQueue'})`. Device returns `{musicList, version, xml}` via `parseQueue` (`LPDevice.dis.txt:4561-4636`). `parseQueue` (`:6002-6441`) reads `QueueVersion`, `LastPlayIndex` (→ `index = int-1`), `ListName`, `SourceName`, `TrackNumber`, `Quality`, `SearchUrl`, `PicUrl`. Per track: `Source→trackSource`, `Id→trackId` (overridden by `song:id` or `id` in metadata), `URL→trackUrl`, `Metadata` DIDL → `dc:title`, `upnp:artist`, `upnp:album`, `res@duration`, `upnp:albumArtURI` (via `_resolveQueueTrackImage`). Source-specific `streamService.parseQueuePlayItem` is used when available. Tracks with neither `trackId` nor `songId` are skipped.
- Jump: `PlayQueueWithIndex {QueueName: 'CurrentQueue', Index: row+1}` (1-based) (`LPQueueListView.dis.txt:3142-3154`).
- Delete: `RemoveTracksInQueue {QueueName: 'CurrentQueue', RangStart: row+1, RangEnd: row+1}` (1-based) (`LPQueueManager.outline.txt:223-235`; device `LPDevice.dis.txt:4749-4771`). Success is `status_code==200`. A second helper `delete_from_queue(index)` passes `RangStart=index` (0-based), and no HOME caller was found in the outlines.
- Current index: `GetQueueIndex {QueueName: 'CurrentQueue'}` returns `CurrentIndex`, `PreloadingIndex` (`LPDevice.dis.txt:4773-4799`).
- Not queueable: `queueSpecialMediaType` = radio, station, Spotify, TIDAL Connect, Roon, Chromecast (`LPQueueManager.outline.txt:22-24`).
- QUEUE XML (`LPPlayMusicList.generateXML`, `OUT\LPClientFramework\LPPlayList\LPPlayList.outline.txt` and `.py:89-124`):
  ```
  <?xml version="1.0"?><PlayList>
    <ListName>{escape(headTitle)}</ListName>
    <ListInfo><Radio>0</Radio><SourceName>{mediaSource}</SourceName><TrackNumber>{n}</TrackNumber>
      <SearchUrl>{escape(searchUrl)}</SearchUrl><Quality>0</Quality><PicUrl>{escape(imageUrl)}</PicUrl>
      <StartPlayIndex>{startPlayIndex or ''}</StartPlayIndex></ListInfo>
    <Tracks>
      <Track1><URL>{escape(trackUrl)}</URL><Source>{mediaSource}</Source><Id>{escape(trackId)}</Id>
        <Metadata>{escape(DIDL)}</Metadata></Track1>
      ...
    </Tracks>
  </PlayList>
  ```
  The DIDL string is `<?xml version="1.0" encoding="UTF-8"?><DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.linkplay.com/song/" xmlns:custom="www.linkplay.com/custom/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item>` followed by `[<custom:uuid>{LPUtility.pcUUID()}</custom:uuid> only when mediaSource == 'PC_RemoteLocal']<song:id>{trackId}</song:id><song:albumid>{albumId}</song:albumid><song:singerid>{artistId}</song:singerid><dc:title>{escape(trackName)}</dc:title><upnp:artist>{escape(artist)}</upnp:artist><upnp:album>{escape(album)}</upnp:album><res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration="{int}">{escape(trackUrl)}</res><upnp:albumArtURI>{escape(trackImage)}</upnp:albumArtURI></item></DIDL-Lite>`. Note: `song:id`, `song:albumid` and `song:singerid` are not escaped. The whole DIDL is then escaped into `Metadata`. Source `OUT\LPClientFramework\LPPlayList\LPPlayList.outline.txt:84-96` and `.py:89-124`.
  - Local-music header: `LPLocalMusicPlayHeader` sets `mediaSource = PC_RemoteLocal` (`OUT\LPClientFramework\LPPlayList\LPLocalMusicPlayList.outline.txt:74`).
- PROTOCOL: all calls are to `http://<ip>:59152/upnp/control/PlayQueue1`, service `PlayQueue:1` (urn `urn:schemas-wiimu-com:service:PlayQueue:1`). Actions: `CreateQueue(QueueContext)`, `AppendTracksInQueueEx(QueueContext, Direction, StartIndex)`, `PlayQueueWithIndex(QueueName, Index)`, `BrowseQueue(QueueName)`, `RemoveTracksInQueue(QueueName, RangStart, RangEnd)`, `GetQueueIndex(QueueName)`, `SetQueueLoopMode(LoopMode)`, `DeleteQueue`, `BackUpQueue(QueueContext)`.
- EVIDENCE: cited lines.
- UNKNOWNS: `apiTimeout` defaults. Whether `CreateQueue` replaces the queue on the device (inferred). `Direction` semantics (inferred from names). `drag_drop_rows` (`LPDevice.dis.txt:6563-6700`) reorder action not traced. `LPQueueManager.py` is garbled (e.g. `None.get('musicList')` at `:97`), so logic comes from `.outline.txt`.

**FEATURE: Presets (read, play, save, delete)**
- ENTRY: `LPPresetQmlViewController` (QML `Qml\Preset\LPPresetQmlPage.qml`, `LPPresetQmlCard.qml`). Legacy widget `LPPresetViewController` shares the same protocol. Save: `LPCommonWidgets\menu\LPPresetMenu` (`.outline.txt:80-88`).
- MODULES: `HOME.PresetQml.LPPresetQmlViewController`, `HOME.PresetQml.LPPresetQmlStore`, `LPClientFramework.LPPresetManager` (`PresetManager`), `LPClientFramework.LPDevice`, `LPStreamServiceManager` (`presetSourceCanPlay`, `supportContents()[source]['preset_icon']`).
- DATA: device-side key mapping only. Cover images go to a local cache (`LPUtility.getCacheImageUrl`, path not traced).
- MECHANISM:
  - Read (`_fetchPresetList`, `OUT\HOME\PresetQml\LPPresetQmlViewController.outline.txt:252-281`): if `presetNum==0`, page is "not supported". Otherwise `GetKeyMapping {}`, response `QueueContext` is the key XML. `parseXmlAndBuildItems` (`LPPresetQmlStore.outline.txt:151-170`) reads `KeyList` and `Key{n}` with `Name`, `Source`, `PicUrl`. `_297`-style `_#~` suffix is stripped for display. Empty slots get `_emptyItem`. `canPlay` uses `presetSourceCanPlay` (Pandora and Pandora2 rules; unknown account state is optimistic, and `GetUserInfo` is fetched per source).
  - Play (`onPresetClicked`, `:124-141`): if the preset cannot play, show a toast and send nothing. If the preset is the one currently playing, send `Pause` or `Play` via `_togglePlayback` (`:245-250`). Otherwise send `MCUKeyShortClick:<n>` over HTTP: `commonHttpGet` (`LPPresetQmlViewController.dis.txt:876-884`).
  - Playing-state match (`_refreshPlayingInfo`, `:212-228`): the cached queue name from `BrowseQueue(CurrentQueue).musicList.header.headTitle` is compared against each preset's display name, with `playState` and `trackSource` (names-only evidence, inferred).
  - Save (`LPPresetMenu.preset`, `OUT\LPCommonWidgets\menu\LPPresetMenu.outline.txt:80-88`): `presetManager.getPlayList` (`BrowseQueue`), `streamService.backupXml(playList, listName, playSection)`, then `BackUpQueue {QueueContext: backupXml}` (`OUT\LPClientFramework\LPPresetManager.dis.txt:121-156`). Then `replaceItemXml` → `replaceKeyMappingXml(index, replaceItemXml, keyMappingXmlObj)` (`:157-`), which replaces the `Key{index}` children and escapes each `Metadata` child's content. Then `SetKeyMapping {QueueContext: xml}`.
  - Delete (`_removePresetItem`, `:283-307`): `Key{index}` is replaced with `<RoutineId>Empty</RoutineId>` inside `<container>`, then `SetKeyMapping {QueueContext: xml}`. Success is `status_code==200`, then local model refresh.
  - Key block builder: `buildKeyBlock` creates `<Key><RoutineId>Empty</RoutineId></Key>`, and `insertKeyBlock` inserts blocks up to `MaxNumber` (`OUT\LPClientFramework\LPPresetManager.outline.txt:51-93`).
- PROTOCOL: `PlayQueue1` actions `GetKeyMapping {}` (out `QueueContext`), `SetKeyMapping {QueueContext}`, `BackUpQueue {QueueContext}`, `BrowseQueue {QueueName: 'CurrentQueue'}`. HTTP: `GET https://<ip>/httpapi.asp?command=MCUKeyShortClick:<n>` through `commonHttpGet` with the device TLS certificate (`OUT\LPClientFramework\LPDevice.outline.txt:636`, `LPTLSTool`).
- EVIDENCE: cited lines.
- UNKNOWNS: exact `Key` content written for a saved source (depends on each stream service's `backupXml`, not traced). `MCUKeyShortClick` response body. `PLAY_SECTION_NAME_MAP_FOR_QOBUZ` and `playSection` values. Whether `MaxNumber` is always present.

**FEATURE: Recently played (storage, write, read, play)**
- ENTRY: `LPRecentlyPlayedViewController.onRecentlyCardPlayClicked` (`OUT\HOME\RecentlyPlayed\LPRecentlyPlayedViewController.outline.txt:598-609`). Read via `getRecentlyRawList`. QML: `Qml\RecentlyPlayed\LPRecentlyPlayed.qml`, `LPRecentlyPlayedCard.qml`, `LPRecentlyPlayedMosaicCover.qml`, `LPRecentlyPlayedSeeAll.qml` (not read).
- Write callers: `addRecentlyPlayedWithMusicList` / `addRecentlyPlayedWithAccount` appear in the StreamService modules (`LPStreamServiceDir\LPQobuzStreamService`, `LPTidalStreamService`, `LPRadioParadise2StreamService`, `LPWiiMRadioStreamService`, `LPPCRemoteLocalStreamService`) and in the MyMusic controllers (names only).
- MODULES: `LPClientFramework.LPMusicLibrary.LPRecentlyManager`, `LPRecentlyPlayListCodec`, `LPMusicLibraryDBManager`, `LPMusicDatabase`. Play: `LPStreamServiceDir.LPPCRemoteLocalStreamService.playRecently` (`.outline.txt:86-102`) and the other stream services.
- DATA: SQLite at `{userDataDir}/beets/musiclibrary.db` (`OUT\LPClientFramework\LPMusicDatabase.outline.txt:4, 17`). Shared with beets.
  - Tables: `LibAccount` (`accountId, source, userId, userName, token, refreshToken, detail`), `LibMusicList` (`directoryId, directoryName, directoryType, accountId, source`), `LibMusicItem` (`itemId, directoryId, directoryName, directoryType, accountId, source, trackName, trackId, trackImage, trackArtist, typeValue, openMore, canNavigate, checkDuplicate, detail, createTime`) (`OUT\LPClientFramework\LPMusicLibrary\LPMusicLibraryDBManager.outline.txt:44-46, 87`).
  - Recently directory: `directoryName='recently'`, `directoryType='favorite'` (`LPMusicLibraryDBManager.dis.txt:37-40`). `detail` is JSON (`.outline.txt` docstring).
  - Capacity: `RECENTLY_MAX_COUNT`, value not read. Default read limit 200 (`LPRecentlyManager.dis.txt:68`). Notification `RecentlyPlayedChangedNotify` (`:66`).
- MECHANISM:
  - Write: `LPRecentlyPlayListCodec.playListToDetail(playList, showDict, extra)` builds `detail = {"playList": ..., "show": ..., "account": ...}` from public attributes. Non-basic values are dropped. `headType` is stored as int (`LPRecentlyPlayListCodec.outline.txt:45-59`). `_writeRecentlyItem` keys rows as `'%s_%s_%s'` (`LPRecentlyManager.outline.txt:113`). Queue-type headers (Collection, Playlist, Album, Artist, Station) dedupe by list id. Songs dedupe by track id (`LPRecentlyManager.py` docstring lines 3-4). Writes are skipped when `playOrigin == 'search_track'` (`LPRecentlyManager.outline.txt:79-83`). The insert trims to `RECENTLY_MAX_COUNT`.
  - Read: `getRecentlyRawList(limit=200)`, ordered by `createTime` descending.
  - Play: `onRecentlyCardPlayClicked` toggles play/pause if the item is already playing (`PLAYING`, `TRANSITIONING`, `PAUSED_PLAYBACK`). Otherwise `playRecently(detail)` on the source's stream service, which calls `LPRecentlyPlayListCodec.playListFromDetail` (headType via `headerTypeEnum`, items, index) and then `fastPlay`. Playback therefore uses the Feature "Queue" sequence (`LPPCRemoteLocalStreamService.outline.txt:87, 198`).
  - Gating: `isAccountMismatch` for sources in `SOURCES_NO_LOGIN`-inverse logic. Unknown device account state is optimistic.
  - Delete: `deleteRecentlyItems(itemIds)` on the DB, then notification.
- PROTOCOL: no new device protocol. Playback is the `fastPlay` sequence above.
- EVIDENCE: cited lines.
- UNKNOWNS: `RECENTLY_MAX_COUNT` value. `LibMusicList` usage. Codec logic beyond docstrings (garbled in `.py`). Security flag: `LibAccount` has `token` and `refreshToken` columns, and `_accountDict` copies `token` and `refreshToken` keys into `detail` (`LPRecentlyManager.outline.txt:58-71`). Names only; values not read.

**FEATURE: Mini bar and play view (controls and display)**
- ENTRY: `LPMiniBarViewController` (`OUT\HOME\Minibar\LPMiniBarViewController.outline.txt`). `LPPlayViewController` (`OUT\HOME\PlayView\LPPlayViewController.outline.txt`).
- MECHANISM: Mini bar wires prev/next, play/pause (`PLAYING`, `PAUSED_PLAYBACK`), progress/seek, volume (`LPVolumeSliderViewController`), mute, queue button (`LPMinibarQueueButton` → `LPQueueDialog`), group edit dialog, marquee labels. Play view: `_updateSource` (source label and icon from `sourceInfoForMedia`), `_updateCoverImageAsync` (AIRPLAY special case), `_updateBackgound` (palette background via `LPPlayViewUtil.getPaletteBackgroundPixmap`), `_updateFormat` (quality badge above), `_updatePlayState`.
- EVIDENCE: `OUT\HOME\PlayView\LPPlayViewController.outline.txt:255-303`, `:265-269`.
- UNKNOWNS: layout policy (`LPPlaybackLayoutPolicy`), progress and volume sliders, full-screen content controllers, `LPPlayViewUtil` internals, and `LPPlayViewController` background logic were not read in depth.

---

**Other features discovered (not traced)**
- Group and device volume and mute from the device dashboard: `OUT\HOME\DeviceDashboard\LPDeviceItemWrapper.dis.txt:920, 996` and `LPGroupItemWrapper.dis.txt:2655` (`SetMute`, `SetVolume`). Likely belongs to the groups agent.
- Drag-and-drop queue reorder: `LPDevice.drag_drop_rows` (`LPDevice.dis.txt:6563-6700`).
- Recently: favorite toggle (`_setRecentlyFavorite`, `:738-745`) and per-card preset menu (`_openRecentlyPresetMenu`, `:725-733`).
- `mediaInfoInterceptor` / `guardMediaInfoRollback` direction shield with watchdog (`LPDevice.dis.txt:7015-7180`).
- Device capability and status: `supportCapability`, `fastPlay` error paths.

**Side effects:** none. I wrote no files and ran no commands other than reads and searches. The tool layer saved one oversized Grep result to `C:\Users\AlexanderKastil\.claude\projects\D--git-projects-audio-star\8e097470-b398-46fa-bccf-3495bd60b6fa\tool-results\toolu_01JyaTBw6pJX2FMqAP6EDUys.txt`. That file is harness output, not something I wrote.

**UI-named features in scope that could not be traced:**
- Full-screen play view content (`LPPlayViewFullScreenContentController`, `LPPlayViewFullScreenQueueContent`).
- `LPProgressSlider`, `LPVolumeSlider` (only the device calls were traced, via the mini bar).
- `LPPlaybackLayoutPolicy`.
- `LPMinibarCoverButton`, `LPMinibarTrackButton`, `LPMinibarArtistButton` (names only).
- `LPQueueOptionMenu` (per-row actions beyond delete and jump).
- `LPRecentlyPlayed` QML files (not read).
- Preset card QML (`LPPresetQmlCard.qml`, `LPPresetQmlPage.qml`) (not read).