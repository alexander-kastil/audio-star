Task: reverse-engineering read of WiiM Home's local music library and PC media-server features, per the report contract. Read-only; no files written, no URLs contacted, no app launched, and the user's library database was not opened.

Base paths used below: DEC = `D:\git-projects\audio-star\evidence\decompiled`, OUT = `D:\git-projects\audio-star\evidence\outline`, WH = `C:\Users\AlexanderKastil\AppData\Local\WiiMHome`.

Questions: the ten features in the lead's list plus Home Share, SMB and caches (one block each below).

---

**FEATURE: Music folder selection and add (My Music folders)**
- ENTRY: `LPMyMusicSettingViewController` (DEC\HOME\LPMyMusicSettingViewController.py; QFileDialog Directory mode, inferred from OUT\HOME\LPMyMusicSettingViewController.outline.txt:162). Adds through `LPMyMusicViewController.myMusicDirAddCallback` (OUT\HOME\LPMyMusicViewController.outline.txt:315) → `_addDirAndQueueImport` (:253-254).
- MODULES: HOME.LPMyMusicSettingViewController, HOME.LPMyMusicViewController, LPClientFramework.LPUtility, LPClientFramework.LPBeetsWrapper.
- DATA: `wiimhome-userconfig.json` in userDataDir, key `mymusic-dir` (list of paths). Default is the Windows Music folder.
- MECHANISM: 1) directory picked; 2) `isDBBusy` check; 3) `addMymusicDir` writes config; 4) `LPBeetsWrapper.importWithoutMusicBrain(dir, callback)`; 5) if the import queue rejects, `removeMymusicDir` rolls back. Remove path: `removeDirMethod` → `removeMymusicDir`, `clearLibraryIfNoMusicDir`, `removeDirAsync` (OUT\HOME\LPMyMusicViewController.outline.txt:244).
- PROTOCOL: none (local only).
- EVIDENCE:
  - observed (DEC\LPClientFramework\LPUtility.py:278): `configPath = userDataDir / 'wiimhome-userconfig.json'`.
  - observed (LPUtility.py:282-292): default list = `[QStandardPaths MusicLocation]`.
  - observed (LPUtility.py:305, 319-323): key `'mymusic-dir'` normalised; non-list values reset.
  - observed (LPUtility.py:326-347): `_saveUserConfigSafely` writes the whole JSON.
  - inferred (names/strings only): the entry and rollback flow above (outline lines cited).
- UNKNOWNS: `_loadUserConfigSafely` body is cut off (LPUtility.py:360). The file-dialog body is not in the .py (decompile incomplete).

**FEATURE: Import and tagging (beets)**
- ENTRY: `importWithoutMusicBrain` / `importDirAsync` / `forceImportTrack` (OUT\LPClientFramework\LPBeetsWrapper.outline.txt:1783-1845). Startup: `LPStreamServiceMainWindow.start` calls `scheduleStartupLocalMusicInitialization` (OUT\HOME\WiiMHome.outline.txt:638, inferred).
- MODULES: LPClientFramework.LPBeetsWrapper (core), beetsplug.lpbeetsplug (WH\beetsplug\lpbeetsplug.py), LPClientFramework.LPMusicDatabase, LPClientFramework.LPUtility; external `beets` package.
- DATA:
  - beets library: userDataDir\beets\musiclibrary.db (see Library database).
  - beets config copy: userDataDir\beets\config.yaml (inferred; strings `beets`, `config.yaml`, `BEETSDIR` at outline:1161-1165).
  - stage dir: cacheDir\beets-stage\task-<id>\ (observed string `'beets-stage'` at LPBeetsWrapper.dis.txt:608; `task-%d` at outline:1016).
  - bundled config: WH\data\beets-config.yaml.
- MECHANISM:
  1. `initBeets`: sets env `BEETSDIR`; loads bundled `beets-config.yaml`; if bundled `wiimversion` is newer than the user copy, overwrites (inferred from strings, outline:1172-1173); sets library path, `pluginpath` (`./beetsplug`, or `./LPClientFramework/beetsplug` when frozen, outline:1175-1177); builds import baseline (incremental, singletons, autotag, resume); starts `LPBeetsTaskCoordinator` and the watchdog.
  2. `LPBeetsTaskCoordinator` (observed names, outline:509-542): one worker thread, an exclusive queue and a deferred queue, dir generations. Task types (outline:405-417): startup_local_init, batch_import, remove_dir, clear_library, rescan_upnp, dir_supplement, file_import, file_delete, mb_import.
  3. `batch_import` (`_runBatchImportTask`, outline:1669-1709): backs up the main DB read-only with the SQLite backup API into a stage DB (`createStageDatabase`, `_backupSqliteDatabase`); runs `runStagedImport` in batches with cancel support; then `mergeStagedBeetsTables` into the main DB in one transaction; then `finishStagedImport`. A dir supplement follows.
  4. Per-file: `callBeets(['import', '-I', '-s', '-A', <path>])` for file_import (outline:1644-1650); `['import', '-I', '-s', '-a', ...]` for mb_import (outline:1663-1667). Flag meanings are beets semantics (inferred).
  5. `replace_import_func` swaps beets' import function and encodes paths as UTF-8 with surrogateescape (outline:1527-1545, inferred).
  6. Progress goes to the UI via notifications `LibraryTaskUIUpdate` and `MyMusicDirTrackingUpdate` (outline:61-62, 397-404).
- PROTOCOL: none (local only).
- EVIDENCE:
  - observed (WH\data\beets-config.yaml:6-22): `copy: no`, `write: no`, `move/link/hardlink/reflink/delete: no`. Files are indexed in place; beets does not copy or rewrite tags on disk.
  - observed (beets-config.yaml:24-36): `autotag: yes`, `singletons: no`, `duplicate_action: ask`.
  - observed (beets-config.yaml:163-168): plugins `lyrics`, `fromfilename`, `lastgenre`, `lpbeetsplug`.
  - observed (beets-config.yaml:40-41): clutter and ignore patterns (`.*`, `*~`, `System Volume Information`, `lost+found`).
  - observed (beets-config.yaml:56, 73-75): `art_filename: cover`, `pluginpath: []`, `threaded: yes`.
  - observed (lpbeetsplug.py:6-38): `BeetsPlugin` listening on `database_change`; skips while import/scan/delete is active; calls `addUPnPDBItemsBatch` or `addUPnPDBItem`, or deletes the `wiim_upnpitems` row when the item is gone.
  - observed (LPBeetsWrapper.py:23): `import musicbrainzngs`.
  - observed (LPBeetsWrapper.dis.txt:608): `'beets-stage'`.
  - inferred (names/strings only): everything else in the mechanism list.
- UNKNOWNS: the .py stops at about line 129 (LPBeetsWrapper.py.err: "PycBuffer::getByte(): Unexpected end of stream"). Coordinator and staging bodies come from outline names and strings only. `statefile: state.pickle` (beets-config.yaml:111) location not traced.

**FEATURE: Folder watching (live import and removal)**
- ENTRY: `LPBeetsWatchDog.startWatch` (started from initBeets and from `importDirAsync` flows); stopped from `stop()`.
- MODULES: LPClientFramework.LPBeetsWrapper (LPBeetsWatchDog, LPPollingObserver, LPPollingEmitter, beetsWatcherHandler), watchdog library.
- DATA: pickle snapshots `cacheDir\watchdog-<name>.pickle` (inferred from `dump` and `initDiff` strings, outline:325-353).
- MECHANISM:
  - `LPPollingObserver` (watchdog PollingObserver) with preset snapshot so startup does not rescan (observed DEC\LPClientFramework\LPBeetsWrapper.py:38-75).
  - `watchDirs` reduces tracked My Music dirs to the minimal set of parent dirs (outline:290-293).
  - Filter patterns `*.<ext>` for each `musicFileType` (outline:294-298).
  - Events: create/modify → `forceImportTrack`; delete/move → `removeFileFromBeets` (outline:369-391), only for audio files and not while import is active.
  - `initDiff`: loads last pickle, diffs against the current snapshot, and applies created/modified/deleted/moved (outline:338-353).
- PROTOCOL: none.
- EVIDENCE:
  - observed (LPBeetsWrapper.py:38-75): polling emitter/observer classes.
  - inferred (names/strings only): the rest.
- UNKNOWNS: `LPBeetsWatchDog` body is past the truncation point. The watched-dir logic is from names only.

**FEATURE: Metadata and artwork sources**
- ENTRY: beets autotag (mb_import / batch import) and `fetchMusicBrainzArtistInfo`, `fetchMusicBrainzArtworkUrl` (outline:1322, 1845) for artist pages.
- MODULES: LPBeetsWrapper, LPWikipedia (DEC\LPClientFramework\LPWikipedia.py), LPUtility, LPMediaHttpServer (cover); beets plugins `lastgenre`, `lyrics`, `fromfilename`; musicbrainzngs; wikidata.client; requests.
- DATA: DB tables `wiim_artists` (avatar, Wikidata, Wikipedia columns); cache `cacheDir\linkplay_requests.sql` (Wikipedia HTTP cache).
- PROTOCOL (no secret values printed):
  - MusicBrainz: `musicbrainz.org`, host and rate limit (beets-config.yaml:113-121, observed). `musicbrainzngs.search_artists(artist, limit, strict)` and `get_artist_by_id(mbid, includes=['url-rels'])` (outline:1334-1346, inferred).
  - Discogs: `GET https://api.discogs.com/artists/<id>?key=<DIS_C>&secret=<DIS_S>`, `User-Agent: WiiMHome/<version> +https://wiimhome.com/`, reads `X-Discogs-Ratelimit-Remaining`, `images.primary.uri`, `uri150` (outline:1349-1367, inferred). Keys are module constants `DIS_C` and `DIS_S` in LPBeetsWrapper (DEC\LPClientFramework\LPBeetsWrapper.py:23-45 area, observed names at LPBeetsWrapper.dis.txt:291-295). Values not reproduced.
  - Wikidata: `wikidata.client.Client` loads the entity; sitelink `'%swiki'` gives the title (dis 18369-18374, outline:1874-1876, observed/inferred).
  - Wikipedia: `LPWikipedia.Wikipedia(currentLan, ExtractFormat.HTML, cachePath=LPUtility.cacheDir / 'linkplay_requests.sql')` (LPBeetsWrapper.dis.txt:18521-18533, observed). API base `https://<lang>.wikipedia.org/w/api.php` (LPWikipedia.py:419, observed).
  - MusicBrainz relation type UUIDs used to pick social links and Wikidata (outline:1861-1869): `99429741-…` (social network), `689870a4-…` (Wikidata). Mapping inferred.
- MECHANISM:
  - Artist info: read `wiim_artists` row; if no `wikidata`/`wikipedia` cached, fetch MB artist with url-rels, extract social/Wikidata links, load Wikidata, fetch the Wikipedia summary in the user language, write `UPDATE wiim_artists SET wikidata=?/wikipedia=?` (outline:1845-1886, inferred).
  - Artwork: MB → Discogs artist image; empty result inserts `avatar_url='na'` (outline:1369-1373).
  - Album covers: embedded art via `mediafile` (see Media HTTP server).
  - Genre: beets `lastgenre` plugin with `auto: no`, `force: yes` (beets-config.yaml:166, 173-175, observed). Bundled genre lists at WH\beetsplug\lastgenre\genres.txt and genres-tree.yaml (Glob observed).
- EVIDENCE: as tagged above. Last.fm: `grep lastfm|last\.fm` over DEC\LPClientFramework returned no match, so no Last.fm code or key exists in WiiMHome's own code. The beets `lastgenre` plugin source is not in the bundle.
- UNKNOWNS: Discogs and Wikipedia call bodies are from names and strings only. The exact MB relation-type mapping is inferred.

**FEATURE: Library database**
- ENTRY: n/a (storage).
- MODULES: LPClientFramework.LPMusicDatabase (DEC\LPClientFramework\LPMusicDatabase.py), LPBeetsWrapper (`_initTables`), LPMusicLibrary (Recently shares the file).
- DATA: `userDataDir\beets\musiclibrary.db`. Not opened (named only). Stage copy: `cacheDir\beets-stage\task-<id>\` plus the stage file.
- MECHANISM:
  - Path: `(userDataDir / 'beets' / 'musiclibrary.db').resolve()` (LPMusicDatabase.py:20-33).
  - Connection: busy timeout 5000 ms; journal mode WAL; `row_factory = sqlite3.Row`; read-only URI opens with `mode=ro` (LPMusicDatabase.py:22-23, 36-58).
  - Tables: beets `items` and `albums` (beets schema; query strings at outline:1385-1397, 1234-1236); `wiim_artists` (id, artist, mb_urllist, avatar_url, thumbnail_url, avatar_suburl, wikidata, wikipedia, UNIQUE(id, artist)); `wiim_upnpitems` (id, upnp_title, upnp_id, upnp_parentid, upnp_refid, upnp_class, item_id → items.id, upnp_thumbnail, child_count, upnp_date, ... truncated at outline:1210).
  - Versioning: `PRAGMA user_version`; migrations add `wikidata`, `wikipedia` columns (outline:1211-1217).
  - Indexes: `BEETS_ITEMS_INDEX_SCRIPT` on items(path), items(genre), items(artist,title), items(album,albumartist), and more (outline:75).
  - Beets-owned table signatures validated before a staged merge (`_validateBeetsOwnedSchemas`, outline:1090).
- PROTOCOL: none.
- EVIDENCE:
  - observed (LPMusicDatabase.py:6, 20-33): path and shared use.
  - observed (LPMusicDatabase.py:22-58): PRAGMAs and connect.
  - inferred (names/strings): the table DDL and migrations from outline strings.
- UNKNOWNS: full `wiim_upnpitems` DDL is cut in the string constant. The beets `items` column list is not in the bundle (beets package schema).

**FEATURE: Browse albums, artists, genres, tracks (My Music UI)**
- ENTRY: `LPMyMusicViewController` (DEC\HOME\LPMyMusicViewController.py; tree of My Music dirs) and tab controllers `LPMyMusicAlbumsViewController`, `LPMyMusicArtistsViewController`, `LPMyMusicGenresViewController`, `LPMyMusicTracksViewController`, plus detail controllers (DEC\HOME\MyMusic\*). Sidebar wiring for My Music not traced (WiiMHome.py:23-43 imports only).
- MODULES: HOME.LPMyMusicViewController, HOME.MyMusic.*, LPClientFramework.LPBeetsWrapper (queries).
- DATA: reads DB only.
- MECHANISM: each controller calls LPBeetsWrapper query functions in-process (synchronous):
  - `queryAlbums(key, sortBy, artist, strict, lib)` (outline:1382-1416): sort by album, artist, playcount, dateadd; `GROUP BY album, COALESCE(NULLIF(albumartist,''), artist)`; each result carries `imageUrl`.
  - `queryAlbumArtists(key, sortBy, strict, lib)` (outline:1244-1259): artist, album_count, avatar_url from `wiim_artists`.
  - `queryGenres(sortBy, lib)` (outline:1230-1242): genre, count (sort genre or albumcount).
  - `queryTracks(title, artist, album, sortBy, desc, strict, genre, parentPath, pageSize, offset)` (outline:1434).
  - Album detail → `queryTracks`; artist detail → `queryAlbumArtists`; track row → `queryTrackArtists` (LPMyMusicAlbumDetailViewController.outline:166, 225, 268).
- PROTOCOL: cover URLs in the rows are `http://<localIP>:22345/media/cover/<hex>`, so the UI loads covers from its own media server (outline:1404, inferred).
- EVIDENCE: names and strings only (inferred), with the function list above.
- UNKNOWNS: the controllers' bodies are cut off in the .py files; their sort and paging wiring is from names only.

**FEATURE: PC UPnP MediaServer (SSDP and ContentDirectory)**
- ENTRY: `LPMyMusicSettingViewController._upnpToggleClicked` (outline:88-92, inferred) → `LPQTSSDPServer.start()` and `LPHttpServerManager.startOne('upnp')`. At app start, `LPStreamServiceMainWindow.start` checks `upnpserver.enable` (WiiMHome.outline.txt:655-657, inferred).
- MODULES: LPClientFramework.LPQTSSDPServer, LPUPnPHttpServer, LPHttpServerManager, LPUtility, LPBeetsWrapper (queries and rescan), cherrypy, PyQt6.QtNetwork, beets.util.
- DATA: WH\data\LPUPnPServer.xml (device description template), WH\data\LPContentDirectory.xml (SCPD template); userconfig key `upnpserver` with `name`, `enable`, `lastUpdate`; `wiim_upnpitems` table.
- MECHANISM:
  - SSDP: binds UDP 1900 on 0.0.0.0 with ShareAddress and ReuseAddressHint; joins multicast 239.255.255.250 on each valid interface (LPQTSSDPServer.py:15-16, 186-188, observed).
  - M-SEARCH → `RequestHandler.run` → `received_MSEARCH` → `respond_MSEARCH` (unicast reply) (LPQTSSDPServer.py:52, 102-119, observed).
  - NOTIFY alive: four messages (`''` uuid, `upnp:rootdevice`, `ContentDirectory:1`, `device:MediaServer:1`) at start and every `responseExpire + 600` s (:74-81, 196-202, observed). byebye on stop (:84-91, 215-225, observed).
  - HTTP: cherrypy tree with `upnp` (DeviceDescription, images, ContentDirectory). Device description is `LPUPnPServer.xml` with `%s` for friendly name, model number, and `uuid:<pcUUID>` (LPUPnPHttpServer.py:29-41, observed).
  - SOAP control (`control_xml`): reads `SOAPAction`, dispatches Browse / Search / GetSearchCapabilities / GetSortCapabilities (outline:75-91, inferred).
  - Browse (`dealWithBrowse`): args ObjectID, BrowseFlag, Filter, StartingIndex, RequestedCount, SortCriteria; `BrowseMetadata` or `BrowseDirectChildren`; SQL `SELECT * from wiim_upnpitems u left join items i on (u.item_id = i.id) where upnp_parentid='%s' and u.upnp_title is not null and u.upnp_title != '' %s limit %d, %d;` (outline:94-119, inferred).
  - Sort mapping observed (LPUPnPHttpServer.py:133-151): `upnp:class`→`u.upnp_class`, `dc:title`→`i.title`, `dc:date`→`u.upnp_date`, `upnp:originaltracknumber`→`i.disk, i.track`, `upnp:album`→`i.album`.
  - Search (`dealWithSearch`): parses `derivedfrom "x"` → `like "x%"`, `contains "x"` → `like "%x%"`; maps `dc:title`, `dc:creator`, `upnp:class`, `upnp:artist`, `upnp:album`, `upnp:genre`, `@id`, `@refID`; paged SELECT with UNION ALL (outline:121-177, inferred).
  - Object IDs (LPBeetsWrapper.dis.txt:268-284, observed): root containers AllMusic `0$4`, genre `0$5`, artist `0$6`, album `0$7`, folder `0$14`, playlist `0$F`. Children are `<parent>$<n>` (containers) and `%s$%s` for tracks (outline:891-925, inferred).
  - DIDL-Lite: track `<item>` with `dc:title`, `upnp:class object.item.audioItem.musicTrack`, `dc:creator`, `upnp:artist`, `upnp:album`, `upnp:originalTrackNumber`, `res` = `http://<localIP>:22345/media/music/<hex(path)>`; album `<container>` with `childCount`, `upnp:albumArtURI` = `http://<localIP>:22345/media/cover/<hex>` (outline:182-214, inferred).
  - Full rebuild `rescanUPnPDB` (DELETE then re-INSERT of all root/genre/album/artist/folder/track rows), `lastUpdate` stored in `upnpserver` (outline:937-988, inferred). Counts via `statisicsUPnPDB` (outline:994-1002).
- PROTOCOL:
  - SSDP: group `239.255.255.250:1900`; `CACHE-CONTROL: max-age = <responseExpire>`; `LOCATION: http://<ip>:<upnpPort>/upnp/DeviceDescription.xml`; `SERVER: <OS>/<rel> UPnP/1.0 DLNADOC/1.50 WiiMHome/<ver>`; `NT`, `NTS`, `USN` (`uuid:<pcUUID>` or `uuid:<pcUUID>::<nt>`), `BOOTID.UPNP.ORG`, `CONFIGID.UPNP.ORG: 1` (LPQTSSDPServer.py:122-153, observed).
  - HTTP: port 22346 (LPUtility.py:107, observed). Paths from the device XML (WH\data\LPUPnPServer.xml:24-33, observed): `/upnp/DeviceDescription.xml`, `/upnp/images/ico.png`, `/upnp/contentdirectory/scpd.xml`, `/upnp/contentdirectory/control.xml`, `/upnp/contentdirectory/event.xml`.
  - Device: `deviceType urn:schemas-upnp-org:device:MediaServer:1`, manufacturer Linkplay Technology Inc., `DLNA DMS-1.50` (LPUPnPServer.xml:8-17, observed).
  - Service: `urn:schemas-upnp-org:service:ContentDirectory:1`; actions Browse, Search, GetSortCapabilities, GetSearchCapabilities (LPContentDirectory.xml:8-132, observed).
- EVIDENCE:
  - observed (LPQTSSDPServer.py:15-16, 52, 74-91, 102-153, 186-188, 196-225).
  - observed (LPUPnPHttpServer.py:18, 29-41, 160 `contentdirectory = ContentDirectory()`).
  - observed (WH\data\LPUPnPServer.xml:1-37; WH\data\LPContentDirectory.xml).
  - inferred (names/strings only): control_xml, Browse, Search, DIDL body.
- UNKNOWNS:
  - `event.xml` (eventSubURL) has no handler in the .py or outline names; subscriptions likely 404 (not confirmed).
  - `responseExpire` default decompiles as `(900,)` (LPQTSSDPServer.py:167). If that is the literal default, `time.sleep(self.responseExpire + 600)` (:202) raises TypeError. Check LPQTSSDPServer.dis.txt.
  - `validInterfaces` sets `retInterfaces = None` then calls `.append` (:25, :36); as decompiled, the first qualifying interface raises. Verify in dis.
  - `control_xml`, `dealWithBrowse`, `dealWithSearch`, `generateBodyXML` bodies are cut at LPUPnPHttpServer.py:88-109; only outline strings were used.

**FEATURE: Media HTTP server (`/media/music`, `/media/cover`)**
- ENTRY: cherrypy route `/media/...` on port 22345 (LPHttpServerManager, see the UPnP block).
- MODULES: LPClientFramework.LPMediaHttpServer (DEC\LPClientFramework\LPMediaHttpServer.py), LPUtility, mediafile, cherrypy, hashlib.
- DATA: reads music files; writes cover cache `cacheDir\cover\<md5>` (LPUtility.py:269; LPMediaHttpServer.dis.txt:601-616).
- PROTOCOL:
  - Ports: media 22345, UPnP 22346, OAuth 22347 (LPUtility.py:106-108, observed). Each cherrypy server binds `0.0.0.0`; on port conflict, port += randint(1, 20) and the bound port is stored back in LPUtility (LPHttpServerManager.dis.txt:139-190, observed).
  - Routes: `GET /media/music/<hex>`, `GET /media/cover/<hex>`, `GET /media/` (index text) (LPMediaHttpServer.py:24-45, observed).
  - `<hex>` = UTF-8 bytes of the absolute path, hex-encoded; decoded with `bytes.fromhex(...).decode('utf-8')`, else 404 "Invalid encode" (LPMediaHttpServer.dis.txt:132; outline:28-29, inferred).
  - Errors: 404 "File empty", "Music dir not found", "File not exists", "Invalid file type" (outline:30-33, inferred).
- MECHANISM:
  - music: decode path; access check `_isAccessibleMusicFilePath` → `LPUtility.isAccessibleLocalMusicFilePath` (LPMediaHttpServer.py:12-21, observed); that rule is "under a tracked My Music dir, or present in the beets index" (LPUtility.outline:356-359, inferred). Checks extension against `musicFileType`.
  - Range: parses `Range` header `bytes=<start>-…`, opens file `rb`, seeks, returns 206 with `Content-Range: bytes <start>-<end>/<size>` when a range is given; always `Content-Type: audio/mpeg`, `Accept-Ranges: bytes`, `Content-Length` from `getsize` (LPMediaHttpServer.dis.txt:267-439, observed for the strings and branches).
  - cover: `md5(path.encode('utf-8')).hexdigest()` → `cacheDir\cover\<digest>`; if absent, `MediaFile(path).art` is written with `'wb'`; if no art, 404 "No cover support"; response `Content-Type: image/png` (LPMediaHttpServer.dis.txt:601-748, observed).
  - No transcoding: no `ffmpeg` or `transcod` string in the outline tree (grep), so files are streamed as stored.
- EVIDENCE: observed (LPMediaHttpServer.py:12-45; dis 132, 267-439, 601-748; LPHttpServerManager.dis.txt:139-290); inferred (outline strings for error messages and access rule).
- UNKNOWNS: exact `Range` end-byte computation past dis line 439 not read. The `hashlib` file name is the digest only, no extension.

**FEATURE: Local track hand-off to the speaker (queue and play)**
- ENTRY: `LPMyMusicViewController.makePlayList(treeItem, selectedItem)` (dis LPMyMusicViewController.dis.txt:2967-3050); queue ops in `LPQueueManager` (DEC\LPClientFramework\LPQueueManager.py); recently playback in `LPPCRemoteLocalStreamService.playRecently` (DEC\LPClientFramework\LPStreamServiceDir\LPPCRemoteLocalStreamService.py:65-103).
- MODULES: HOME.LPMyMusicViewController, LPClientFramework.LPPlayList.LPLocalMusicPlayList, LPClientFramework.LPQueueManager, LPClientFramework.LPDevice, LPClientFramework.UPnPTool, LPClientFramework.LPUtility.
- DATA: none persisted beyond the DB (recently).
- PROTOCOL:
  - Speaker control base is `http://<speaker>:59152/upnp/control/<svc>` with `PlayQueue1` (`urn:schemas-wiimu-com:service:PlayQueue:1`), `rendercontrol1` (`RenderingControl:1`), `rendertransport1` (`AVTransport:1`) (LPDevice.outline.txt:547, 568, 572, inferred from strings).
  - SOAP envelope and `SOAPACTION: "<serviceStr>#<method>"` (UPnPTool.py:10-22, observed). Actions: `CreateQueue` with `QueueContext`, `AppendTracksInQueueEx` with `Direction` and `StartIndex`, `BrowseQueue` with `QueueName=CurrentQueue`, `PlayQueueWithIndex` (LPQueueManager.py:102-173, observed; LPDevice.outline.txt:512-606, inferred).
  - Track URL: `http://<fetchLocalIP()>:22345/media/music/<hex(utf-8 path)>` (dis 3017-3025, observed); cover `…/media/cover/<hex>` (dis 3027-3035, observed).
  - Queue XML: `<PlayList><ListName/><ListInfo>SourceName=UPnPServer/LocalMusic…<Tracks><TrackN><URL>…<Source>…<Id>…<Metadata>` with DIDL-Lite (escaped) in `<Metadata>` (LPLocalMusicPlayList.py:55-91, observed). Source value from `LPPlayListSource.LocalMusic` (:111, observed).
- MECHANISM:
  1. `makePlayList` builds items from the tree: path → hex URL, trackName, trackId (index), artist, album, duration (dis 2967-3050, observed).
  2. `generateXML` builds the queue XML (LPLocalMusicPlayList.py:55-91, observed).
  3. Not playing a special source: `CreateQueue(QueueContext=xml)`; otherwise `AppendTracksInQueueEx` with `Direction=1`, `StartIndex=<last+1>` (LPQueueManager.py:115-173, observed).
  4. Play: `device.fastPlay(playList, cb)` for recently (LPPCRemoteLocalStreamService.py:102, observed); queue play index via `PlayQueueWithIndex` (inferred).
  5. The speaker then fetches `http://<PC>:22345/media/music/<hex>` (inferred from the URL shape; the speaker-side fetch is not in the code).
- EVIDENCE: as tagged above.
- UNKNOWNS: `fastPlay` body and device-side handling of `Source=LocalMusic` not traced. `generateXML` in LPPlayList.py:105-118 is the base version used by queue ops (not read in full).

**FEATURE: Home Share (browse LAN UPnP media servers)**
- ENTRY: sidebar entry id `homeshare` (DEC\HOME\SideBar\LPSideBarBrowseViewController.py:34-35, 80-81, observed) → `LPHomeShareViewController` (DEC\HOME\HomeShare\LPHomeShareViewController.py:75).
- MODULES: LPClientFramework.LPDeviceDiscoverManager, LPMediaServer, LPDeviceFileCache, LPUPnPServerPlayList, LPUPnPObserverManager, HOME.HomeShare.LPPagedTreeModel, zeroconf.
- DATA: device cache `mediaServerCacheV2.json`-style file (see Caches).
- PROTOCOL:
  - SSDP M-SEARCH to `239.255.255.250:1900` with `ST: urn:schemas-upnp-org:service:ContentDirectory:1` and `ST: urn:schemas-upnp-org:device:MediaServer:1`, `MX: 3`, `USER-AGENT: mac/1.0 UPnP/1.1 upnpx/1.0` (outline:145-150, inferred; MCAST_IP/PORT observed at LPDeviceDiscoverManager.py:25-26).
  - Parses `LOCATION`, `ST`, `NT`, `NTS`, `USN` from replies and NOTIFYs; accepts `ssdp:alive` (outline:127-143, inferred).
  - mDNS: `ServiceBrowser` for `_linkplay._tcp.local.` (outline:105, inferred).
  - Then `LPMediaServer(ip, port, descURL)` fetches the description, finds the ContentDirectory `controlURL` and runs Browse/Search via SOAP (LPMediaServer outline:183-212, 256-…, inferred).
- MECHANISM:
  1. Discovery threads (SearchThread, DealWithResponseThread, DealWithNotifyThread, CheckThread) (outline:94-113, inferred).
  2. Server only accepted when it is on the active physical LAN gateway (`isIPInGateway`) (outline:157-171, inferred).
  3. `mediaServerCome` creates `LPMediaServer` (LPDeviceDiscoverManager.py:240, observed) and caches it with `CacheType.MediaServer` (LPDeviceDiscoverManager.py:253, observed).
  4. The UI: `mediaServerAddMethod` appends a root node per server to the tree model; `mediaServerRmvMethod` removes by IP (LPHomeShareViewController.py:25-48, observed).
  5. Playback uses `LPUPnPServerPlayList` (header `mediaSource = UPnPServer`) (LPHomeShareViewController.py:17; LPUPnPServerPlayList.py:13-18, observed).
- EVIDENCE: observed (listed); inferred (discovery strings).
- UNKNOWNS: the item URL handed to the speaker for remote servers and the `LPHomeShareViewController` play path (line 250-257) not traced. `LPPagedTreeModel` paging not traced.

**FEATURE: SMB artwork read (client only)**
- ENTRY: callers `LPUtility`, `LPMediaInfo` (DEC\LPClientFramework\LPMediaInfo.py:68-75, observed: `uri.startswith('smb://')`), `LPGlobalQmlImageService` (DEC\LPClientFramework\LPImageService\LPGlobalQmlImageService.py:478, observed).
- MODULES: LPClientFramework.LPSMBService (DEC\LPClientFramework\LPSMBService.py is an empty file; outline only at OUT\LPClientFramework\LPSMBService.outline.txt).
- DATA: none written.
- PROTOCOL: `smb://[user:pass@]host[:port]/share/path`; reads one file via `smbclient` `register_session` and `open_file(..., mode='rb', share_access='rwd')`, with connection timeout and exponential retry; in-memory byte cache with limit (outline:101-151, inferred). Dependency pins named in a log string: `smbprotocol==1.16.1 cryptography pyspnego` (outline:127, inferred).
- MECHANISM: parse URL → build UNC `\\host\share\path` → read bytes → cache. Never reads sibling files (docstring, outline:4, inferred).
- EVIDENCE: observed (LPMediaInfo.py:68-75; LPGlobalQmlImageService.py:478); inferred (LPSMBService strings).
- UNKNOWNS: no SMB server code exists in WiiMHome; the module is client-only (docstring, inferred). Where `smb://` artwork URLs originate was not traced.

**FEATURE: File caches**
- ENTRY: n/a.
- MODULES: LPClientFramework.LPUtility (paths), LPCache.LPFileCache, LPCache.LPDeviceFileCache, LPCache.LPPickleCache (DEC\LPClientFramework\LPCache\).
- DATA:
  - `cacheDir` = `QStandardPaths.CacheLocation\com.linkplay.wiimhome` (LPUtility.py:112, observed).
  - `cacheCoverDir` = `cacheDir\cover` (LPUtility.py:269, observed); album art cache by md5 of path.
  - `SSCacheDir` = `cacheDir\SS` (LPUtility.py:113, observed); `logDir` = `cacheDir\log` (:114, observed).
  - `cacheDir\beets-stage\task-<id>\` (outline:1013-1017, inferred).
  - `cacheDir\watchdog-<name>.pickle` (outline:325-353, inferred).
  - `cacheDir\linkplay_requests.sql` (Wikipedia HTTP cache) (LPBeetsWrapper.dis.txt:18529, observed).
  - Device caches: `LPDeviceFileCache._getFilePath` → `<type.value>CacheV2.<fileType>` with `type` in {`device`, `mediaServer`} (LPDeviceFileCache.py:18-19, observed; CacheType at outline:24-28, inferred). Directory is `FileCache.cacheDir` (not traced).
  - `userDataDir` = `AppConfigLocation\com.linkplay.wiimhome` (LPUtility.py:270, observed): `beets\musiclibrary.db`, `wiimhome-userconfig.json` (:278), `beets\config.yaml` (inferred).
- PROTOCOL: none.
- EVIDENCE: as tagged.
- UNKNOWNS: `FileCache` base directory, `LPPickleCache` and `LPFileCache` bodies not read. Cache eviction policy not traced.

---

**Not traced (UI-named features in scope):**
- Sidebar entry that opens My Music (only imports in WiiMHome.py:23-43 seen).
- Recently (local playback restore): uses the same DB; LPRecentlyManager not read.
- Rescan UPnP DB button path (LPMyMusicSettingViewController outline:169 names only).
- Full queue-play path `fastPlay` / `PlayQueueWithIndex` body (LPDevice).
- Home Share play path for remote items (LPHomeShareViewController.py:240-260).
- Last.fm genre fetch: no code in WiiMHome; the beets plugin source is absent from the bundle.

**Obstacles Encountered:**
- Decompiled .py files are truncated: LPBeetsWrapper.py (stops ~line 129, .err "Unexpected end of stream"), LPUtility.py (stops ~line 399), LPUPnPHttpServer.py (bodies at 88-109), LPMediaServer.py, LPSMBService.py (empty). Those claims come from the .dis.txt or outline names and strings, tagged `inferred` where only names/strings support them.
- LPCache classes (LPFileCache, LPPickleCache) were not read.
- Side effects: none. No writes, no git operations, no network, no app launched, no DB opened.