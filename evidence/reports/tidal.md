Task: reverse-engineer the TIDAL integration of WiiM Home (login, pages, search, detail views, favorites, playlists, collection prefs, images, scheduling, diagnostics, event tracking, playback), read-only, with sources.

Questions: the 19 feature blocks below, in the order of the team lead's list. Citation convention: `DP-outline:N` = `evidence/outline/HOME/StreamService/Tidal/data/LPTidalDataProvider.outline.txt` line N; `dis` = the matching `.dis.txt`; the `.py` paths are full paths. The `.py` is authoritative only where it is complete; `LPTidalDataProvider.py` stops at line 216, so its methods come from the outline and dis.

Install paths used: `C:\Users\AlexanderKastil\AppData\Local\WiiMHome\Qml\Tidal\`. Secrets are not printed; the client ID comes from the device at runtime and is never in PC code.

---

**FEATURE: TIDAL login (browser OAuth through the speaker)**
- ENTRY: `controllers/pages/LPTidalLoginViewController.py` `onBrowserLoginClicked` (outline line 89) calls `LPTidalLoginManager.beginBrowserLogin` (`LM` line 196). Route: `LPTidalLoginManager.showLoginPage` (line 586, stacked item `tidal_login`).
- MODULES: `LPClientFramework.LPMSManager.Tidal.LPTidalLoginManager`, `LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel`, `LPClientFramework.LPOAuthHttpServer`, `LPClientFramework.util.LPUriHandler`, `HOME.StreamService.Tidal.services.LPTidalEventTrack`, `LPClientFramework.LPStreamServiceDir.LPTidalStreamService`.
- DATA: no file written by the PC for login. In-memory `LPTidalStore.accountState` only.
- MECHANISM:
  1. `beginBrowserLogin` sends UPnP `GetUserInfo` to the current device with source Tidal (`LPUpnpAsyncDataModel.getUserInfo`, `LM` outline line 200 onward). Version `USER_INFO_VERSION = '2'` (`LM` line 27).
  2. The callback reads `clientId` and `redirectUrl` (or `redirectURI` / `redirect_uri`) from the device answer. `clientId` is decrypted with `_decodeDeviceValue`, which uses the device UUID prefix as key (`LM` outline line 604; key not printed).
  3. `loginUrlFromUserInfo` builds the authorize URL and the browser opens it (`webbrowser.open`, outline line 233).
  4. The browser returns to the PC by one of two paths: (a) `LPOAuthHttpServer.tidal` at `/tidal/wiimhome` (source `LPOAuthHttpServer.py` lines 30–56), which accepts `state` = `login_state` or `pc` and posts `OAuthCodeChanged` with `{exchange_code, source}`; (b) `LPUriHandler.handleOAuthCallback` for scheme `com.linkplay.wiimhome` or `wiim`, netloc `callback`, `category=oauth`, `service`, `code`, `state` (`LPUriHandler.py` lines 61–94).
  5. `onOAuthExCodeReceived` (`LM` line 1139, state check `login_state`/`pc`) sends UPnP `UserLogin` with the AES-encrypted code (`LPUpnpAsyncDataModel.userLoginByCode`, line 46; key from device UUID; the cipher key is not printed).
  6. The device answers asynchronously with an `accountChangedForSource` notify; `onAccountChanged` (`LM` line 1201) then calls `syncAccountFromDevice` and `LPFavoriteSyncCoordinator.requestSync(force)`.
- PROTOCOL:
  - Browser: `GET https://login.tidal.com/authorize?lang=en&response_type=code&redirect_uri=<device redirect>&client_id=<device value>&state=pc&restrictSignup=true` (`LM` outline lines 238–253).
  - Local callback: `http://localhost:22347/tidal/wiimhome` (port `LPUtility.py:108`, `oauthServerPort = 22347`; server `LPHttpServerManager.start`, line 54). Callback page redirects to `wiim://active`.
  - Deep link: `com.linkplay.wiimhome://callback?category=oauth&service=<svc>&code=…&state=…` or `wiim://…` (`LPUriHandler.py:71–81`).
  - UPnP SOAP on the device: `http://<device-ip>:59152/upnp/control/PlayQueue1`, service `urn:schemas-wiimu-com:service:PlayQueue:1`, actions `GetUserInfo` (Result payload), `UserLogin`, `UserLogout` (`LPDevice.dis.txt` lines ~4113–4135 and ~4845–4876).
  - Envelope and SOAPACTION: `UPnPTool` outline lines 18–28.
- EVIDENCE:
  - observed (`LM` lines 27–29, 115–151, 196–231, 262–297, 1139, 1201): login flow and constants.
  - observed (`LPOAuthHttpServer.py` 30–66; `LPUriHandler.py` 61–94; `LPUtility.py:108`).
  - observed (`LPDevice.dis.txt` 4113–4135, 4845–4876): command-to-service mapping.
  - inferred (names/strings only): the `UserLogin` answer is consumed only through the notify, not the reply (`LM` outline line 653 "wait for accountChange notify").
  - The repo doc `QML/Tidal/docs/ui-design.md:787–796` documents the same sequence (`UserLogin(AccountSource=Tidal, Version=2.0)`).
- UNKNOWNS:
  - The `.py` of `LM` line 221 reads `if not client_id or redirect_url`. The dis (`LM.dis.txt` lines 1779–1785) shows `not client_id or not redirect_url`. The `.py` is wrong here; the dis is authoritative.
  - The socket bind host: `LPHttpServerManager.bindServer` sets `0.0.0.0` (`LPHttpServerManager.py:26`), while `start()` names `localhost:22347` (line 54). The actual bind call is cut off in the `.py`; the dis was not read.
  - `_sourceFromOAuthService` mapping (service string to source) is not read.
  - `LPUpnpAsyncDataModel.getUserInfo` and `userLoginByCode` bodies are cut off (`LPUpnpAsyncDataModel.py` lines 36–49).
  - `docs/login-flow.md`, referenced by `ui-design.md:796`, is not in the install.

**FEATURE: TIDAL username and password login (no UI entry)**
- ENTRY: `LPTidalLoginManager.login(username, password)` (`LM` line 115). No caller exists in `evidence/decompiled` (grep for `.login(` finds none outside `LM`).
- PROTOCOL: `POST https://api.tidal.com/v1/login/username` via `LPTidalDataProvider.loginByUsername` (`DP-outline:1767–1777`, `postJson`).
- EVIDENCE: observed (`DP-outline:1773`); observed no caller (grep).
- UNKNOWNS: the `.py` condition at `LM` line 129 (`if not normalized_username or normalized_password`) looks inverted (the `not` on the password is missing). The dis for `login` (`LM.dis.txt` line 964) was not read to confirm. The code is dormant in this build.

**FEATURE: Token storage and refresh**
- MODULES: `LPTidalLoginManager`, `LPTidalDataProvider`, `LPTidalStore`, `LPTidalStreamService`.
- DATA: the token lives in three places: (1) the device (its own account registry via `registerAccountForSource`, `LM` line 348); (2) PC memory, `LPTidalStore.accountState` (keys: `isLoggedIn, userId, userName, email, token, sessionId, countryCode, expiresIn, tokenUpdatedAt, tokenExpiresAt, subscription, subscriptionTitle, supportReplayGain, showAutoplay, _rawAccount`, `LM` outline lines 461–531); (3) `LPTidalAccount.credential` and `.rawUserInfo` (`LPTidalPlayList.outline.txt:227`).
- MECHANISM:
  1. The PC does not persist a refresh token and does not call a TIDAL token endpoint. It asks the device for a fresh user info (`GetUserInfo`).
  2. `_shouldRefreshToken` is true when `tokenExpiresAt` is within `TOKEN_REFRESH_LEEWAY_SECONDS = 300` (`LM.py:28`).
  3. `ensureFreshToken` runs `_fetchAccountFromDeviceBlocking(device, 'scheduled')` with an 8-second wait (`TOKEN_REFRESH_TIMEOUT_SECONDS = 8`, `LM.py:29`), reusing a concurrent refresh via a Condition (`LM` outline lines 331–352).
  4. On HTTP 401 the provider runs `_retryAfterForcedTokenRefresh` once: `ensureFreshToken(force=True)` then retry (`DP-outline:766–783`).
  5. Headers: `Authorization: Bearer <token>` (`DP-outline:1941–1944`); session mode adds `X-Tidal-SessionId` (`DP-outline:1945–1946`).
  6. `_headersFromCurrentAccount` rebuilds headers from Store (`DP-outline:1955–1963`).
- EVIDENCE: observed (`LM.py:27–29`, `DP-outline:766–783, 1938–1963`); inferred (the 300 s and 8 s use is from names).
- UNKNOWNS: whether `LPTidalAccount.credential` or `rawUserInfo` is serialized into the Recently Played store. `LPTidalController._buildRecentlyPlayList` names `rawUserInfo` and `credential` (`PC-outline:599–604`), but the Recently writer (`LPRecentlyManager`) was not read.

**FEATURE: Logout**
- ENTRY: `LPTidalShellViewController.py:498` calls `LPTidalLoginManager.logout()`.
- MECHANISM: `logout` (`LM` line 156) calls the device's `logoutAccountForSource`. The docstring says the PC makes no direct TIDAL HTTP call (`LM.py:159`). `LPTidalStreamService.logoutAccount` sends UPnP `UserLogout` (`LPTidalStreamService.outline` line 600–606). Then `_performLogoutCleanup` clears the Store, `clearCaches()` on the provider (requests_cache and ETag memory), `LPTidalImageService.cancelPendingAndClear`, and `LPFavoriteSyncCoordinator` cache clear (`LM` line 172).
- EVIDENCE: observed (`LM.py:156–159, 171–183`; `LPTidalStreamService.outline:600–606`).
- UNKNOWNS: `clearCaches` body is cut off (`DP.py` line 145).

**FEATURE: Home page**
- ENTRY: `controllers/pages/LPTidalHomeViewController.py` (`loadHomeData` scheduled with `LPTidalRequest` tags, `HomeVC-outline:629`); QML `pages/TidalHome.qml`.
- MODULES: `LPTidalDataProvider.loadHomeData` (`DP-outline:824`), `_buildFeaturedResourceSections`, `_probeFeaturedCategoryPaths`, `LPTidalCollectionSortPreference`.
- PROTOCOL (all `GET https://api.tidal.com…`, Bearer token, parallel via `_executeConcurrentRequests` with 5 workers):
  - `/v1/featured`, `/v1/featured/new/albums`, `/v1/featured/new/tracks`, `/v1/featured/new/playlists`, `/v1/rising/new/tracks`, `/v1/rising/new/albums`, `/v1/genres`, `/v1/moods`, `/v1/master/recommended/albums`, `/v1/pages/my_collection_my_mixes` (`DP-outline:917–980`).
  - Category probes: `/v1/featured/{path}/{albums|tracks|playlists}` with failure policy `capability_probe` (`DP-outline:2037–2048`, `2098–2134`).
  - Genre image map from `/v1/genres` (`DP-outline:600–609`).
- DATA: the genre image fallback map is a constant in `DP.py:45–65` (IDs not printed).
- EVIDENCE: observed (`DP-outline:917–980, 2037–2048`); inferred for the probe policy from `_probeFeaturedCategoryPaths` names.
- UNKNOWNS: the detail of `_buildFeaturedResourceSections` output.

**FEATURE: Search**
- ENTRY: `LPTidalSearchViewController` (`pages/`); playback path `LPTidalPlayController.playTidalSearchTrack` (`PC-outline:124–136`).
- PROTOCOL: `GET https://api.tidal.com/v1/search/top-hits/` with query `query, countryCode, types, offset, limit` (`DP-outline:784–798`); normalized by `normalizeSearchResults` into top/artists/albums/tracks/playlists (`DP-outline:2149–2207`).
- EVIDENCE: observed (`DP-outline:786, 792`; `LPTidalPlayController.outline:275–287`).
- UNKNOWNS: the search `types` values were not enumerated.

**FEATURE: See All**
- ENTRY: `LPTidalSeeAllViewController` (`pages/`); QML `pages/TidalSeeAll.qml`.
- MECHANISM: `LPTidalDataProvider.loadSeeAll(descriptor, offset, limit, order, orderDirection, countryCode, skipCache)` (`DP-outline:1514`) builds the path from the `LPTidalSeeAllDescriptor` (`endpointPath`, `sourceKind`). Sort uses `supportsSort` / `defaultOrder` (`PC-outline:723`). Requests are cancelled per tag before a new fetch (`SeeAllVC-outline:559`).
- PROTOCOL: `GET https://api.tidal.com/v1/users/{userId}/favorites/{tracks|albums|artists|videos}`, `/v1/users/{userId}/playlistsAndFavoritePlaylists`, `/v1/genres/{genre}/{tracks|albums}`, `/v1/moods/{mood}/playlists` (`DP-outline:1700–1754, 1458–1466`).
- EVIDENCE: observed (listed lines); the view-mode key is in `LPTidalSeeAllViewPreference`.
- UNKNOWNS: the exact descriptor-to-path table in `LPTidalStore`, not read.

**FEATURE: Album detail**
- ENTRY: `controllers/details/LPTidalAlbumDetailViewController.py`; QML `pages/TidalAlbumDetail.qml`.
- PROTOCOL: `GET https://api.tidal.com/v1/albums/{id}`, `/v1/albums/{id}/similar`, `/v1/albums/{id}/credits` (`DP-outline:1022–1031`); tracks `/v1/albums/{id}/tracks` paged in `_loadAllAlbumTracks` (`DP-outline:1081–1082`). Artist albums `/v1/artists/{id}/albums` (`DP-outline:1049–1050`).
- EVIDENCE: observed (`DP-outline:1017–1088`).

**FEATURE: Artist detail and artist radio**
- ENTRY: `LPTidalArtistDetailViewController`, `LPTidalArtistRadioDetailViewController`.
- PROTOCOL: `GET /v1/artists/{id}` with sub-resources `/toptracks`, `/albums`, `/videos`, `/similar`, `/related`, `/radio`, `/bio` (`DP-outline:1096–1113`); radio `GET /v1/artists/{id}/radio` (`DP-outline:1159–1163`).
- EVIDENCE: observed (`DP-outline:1089–1172`).
- UNKNOWNS: `wimpLink` bio text is parsed by `LPTidalWimpLinkParser` (see the separate item below).

**FEATURE: Playlist detail and playlist items**
- ENTRY: `LPTidalPlaylistDetailViewController`.
- PROTOCOL: `GET /v1/playlists/{uuid}` (`DP-outline:1210, 1248`) and `GET /v1/playlists/{uuid}/items` (`DP-outline:1269–1270`), paged with `offset` and `limit`.
- EVIDENCE: observed (`DP-outline:1205–1294`).

**FEATURE: Mix detail**
- ENTRY: `LPTidalMixDetailViewController`.
- PROTOCOL: `GET /v1/mixes/{mixId}/items` (`DP-outline:1182–1183`).
- MECHANISM: mix title and image are cached in a class-level dict `_mix_meta_by_id`, capped at 500 entries (`DP.py:39–41, 178–186`).
- EVIDENCE: observed.

**FEATURE: Genre detail and mood See All**
- ENTRY: `LPTidalGenreDetailViewController`; QML `pages/TidalGenreDetail.qml`, `docs/genre-mood-detail.md`.
- PROTOCOL: `GET /v1/genres/{genre}/tracks`, `/v1/genres/{genre}/albums` (`DP-outline:1464–1466`); `GET /v1/moods/{mood}/playlists` (`DP-outline:1458–1459`). Genre path normalized by `_normalizeGenrePath` (`DP-outline:1788–1794`).
- EVIDENCE: observed.

**FEATURE: Video detail**
- ENTRY: `LPTidalVideoDetailViewController`.
- PROTOCOL: `GET /v1/videos/{id}` and `/v1/videos/{id}/recommendations` (`DP-outline:1435–1439`).
- EVIDENCE: observed.

**FEATURE: Favorites (add and remove)**
- ENTRY: `LPTidalFavoriteService.setFavorite` (`services/LPTidalFavoriteService`, outline line 74) to `LPMSManager.Tidal.LPTidalFavoriteManager.setFavorite` (line 202) to `requestSetFavorite` (line 218).
- PROTOCOL:
  - `GET /v1/users/{userId}/favorites/ids` (`DP-outline:1811–1812`).
  - `POST /v1/users/{userId}/favorites/{type}` with a form body whose key depends on the type: `artistIds`, `albumIds`, `trackIds`, `uuids` (playlists), `videoIds` (`DP-outline:2316–2328`; `addFavorite` line 1817, method `POST` at 1821).
  - `DELETE /v1/users/{userId}/favorites/{type}/{itemId}` (`DP-outline:1830–1835`).
  - `{type}` maps `artist|album|track|playlist|video` to `artists|albums|tracks|playlists|videos` (`DP-outline:2297–2314`).
- MECHANISM: optimistic update with a fallback to `previousFavoriteIds` on failure (`LPTidalFavoriteManager._fallbackFavoriteIdsForDesired`, line 253); a sync pass via `LPFavoriteSyncCoordinator` and `accountChangedForSource`.
- EVIDENCE: observed (listed lines).
- UNKNOWNS: `LPFavoriteSyncCoordinator` body (in `LPClientFramework`, not read).

**FEATURE: Playlist management (create, rename, delete, add, remove, move)**
- ENTRY: `services/LPTidalPlaylistManager.py`; dialog `widgets/LPTidalAddToPlaylistDialogHost` and QML `dialogs/TidalAddToPlaylistDialog.qml`.
- PROTOCOL:
  - `POST /v1/users/{userId}/playlists` (`createUserPlaylist`, `postForm`, `DP-outline:1295–1308`).
  - `POST /v1/playlists/{uuid}` (`updatePlaylist`, `postForm`, `1309–1319`).
  - `DELETE /v1/playlists/{uuid}` (`deletePlaylist`, `deleteJson`, `1320–1327`).
  - `POST /v1/playlists/{uuid}/items` with `itemIds`, `toIndex`; header `If-None-Match` (ETag, default wildcard) (`addPlaylistItems`, `1328–1351`).
  - `DELETE /v1/playlists/{uuid}/items/{index}` (`removePlaylistItems`, `1352–1363`).
  - `POST /v1/playlists/{uuid}/items/{index}` with `toIndex` (`movePlaylistItems`, `1364–1377`).
  - `GET /v1/users/{userId}/playlists` (`loadMyPlaylists`, `1406–1430`).
  - Write requests use session auth (`_playlistMutationHeaders`, `DP-outline:1858–1864`).
- EVIDENCE: observed (listed lines; method per the called helper, `postForm` / `deleteJson`).
- UNKNOWNS: the method used for `updatePlaylist` is inferred from `postForm`; the body is cut off.

**FEATURE: Collection (My Collection) and sort preferences**
- ENTRY: `LPTidalHomeViewController` and `LPTidalCollectionSortPreference` (`services/`).
- MECHANISM: `loadCollection(userId, countryCode, skipCache, sortPreferences)` (`DP-outline:1670`) runs parallel GETs for user playlists and favorites, with `order` and `direction` query params from `_collectionSortParams` (defaults `DATE` / `DESC`, upper-cased, `DP-outline:1658–1669`).
- SORT OPTIONS (observed, `services/LPTidalCollectionSortPreference.py` lines 17–110): per section, `{order, direction, label}` lists. Sections: `userPlaylists`, `favoriteArtists`, `favoriteAlbums`, `favoriteTracks`, `favoriteVideos`. Orders: `DATE`, `NAME`, `ARTIST`, `ALBUM`, `RELEASE_DATE`.
- PERSISTENCE: `QSettings` (`LPUtility.settings`), group keys `Tidal/<userId>` (inferred from the strings `settings`, `/`, `beginGroup`, `setValue`, `sync`), value key `collectionSeeAllSort:<section>` (`LPTidalCollectionSortPreference.py:117–122`).
- See All view mode: key `seeAllViewMode`, values `grid` (default) and `list` (`LPTidalSeeAllViewPreference.outline.txt:15–18`), same group scheme.
- Playlist quality and ReplayGain are also `QSettings` per user (`LPTidalPlayList.outline.txt:116–138`), read by `tidalReadLocalQualityValue` and `tidalReadLocalReplayGainValue`.
- EVIDENCE: observed (`.py` and outline lines); the group format is inferred.

**FEATURE: Image service (album, playlist and artist covers)**
- ENTRY: `services/LPTidalImageService.py`, extends `LPClientFramework.LPImageService.LPGlobalQmlImageService` with profile `TIDAL_COVER_320_PROFILE`.
- DATA: cache directory `LPUtility.cacheCoverDir` (created with `mkdir(parents, exist_ok)`, `LPTidalImageService.py` line 38); the owner key tracks in-flight downloads so a cancel can drop them (`_owner_key_locked`, `cancelOwner`).
- PROTOCOL: `https://resources.tidal.com/images/{uuid with "-" replaced by "/"}/{WxH}.jpg`, sizes from `LPTidalImageSize` (160, 320, 480, 640, 750, 1280) (`LPTidalImageConfig.py:10–17`; `buildTidalImageUrl` strings, `LPTidalImageConfig.outline.txt:73–81`).
- USE CASE SIZES: `_USE_CASE_SIZE_MAP` (`LPTidalImageConfig.py:30–37`): list thumbnail, card, table row, dialog thumbnail and artist avatar use 320; detail cover and hero use 640.
- EVIDENCE: observed (listed); mechanism of the replace is inferred from the string order.

**FEATURE: Request scheduling and HTTP caching**
- MODULES: `services/LPTidalRequestScheduler.py` (`LPTidalRequest`, priority queue, worker threads) and `data/LPTidalDataProvider.py` (`requests_cache`).
- MECHANISM:
  - Scheduler: `queue.PriorityQueue`, `max(1, maxWorkers)` daemon threads named `TidalScheduler-<n>`; jobs keyed by `request.key`; `cancelByTag(tag)`; results delivered through the `_deliveryReady` signal; `MAIN_THREAD_WARN_MS = 16` (`LPTidalRequestScheduler.py:19–70`).
  - Provider cache: `requests_cache.CachedSession(<GenericCacheLocation>/com.linkplay.wiimhome/tidal_request_cache, expire_after=3000)` (`DP.py:79–82`, outline 650–653). Response cache entries 200, LRU (`DP.py:27`). Optional 404 negative cache 600 s, 200 entries (`DP.py:28–29`). ETag via `If-None-Match` and `ETag` / `Etag` (`DP-outline:676–705`).
  - Cache key: SHA-256 over method, url, params, payload, and the Authorization and session headers, JSON with sorted keys (`DP-outline:1988–2004`; hashing in `requestJson`, `DP-outline:657`).
  - Aggregate concurrency: 5 workers via `BoundedSemaphore` (`DP.py:42–43`).
- EVIDENCE: observed (listed lines).
- UNKNOWNS: the backend of `requests_cache` (default SQLite is assumed, not observed; the file name is not confirmed on disk).

**FEATURE: Network diagnostics (QML image loads)**
- ENTRY: `services/LPTidalNetworkDiagnostics.py`, function `installTidalQmlNetworkDiagnostics(quickWidget, tag)` (line 89).
- MECHANISM: installs a network reply logger on the QQuickWidget network manager, sets the QML image cache directory to `cacheCoverDir`, and logs cache traces with tag `tidal_qml` (`LPTidalNetworkDiagnostics.py:94–106`). `_looks_like_image_url` decides by file suffix (`line 78`).
- EVIDENCE: observed (`LPTidalNetworkDiagnostics.py:17–106`).

**FEATURE: Event tracking**
- ENTRY: `services/LPTidalEventTrack.py`, class methods `login_event`, `api_error`, `playback_event`.
- PROTOCOL (local, no HTTP here): `LPGlobalUI.eventTrack.logEvent(name, params)` with `name = "tidal_" + suffix` (`LPTidalEventTrack.dis.txt:268–323`).
- EVENTS (observed, `LPTidalEventTrack.py:12–16`): `tidal_login` (success or failure), `tidal_api_error` (non-2xx, non-304 responses), `tidal_playback` (success or failure). Parameters include `device_uuid` truncated to 8 characters (`_desensitize_uuid`, `LPTidalEventTrack.py:40–44`), `country_code` from `LPUtility.eventCountryCode` (fallback `ZZ`), and `tidal_account_country_code`.
- EVIDENCE: observed (listed lines).
- UNKNOWNS: `logEvent` transport was not read (in `LPGlobalUI`).

**FEATURE: Playback of a TIDAL track or list on the speaker**
- ENTRY: `LPTidalPlayController.playTidalTrackFromModel`, `playTidalSearchTrack`, `playTidalDetailTrack`, `playTidalMediaQueue`, `playTidalCollectionTrack` (`controllers/base/LPTidalPlayController.outline.txt:71–121`).
- MECHANISM:
  1. The controller builds the queue `SearchUrl` from the TIDAL endpoint path and params: `_buildTidalSearchUrl` (`PC-outline:781–788`) produces an absolute `https://api.tidal.com/...` URL.
  2. `LPTidalPlayList.generateXML(startPlayIndex)` (`PL-outline:302–343`) builds the XML. Each track is `Track%d` with `Source`, `Id`, `URL` and `Metadata` (DIDL-Lite, class `object.item.audioItem.musicTrack`). Track URLs are `wiimu_search://...` when inline track URLs are used (`PL-outline:341–342`).
  3. The XML is sent to the speaker as UPnP `CreateQueue` by `LPUpnpAsyncDataModel.palyWithSearchUrl` (`UPNP-outline:41`), then `_on_play_result` logs the outcome (`PC-outline:585–596`).
  4. Preset save uses `BackUpQueue` with `generateBackupQueueXML` (`PL-outline:344–362`) and `SetKeyMapping` with `generateSetKeyMappingXML` (`PL-outline:363–374`).
  5. Queue navigation: `SkipQueue`, `PlayQueueWithIndex`, `AppendTracksInQueueEx`, `RemoveTracksInQueue`, `GetQueueIndex`, `SetQueueLoopMode`, `BrowseQueue` (`LPDevice.outline.txt:598–617`).
- PROTOCOL (what the PC sends to the device): one UPnP SOAP call to `http://<device-ip>:59152/upnp/control/PlayQueue1`, service `urn:schemas-wiimu-com:service:PlayQueue:1` (`LPDevice.dis.txt` 4113–4135; `UPnPTool` outline 18–28). The XML `<ListInfo>` carries `ListName, SourceName, SearchUrl, UserId, PicUrl, StreamType, StreamId, ShowName, ContentType, requestQuality, EnableReplayGain, ReplayGainType, StartPlayIndex` (`PL-outline:307–335`). The XML has no token field (the `generateXML` names list, `PL-outline:303`, contains no token name). The account binding is the `UserId` value only; the speaker holds the token.
- EVIDENCE: observed (listed lines); the statement that the speaker fetches the tracks from `SearchUrl` itself is inferred from the field names.
- UNKNOWNS: how the speaker resolves `wiimu_search://` track URLs and fetches the paged `SearchUrl` (device firmware, not in this code). The CreateQueue branch of `LPDevice.upnpPost` was inferred to use `PlayQueue1` by position (`LPDevice.dis.txt` ~4448–4574); it was not fully confirmed.

**FEATURE: Recently Played (TIDAL)**
- ENTRY: `LPTidalStreamService.playRecently` (`LPTidalStreamService.outline:292`), `recentlyDidSelect` (line 279).
- MECHANISM: stores a snapshot `LPTidalPlayList` into `LPRecentlyManager.addRecentlyPlayedWithMusicList` (`PC-outline:586`); on replay it sends `CreateQueue` again (`LPTidalStreamService.outline:355–363`).
- EVIDENCE: observed (listed lines).
- UNKNOWNS: `LPRecentlyManager` persistence path and whether `credential` is saved (see the token item above).

**FURTHER FEATURE: Bio and review text (wimpLink)**
- ENTRY: `data/LPTidalWimpLinkParser.py`, `parseBioText(raw)`, `segmentsToRichText`.
- MECHANISM: parses `[wimpLink artistId|albumId|trackId|videoId|playlistId="…"]text[/wimpLink]` plus `<br/>`, to segments (`text`, `link`, `break`) and to RichText HTML with link colours (`LPTidalWimpLinkParser.outline.txt:8–90`).
- EVIDENCE: observed.

**FURTHER FEATURE: Cursor bridge (QQuickWidget host cursor)**
- Module `services/LPTidalCursorBridge` (outline exists, `LPTidalCursorBridge.dis.txt`). Named in `LPTidalQmlContext` and login teardown (`LM` outline 391). Not read.

---

**UI-named features in scope that could not be traced**
- Qobuz-style "Add to playlist" from the queue More menu: `LPTidalStreamService.LPTrackMoreViewControllerAddToPlaylist` (outline line 528) reaches `LPTidalAddToPlaylistDialogHost.showForTrack`. The dialog data path was not read.
- Shell quality and ReplayGain dialog: `LPTidalShellViewController` (`_save_quality_value`, line 787). The `QSettings` key names were not read.
- Favorites sync: `LPFavoriteSyncCoordinator` (in `LPClientFramework`, not read).
- `LPTidalStore` internals (state shape, the descriptor-to-path table), `LPTidalQmlContext`, `LPTidalShellRouter`, `LPGlobalQmlImageService`, the device answer parser `_userInfoFromResponse` body.
- Repo docs `LPMSManager/Tidal/docs/integration-plan.md`, `HOME/StreamService/Tidal/docs/code-structure.md`, `docs/login-flow.md`: `login-flow.md` is referenced by `ui-design.md:796` but is not in the install. The others were not searched for.
- `LPDevice.upnpPost` rendercontrol1 branch name for volume and mute (`LPDevice.dis.txt:4038, 4087`), not traced to a TIDAL feature.

**Obstacles Encountered**
- `LPTidalDataProvider.py` is truncated at line 216; the outline and dis were used (outline line numbers in the report refer to the outline file).
- `LPTidalPlayList.py` and `LPTidalWimpLinkParser.py` have no outline string dump in the `.py` form; grep for URL and key strings against the `.py` returned no matches, so the outline was used.
- The outline path is `evidence\outline\...`, not `evidence\decompiled\outline\` as given in the brief.
- `LPOAuthHttpServer` mount point in `LPHttpServerManager.start` is cut off; the port number is confirmed from `LPUtility.py`.
- No secrets were printed. The device client ID and the cipher key are described by name only (`LPTidalLoginManager._decodeDeviceValue`, `LPUpnpAsyncDataModel.userLoginByCode`). A hard-coded sample device address exists in `UPnPTool` outline line 9; its use was not traced.

**Side effects:** none. No files written, no URLs contacted, no servers started, no packages installed, no processes killed.