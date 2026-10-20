# Report: wiim-feature-report (device discovery, connection, control protocol)

**Task:** Trace how WiiM Home finds, connects to, subscribes to and controls a WiiM device, and report the wire protocol. Covers SSDP, mDNS, cache, manual IP, HTTP API, SOAP, TLS, UPnP eventing, audio input/output switching, cloud state, telemetry and network utilities.

**Questions the task depends on:** how a device is found; which transport and commands control it; what is subscribed and how events arrive; how audio inputs and outputs are switched; which cloud and telemetry calls are made.

**Base paths:** `DEC` = `D:\git-projects\audio-star\evidence\decompiled\`, `OUT` = `D:\git-projects\audio-star\evidence\outline\`. "dis:N" is line N of `OUT\<module>.dis.txt`, the authoritative bytecode listing. Where the `.py` is truncated (`LPDevice.py`, `LPDeviceDiscoverManager.py`, `LPCloudDeviceState.py`, `LPUPnPObserverManager.py`), the dis is used. `LPDiscoveryTelemetry.py` is empty, so its outline is used. Secret constants are named only, never printed.

---

## FEATURE: Device discovery (SSDP, mDNS, cache)

- ENTRY: `LPDeviceDiscoverManager.startSearch()` (`DEC\LPClientFramework\LPDeviceDiscoverManager.py:138`). Network change re-runs it via `onNetworkChanged` (`.py:454-471`), wired from `Network_Changed_Signal` (`DEC\HOME\WiiMHome.py:522`, `DEC\LPClientFramework\LPSignalBus.py:13`). Who constructs the manager: not traced.
- MODULES: `LPClientFramework.LPDeviceDiscoverManager`, `LPUPnPObserverManager`, `LPDevice`, `LPDiscoveryTelemetry`, `LPCache.LPDeviceFileCache`, `LPCache.LPFileCache`, `LPUtility` (network helpers via `util.LPNetworkUtility`). Third-party: `zeroconf` (named, not read).
- DATA:
  - Cache files under `LPUtility.cacheDir` (`LPUtility.py:112`, a Qt CacheLocation/bundleId path): `deviceCacheV2.json` and `mediaServerCacheV2.json` (`LPDeviceFileCache.py:19`, `LPFileCache.py:17,31`). Rows hold `ip`, `port`, `name`, `gateway` (`dis` of startSearch 3399-3417, `.py:320`).
  - No settings keys and no DB.
- MECHANISM:
  1. `startSearch` loads cache rows (`onlineCachedDevice`, `onlineCachedMediaServer`). Rows on the current gateway are re-probed with `deviceCome(uuid, ip, port, 'cache')` (`.py:139-140`, `.py:289-295`).
  2. Starts threads named `SearchThread`, `DealWithResponseThread`, `DealWithNotifyThread`, `CheckThread`, `InternetMonitorThread` (dis:1207-1296; thread targets inferred from names).
  3. `sendMSearch` (dis:1796-1899) sends three M-SEARCH datagrams on the unicast socket, to `239.255.255.250:1900`. Loop sleeps 2 s when `fastSearchingSwitch` is set, else 15 s (dis:1885-1897).
  4. `dealWithSSDPResponse` (dis:1540-1795) parses `LOCATION` (fallback `Location`) for ip and port, `USN: uuid:` for the uuid, and `ST`, or `NT` when `NTS` is `ssdp:alive` (dis:1678-1694). If `'MediaRenderer'` is in the type, the uuid is normalised and `deviceCome(uuid, ip, port)` runs (dis:1704-1736). If `'ContentDirectory'` or `'MediaServer'` is in the type, `mediaServerCome` runs with the description URL (dis:1738-1794).
  5. `deviceCome` (`.py:280-343`): drops devices outside the current subnet (`isIPInGateway`, `.py:284-294`). A new device creates `LPDevice(ip, port)` and calls `init()` (`.py:314,327`). Failure drops the record. Success adds the UPnP observer (`.py:338`), caches the device (`.py:339`), calls telemetry (`.py:340`) and the add callback plus `deviceNodeMgr.deviceOnline` (`.py:341-343`). A changed ip or port removes and re-adds the observer (`.py:304-312`).
  6. mDNS: `ServiceBrowser` on `_linkplay._tcp.local.` (dis:1168). `add_service` reads TXT key `b'uuid'`, normalises it and calls `deviceCome(uuid, ip, info.port, 'mdns')` (`.py:399-421`). `update_service` only logs; `remove_service` only logs.
  7. Liveness: `ssdpCheckThread` sleeps 10 s (dis:1492-1493) and expires stale records. `monitorInternet` polls every 5 s (dis:3157-3158). A gateway change emits `Network_Changed_Signal` (`.py:431-433`).
- PROTOCOL:
  - M-SEARCH text (dis:1808, same at 1823 and 1837): `M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 3\r\nST: %s\r\nUSER-AGENT: mac/1.0 UPnP/1.1 upnpx/1.0\r\n\r\n`
  - ST values: `ssdp:wiimudevice` (default `searchKey`, `.py:35`, `dis:184`), `urn:schemas-upnp-org:service:ContentDirectory:1` (dis:1824), `urn:schemas-upnp-org:device:MediaServer:1` (dis:1838).
  - Reply/NOTIFY keys parsed: `LOCATION`/`Location`, `USN`, `ST`, `NT`, `NTS`.
  - Multicast membership: `struct` format `'4sl'` (dis:901, 1062), inferred to be an ip_mreq join.
  - Port 1900 (`.py:26`).
  - uuid transform (dis:1704-1727): `uuid[:-len(first 8-char group)].replace('-','')`. For a 36-char USN uuid this gives the first four groups plus the first 4 hex of the last group, the 24-hex device id.
  - mDNS: type `_linkplay._tcp.local.`, TXT key `uuid`, decoded, `[5:]` strips the `uuid:` prefix, then the same transform.
- EVIDENCE: observed (above file:line refs). Cadence values observed in dis. The `'MediaRenderer'` branch is observed at dis:1704; the `.py` shows `None in serviceType` because of the decompile artifact.
- UNKNOWNS:
  - The record-expiry threshold: the docstring says 100 s (`.py:38`), but no constant 100 appears in dis.
  - `refreshMultiroomState` callers are not in the decompiled tree (grep found none).
  - Whether the SSDP-derived `port` is the UPnP event port (inferred from `deviceCome` usage).
  - `add_service` and `validInterfaces` (`LPQTSSDPServer.py:32`) conditions read oddly in pycdc; verify in dis before relying on them.

---

## FEATURE: Device connection and state init (LPDevice)

- ENTRY: `LPDeviceDiscoverManager.deviceCome` calls `LPDevice.init()` (`LPDevice.py` class at line 151; `init` at `.py:205`, dis:1130).
- MODULES: `LPClientFramework.LPDevice`, `UPnPTool`, `LPTLSTool`, `LPDeviceStreamServiceManager`, `LPDeviceGroupInfo`, `LPMediaInfo`, `LPQueueManager`.
- DATA: device config tables `LPDeviceConfigDict` and `LPDeviceImageNameDict` (`LPDevice.py:23-160`), product name to feature flags. No file writes found in this module.
- MECHANISM:
  1. `init` starts `_asyncLoadInit` (outline:273-288). It calls `fetchMediaInfo` (GetInfoEx), then `upnpPostWithRetry('StreamServicesCapability', apiTimeout=3)` (dis:1184-1188). The reply `StreamCapability` is parsed as JSON for `version` and `streamServices`, which feed `updateAppStreamServiceCapability` and `registerDeviceStreamService` (dis:1199-1231).
  2. Then `commonHttpGet('getModeRename')` (dis:1250-1253). Its JSON body gives the `SPDIF-In` and `Line-In` display names (dis:1277-1291).
  3. `updateDeviceInfo` (outline:353-388) calls `upnpPost('GetControlDeviceInfo')` and parses the `Status` string as JSON (keys below).
  4. Multiroom state: `refreshMultiroomState` (dis:2980+) calls `getStatusEx` (dis:2986), then `multiroom:getSlaveList` if roomState is master (dis:3093).
  5. Live state after that comes from UPnP NOTIFY pushes (see UPnP eventing).
  6. Retry: `upnpPostWithRetry` retries only on status -2, the timeout code (outline:628-632).
- PROTOCOL: see the command tables under the control, HTTP and eventing features.
  - `GetControlDeviceInfo` `Status` JSON keys (outline:355-386): `uuid`, `DeviceName`, `project`, `preset_key`, `security_version`, `plm_support`, `capability`, `volume_control`, `HiFiSRC_version`, `audio_channel_config`, `eth0`, `audioOutputModeVer`, `audiocast`, `autoSenseVersion`, `essid` (hex, decoded as UTF-8), `group`, `master_uuid`, `GroupName`.
  - Other out params requested in the same call: `SlaveList`, `CurrentMute`, `CurrentVolume`, `Ssid`, `MultiType`, `Router`, `SlaveMask`, `CurrentChannel`.
  - `getStatusEx` JSON keys used by `_applyMultiroomStatus` (outline:454-463): `GroupName`, `group` (`'0'`/`'1'`), `master_uuid`, `slave`/`master`.
  - `multiroom:getSlaveList` JSON keys: `slave_list` (items keyed by `uuid`), `group_type` (outline:465-471, 446-449).
- EVIDENCE: observed (dis and outline refs above). Key-to-attribute mapping is partly inferred from string constants and function names.
- UNKNOWNS: `LPDevice.py` is cut at line 162, so method bodies come only from dis. Exact JSON-to-attribute mapping in `updateDeviceInfo` (dis:1718-2134) not fully read. Cadence of `refreshMultiroomState` not found.

---

## FEATURE: Device control over SOAP (UPnP actions)

- ENTRY: `LPDevice.upnpPost(command, inParams, apiTimeout)` (dis:4025-4940), wrapped by `asyncUpnpPost`, `upnpPostWithRetry`, `getUserInfoAsync`. Callers in the player UI (for example `fastPlay`, dis:3371).
- MODULES: `LPClientFramework.UPnPTool` (`UPnPTool.py:10`), `LPDevice`.
- MECHANISM (`UPnPTool.upnpPost`, dis:62-316): builds a SOAP 1.1 envelope with each inParam XML-escaped. POSTs it through `requests.Session` with `headers`, `data` (UTF-8 bytes) and `timeout` (default 15, `UPnPTool.py:10`). Parses the reply with BeautifulSoup `xml` and returns a dict keyed by each out-param name, plus `status_code: 200`. Errors return `{'status_code': -2, 'error': e}` on timeout, `{'status_code': -1, 'error': e}` on other exceptions, and `{'status_code': N, 'error': N}` on non-200 (dis:238-354).
- PROTOCOL:
  - Transport: plain HTTP to port 59152 (`upnpPost`, `.py:547,568,572`).
  - Headers: `Content-Type: text/xml; charset="utf-8"`; `SOAPACTION: "<serviceStr>#<Action>"`.
  - `serviceStr` is `urn:schemas-upnp-org:service:<svc>` except PlayQueue, which is `urn:schemas-wiimu-com:service:PlayQueue:1` (`UPnPTool.py:12-13`).
  - Endpoints: `/upnp/control/rendercontrol1` (RenderingControl:1), `/upnp/control/rendertransport1` (AVTransport:1), `/upnp/control/PlayQueue1` (PlayQueue:1).

| Endpoint | Action | Fixed inParams | Out params (reply keys) |
|---|---|---|---|
| rendercontrol1 | GetControlDeviceInfo | InstanceID=0 | MultiType, Router, SlaveMask, SlaveList, Ssid, Status (JSON string), CurrentVolume, CurrentMute, CurrentChannel |
| rendercontrol1 | StreamServicesCapability | InstanceID=0, AppVersion=1.0 | StreamCapability (JSON string) |
| rendercontrol1 | SetVolume | InstanceID=0, Channel=Master, plus caller | none |
| rendercontrol1 | SetMute | InstanceID=0, Channel=Master, plus caller | none |
| rendercontrol1 | AirplayAutoSyncDelay | caller | none |
| rendertransport1 | GetInfoEx | InstanceID=0 | CurrentTransportState, TrackDuration, TrackMetaData, TrackURI, RelTime, LoopMode, CurrentVolume, TrackSource, PlayMedium |
| rendertransport1 | Next, Previous | InstanceID=0 | none |
| rendertransport1 | Play | InstanceID=0, Speed=1 | none |
| rendertransport1 | Pause | InstanceID=0 | none |
| rendertransport1 | Seek | InstanceID=0, Unit=REL_TIME, plus caller | none |
| PlayQueue1 | GetUserInfo, GetBasicUserInfo, UserLogin, UserLogout | caller | Result (for UserLogin/Logout Result is returned raw; GetUserInfo and GetBasicUserInfo json-load Result) |
| PlayQueue1 | CreateQueue | QueuePolicy=0, plus caller | none |
| PlayQueue1 | AppendTracksInQueueEx | QueuePolicy=0, plus caller (fastPlay adds Direction, StartIndex, QueueContext) | none |
| PlayQueue1 | PlayQueueWithIndex | caller (QueueName, Index) | none |
| PlayQueue1 | BrowseQueue | QueueContext | QueueContext (parsed into musicList, version, xml) |
| PlayQueue1 | SkipQueue | QueueContext | none |
| PlayQueue1 | GetQueueIndex | caller | CurrentIndex, PreloadingIndex |
| PlayQueue1 | RemoveTracksInQueue | QueueName, RangStart, RangEnd (drag/drop) | none |
| PlayQueue1 | DeleteQueue, BackUpQueue | caller | none |
| PlayQueue1 | GetKeyMapping | caller | QueueContext |
| PlayQueue1 | SetKeyMapping | caller | none |
| PlayQueue1 | SetQueueLoopMode | caller | Result |

- Source for the table: dis:4026-4936 (dispatch), dis:4041-4052 (StreamServicesCapability), dis:4079-4111 (GetControlDeviceInfo), dis:4137-4162 (GetInfoEx), dis:4502-4559 (queue actions), `LPDevice.py` outline:542-625.
- EVIDENCE: observed (dis lines above). "caller" means the inParams dict is supplied by the caller.
- UNKNOWNS: the exact inParams keys supplied by callers (for example Volume/DesiredVolume and Target names) are not in this module.

---

## FEATURE: HTTPS HTTP API (httpapi.asp) and TLS

- ENTRY: `LPDevice.commonHttpGet` (dis:5040-5201) and `commonHttpPost` (dis:5419-5591). Also `httpGetBytes` (dis:5202-5418) for downloads.
- MODULES: `LPDevice`, `LPTLSTool` (`DEC\LPClientFramework\LPTLSTool.py`), `requests`, `urllib3` (warnings disabled).
- DATA: the client certificate, key and CA are base64+ROT13 strings in `LPTLSTool.py:11-13` (`str1` cert, `str2` key, `str3` CA). They are written to temp files and removed after loading (`LPTLSTool.py:19-33`). Not decoded or printed here.
- MECHANISM:
  - GET: `https://<ip>/httpapi.asp?command=<cmd>` (dis:5041). `requests.session().get(url, cert=(cert, key), verify=False, timeout=15)` (dis:5094-5097). Returns `{'status_code', 'body'}`, or `{'status_code': -1, 'error'}` on exception.
  - POST: `https://<ip>/httpapi.asp` (dis:5420). Form body `command=<cmd>:<json.dumps(payload)>` (dis:5434-5443), with `cert`, `verify=False`, `data=`; no timeout.
  - `httpGetBytes`: tries `https` with the cert, and `http` directly for `http://` URLs (outline:648-660).
  - `tlsCommand` / `LPTLSTool.tlsCmd` (`LPTLSTool.py:37-71`): raw TLS 1.2 socket to `<ip>:8893`, `CERT_REQUIRED`, CA from `str3`, client cert chain from `str1`/`str2`, `server_hostname=ip`. Writes the command bytes raw (no `httpapi` prefix) and reads a single `recv(1024)`.
- PROTOCOL (GET unless marked POST):
  - `getStatusEx`: JSON body, see state init.
  - `multiroom:getSlaveList`: JSON body.
  - `multiroom:getnamegrouplist`, `multiroom:Ungroup` (GET).
  - `multiroom:savenamegrouplist`, `multiroom:setcurrentnamegroup` (POST, dict payload).
  - `getModeRename`: JSON with `SPDIF-In`, `Line-In`.
  - `MCUKeyShortClick:<index>` (`DEC\HOME\LPPresetViewController.py:290`), a remote-key emulation.
  - Voice/Bluetooth/device-setting commands are listed under "Other command families".
- EVIDENCE: observed (dis lines above; call sites `LPPresetViewController.py:290`, `LPQobuzLogoutDialog.py:128,148`).
- UNKNOWNS: `tlsCmd` callers: none found except `LPDevice.tlsCommand` (dis:3973-3980) and the `__main__` test line (`LPTLSTool.py:74`, example IP `192.168.1.35`). The `wrap_socket` and `load_cert_chain` argument shapes are read from kwnames and are consistent but not confirmed in dis. `httpGetBytes` callers (for example the `/data/sys.log` download) are not found.

---

## FEATURE: UPnP eventing (subscriptions and NOTIFY)

- ENTRY: `LPDeviceDiscoverManager.deviceCome` calls `upnpObserverManager.addObserver(ip, upnpPort, uuid)` (`.py:338`). Manager at `LPUPnPObserverManager.py:260`.
- MODULES: `LPClientFramework.LPUPnPObserverManager` (`DEC\LPClientFramework\LPUPnPObserverManager.py`).
- MECHANISM:
  1. `SERVICES = ('rendercontrol1', 'PlayQueue1', 'rendertransport1')` (`.py:262`). Each device gets one subscription per service.
  2. Local listener: `LPThreadHTTPServer` on port 22334 (`.py:272`), serving path `/Event` (`.py:230`).
  3. Subscribe: `SUBSCRIBE http://<ip>:<upnpPort>/upnp/event/<service>` (`.py:336`). Headers: `TIMEOUT: Second-1800`, `User-Agent: <system>/<release> UPnP/1.1 LPUnittest/<appVersion>` (the literal `LPUnittest` is in the code), and `NT: upnp:event` plus `CALLBACK: <http://<localIP>:22334/Event>` (`.py:406-413`). Subscription port is `upnpPort` (from discovery; 59152 for manual add).
  4. Reply: `SID` header, and `TIMEOUT` parsed as `Second-<n>` or `Second-infinite` (= 1800), `.py:419-430`.
  5. Renew: `SUBSCRIBE` with `SID` header at 0.8 x timeout (`RENEW_RATIO`, `.py:263`), about 1440 s. Retry interval 10 s (`.py:264`). The first NOTIFY must arrive within 10 s (`FIRST_NOTIFY_TIMEOUT`, `.py:265`), or the subscription is re-created once (`.py:383-391`).
  6. Unsubscribe: `UNSUBSCRIBE http://<ip>:<port>/upnp/event/<service>` with `SID` (`.py:398-403`).
  7. NOTIFY handling (`LPSimpleUPnPObserverHandler.do_NOTIFY`, `.py:228-241`): reads `SID`, `SEQ` and the `LastChange` element from the body. Unknown paths get 404 with `{"error": "404"}` (`.py:247-255`). Early notifications are cached up to 20 items for 10 s (`.py:261-267`, `.py:587-623`).
  8. Parsers by service (`.py:55-210`):
     - rendercontrol1: `Volume`→`volume` (float), `Mute`→`mute` (bool), `FixVolume`→`fixedVolume` (bool), `DeviceName`→`deviceName`. Also `Slave` element with `action`/`val` → `slaveAction` {`action`, `slaveId`}, and `commonevent` element JSON with key `lpmrm`.
     - rendertransport1: `TransportState`→`playState`, `CurrentTrackMetaData`→`metaData` (DIDL-Lite parsed for `dc:title`, `upnp:artist`, `upnp:album`, `upnp:albumArtURI`, `song:quality`, `song:rate_hz`, `song:bitrate` and others), `CurrentTrackURI`→`playUri`, `CurrentTrack`→`lastPlayIndex`, `TrackSource`, `PlaybackStorageMedium`→`mediaType`, `CurrentTrackDuration`→`duration`, `A_ARG_TYPE_SeekTarget`→`progress`.
     - PlayQueue1: `LoopMode`/`LoopMpde`→`loopMode`, `CurretPlayListName`→`queueName`, `info`.
- PROTOCOL: as above. Method names: `SUBSCRIBE`, `UNSUBSCRIBE`, NOTIFY POST to `/Event` on the PC.
- EVIDENCE: observed (`LPUPnPObserverManager.py` lines as cited; outline:215-235, 336, 399, 406-413).
- UNKNOWNS: the decompiled `parserForService` reads `if None == 'rendertransport1'` and `if None == 'PlayQueue1'` (`.py:44-47`), so only the rendercontrol1 branch is confirmed. The `do_NOTIFY` success status code is cut (`.py:244`). The `_performSubscription` body after line 416 is cut.

---

## FEATURE: Manual IP add ("Connect Device by IP Address")

- ENTRY: QML `connectByIpRequested` (`DEC` of `Qml\DeviceDiscovery\LPDeviceDiscoveryEmpty.qml:36,423`) → `WiiMHome.py:342-345` → `_openIPDiscoverDialogFromQml` (`WiiMHome.py:464`). Also `LPDeviceDashboardViewController.py:591` opens the same dialog.
- MODULES: `LPCommonWidgets.dialog.LPIPDiscoverDeviceDialog` (`DEC\LPCommonWidgets\dialog\LPIPDiscoverDeviceDialog.py`), `UPnPTool`, `LPGlobalUI.deviceManager`.
- MECHANISM: user enters an IP. `_preDiscover` validates (`validateIP` body cut, `.py:170-172`, `ipaddress` imported at `.py:10`) and emits `discoverSignal(ip)` (`.py:112-120`). `attemptDiscover` runs a thread (`.py:147-166`): calls `UPnPTool.upnpPost('http://<ip>:59152/upnp/control/rendercontrol1', 'RenderingControl:1', 'GetControlDeviceInfo', {'InstanceID': '0'}, ['Status'], timeout=5)`. On success it reads `json.loads(response['Status'])['uuid']` and calls `deviceManager.deviceCome(uuid, ip, 59152, 'manual')`.
- PROTOCOL: SOAP as in the control table; port 59152 hard-coded.
- EVIDENCE: observed (`LPIPDiscoverDeviceDialog.py:147-166`). The help-link URL `https://faq.wiimhome.com/...` (`.py:84`) is text only, not fetched.
- UNKNOWNS: `validateIP` body. The manual path passes the raw `Status.uuid` to `deviceCome` with no 24-hex normalisation, unlike the SSDP path (observed `.py:156-158` vs `.py:207`). Whether the two forms match is not known.

---

## FEATURE: PC as UPnP/SSDP responder (LPQTSSDPServer)

- ENTRY: `LPQTSSDPServer.start()` (`DEC\LPClientFramework\LPQTSSDPServer.py:179`). Caller not traced.
- MODULES: `LPClientFramework.LPQTSSDPServer` (PyQt6 `QUdpSocket`).
- MECHANISM: binds UDP `AnyIPv4:1900` with `ShareAddress | ReuseAddressHint` (`.py:186`), joins `239.255.255.250` on valid interfaces (`.py:187-188`), and starts `sendLiveNotify` (`.py:191-193`).
  - Live NOTIFY `ssdp:alive` for: uuid root (`uuid:<pcUUID>`), `upnp:rootdevice`, `urn:schemas-upnp-org:service:ContentDirectory:1`, `urn:schemas-upnp-org:device:MediaServer:1` (`.py:74-81`). Repeats every `responseExpire + 600` = 1500 s (`.py:196-202`).
  - `ssdp:byebye` for the same four on stop (`.py:84-91`, `.py:215-226`).
  - M-SEARCH answered by `respond_MSEARCH` (`.py:102-119`): `HTTP/1.1 200 OK` with `CACHE-CONTROL: max-age = 900`, `EXT`, `LOCATION: http://<localIP>:<upnpServerPort>/upnp/DeviceDescription.xml`, `SERVER`, `ST`, `USN`, `OPT: "http://schemas.upnp.org/upnp/1/0/"; ns=01`, `01-NLS`, `BOOTID.UPNP.ORG`.
  - `SERVER` string (`.py:173`): `<system>/<release> UPnP/1.0 DLNADOC/1.50 WiiMHome/<appVersion>`.
  - Local IP is `fetchLocalIP()` unless the sender is `127.0.0.1` (`.py:105-106`).
- PROTOCOL: as above. `upnpServerPort` (`LPUtility`) is not traced.
- EVIDENCE: observed (lines cited).
- UNKNOWNS: `received_MSEARCH` and `http_parse_raw` bodies are cut (`.py:62`, `.py:147`). The HTTP server that serves `DeviceDescription.xml` is not traced.

---

## FEATURE: Audio output switching (Sound settings)

- ENTRY: `LPDeviceSettingSoundViewController._updateAudioOutputUI._outputBoxChange` (`OUT\HOME\DeviceSetting\LPDeviceSettingSoundViewController.dis.txt:6542`), applied by `._outputHttp` (dis:6735-6858).
- MODULES: `LPClientFramework.LPDeviceAudioOutput` (`DEC\LPClientFramework\LPDeviceAudioOutput.py`), `HOME.DeviceSetting.LPDeviceSettingSoundViewController`.
- DATA: none written by the device side. UI tables from `makeAudioOutputArray` and `outputInfoTemplate` (`LPDeviceAudioOutput.py:7-93`).
- MECHANISM:
  1. Options by product (`LPDeviceAudioOutput.py:7-70`):
     - AMP: Speaker Out `'2'`, Bluetooth Out `'5'`.
     - Ultra: Line Out `'2'`, Optical `'1'`, COAX `'3'`, Headphone `'4'`, Bluetooth `'5'`.
     - Pro and Pro Plus: Line `'2'`, Optical `'1'`, COAX `'3'`, Bluetooth `'5'`.
     - Others: `'AUX'`, `'SPDIF'`, `'BLUETOOTH'`.
  2. Apply (`_outputHttp`, dis:6735-6858):
     - If `device.audioOutputModeVer` is not None: `GET setSoundCardOutputMode:<json>` where json = `{"index", "mode", "cardId", "devName", "devNameHex"}` (dis:6806-6820). `devNameHex` is `devName` as UTF-8 hex.
     - Else `GET setAudioOutputHardwareMode:<value>` (dis:6823-6843).
     - For `productName == 'Muzo_Mini'`: `GET GNOTIFY=KeyEvent:<value>` (dis:6832-6843).
  3. Reads: `getSoundCardModeSupportList`, `getActiveSoundCardOutputMode`, `getNewAudioOutputHardwareMode`, `getSpdifOutSwitchDelayMs`, `getSpdifOutMaxCap`, `getCoaxOutMaxCap`, `getOutputVoltage`, `getAuxVoltageSupportList`, `getChannelMode`, `getChannelBalance`, `getDigitalFilterTypeSupportList`, `getDigitalFilterType`, `getSubLPF`, `getbthistory` (dis lines 910-2260 by name).
  4. Writes: `setOutputVoltage:%d` (dis:4660), `setVolumeControl:%d` (4589), `setMaxVolume:%d` (4723), `setSpdifOutMaxCap:%d:%d:%d` (4951), `setCoaxOutMaxCap:%d:%d:%d` (5314), `setChannelMode:%d` (5532), `setChannelBalance:%.2f` (5597), `setSpdifOutSwitchDelayMs:%d` (6910), `setDigitalFilterType:%d` (6995), `setSubLPF:status|level|cross|phase|sub_delay:%d` (7749-8126).
- PROTOCOL: GET httpapi commands above (HTTPS). Reply key names for the getters are not read.
- EVIDENCE: observed (lines cited).
- UNKNOWNS: the `mode` values for `outputBox` items come from the getter replies, which are not traced. `device.audioOutputModeVer` is set in `updateDeviceInfo`.

## FEATURE: Audio input switching

- ENTRY: `LPDeviceSettingSoundViewController._updateAudioInputUI._inputBoxChange` (dis:9054), applied by `._switchModeHttp` (dis:9139-9160) and `._phonoTypeBoxChange._switchPhonoTypeHttp` (dis:9276-9296).
- MODULES: `LPClientFramework.LPDeviceAudioInput` (`DEC\LPClientFramework\LPDeviceAudioInput.py`), the same Sound controller.
- MECHANISM: the input template is chosen per product (`LPDeviceAudioInput.py:8-139`). Each option has `title`, `mode` and `mediaType`.
  - Apply: `GET setPlayerCmd:switchmode:<mode>` (dis:9142), then sets `device.mediaInfo.mediaType`.
  - Phono: `GET PHONO_MODE_SWITCH_SET:<index>` (dis:9279). Read: `GET PHONO_MODE_SWITCH_GET` (dis:2386).
- PROTOCOL: `mode` strings: `HDMI`, `line-in`, `optical`, `bluetooth`, `wifi`, `phono`, `arc`, `PCUSB`, `extern_bluetooth`, `co-axial`, `RCA`, `FM`, `XLR`, `TFCard`, `udisk`. Pro list uses plm id `10001` for Wi-Fi (`LPDeviceAudioInput.py:71`).
  - Input setters: `setAuxAutoSenseEnable:%d` (dis:9212), `setSpdifAutoSenseEnable:%d` (9348), `setAuxInMaxCap:%d:%d` (9420, 9491), `setPlayModeVolumeEnable:%d` (9561), `setCecPowerCtrl:%d` (9632).
  - Input getters: `getAuxAutoSenseEnable`, `getSpdifAutoSenseEnable`, `getAuxInMaxCap`, `getPlayModeVolumeEnable`, `getCecPowerCtrl` (dis:2434-2654).
- EVIDENCE: observed (lines cited).
- UNKNOWNS: the plm id to mode mapping in `LPPublicDefine` is not traced.

---

## FEATURE: Cloud device state (queryDeviceStateV2), diagnostic only

- ENTRY: `LPDiscoveryTelemetry._diagnoseDevice` (outline:318-362) calls `queryDeviceStateV2(deviceUid, timeout)` (`DEC\LPClientFramework\LPCloudDeviceState.py:57`).
- MODULES: `LPClientFramework.LPCloudDeviceState`.
- DATA: the three constants `_CLOUD_APP_ID`, `_CLOUD_ACCESS_KEY`, `_CLOUD_SECRET_KEY` are at `LPCloudDeviceState.py:27-29`. Not printed here.
- MECHANISM:
  - `_signedHeaders()` (`.py:31-54`): `timestamp` = milliseconds; `nonce` = 16 random alnum; `appId` = SHA-256 hex (lowercase) of `accessKey + appId constant`; `sign` = SHA-256 hex, uppercase, of `secretKey + "accessKey=..&appId=<hashed>&nonce=..&timestamp=..&secretKey=.."`.
  - `requests.post(URL, json={'deviceUid': uid}, headers=..., timeout=5)` (dis:173-174 keyword mapping).
  - Response: JSON, `result` key (dis:209). Failure logs and returns None.
- PROTOCOL: `POST https://cloud-api-us.linkplay.com/v1/rest/api/queryDeviceStateV2`, body `{"deviceUid": "<24-hex>"}`, headers `Content-Type: application/json`, `accessKey`, `timestamp`, `nonce`, `sign`, `appId`. Result keys read by telemetry (`LPDiscoveryTelemetry` outline:143-157): `networkInfo` (`wlan0`, `eth0`, `wlanSsid`, `wlanBssid`, `wlanRssi`), `connectStatus`, `source`, `iotVersion`, `otaStatus`.
- EVIDENCE: observed (`LPCloudDeviceState.py:26,31-79`; dis lines above).
- UNKNOWNS: the body after line 73 is cut in pycdc; the return path is confirmed only from dis.

---

## FEATURE: Discovery telemetry

- ENTRY: `LPDiscoveryTelemetry` hooks from `LPDeviceDiscoverManager` (`onDeviceSeen`, `onDeviceAdded`, `onDeviceRemoved`, `onGatewayPoll`, `onInternetPoll`, `onNetworkChanged`, `appStart`), outline:255-296, 469-570.
- MODULES: `LPClientFramework.LPDiscoveryTelemetry` (source file empty; outline only), `LPEventTrack`/`LPEventsType` (not traced), `LPCloudDeviceState`, `UPnPTool`, `LPNetworkUtility`.
- MECHANISM:
  1. Snapshot events fire when the network state changes (`network_context_snapshot`, outline:163).
  2. Convergence report after startup or network change (`device_discovery_report`, outline:214). Settles on a quiet period, or on a forced maximum (`FORCE_REPORT_SECONDS`).
  3. Failure diagnosis for cached devices not seen on the current gateway (`device_discovery_failure`, outline:318-362). Each device runs once per session. Probes: SOAP `GetControlDeviceInfo` to `http://<ip>:59152/upnp/control/rendercontrol1` (`_probeHttp`, outline:303-316), TCP to port 443, ICMP ping, cloud query. Skipped when the device reports OTA.
- PROTOCOL: events and fields:
  - `device_id_hash` = SHA-1 of uuid, first 8 hex (outline:26).
  - `phase`, `sequence`, `found_any`, `device_count`, `device_count_cumulative`, `ssdp_count`, `mdns_count`, `device_id_hashes`, `elapsed_ms`, `settled`, `country_code`.
  - `gateway_class` (`rfc1918_192`, `rfc1918_10`, `rfc1918_172`, `public`, `empty`, `other`), `ssid_present`, `bssid`, `if_type` (`wifi`/`eth`/`none`), `internet_ok`.
  - Failure: `casecode`, `httpcode_result`, `httpcode_errorcode`, `samessid`, `samebssid`, `tcp443` (tcp), `ping`, `connectStatus`, `dev_*` fields.
- EVIDENCE: observed (outline lines cited).
- UNKNOWNS: the event-channel endpoint (`LPEventTrack`) is not traced. The timing constants' values are not extracted. Full field lists need `LPEventTrack` and the dis.

---

## FEATURE: Network utilities (LPNetworkUtility)

- ENTRY: `LPUtility` forwards to `LPNetworkUtility` (`DEC\LPClientFramework\util\LPNetworkUtility.py:344`).
- MECHANISM:
  - `fetchNetworkInfo` (outline:378-405): gateway, interface, netmask, localIP, cached for 3 s. Windows uses `GetAdaptersAddresses` via `iphlpapi` (`.py:258-316`), preferring Wi-Fi then lowest ifIndex. Linux runs `ip route show default`. macOS uses SystemConfiguration.
  - `fetchLocalIP` (outline:504-510): UDP socket to `8.8.8.8`, returns `getsockname()`.
  - `pingGoogle` (outline:540-545): TCP connect to `8.8.8.8:53`.
  - `tcpProbeHost(ip, port=443, timeout)` (outline:534-538).
  - `icmpPingHost`: `ping -n 1 -w <ms>` (Windows), `-c` (Linux), `-t` (macOS) (outline:518-532).
  - SSID: Windows WLAN API (`wlanapi.dll`: `WlanOpenHandle`, `WlanEnumInterfaces`, `WlanQueryInterface` with opcode 7 (`.py:349-439`)), fallback `netsh wlan show interfaces` with 5 s timeout (outline:251-267). Linux `iwgetid -r`. macOS `scutil`/CoreWLAN.
  - `isIPInGateway` (outline:512-516): netmask subnet check.
- EVIDENCE: observed (`.py` and outline lines cited).
- UNKNOWNS: the Windows WLAN body after line 442 is cut. The macOS SSID caches are not traced in detail.

---

## Other command families seen (not traced beyond names)

- Device settings: `setWlanBandConfig:%d`, `setNetworkPreferDNS:%s`, `setWlanRoamConfig:%d`, `setIPV6Enable:%d`, `setPowerModeTime:{"idleInterval":"%d"}`, `setHexDeviceName:%s` and matching getters (`OUT\HOME\DeviceSetting\LPDeviceSettingDeviceViewController.dis.txt:1571-2486`).
- Voice: `getAlexaCountry`, `setAlexaCountry:%s`, `getAvsMusicHDEnable`, `setAvsMusicHDEnable:%d` (`LPDeviceSettingVoiceViewController.dis.txt:837-1567`).
- Bluetooth source: `getbtpairstatus`, `getbtdiscoveryresult`, `getbthistory` (`LPDeviceSettingBtSourceViewController.dis.txt:1709-2456`).
- Stream service: `getStreamServiceConfig:<source>` (GET) and `setStreamServiceConfig` (POST) (`DEC\HOME\StreamService\Qobuz\Login\LPQobuzLogoutDialog.py:128,148`).
- Account (UPnP): `LPUpnpAsyncDataModel.userLoginByCode` derives an AES key from `device.uuid[:16]` and calls `AESCipher.encrypt2` (`DEC\LPClientFramework\LPDataModel\UpnpDataModel\LPUpnpAsyncDataModel.py:46-48`). Its body is cut.

---

## UNKNOWNS (summary)

- The record-expiry threshold for SSDP (docstring 100 s; no matching constant found in dis).
- `refreshMultiroomState` callers and cadence; `init()` re-run cadence beyond discovery.
- Which port the UPnP SUBSCRIBE uses for SSDP-discovered devices (`upnpPort` from LOCATION is inferred).
- Whether the manual-add `uuid` and the SSDP 24-hex uuid are the same identifier.
- `tlsCmd` (port 8893) callers beyond `LPDevice.tlsCommand`.
- `httpGetBytes` callers (the `/data/sys.log` download path).
- Reply key names for all Sound and Device settings getters.
- The `validInterfaces` condition in `LPQTSSDPServer.py:32` and the `if None == ...` branches in `LPUPnPObserverManager.py:44-47` need dis confirmation.

---

## Not found: UI-named features in scope that could not be traced

- "Log download" button (no caller of `httpGetBytes` found in the decompiled tree).
- "Test audio" playback in the Sound settings (`_playTestAudioButtonClicked`, dis:4753-4895): the stream source was not traced.
- Device login by code (`LPUpnpAsyncDataModel`): body cut in pycdc, only the key derivation is visible.
- Send Feedback (`sendFeedbackRequested`): handled outside this scope.
- `LPDeviceSearchingViewController_ui` is generated layout only; its controller class is `LPDeviceSearchingViewController` at `DEC\HOME\WiiMHome.py:152`, traced for the QML entry only.

## Obstacles Encountered

- Truncated pycdc output in `LPDevice.py` (cut at 162), `LPDeviceDiscoverManager.py`, `LPUPnPObserverManager.py`, `LPCloudDeviceState.py`, `LPUpnpAsyncDataModel.py`, `LPNetworkUtility.py`, `LPQTSSDPServer.py`, `LPDeviceAudioInput.py` (`.err`). Dis used where needed.
- `LPDiscoveryTelemetry.py` is empty. Outline used.
- `LPDeviceAudioOutput.py` was complete.
- Path for the UpnpDataModel file: `LPClientFramework\LPDataModel\UpnpDataModel\LPUpnpAsyncDataModel.py` (the glob matched it).
- Two greps returned very large output. Output was saved under the session tool-results folder. No workspace file changed.
- Third-party packages (`zeroconf`, `requests`, `httpx`) were named only, not read.

## Side effects

- No file writes in the workspace. No git commands. No URLs fetched or contacted. No processes, servers, ports, packages or database rows touched.
- Harness-saved grep outputs exist under `C:\Users\AlexanderKastil\.claude\projects\D--git-projects-audio-star\8e097470-b398-46fa-bccf-3495bd60b6fa\tool-results\`.