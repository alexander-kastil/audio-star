**Task:** Reverse-engineer WiiM Home's multiroom groups, dashboard, and per-device settings, with the wire protocol for grouping and each setting. Read-only; nothing was written, launched, or fetched.

**Sources.** `OUT` = `D:\git-projects\audio-star\evidence\outline\` (`.dis.txt` is authoritative; `file:line` refers to it). `DEC` = `D:\git-projects\audio-star\evidence\decompiled\`. `QML` = `C:\Users\AlexanderKastil\AppData\Local\WiiMHome\Qml\`. The decompiled `.py` for LPGroup, LPDeviceGroupManager, LPDeviceNodeManager and LPGroupEditState is empty or garbled, so bytecode was used wherever they disagree. Tags: `obs` = observed at the cited line, `inf` = inferred from names or strings only.

**Common transport (obs `OUT\LPClientFramework\LPDevice.dis.txt`:5041-5099, 5420-5486):**
- GET `https://<ip>/httpapi.asp?command=<cmd>`, `verify=False`, timeout 15 s. The command is put in the URL unencoded.
- POST `https://<ip>/httpapi.asp`, form body `command=<cmd>:<json.dumps(payload)>`.
- TLS client cert comes from `LPTLSTool.twoNames()` (name only, value not printed).
- Result is a dict `{status_code, body}`; on exception `{status_code:-1, error}`.
- Success is `status_code == 200` in the group code.

**Common UPnP transport (obs `LPDevice.dis.txt`:4025-4395; `UPnPTool.dis.txt`:63-73; `UPnPTool.outline.txt`:20-28):**
- `LPDevice.upnpPost` adds `{"ControlSource":"WiiMApp"}`.
- For SetVolume and SetMute the base is `{"InstanceID":"0","Channel":"Master"}`, overridden by the caller's inParams.
- Endpoints: `http://<ip>:59152/upnp/control/rendercontrol1` (RenderingControl:1), `.../rendertransport1` (AVTransport:1, default), `.../PlayQueue1` (PlayQueue:1).
- SOAP SOAPACTION namespace is `urn:schemas-wiimu-com:service:` if service is `PlayQueue:1`, else `urn:schemas-upnp-org:service:`.

---

**FEATURE:** Named group create, activate, deactivate, edit, dissolve

**ENTRY:** `QML\DeviceDashboard\LPDeviceDashboard.qml:143` `controller.openEditGroupDialog(wrapper)`. `LPNewGroupEditDialog.qml:182-184` `prepareGroupEdit` / `prepareGroupEditWithWrapper`. `LPNewGroupEditDialog.qml:773` `editController.submitGroupEdit(selectedUuidList, selectedGroupId)`.

**MODULES:** HOME.DeviceDashboard.LPEditGroupDialogViewController; LPClientFramework.LPDeviceManager.LPGroupManager, LPDeviceGroupManager, LPGroup, LPGroupEditState, LPDeviceNodeManager; LPClientFramework.LPDevice (`saveNameGroupList`, `setCurrentNameGroup`, `getSlaveList`, `ungroup`, `refreshMultiroomState`).

**DATA:** No local files or settings keys. Group state lives in memory in `LPDeviceGroupObject` buckets, one per master device (`groupList`, `editGroupList`, `rawGroupList`, `rawEditGroupList`), and is persisted on the device by the commands below (obs `DEC\...\LPDeviceGroupManager.py:91-101`).

**MECHANISM:**
1. `LPEditGroupDialogViewController._submitGroupEdit` (obs `OUT\HOME\DeviceDashboard\LPEditGroupDialogViewController.dis.txt`:4583-4770) calls `getActiveGroupWithDevice`, `supportNewGroup`, then `LPGroupManager.editGroupResult`.
2. `editGroupResult` branches (obs `LPGroupManager.outline.txt`:132-150): `deactivateNamedGroup`, `noSelectedNoCurrentGroup`, `switchNamedGroup`, `singleSelected`, `createTempGroup`, `editTempGroup`.
3. Create: `operateGroup` then `LPDeviceGroupManager.addGroup`. The new group is inserted at index 0 of the master's bucket (inf `DEC\...\LPDeviceGroupManager.py:104-111, 436`). The full list is saved with `savenamegrouplist`. The bucket is then confirmed or rolled back on success (obs `LPDeviceGroupManager.dis.txt`:1868-1968).
4. Activate: `changeGroupActiveStatus` then `switchCurrentGroup(group, True)` (obs `LPGroupManager.dis.txt`:2437-2622).
5. Verify: `checkDeviceMultiResult` polls `multiroom:getSlaveList` and compares the uuid sets with the expected online slaves (obs `LPGroupManager.outline.txt`:196-207).
6. Edit: `LPDeviceGroupManager.updateGroup` then `deviceUpdateGroupObj` then `saveGroupList`, then `changeGroupActiveStatus` if needed (obs `LPGroupManager.outline.txt`:185-190; `LPDeviceGroupManager.outline.txt`:371-377).
7. Deactivate: `switchCurrentGroup(group, False)` sends `group_id:"-1"` (obs `LPGroupManager.dis.txt`:2470).
8. Dissolve whole group: `LPGroupManager.ungroup(master)` sends `multiroom:Ungroup` and checks 200 (obs `LPGroupManager.dis.txt`:2624-2690; `LPDevice.dis.txt`:7377-7398).
9. Single device leaves: `_dealSingleSelectedDevice` ungroups the master of a grouped device (with retry), then calls `checkDeviceMultiResult` on an empty group (obs `LPGroupManager.outline.txt`:287-303).

**PROTOCOL:**
- POST `multiroom:savenamegrouplist`, payload `{"grouplist":[<group>,...]}` (obs `LPDeviceGroupManager.dis.txt`:2061-2064; `LPDevice.dis.txt`:7261-7262).
- Group record, from `covertGroupObjToDictionary` (obs `LPDeviceGroupManager.dis.txt`:586-843): `group_name` (groupName), `fullName` (groupFullName, else groupName), `group_id`, `group_type` (normalized int, default), `update_time`, `channel` (int), `slavelist` of `{name, uuid, ipv4 (only when known)}`. Unknown keys from the device's own group dict are kept via deepcopy.
- POST `multiroom:setcurrentnamegroup` (obs `LPDevice.dis.txt`:7201-7203). Active payload (obs `LPGroupManager.dis.txt`:2464-2550): `{"group_id":"<id>","group_name":"<name or ''>","fullName":"<groupFullName or name or ''>","slavelist":[{"uuid":"<slave uuid>","ipv4":"<ip, optional>"}]}`. The master is not in slavelist. Inactive payload: `{"group_id":"-1"}`.
- GET `multiroom:getnamegrouplist` (obs `LPDevice.dis.txt`:7299-7302). Response keys seen as string constants (inf): `grouplist`, `group_id`, `group_name`, `fullName`, `full_name`, `groupFullName`, `group_type`, `channel`, `slavelist` (`LPDeviceGroupManager.outline.txt`:279-293).
- GET `multiroom:getSlaveList` (obs `LPDevice.dis.txt`:7338-7341). Response key `slave_list` (obs `LPGroupManager.outline.txt`:256).
- GET `multiroom:Ungroup` (obs `LPDevice.dis.txt`:7395-7398).
- Display name: `"<master name> +<n>"`, documented as e.g. `Living Room +2` (obs `LPGroupManager.outline.txt`:168). Truncated variant uses `...` (obs `LPGroupManager.outline.txt`:162-165).

**EVIDENCE:** Each step above is obs at the cited dis line, except step 3's insert-at-0 (inf, from `.py`) and the getnamegrouplist keys (inf, string constants).

**UNKNOWNS:**
- Timeout and retry count for `checkDeviceMultiResult` (not traced).
- Full getnamegrouplist response shape (`LPDeviceGroupManager.py` is garbled).
- No delete-named-group path found. Only `updateGroup`, `ungroup`, and the local `clearNameGroup` cache clear exist in the method lists.

---

**FEATURE:** Leader and follower model (roomState, masterID) and device push notifications

**ENTRY:** `LPDevice.refreshMultiroomState` (obs `LPDevice.dis.txt`:2980). Called after edits (obs `LPEditGroupDialogViewController.dis.txt`:4495). Push path: `LPDevice.dealLPMRM` (obs `LPDevice.dis.txt`:2550) and `LPDeviceNodeManager.deviceInfoUpdate` (inf `DEC\...\LPDeviceNodeManager.py:171-182`).

**MODULES:** LPClientFramework.LPDevice, LPDeviceNodeManager, LPGroupManager. LPDeviceGroupInfo.py is truncated to one method.

**DATA:** In-memory `LPDevice.groupInfo`: `roomState` (`master`|`slave`), `masterID`, `slaveList`, `groupName`, `groupTitle`, `currentGroupType` (obs `LPDevice.outline.txt`: `_applyMultiroomStatus`, `_applySlaveList`, `initGroupInfo`).

**MECHANISM:**
1. GET `getStatusEx`. If `statusDict['group'] == '1'` the room state is `slave`, otherwise `master`. The name comes from `statusDict['GroupName']` (obs `LPDevice.dis.txt`:2155-2172, 2174-2190).
2. GET `multiroom:getSlaveList`, parse `slave_list`, then `_applySlaveList` (obs `LPDevice.dis.txt`:3092-3093; `LPDevice.outline.txt`: `_applySlaveList`).
3. Push `multiroom` detail with `slaveAction` (`action` add or rm, `master`, `slaveId`) updates roomState and masterID locally (obs `LPDevice.dis.txt`:2503-2535; inf `LPDeviceNodeManager.py:112-168`).
4. Push `lpmrm`: `group_relationship_changed == '1'` triggers `readyGroupWithDevice`. A `group_id` triggers `updateGroupActive` (inf `LPDeviceNodeManager.py:185-214`).

**PROTOCOL:** `GET getStatusEx`; `GET multiroom:getSlaveList`; push keys `multiroom` > `slaveAction` / `lpmrm` (obs `LPDeviceDashboardViewController.dis.txt`:3230).

**EVIDENCE:** As tagged above.

**UNKNOWNS:** Source key for slave `masterID` (not traced past `LPDevice.dis.txt`:2199). Other `getStatusEx` keys.

---

**FEATURE:** Group volume, group mute, and per-member volume and mute (dashboard)

**ENTRY:** `QML\DeviceDashboard\LPDeviceVolumeSlider.qml:49-50` (`valueChanging`, `valueCommitted`). `LPGroupItemWrapper.setVolume`, `toggleMute`, `setMemberVolume`, `toggleMemberMute`. `LPDeviceItemWrapper.setVolume`, `mute`.

**MODULES:** HOME.DeviceDashboard.LPGroupItemWrapper, LPDeviceItemWrapper; LPClientFramework.LPDeviceManager.LPGroup (`LPGroupObject` volume/mute methods); LPClientFramework.LPDevice (`asyncUpnpPost`, `commonHttpGet`).

**MECHANISM:**
1. Group volume: throttled to one post per 0.15 s unless forced (obs `LPGroupItemWrapper.dis.txt`:957-963, 3188-3192). Calls `LPGroupObject.set_group_volume(value, member_rows, online_slave_list, resolver, post_to_device, force_post)` (obs `LPGroupItemWrapper.dis.txt`:3195-3220).
2. Inside `set_group_volume`: if the group is muted, members that are not fixed-volume get `SetMute 0` first (obs `LPGroup.dis.txt`:2199-2203). Each member whose volume changed, and is not fixed-volume, gets `SetVolume` (obs `LPGroup.dis.txt`:2614-2635, 2885-2894).
3. Group read: group mute is true only if every adjustable member is muted (obs `LPGroup.dis.txt`:411-423). Group volume is a rounded `max` over adjustable members (inf, names `max`, `round`; `LPGroup.dis.txt`:387-404).
4. Slave member volume: `_sendMemberVolumeOnly` then `_dispatchMemberVolumePost`. If the member's uuid differs from the master's, the master is present, and the slave IP is known, a background thread GETs `multiroom:SlaveVolume:<slave ip>:<int>` on the master. Otherwise it posts `SetVolume` to the member (obs `LPGroupItemWrapper.dis.txt`:2546-2738).
5. Member mute: `toggle_member_mute` posts `SetMute` to the member. Refused for stereo pairs (obs `LPGroup.dis.txt`:2799-2810).
6. Single device volume: rounds to int, posts `SetVolume`, then updates media info locally (obs `LPDeviceItemWrapper.dis.txt`:949-1019). Single device mute posts `SetMute` (obs `LPDeviceItemWrapper.dis.txt`:912-930).

**PROTOCOL:**
- UPnP `SetVolume` on member, inParams `{"Channel":"Single","DesiredVolume":"<int>"}` (obs `LPGroupItemWrapper.dis.txt`:2655-2663; `LPGroup.dis.txt`:2627-2635).
- UPnP `SetVolume` on single device, inParams `{"DesiredVolume":"<int>"}` only, so Channel is `Master` from base (obs `LPDeviceItemWrapper.dis.txt`:994-1002).
- UPnP `SetMute`, inParams `{"DesiredMute":"1"|"0"}` (obs `LPDeviceItemWrapper.dis.txt`:919-929; `LPGroup.dis.txt`:2199-2203, 2315-2317, 2800-2810).
- GET `https://<master ip>/httpapi.asp?command=multiroom:SlaveVolume:<slave_ip>:<int>` (obs `LPGroupItemWrapper.dis.txt`:2728-2740).

**EVIDENCE:** As tagged above.

**UNKNOWNS:** Slider-to-volume clamp (`handle_volume_limits` body not traced). Drag-snapshot logic in `QML\...\LPDeviceGroupItem.qml:125-211` is named only, not traced.

---

**FEATURE:** Device dashboard grid, play and pause all, cover images

**ENTRY:** `LPDeviceDashboardViewController.setupQmlDashboard` (obs `LPDeviceDashboardViewController.dis.txt`:2147). QML `LPDeviceDashboard.qml:89` `onAddDeviceButtonClicked`, `:119` `onPauseAllButtonPressed(checked)`. `LPDeviceGridView.qml:64-66` signals. `LPDeviceItem.qml:53-54`, `LPDeviceGroupItem.qml:116-118`.

**MODULES:** HOME.DeviceDashboard.LPDeviceDashboardViewController, LPDeviceListModel, LPDeviceItemWrapper, LPGroupItemWrapper, LPGroupMemberListModel, LPDeviceCoverImageHelper.

**MECHANISM:**
- Devices are classified into single devices and groups. Keys are `device:` and `group:` (obs `LPDeviceDashboardViewController.dis.txt`:716, 1574-1581). Sub-devices are skipped (obs same, :1834).
- Selection key format `group:<id>` / `<uuid>` (obs same, :2522-2528).
- Play all and pause all call `asyncUpnpPost('Play'|'Pause', None)` on each control device (obs same, :3307-3334).
- Cover: `LPDeviceItemWrapper._updateCoverImageAsync` uses `device.mediaInfo.artworkImage`. If null or empty, it uses `LPGlobalUI.defaultCoverPath(trackSource, 'mini', mediaType)`. Then rounds and converts for QML (obs `LPDeviceItemWrapper.dis.txt`:1372-1501).
- Cover canvas: `coverCanvasPixmap(pixmap, width, height, radius)` keeps aspect ratio, centres, and clips rounded corners (obs `LPDeviceCoverImageHelper.outline.txt`:16-18).
- Group card: default art `miniBar/trackDefault.png` (obs `LPGroupItemWrapper.dis.txt`:3957). Background colour from `getPalette` / `pixmapToPIL` (obs `LPGroupItemWrapper.dis.txt`:4244-4312).

**PROTOCOL:** Play and Pause are `asyncUpnpPost` with no inParams (obs `LPDeviceDashboardViewController.dis.txt`:3319-3328). Routing to a service is not traced (inf: the default AVTransport branch). No HTTP or UPnP call fetches the cover in these modules.

**UNKNOWNS:** How `mediaInfo.artworkImage` is fetched (set outside these modules).

---

**FEATURE:** Device info, rename, network, standby, factory reset (Device settings page)

**ENTRY:** `LPDeviceSettingDeviceViewController`: `_deviceNameButtonClicked` / `_setDeviceName` (obs `LPDeviceSettingDeviceViewController.dis.txt`:2024-2135); `_updateNetworkStatusSlot` (obs :810-1520); `standbyIndexChanged` (obs :1789-1851); `_factoryResetButtonClicked` (obs :2575-2682).

**MECHANISM:** Rename hex-encodes the text as UTF-8 (obs `...Device.dis.txt`:2121-2135). Network page first reads six values (obs :2285-2504), then each toggle writes. Factory reset confirms with the string `Restore Factory Settings` (obs :2600).

**PROTOCOL:**
- GET `setHexDeviceName:<utf-8 hex of name>` (obs :2134-2135).
- GET `getWlanBandConfig` / `setWlanBandConfig:%d` (5 GHz) (obs :1570-1571, 2321).
- GET `getNetworkPreferDNS` / `setNetworkPreferDNS:%s` (obs :1637-1638, 2357).
- GET `getWlanRoamConfig` / `setWlanRoamConfig:%d` (obs :1704-1705, 2404).
- GET `getIPV6Enable` / `setIPV6Enable:%d` (obs :1771-1772, 2444).
- GET `getPowerModeTime` / `setPowerModeTime:{"idleInterval":"%d"}` (obs :1851-1852, 2486). Unit strings `%s seconds`, `1 %s`, `%d %s` (obs :1380-1427).
- GET `restoreToDefault` (obs `LPDeviceSettingDeviceViewController.dis.txt`:2682-2683).
- Device info page: `requestData` makes no HTTP call (grep found none).

**UNKNOWNS:** Field source for the info page. Response parsing for the `getX` reads.

---

**FEATURE:** Sound settings (Sound page, includes Auto sync)

**ENTRY:** `LPDeviceSettingSoundViewController.requestData` (obs `LPDeviceSettingSoundViewController.dis.txt`:697). Reads: `_requestSyncAudioData` (771), `_requestAudioSettingsData` (862), `_requestOutputData` (1424), `_requestSubwooferData` (2241), `_requestInputData` (2353). Writes: lambdas inside each `_update*UI`.

**MECHANISM:** Each `_request*` issues GET `get<X>` and fills widgets. Each widget signal runs a lambda that GETs `set<X>:<args>`. No EQ, preset, or DSP command exists in this page. The only DSP-like commands are the DAC digital filter and the subwoofer LPF.

**PROTOCOL (all GET `commonHttpGet`; line refs are `LPDeviceSettingSoundViewController.dis.txt`):**

| Setting | Read | Write (args) |
|---|---|---|
| Volume limit | not in page | `setMaxVolume:%d` (4723) |
| Fixed volume toggle | not in page | `setVolumeControl:%d` (4589) |
| Aux out voltage | `getAuxVoltageSupportList` (910), `getOutputVoltage` (1061) | `setOutputVoltage:%d` (4660) |
| SPDIF out max cap | `getSpdifOutMaxCap` (1108) | `setSpdifOutMaxCap:%d:%d:%d` (4951, 5024, 5096) |
| Coax out max cap | `getCoaxOutMaxCap` (1186) | `setCoaxOutMaxCap:%d:%d:%d` (5314, 5387, 5459) |
| Channel mode | `getChannelMode` (1264) | `setChannelMode:%d` (5532) |
| Balance | `getChannelBalance` (1302) | `setChannelBalance:%.2f` (5597) |
| Crossfade | `GetFadeFeature` (1354) | `SetFadeFeature:%d` (5679) |
| Sound card output | `getSoundCardModeSupportList` (1449), `getActiveSoundCardOutputMode` (1571), `getNewAudioOutputHardwareMode` (1711) | `setSoundCardOutputMode:%s:%s` (6810-6811), `setAudioOutputHardwareMode:%s:%s` (6823-6837) |
| SPDIF switch latency | `getSpdifOutSwitchDelayMs` (1993) | `setSpdifOutSwitchDelayMs:%d` (6910) |
| DAC digital filter | `getDigitalFilterTypeSupportList` (2124), `getDigitalFilterType` (2185) | `setDigitalFilterType:%d` (6995) |
| Subwoofer | `getSubLPF` (2260) | `setSubLPF:status:%d` (7749), `setSubLPF:level:%d` (7816), `setSubLPF:cross:%d` (7896), `setSubLPF:phase:%d` (7982), `setSubLPF:sub_delay:%d` (8045). Speaker delay also uses `setSubLPF:sub_delay:%d` (8126), same string |
| Aux in auto sense | `getAuxAutoSenseEnable` (2434) | `setAuxAutoSenseEnable:%d` (9212) |
| SPDIF auto sense | `getSpdifAutoSenseEnable` (2483) | `setSpdifAutoSenseEnable:%d` (9348) |
| Aux in max cap | `getAuxInMaxCap` (2528) | `setAuxInMaxCap:%d:%d` (9420, 9491) |
| Per-source volume | `getPlayModeVolumeEnable` (2590) | `setPlayModeVolumeEnable:%d` (9561) |
| CEC | `getCecPowerCtrl` (2654) | `setCecPowerCtrl:%d` (9632) |
| Input switch | not in page | `setPlayerCmd:switchmode:%s` (9142) |
| Phono type | not in page | `PHONO_MODE_SWITCH_SET:%d` (9279) |
| Auto sync (sync delay) | `GetSyncPlayExtraDelay` (790, 9973) | `SetSyncPlayExtraDelay:%d` (10123) |

Auto sync start (obs `LPDeviceSettingSoundViewController.dis.txt`:9956-9975): `upnpPost('AirplayAutoSyncDelay', {"Name":"Start"})`, sleep 10 s, then GET `GetSyncPlayExtraDelay`. The dialog text `Audio path latency: %d` is at `LPDeviceSettingAutoSyncViewController.dis.txt:389`.

Test tone (obs :4815, 5176): `https://app-resource.linkplay.com/music/July-MySoul_%s_%s.flac`.

**UNKNOWNS:** Widget-index-to-value tables (only format strings are visible). Meaning of `GNOTIFY=KeyEvent` (obs :6832). Response parsing.

---

**FEATURE:** Hardware settings

**ENTRY:** `LPDeviceSettingHardwareViewController.requestData._asyncUpdate` (obs `LPDeviceSettingHardwareViewController.dis.txt`:274-458) and `_updateHardwareSlot` (obs :651-1380).

**PROTOCOL:**
- Reads (GET): `LED_SWITCH_GET` (311), `VOL_LED_SWITCH_GET` (353), `Button_Enable_GET` (396), `Reload_Button_GET` (440).
- Writes (GET): `LED_SWITCH_SET:%d` (1112), `VOL_LED_SWITCH_SET:%d` (1179), `Button_Enable_SET:%d` (1246), `Reload_Button_UPDATE:%s` (1380).
- Reboot (GET): `StartRebootTime:1` (609).
- Status-light read is gated on `deviceSetting.supportStatusLight()` (obs :303-307).

**UNKNOWNS:** Response parsing.

---

**FEATURE:** Bluetooth source (history, connect, discovery, pairing)

**ENTRY:** `LPDeviceSettingBtSourceViewController.viewWillAppear`, `historyClicked`, `discoveryClicked`, `connectBlueTooth`, `startBlueToothDiscovery` (obs `LPDeviceSettingBtSourceViewController.dis.txt`:1067-2645).

**PROTOCOL (GET):**
- `getbthistory` (2456)
- `delbthistory:%s` (1502), forget
- `connectbta2dpsynk:%s` (1927)
- `disconnectbta2dpsynk:%s` (1363)
- `getbtpairstatus` (1709), polled; log `getbtpairstatus %d` (1799)
- `startbtdiscovery:%d` (2361)
- `getbtdiscoveryresult` (2099), polled; log `bt discovery: %s` (2290)

**UNKNOWNS:** `%d` value for start discovery. Stop discovery sends no constant that was found (`LPDeviceSettingBtSourceViewController.dis.txt`:2396-2413). Pair status response shape.

---

**FEATURE:** Voice assistant (Alexa)

**ENTRY:** `LPDeviceSettingVoiceViewController.requestData._asyncUpdate` (obs `LPDeviceSettingVoiceViewController.dis.txt`:806-1011); `avsLanChange` (obs :1328-1575).

**PROTOCOL (GET):**
- Reads: `getAlexaCountry` (837), `alexaGetLanguage` (874), `getAvsMusicHDEnable` (991); parse token `AvsMusicHDEnable:` (1011).
- Writes: `setAvsMusicHDEnable:%d` (1311), `setAlexaCountry:%s` (1567), `alexaSetLanguage:%s` (1575).
- Language-change confirmation text: `Would you like to change your device language to %s?` (1404).

---

**FEATURE:** AP cast (DLNA out, WiiM Cast, AirPlay speakers)

**ENTRY:** `LPDeviceSettingApCastViewController.connectAp`, `enterPassword`, `disconnectAp`, `getApList` (obs `LPDeviceSettingApCastViewController.dis.txt`:607-1209).

**PROTOCOL (GET):**
- `audio_cast:get_speaker_list` (1141)
- `audio_cast:speaker_enable:%s` (689)
- `audio_cast:speaker_set_password:%s:%s` (882). Speaker id and password are user-supplied secrets, not printed here.
- `audio_cast:speaker_disable:%s` (1007)

Titles: `%s - DLNA Out`, `%s - WiiM Cast` (obs :409, 449).

---

**FEATURE:** Music transfer on group change

**ENTRY:** `LPGroupManager.changeMusicFromDevice` (obs `LPGroupManager.dis.txt`:3008-3028) to `_transferMusic` (obs :3029-3148). Gated by `canChangeMusic` (obs `LPGroupManager.dis.txt`:2966).

**MECHANISM:** `upnpPost('BrowseQueue', {"QueueName":"CurrentQueue"})` on the source gets `musicList`. Then `toDevice.fastPlay(list, cb)`, waiting up to 20 s (obs :3040-3104). Unsupported source types: LINEIN, BLUETOOTH, EXTERNAL_USB, USB_DAC, EXTERNAL_TF, OPTICAL, OPTICAL2, AIRPLAY, CO_AXIAL, CO_AXIAL2, HDMI, PHONO (obs `DEC\...\LPGroupManager.py:23-35`).

**UNKNOWNS:** Which PlayQueue route `BrowseQueue` uses (inf only).

---

**Not traced, in scope:**
- Artwork fetch behind `mediaInfo.artworkImage`
- Delete named group (no path found)
- Equalizer, presets, DSP (only digital filter and subwoofer LPF exist)
- Device info page field source
- Hardware and device `getX` response parsing
- Stop Bluetooth discovery command

**Side effects:** None. No file writes, no network, no processes started. The grep tool persisted some large results under the session `tool-results` folder (harness storage, not the project).