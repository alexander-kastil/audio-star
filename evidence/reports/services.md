## Task
Reverse-engineering read of WiiM Home's non-TIDAL music services (framework, Qobuz, WiiM Radio, Radio Paradise 2, the sidebar list, favorites, images), per the report contract. Read-only; no files written, nothing launched or fetched.

## Questions
1. Which services the app offers and how that list is decided.
2. The stream-service manager abstraction.
3. Qobuz login, token handling, browse/discover/library/search/favorites/playlists, request signing.
4. WiiM Radio home, categories, stations, favorites, backend.
5. Radio Paradise 2 channel list, account and playback.
6. How each service's item plays on the speaker.
7. Favorites cache and sync.
8. The shared image service.
9. The sidebar music-service list.

## Conventions
- Paths: `.py` = `D:\git-projects\audio-star\evidence\decompiled\<pkg>.py`; `outline` = `D:\git-projects\audio-star\evidence\outline\<pkg>.outline.txt` (its `def ... line N` is the source line). `dis` = the matching `.dis.txt`, authoritative where the `.py` is incomplete.
- Secrets are not printed. Constants are named by module and line only.

## Facts

**FEATURE: Music Services sidebar list and which services are offered**
- ENTRY: `HOME\SideBar\LPSideBarMusicServiceViewController` `setupTable` (outline `def` line 392).
- MODULES: `HOME.SideBar.LPSideBarMusicServiceViewController`, `LPClientFramework.LPDeviceStreamServiceManager`, `LPClientFramework.LPConfig.LPAppFeatureConfig`, `LPClientFramework.LPStreamServiceManager`.
- DATA: `data\LPSupportedStreamServiceConfig.json` (loaded from `LPUtility.appLocalDataPath()`, observed `LPDeviceStreamServiceManager.dis.txt:988-1000`). Feature flag `WIIM_RADIO_ENABLED = True` (observed `LPAppFeatureConfig.py:7`).
- MECHANISM:
  - `setupTable` lists `LPDeviceStreamServiceManager.pcServiceCapability()`, which is `supportContents()`. Its docstring comment (`outline` line 152) says PC-supported services are shown regardless of device.
  - `supportContents()` iterates the JSON's keys only. The result is `{source: {**builtin.get(source, {}), **jsonConfig}}`, so the built-in table fills missing fields (observed `LPDeviceStreamServiceManager.dis.txt:1018-1071`).
  - If `isWiiMRadioEnabled()` is false, `WiiMRadio` is popped (observed `dis.txt:1036-1046`).
  - The JSON has four keys: `RadioParadise2`, `Qobuz`, `Tidal`, `WiiMRadio` (observed `LPSupportedStreamServiceConfig.json:2-47`). Each has `title`, `authType`, `module` and `class`. Qobuz is `OAuth`; WiiM Radio and Radio Paradise 2 are `none`.
  - The built-in table `LPStreamServiceManager.supportContents` (`LPStreamServiceManager.outline` lines 71-310) holds about 50 services, including Alexa, Amazon, TuneIn, Deezer, Spotify and others. Only the four JSON keys are returned.
  - Rows are rendered from `title`, `browse_icon` and `content`. The account name comes from `deviceStreamServiceManager.accountForSource` via `_accountDisplayName` (`outline` lines 141-148). Selecting a row calls `serviceSelectMethod` (`outline` line 164).
- PROTOCOL: none (local).
- EVIDENCE: as tagged above; `LPSideBarMusicServiceViewController.outline.txt` lines 150-170.
- UNKNOWNS: where `streamServiceCapability` is populated. `updateAppStreamServiceCapability` pops keys from `supportContents()` (`outline` names list), so the link to device capability is inferred, not confirmed.

**FEATURE: Stream-service manager (framework)**
- MODULES: `LPClientFramework.LPStreamServiceManager`, `LPClientFramework.LPDeviceStreamServiceManager`, `LPClientFramework.LPStreamServiceDir.*`.
- MECHANISM:
  - Module-level registry `streamServiceDict`. `registerStreamService(source, service)` and `streamServiceForSource(source)` (`LPStreamServiceManager.outline` lines 626-630).
  - `LPStreamService` is the base class. Overridable hooks include `canFavorite`, `favoriteState`, `setFavorite`, `recentlyDidSelect`, `playRecently`, `updateMediaInfoWithItem`, `registerAccount`, `loginAccount` and `logoutAccount` (`LPStreamServiceManager.outline` lines 315-390).
  - Per-device `LPDeviceStreamServiceManager`: `registerDeviceStreamService` imports `module`/`class` with `import_module` and registers them (`LPDeviceStreamServiceManager.outline` line 90). Account state is kept per source; `DEVICE_ACCOUNT_UNKNOWN` is a sentinel for "device has not reported". Device `accountChange` and `logout` notifications update it (outline lines 150-190).
  - Media-info updates run on one worker thread with a queue of depth at most 1 (`LPDeviceStreamServiceManager.py:43-70`, observed).
  - `LPStreamServiceManager.py` and `LPStreamServiceDir.py` decompile to headers only. The outlines are used instead.
- EVIDENCE: `LPDeviceStreamServiceManager.outline.txt`, `LPStreamServiceManager.outline.txt`.

**FEATURE: Qobuz login (browser OAuth through the speaker)**
- ENTRY: `LPQobuzLoginManager.showLoginPage` and `beginBrowserLogin` (`LPMSManager\Qobuz\LPQobuzLoginManager.outline.txt` lines 94-107). Login page `HOME\StreamService\Qobuz\Login\LPQobuzLoginViewController`.
- MECHANISM:
  - `beginBrowserLogin` calls `webbrowser.open` on the OAuth URL: `https://www.qobuz.com/signin/oauth2?client_id=<redacted>&redirect_uri=https://auth.wiimhome.com/qobuz/wiimhome&response_type=code&state=pc` (observed `LPQobuzLoginManager.outline.txt:43`; client_id constant not printed).
  - The redirect carries an `exchange_code`. An `OAuthCodeChanged` notification triggers `onOAuthExCodeReceived`, which calls `userLoginByCode` on the device's upnp model (`outline` lines 103-118).
  - `getUserInfo` asks the device for account info through an upnp action named `GetUserInfo`. A `Result` JSON with `userId` means logged in; otherwise the login page is shown (`outline` lines 76-101).
  - `logout` calls `logoutAccountForSource` and clears the favorite cache (`outline` lines 278-292).
- PROTOCOL:
  - Device-side upnp actions (names as in code; exact XML not traced): `GetUserInfo`, `UserLogin`-by-code, `UserLogout`, and `AccountSource` with value `Qobuz` (observed `LPQobuzStreamService.outline.txt` lines 213-215).
  - Device notifications: `eventType` `accountChange` or `logout`, with `payload` and `source` (`LPQobuzStreamService.outline.txt` 229-243).
- EVIDENCE: `LPQobuzLoginManager.outline.txt`, `LPQobuzStreamService.outline.txt`.
- UNKNOWNS: the exact upnp service and action strings in `LPUpnpAsyncDataModel` (not read).

**FEATURE: Qobuz token handling and request path**
- MODULES: `LPNetworkClient.LPNetworkClient`, `LPNetworkClient.LPQobuz.LPQobuzNetworkClient`, `LPNetworkClient.LPQobuz.LPQobuzTokenProvider`, `LPMSManager.Qobuz.LPQobuzManager`, `LPStreamServiceDir.LPQobuzStreamService`.
- MECHANISM:
  - `LPQobuzStreamService.registerAccount` takes `accessToken` from the device's `GetUserInfo` result and decrypts it with `AESCipher.decrypt2`. Fields: `userId`, `userName`, `expressIn`, `showName`, `email`, `subscription`, `maxStreaming`, `credential.parameters.hires_purchases_streaming` (`LPQobuzStreamService.outline.txt` lines 193-208). The AES key source is not traced.
  - The token is held in memory by `LPQobuzTokenProvider` (`LPNetworkClient\LPQobuz\LPQobuzTokenProvider.outline.txt`). It is refreshed by `_refresh_token`, which calls upnp `GetUserInfo` and then `replaceToken` (`LPQobuzNetworkClient.outline.txt` lines 37-45).
  - Each request sets `Authorization: Bearer <token>` (`LPQobuzNetworkClient.outline.txt` lines 20-21). On HTTP 401 it refreshes the token and retries once (`LPNetworkClient.outline.txt` line 90; `LPQobuzNetworkClient` "retry" strings).
  - When `useCache` is set, requests go through `requests_cache` `CachedSession` with memory backend and `expire_after` (`LPQobuzNetworkClient.outline.txt` lines 26-28).
- Request signing: none found. Grep for `request_sig`, `app_id`, `app_secret`, `secret`, `sign` over all Qobuz modules returned no hits. The only hashing in the Qobuz path is `hashlib.md5` for image-cache file names in `HOME\StreamService\Qobuz\Util\LPQobuzUtil.outline.txt` line 203 (`checkCachedBlurredPixmapWithUrl`).
- EVIDENCE: as tagged.

**FEATURE: Qobuz browse, discover, library, search, favorites, playlists**
- ENTRY: `HOME\StreamService\Qobuz\Browse\LPQobuzViewController` (also Discover and Library controllers), `Search\LPQobuzSearchViewController`, `Detail\*`, `SeeAll\*`, `Component\Playlist\LPQobuzAddToPlaylistDialog`.
- MODULES: `LPNetworkClient.LPQobuz.LPQobuzRequester`, `LPMSManager.Qobuz.LPQobuzRequestManager` (ThreadPoolExecutor, `fetch` wraps errors), `LPMSManager.Qobuz.LPQobuzLibraryCacheManager`, `LPMSManager.Qobuz.LPQobuzFavoriteManager`.
- PROTOCOL: base `https://www.qobuz.com/api.json/0.2/` (`LPQobuzRequester.outline.txt` line 50). Paths below are as listed in the requester constants and methods (`outline` lines 51-84 and the method strings):
  - Discover: `album/getFeatured?type=new-releases`, `dynamic-tracks/get?type=weekly` (Weekly Q), `playlist/getFeatured?&type=last-created`, `album/getFeatured?type=ideal-discography`, `album/getFeatured?type=most-streamed`, `album/getFeatured?type=qobuzissims`, `album/getFeatured?type=press-awards`, `album/getFeatured?&type=best-sellers`, `playlist/getTags`, `genre/list`.
  - Library: `playlist/getUserPlaylists?offset=&limit=`, `favorite/getUserFavorites?type=<t>&offset=&limit=&genre_ids=`, `purchase/getUserPurchases?type=<t>&offset=&limit=`.
  - Detail: `album/get?album_id=`, `playlist/get?extra=tracks,subscribers&playlist_id=&offset=&limit=`, `artist/page?artist_id=`, `artist/getReleasesGrid?artist_id=&release_type=&sort=&offset=&limit=`, `artist/getSimilarArtists?artist_id=`.
  - Search: `catalog/search?query=`, and typed `artist/search`, `album/search`, `track/search`, `playlist/search` with `?query=`.
  - Favorites: `favorite/getUserFavoriteIds` (POST), `user/lastUpdate` (POST), `favorite/status?type={}&item_id={}`, `favorite/create` and `favorite/delete` (POST, bodies `album_ids`, `track_ids` or `artist_ids`), `playlist/subscribe` and `playlist/unsubscribe` (POST, `playlist_id`).
  - Playlists: `playlist/create` (POST: `name`, `description`, `is_collaborative`, `is_public`, `track_ids` or `album_id`), `playlist/delete` (POST `playlist_id`), `playlist/addTracks?playlist_id=&track_ids=` (POST), `playlist/deleteTracks` (POST `playlist_id`, `playlist_track_ids`).
  - Images: `https://static.qobuz.com/images/artists/covers/large/` (`LPQobuzNetworkDataParser.outline.txt` line 271).
- MECHANISM: `LPQobuzLibraryCacheManager` sections are My Playlists, Favorite Albums, Favorite Artists, Favorite Tracks, Purchased Albums and Purchased Tracks. Each is paged and cached as a pickle: `favAlbumCache.pkl`, `myPlaylistCache.pkl`, `favTrackCache.pkl`, `favArtistCache.pkl`, `purAlbumCache.pkl`, `purTrackCache.pkl` (`LPQobuzLibraryCacheManager.outline.txt` lines 18-24). Staleness uses `fetchLastUpdate` (`user/lastUpdate`) per section.
- EVIDENCE: `LPQobuzRequester.outline.txt`, `LPQobuzRequestManager.outline.txt`, `LPQobuzLibraryCacheManager.outline.txt`.
- UNKNOWNS: the Qobuz artist biography dialog's data source (`LPQobuzArtistBiographyDialog`); `LPQobuzStreamService` imports BeautifulSoup (used for queue XML parsing, not for the web).

**FEATURE: Playing a Qobuz item on the speaker**
- MECHANISM: the PC builds DIDL-Lite XML (`LPQobuzPlayList` `generateXML`, `outline` line 109). `playRecently` sends it with `palyWithSearchUrl`, using `playOrigin` `search_track` for search single tracks and `searchUrl` (`LPQobuzStreamService.outline.txt` lines 380-392). `playRecently` requires `streamable` on the track. `backupXml` and `replaceItemXml` use `generateBackupQueueXML` and `generateSetKeyMappingXML`.
- PROTOCOL: the device endpoints are `http://<device>:59152/upnp/control/PlayQueue1` (also `rendercontrol1` and `rendertransport1`) and `https://<device>/httpapi.asp` (`LPDevice.outline.txt` lines 547-664). Which one `palyWithSearchUrl` hits is not traced.
- UNKNOWNS: the Qobuz track stream URL is resolved on the speaker; the PC side only sends the XML.

**FEATURE: WiiM Radio home, categories, stations and search**
- ENTRY: `HOME\StreamService\WiiMRadio\LPWiiMRadioHomeViewController` with `Qml\WiiMRadio\WiiMRadioHome.qml`. Other QML: `WiiMRadioSeeAll.qml`, `WiiMRadioCategoryDetail.qml`, `WiiMRadioCard.qml`, `WiiMRadioSection.qml`.
- MODULES: `HOME.StreamService.WiiMRadio.utils.LPWiiMRadioStore`, `...utils.LPWiiMRadioDataProvider`, `...utils.LPWiiMRadioRequestScheduler`, `...utils.LPWiiMRadioStationListModel`, `...utils.LPWiiMRadioThumbnailService`, `...utils.__init__` (category definitions), `...WiiMRadio.LPWiiMRadioPlayController`.
- Home sections (observed `LPWiiMRadioStore.dis.txt` lines 8383-8500, six sections returned in this order):
  - `popular`: title "Popular in Your Area", `baseQuery` with `countryCode` and `subcountryCode`.
  - "Top Music" (`categories` Music), "Top News" (News), "Top Talk" (Talk), "Top Sports" (Sports).
  - `sleepRadio`: "Relax & Unwind Stations", `tags` "Relaxation Music".
  - Local `favorites` section (`LPWiiMRadioHomeState.FAVORITES_SECTION_KEY`, `LPWiiMRadioStore.py:1749`). Search section key `homeSearch` (`LPWiiMRadioStore.py:1751`).
- Category cards: `WIIM_RADIO_CATEGORY_DEFINITIONS` (`HOME\StreamService\WiiMRadio\utils\__init__.py:5-33`): categoryKey and queryCategories `music`/`Music`, `news`/`News`, `talk`/`Talk`, `sports`/`Sports`, all with `useCountryCode: False`.
- MECHANISM: `LPWiiMRadioHomeState` uses `_build_remote_section_specs` (`dis` line 6235) to build the section specs. Each section is loaded through `LPWiiMRadioDataProvider.fetchStations`, which submits to the scheduler at PRIORITY_BACKGROUND or PRIORITY_VISIBLE. Results come back through `_dispatch_response` on the main thread. Pages are 10 remote, with `pageNo` and `hasMore` (`LPWiiMRadioStore.py:1101-1129`, observed). A popular request with `subcountryCode` that returns empty is retried once without it (`_should_retry_popular_without_subcountry`, `LPWiiMRadioStore.py:72-90`).
- The scheduler has three named pools: `api`, `image_download`, `image_decode` (`LPWiiMRadioRequestScheduler.outline.txt` lines 120-125). Jobs are deduped by `jobKey`, and priorities are visible, preload and background.
- PROTOCOL:
  - `POST https://cloud-api.linkplay.com/prod/radio/station/list` (`LPWiiMRadioDataProvider.py:20` host constant, `:25` endpoint constant, `_request_station_list` via `_client.post`). Request keys: `isDistinct`, `stationId`, `name`, `customName`, `language`, `languageCodes`, `country`, `countryCode`, `subcountry`, `subcountryCode`, `city`, `radioId`, `categories`, `customTags`, `tags`, `pageNo`, `pageSize`, `orderByStr`, `sortStr` (`dis` lines 8572 and `LPWiiMRadioDataProvider.py:495-510`). Sort values: `name_asc` maps to `ASC`, `name_desc` to `DESC`.
  - Response keys: `code` (non-zero is a business error), `message`, `requestId`, `resultList`, `pageNo`, `pageSize`, `totalPages`, `totalRows`. Item keys read as `StationID`/`stationId`, `Name`/`name`, `Favicon`/`favicon`, `StreamUrl`/`Url`/`URL`/`streamUrl`, `City`, `Subcountry`, `Region`, `Country`, `CountryCode`, `Genres` (`LPWiiMRadioDataProvider.py:846-891`).
  - `GET https://api.linkplay.com/apiv1/tool/location` (host at `LPWiiMRadioDataProvider.py:18`, endpoint at `:22`). Reads `data.countryCode` and `data.region` (`LPWiiMRadioDataProvider.py:700-719`). Query params are not traced.
  - Auth: `LPAuthenticatedRequestClient` (`LPEventTrack.py`). Headers `accessKey`, `timestamp` (ms), `nonce` (16 chars), `sign`, `appId`. `appId` = SHA-256 hex of accessKey + appId constant. `sign` = SHA-256 hex, uppercase, of `secretKey` + `accessKey=<ak>&appId=<hashed>&nonce=<n>&timestamp=<ts>&secretKey=<sk>` (dis lines 494-506). The decompiled `LPEventTrack.py:154` omits the `accessKey=` literal; the dis is authoritative.
  - Constants: app ID `LPWiiMRadioDataProvider.py:22`, access key `:23` (same value as app ID; not printed), secret `:24`.
- Analytics: events `ss_wiimradio_station_list`, `ss_wiimradio_area_num`, `ss_wiimradio_station_list_time_cost` (batched every 10), `ss_wiimradio_tool_location` (`LPWiiMRadioDataProvider.py:27-30`). They go through `LPGlobalUI` eventTrack, which posts to `https://api.linkplay.com/apiv1/mp/collect` (`LPEventTrack.py:45`).
- EVIDENCE: `LPWiiMRadioDataProvider.py:17-30, 327-575, 846-891`; `LPWiiMRadioStore.dis.txt:8383-8572`; `LPWiiMRadioStreamService.outline.txt`.
- UNKNOWNS: `LPWiiMRadioThumbnailService` not read. Station list decompile is incomplete in `_request_station_list`; the dis was used for URL and keys.

**FEATURE: Playing a WiiM Radio station**
- ENTRY: `LPWiiMRadioPlayController.playStation` (mixin used by the Home, SeeAll and CategoryDetail controllers).
- MECHANISM: build a one-item playlist, `updateMediaInfoForSource(device, 'WiiMRadio', item, header)`, then `palyWithSearchUrl(device, xml, cb)`. On success, `LPRecentlyManager.addRecentlyPlayedWithMusicList` is called with `openMore` true and `canNavigate` false (`LPWiiMRadioPlayController.py:42-79`). Recently replay uses upnp `CreateQueue` with `QueueContext` (`LPWiiMRadioStreamService.outline.txt` lines 65-72).
- PROTOCOL: DIDL-Lite items with `upnp:class` `object.item.audioItem.musicTrack` (`LPWiiMRadioPlayList.outline.txt` line 54). Media type `MEDIATYPE_RADIO`.

**FEATURE: WiiM Radio favorites**
- MECHANISM: `LPWiiMRadioFavoriteStorage` writes into the shared `LPFavoriteCacheManager` as source `WiiMRadio`, user `WIIMRADIO_LOCAL_USER_ID`. A legacy `wiimradio-favorites.json` is migrated once, only when the cache is empty (`LPWiiMRadioFavoriteStorage.outline.txt` lines 3-40, 120). It is local only; the sync coordinator marks it synced (`LPFavoriteSyncCoordinator` `_syncWiiMRadioLocal`).
- Only `station` is favoritable (`canFavorite`, `LPWiiMRadioStreamService.outline.txt` line 86).
- EVIDENCE: `LPWiiMRadioStreamService.outline.txt` lines 83-131.

**FEATURE: Radio Paradise 2**
- ENTRY: `HOME\StreamService\RadioParadise2\LPRadioParadise2ViewController`.
- PROTOCOL:
  - Channel list: `GET https://api.radioparadise.com/api/list_chan?C_user_id={}` (`LPRadioParadise2NetworkDataModel.outline.txt:18`). The `C_user_id` value comes from the account's `cUserId`.
  - Stream URL for a channel: `https://api.radioparadise.com/api/gapless?C_user_id={}&player_id={}&chan={}&bitrate=4` (`LPRadioParadise2ViewController.outline.txt:120`).
  - Playlist XML: `SearchUrl` is the gapless URL; `SourceName` is `RadioParadise2`; `ListName` is e.g. "RP Global Mix" (`LPRadioParadise2PlayList.outline.txt:38, 52`).
- Account: device upnp `UserLogin` with `AccountSource` `RadioParadise2`, `UserName` and `PassWord` (`LPRadioParadise2StreamService.outline.txt` lines 100-108). Logout is `UserLogout` (`:94-98`). Account fields: `anonUserId`, `userId`, `cUserId`, `userName`, `showName`, `expressIn`, `token`.
- Behavior: `LPTrackMoreCanPreset` always returns True (`:181`). Favorites are not overridden, so the base class (no favorites) applies. Playback: `recentlyDidSelect` builds the XML and sends `CreateQueue` (`:260-307`).
- UNKNOWNS: the source of `player_id` (uuid pattern in the example only).

**FEATURE: Favorites cache and sync (Tidal, Qobuz, WiiM Radio)**
- MODULES: `LPFavoriteCacheManager`, `LPFavoriteSyncCoordinator`.
- DATA: `LPFavoriteCacheManager._pathFor` writes one `.json` per `(source, userId)` under `cacheRoot` (`LPFavoriteCacheManager.outline.txt` lines 185-211).
- MECHANISM:
  - `FAVORITE_SOURCES = ('Tidal', 'Qobuz', 'WiiMRadio')`, `SYNC_TTL_SECONDS = 3600`, `PERIODIC_SYNC_INTERVAL_SECONDS = 3600`, `RETRY_DELAYS = (30, 120, 600)` (observed `LPFavoriteSyncCoordinator.py:18-21`).
  - Triggers: `requestSync` (with TTL), a periodic thread, account-changed and device-changed notifications, and `deviceInfoUpdate`.
  - Qobuz: `_fetchQobuzIds` calls `LPQobuzManager.requestMgr.fetchFavoriteIds` (POST `favorite/getUserFavoriteIds`) and then `applyServerSnapshot` (`LPFavoriteSyncCoordinator.outline.txt` lines 275-276).
  - WiiM Radio: `_syncWiiMRadioLocal` calls `ensureLoaded`. No network.
  - Failed syncs retry on `RETRY_DELAYS`.
- Stale snapshots are dropped by `snapshotAt` comparison (`LPFavoriteCacheManager` `applyServerSnapshot`, line 296).

**FEATURE: Shared image service**
- MODULES: `LPClientFramework.LPImageService.LPGlobalQmlImageService`, `...LPGlobalImageScheduler`, `...LPImageProfiles` (not read).
- MECHANISM:
  - `ensureThumbnail(url, profile, priority, ownerKey)` (`LPGlobalQmlImageService.outline.txt`, `def` line 81) returns a local file URL. Remote only for `http://` and `https://` (`_is_remote_url`, `def` line 231).
  - Downloads go through the scheduler's `image_download` pool, decoding through `image_decode`. Results land in `cacheCoverDir` at `_cache_file_path`, with an original copy at `_original_cache_file_path`. Expiry is per profile (`_is_expired`). Failures are remembered and purged when expired. `cancelOwner` cancels jobs by owner.
  - Stats keys: `cacheHit`, `cacheMiss`, `cacheFail` (`def stats` line 173).
- EVIDENCE: `LPGlobalQmlImageService.outline.txt`, `LPGlobalImageScheduler.outline.txt`.

## Not found
- WiiM Radio `/apiv1/tool/location` query parameters: searched the dis for `_location_client.get` call arguments; not settled.
- Upnp service and action strings for `GetUserInfo`, `UserLogin`, `userLoginByCode`, `CreateQueue`, `palyWithSearchUrl`: the names are in `LPUpnpAsyncDataModel` (not read).
- Qobuz `registerAccount` AES key source: `AESCipher.decrypt2` is at `LPClientFramework\util\aes.py`; the caller's key was not traced. The key literals there (`aes.py:83`) are in a test block and not printed.
- Qobuz track stream URL resolution: not on the PC side.
- Whether `streamServiceCapability` comes from device capability or from the JSON: the link is inferred only.
- `LPImageProfiles` contents: not read.
- `LPWiiMRadioThumbnailService`: not read.
- UI-named features in scope not traced to endpoints: Qobuz artist biography dialog, Qobuz genres selector (`LPQobuzGenresSelector`, `LPQobuzGenreManager`), WiiM Radio QML details beyond the file list.

## Side effects
None. No files written, no processes started, no URLs fetched, no git commands run.

## Obstacles Encountered
- `LPStreamServiceManager.py`, `LPStreamServiceDir.py` and `LPDeviceStreamServiceManager.py` decompile to headers or a partial stub. The outlines were used.
- `LPWiiMRadioStore.py` decompile is incomplete (`# WARNING: Decompyle incomplete`). The dis gave the section specs and request keys.
- `LPEventTrack.py` has an incomplete `_logEvent`. The `_getSignKey` decompile differs from the dis (missing `accessKey=` literal); the dis was treated as authoritative.
- Several `.py` have `.err` siblings (`LPQobuzStreamService.py.err`, `LPSideBarMusicServiceViewController.py.err`), so those are incomplete too.
- Secret and identifier constants exist in `LPCloudDeviceState.py:27-29`, `LPEventTrack.py:49-51` and `LPFeedbackConfig.py:10-12`. They were not printed; `LPCloudDeviceState` and `LPFeedbackConfig` are outside this scope.
- Tidal is excluded per scope.