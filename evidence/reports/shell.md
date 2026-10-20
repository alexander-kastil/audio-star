**Task:** Reverse-engineering read of WiiM Home's application shell and infrastructure (startup, single instance, UI shell, config, updates, feedback, analytics, crash handling, hibernation, AES helper, localisation), per the report contract. Read-only.

**Questions:**
1. How does startup run, and how do Widgets and QML connect?
2. Single-instance and `wiim://` URI handling?
3. Menus, tray, title bar, sidebar, toasts?
4. Config, feature flags, user config keys?
5. Auto-update (WinSparkle, feed URLs, speaker OTA)?
6. Feedback and log upload (STS, S3, SigV4, Lkp1)?
7. Analytics endpoints and payload?
8. Crash handling, hibernation, `util/aes`, localisation?

## Facts

**FEATURE: Application startup (main.py to setupUI to event loop)**
- ENTRY: `__main_script__` (`main.py`), run by the frozen exe.
- MODULES: `__main_script__`, `LPClientFramework.util.LPNativeCrashHandler`, `HOME.LPApplication`, `HOME.WiiMHome`, `LPClientFramework.LPSingletonAppManager`, `LPClientFramework.util.LPUriHandler`, `LPClientFramework.util.LPExceptionHandler`, `LPClientFramework.util.LPCrashDumper`, `LPClientFramework.LPUtility`, `LPGlobalUI`.
- DATA: `crash_faulthandler.log` opened in append mode under the crash dir returned by `LPNativeCrashHandler.get_crash_dir` (observed `D:\git-projects\audio-star\evidence\decompiled\__main_script__.py:11-15`).
- MECHANISM:
  1. Module import installs the native crash handler, enables `faulthandler` to the crash log, and optionally imports `resources.app_rc` (prints on failure) (observed `...\outline\__main_script__.dis.txt:100-126`).
  2. Imports pull in `LPUtility`, which reads `%s/config.json` from `appLocalDataPath()`, creates `userDataDir`, `cacheCoverDir`, and the logger (observed `...\outline\LPClientFramework\LPUtility.outline.txt:39`; `LPUtility.py:53-56`, `:270-277`).
  3. `__main__` sets `sys.excepthook = LPExceptionHandler.globalHandler` after `configureCrashDumper(LPCrashDumper(cacheDir/'crash', appVersion, bundleId))` (observed `...\__main_script__.dis.txt:292-324`).
  4. `main()` sets env `QT_QUICK_CONTROLS_STYLE=Fusion` and `QSG_RHI_BACKEND=opengl`, creates `LPApplication.get([])`, and installs the Windows or macOS Qt fatal handler (observed `...\__main_script__.dis.txt:206-261`).
  5. On Darwin, `setQuitOnLastWindowClosed(False)` (observed `...:263-274`).
  6. On Windows only, `argv[1]` is the URI and `LPSingletonAppManager` is consulted (see next block). Non-Windows skips the singleton and calls `setupUI(app)` then `sys.exit(app.exec())` (observed `...:276-352`).
  7. `HOME.WiiMHome.setupUI(app)`: sets font (`getStartupApplicationFont`, normal weight, `DEFAULT` point size), calls `LPGlobalUI.changeLocalize('en')`, sets app name `WiiM Home` and version `LPUtility.appVersion`, then `rootUI = LPGlobalUI.loadUI(LPUIPath.WiiMHomeUI, Ui_MainWindow, LPStreamServiceMainWindow)` and `LPGlobalUI.mainWindow = rootUI` (observed `...\outline\HOME\WiiMHome.dis.txt:11432-11508`).
  8. `setupUI` restores geometry from `QSettings('Linkplay','WiiMHome')` key `main/geometry`; if absent, sizes to 65% of primary screen width, and if that is below 1200 px resizes to width x 3/4 and centres (observed `WiiMHome.dis.txt:11521-11553`).
  9. `rootUI.start()`, then `show()`, then a zero-delay single-shot resets `_last_mask_size` and calls `updateWindowMask()` (observed `WiiMHome.dis.txt:11614-11628`).
  10. `LPStreamServiceMainWindow.__init__` builds the device manager, sidebar and page controllers, tray, menu bar, play view, OTA telemetry, update coordinator, the searching view, beets init, image cache and notification observers (names only, observed `...\outline\HOME\WiiMHome.outline.txt:433-441`).
- PROTOCOL: none directly. Local ports from `LPUtility.py:106-108`: media 22345, UPnP 22346, OAuth 22347.
- EVIDENCE: as tagged above (observed unless noted).
- UNKNOWNS: `LPNativeCrashHandler` body (not read). Where the `LPSingletonAppManager` key default is set beyond the constant (see next block).

**FEATURE: Single instance and wiim:// URI handling**
- ENTRY: `main()` on Windows (`__main_script__`); `LPApplication.event` for macOS FileOpen.
- MODULES: `LPClientFramework.LPSingletonAppManager`, `LPClientFramework.util.LPUriHandler`, `HOME.LPApplication`.
- DATA: none on disk. Local server name is the constant `'wiim_singleton!#@'` (observed `...\outline\LPClientFramework\LPSingletonAppManager.outline.txt:15`).
- MECHANISM:
  1. Second instance: `QLocalSocket.connectToServer(key)`; if it connects, it sends `argv[1]` or `wiim://showApp`, then `sys.exit(0)` (observed `LPSingletonAppManager.py:26-35`, `:71-85`; `__main_script__.dis.txt:298-318`).
  2. First instance: `QLocalServer` with `WorldAccessOption`. Each new connection's text is emitted as `messageReceived`, connected to `LPUriHandler.handlerUri` (observed `LPSingletonAppManager.py:38-68`; `__main_script__.dis.txt:320-331`).
  3. `handlerUri` routes: `com.linkplay.wiimhome://callback` and `wiim://callback` to OAuth; `wiim://active` to activeWindow; `wiim://showApp` to showApp (observed `...\decompiled\LPClientFramework\util\LPUriHandler.py:23-59`).
  4. OAuth callback reads `service`, `code`, `state` (query), maps `service` (`tidal`), and posts `OAuthCodeChanged` (observed `LPUriHandler.py:61-95`, `:113-124`).
  5. `LPOAuthHttpServer` serves an HTML page that links to `wiim://active` after 1 s (observed `...\decompiled\LPClientFramework\LPOAuthHttpServer.py:77`).
- PROTOCOL: local QLocalServer/QLocalSocket only; OAuth via the loopback HTTP server on port 22347 (observed `LPUtility.py:108`).
- EVIDENCE: observed as tagged. No network.
- UNKNOWNS: how the OAuth browser flow is started (the auth host is named in the docstring only).

**FEATURE: Main window, tray, menus, title bar, sidebar, toasts**
- ENTRY: `LPStreamServiceMainWindow` (QMainWindow loaded by `LPGlobalUI.loadUI`).
- MODULES: `HOME.WiiMHome`, `HOME.Menu.LPTrayMenuController`, `HOME.Menu.LPMenuBarController`, `HOME.Menu.LPSearchMoreMenuController`, `HOME.SideBar.*`, `LPGlobalUI`.
- DATA: `QSettings('Linkplay','WiiMHome')` key `main/geometry` (observed `WiiMHome.outline.txt:527-531`). Tray icons `tray_ico.png` (Darwin) and `app.ico` (observed `...\outline\HOME\Menu\LPTrayMenuController.outline.txt:29-30`).
- MECHANISM:
  - Frameless window with four side grips and corner grips; macOS rounds corners via `updateWindowMask` (observed `WiiMHome.outline.txt:107-130`, `:415`).
  - Tray: `LPTrayMenuController(owner, onShow, onQuit)`; menu items `Open WiiM` and `Quit`; Windows tray click handled in `onTrayActivated` (observed `LPTrayMenuController.outline.txt:17-38`).
  - Close and minimise: `closeEvent` logs, stops library/SSDP/cherrypy threads and saves geometry; `hide` saves geometry; `showApp` restores maximised or normal state and raises (observed `WiiMHome.outline.txt:517-547`).
  - Quit: `quitApp` runs on WinSparkle shutdown request; a watchdog thread force-kills the process after a timeout (observed `WiiMHome.outline.txt:563-577`).
  - Device-searching title bar: QML buttons call `_closeWindowFromQml` (which hides if `enableMemoryResident`, otherwise quits), `_minimizeWindowFromQml`, `_maximizeWindowFromQml`, `_fullscreenFromQml`, `_startWindowMoveFromQml` (observed `WiiMHome.outline.txt:277-296`).
  - Sidebar: scroll bar auto-hide (`setSideScrollBar`, `_onSideBarScroll`, `_hideSideBarScrollBar`); side controllers Browse, CurrentDevice, MusicService, More, MyLibrary built in `__init__` (observed `WiiMHome.outline.txt:346-348`, `:434`).
  - Toasts: `LPGlobalUI.Toast.showToast(text, parent, timeout)`, anchored to a parent widget (observed `...\outline\LPGlobalUI.outline.txt:335-360`).
- PROTOCOL: none.
- EVIDENCE: observed as tagged. Menu item lists for `LPMenuBarController` and `LPSearchMoreMenuController` not read.
- UNKNOWNS: `LPTitleBar`, `LPToaster`, `LPAboutViewController`, `LPMenuBridge` (decompile `.err`), sidebar handlers (`updateSideBar`, `streamServiceSelectMethod`) not read.

**FEATURE: Widgets to QML bridge**
- ENTRY: `LPGlobalUI.qmlPath(...)` and each controller's `quick.setSource(...)`.
- MODULES: `LPGlobalUI`, `LPClientFramework.LPConfig.LPUIPath`, `HOME.Feedback.LPFeedbackDialogViewController`, `HOME.DeviceDashboard.LPDeviceDashboardViewController`, `HOME.StreamService.WiiMRadio.LPWiiMRadioHomeViewController`, `HOME.LPDeviceSearchingViewController_ui` (inside WiiMHome).
- DATA: QML under `C:\Users\AlexanderKastil\AppData\Local\WiiMHome\Qml\`; `LPGlobalUI.qmlPath` returns `qrc:/qml/<rel>` (observed `...\outline\LPGlobalUI.outline.txt:326-327`). `LPConfirmDialogHost` loads a local file if present, else `qrc:/qml/common/LPConfirmDialog.qml` (observed `...\decompiled\LPCommonWidgets\dialog\LPConfirmDialogHost.py:44-46`).
- MECHANISM:
  - Python owns `QQuickWidget`s inside Widgets pages.
  - Objects are exposed by `quick.rootContext().setContextProperty(name, obj)`: Feedback dialog exposes `controller` (`LPFeedbackDialogViewController.py:108-111`); device dashboard exposes `deviceModel`, `rawDeviceModel`, `groupModel`, `controller`, `groupEditController` (`LPDeviceDashboardViewController.py:395-402`); WiiM Radio exposes `*State`, `*Actions`, `*Controller` (`LPWiiMRadioHomeViewController.py:278-281`).
  - Theme colours and fonts are passed as context properties.
  - QML to Python is by signals and slots: `_bindQmlSearchingSignals` connects `connectByIpRequested`, `sendFeedbackRequested`, `closeWindowRequested`, `minimizeWindowRequested`, `maximizeWindowRequested`, `fullscreenRequested`, `startWindowMoveRequested` (observed `WiiMHome.outline.txt:251-275`).
  - No `qmlRegisterType` call was found in the decompiled files.
- PROTOCOL: none.
- EVIDENCE: observed as tagged.
- UNKNOWNS: whether the on-disk `Qml\` folder or the compiled `qrc` bundle is used at runtime when both exist.

**FEATURE: Configuration, feature flags, user config**
- ENTRY: read at import (`LPUtility`, `LPFeaturesManager`, `LPUIConfig`).
- MODULES: `LPClientFramework.LPUtility`, `LPClientFramework.LPFeature.LPFeaturesManager`, `LPClientFramework.LPConfig.LPUIConfig`, `LPClientFramework.LPConfig.LPAppFeatureConfig`.
- DATA:
  - `data\config.json` (observed): `version` 0.2.10.5, `release` "2026-10-10 15:20:38", `sparkle.enabled` true, `sparkle.auto_check` false, `sparkle.feed.stable.{arm64,x86_64,windows_x64}` (beta appcast URLs).
  - `data\feature.yml` (observed): `QUEUE_MOVE_DELETE` with `min_version` "1.4", `max_version` null, `condition` true, `enabled` true.
  - `data\win-uiconfig.yml` (observed keys): `common.font`, `sidebar.{font,musicService,devices}`, `stackedWidget`, `dialog.loginDialog`.
  - `data\mac-uiconfig.yml` (not read).
  - `data\en.qm`, `zh.qm` (compiled translations), `en.ts`, `zh.ts`, `LPUPnPServer.xml`, `LPContentDirectory.xml`, `LPSupportedStreamServiceConfig.json`, `beets-config.yaml`, font files.
  - `C:\Users\AlexanderKastil\AppData\Local\com.linkplay.wiimhome\wiimhome-userconfig.json` (path `LPUtility.py:278`; `userDataDir` from AppConfigLocation plus bundle id, `LPUtility.py:270`). Top-level and nested key names found by pattern match (nesting not resolved): `mymusic-dir`, `pcId`, `pcName`, `userConfig`, `upnpserver`, `enable`, `name`, `lastUpdate`, `otaSession`. Inferred from names: `preventSleepEnable` (set from `LPMyMusicSettingViewController`).
- MECHANISM:
  - `isEnabled(featureName, currentVersion, customConditionMethod)` loads `feature.yml` with `yaml.safe_load` and checks `enabled`, `min_version`/`max_version` via `distutils.LooseVersion`, then `condition` (observed `LPFeaturesManager.py:19-51`).
  - `isWiiMRadioEnabled()` is the only named app-level feature switch in `LPAppFeatureConfig` (observed `...\outline\LPClientFramework\LPConfig\LPAppFeatureConfig.outline.txt:5-9`).
  - `LPUIConfig` loads `mac-uiconfig.yml` on Darwin, else `win-uiconfig.yml` (observed `LPUIConfig.py:13-17`).
  - `userConfig` helpers: `_loadUserConfigSafely`, `_saveUserConfigSafely`, rebuild on corruption (`load user config failed, rebuild config file`) (observed `LPUtility.outline.txt:257-275`).
- PROTOCOL: none.
- EVIDENCE: observed as tagged.
- UNKNOWNS: `win-uiconfig.yml` value semantics. `QUEUE_MOVE_DELETE` consumer not traced.

**FEATURE: Auto-update (WinSparkle, appcast, hidden beta, OTA telemetry)**
- ENTRY: `LPStreamServiceMainWindow.__init__` creates `LPUpdateFlowCoordinator` and `sparkleTimer`; manual check from menu (`manual_menu`); startup and periodic timers (observed `WiiMHome.outline.txt:434`, `WiiMHome.dis.txt:6085`, `LPUpdateCoordinator.outline.txt:892-897`).
- MODULES: `LPClientFramework.LPWinSparkleUpdater`, `LPClientFramework.LPMacSparkleUpdater`, `LPClientFramework.LPUpdateCoordinator` (`LPUpdateFlowCoordinator`, `LPOTATelemetryTracker`), `LPClientFramework.LPEventTrack`.
- DATA: `WinSparkle.dll` from `WIIM_WINSPARKLE_DLL_PATH`, else `_MEIPASS\WinSparkle.dll`, else `HOME\third_party\winsparkle\win-x64` (observed `LPWinSparkleUpdater.outline.txt:110-116`). OTA session in userconfig key `otaSession` via `readOTASession`/`writeOTASession`/`clearOTASession` (observed `LPUtility.outline.txt:119-121`).
- MECHANISM:
  - WinSparkle init (Windows only, if `sparkle.enabled`): `win_sparkle_set_appcast_url(resolveFeedURL())`, app details `Linkplay` / `WiiM Home`, overrides `automatic checks = False`, `update check interval = 7200 s`, `lang = en`, then `win_sparkle_init` (observed `LPWinSparkleUpdater.outline.txt:375-391`).
  - Callbacks: can-shutdown, shutdown-request, did-find-update, did-not-find-update, error, user-run-installer (download-complete signal) (observed `LPWinSparkleUpdater.outline.txt:121-131`, `:138-221`).
  - Shutdown-request path: `_onWinSparkleShutdownRequest` marks install started, emits a main-thread signal, then `quitApp`; watchdog force-kills after the timeout (observed `WiiMHome.outline.txt:553-577`).
  - Background probe: Python `urllib` fetch of the appcast with User-Agent `WiiM Home WinSparkle Probe` and parse of `<item>`, `enclosure`, `sparkle:shortVersionString` / `sparkle:version` (namespace `http://www.andymatuschak.org/xml-namespaces/sparkle`) (observed `LPWinSparkleUpdater.outline.txt:296-311`).
  - Hidden beta: `triggerHiddenBetaCheck(triggerSource)` switches the process-only feed to a beta appcast, with cooldown and lock timeout. Trigger source `friendly_name_hidden_tap`. Caller is `LPMyMusicSettingViewController` (tap count and window attributes `_hiddenBetaTapThreshold`, `_hiddenBetaTapWindowSeconds`). On success the UI shows `Enter Beta Mode!` (observed `LPUpdateCoordinator.outline.txt:729-737`, `:899-932`; `LPMyMusicSettingViewController.outline.txt:49`).
  - OTA telemetry: events `ota_check_started`, `ota_check_result`, `ota_update_started`, `ota_download_result`, `ota_install_started`, `ota_final_result`; enums for stage, category, code (observed `LPUpdateCoordinator.outline.txt:22-74`). Sent via `LPEventTrack.logEvent` with event name `ota` (see analytics).
- PROTOCOL:
  - Stable config feeds (`config.json`): `https://assets.wiimhome.com/appexe/beta/appcast-win-x86_64.xml`, `.../appcast-mac-arm64.xml`, `.../appcast-mac-x86_64.xml` (observed `config.json:9-11`).
  - Hidden-beta feeds (module constants `_HIDDEN_BETA_FEED_MAC_ARM64`, `_MAC_X86_64`, `_WIN_X64`): `https://assets.wiimhome.com/appexe/beta/appcast-beta-{mac-arm64,mac-x86_64,win-x86_64}.xml` (observed `LPUpdateCoordinator.outline.txt:9-11`, `:761`).
  - WinSparkle feed (`resolveFeedURL`, hard-coded, returns the only value used by init): `https://assets.wiimhome.com/appexe/appcast-beta-win-x86_64.xml` (observed `LPWinSparkleUpdater.outline.txt:351`).
  - macOS feed constants: `https://assets.wiimhome.com/appexe/appcast-beta-mac-{x86_64,arm64}.xml` (observed `LPMacSparkleUpdater.outline.txt:277-278`).
- EVIDENCE: observed as tagged. Inferred (names only): `config.json` feed entries are not read by the WinSparkle feed path, because `resolveFeedURL` names contain no config lookup (`LPWinSparkleUpdater.outline.txt:348-351`).
- UNKNOWNS:
  - Three different appcast path layouts exist (`beta/appcast-win-...`, `beta/appcast-beta-win-...`, `appcast-beta-win-...`). Only the hard-coded WinSparkle one reaches WinSparkle; which applies to the hidden-beta path is not resolved beyond the constant names.
  - Speaker firmware OTA: no speaker firmware-update command was located in scope. `LPDiscoveryTelemetry` names a device-state field `dev_ota_status` (`...\outline\LPClientFramework\LPDiscoveryTelemetry.outline.txt:155`); its request is not traced.
  - Periodic interval value (`_SPARKLE_FIXED_INTERVAL_MS`) and hidden-beta cooldown and lock values are not in the outline strings.

**FEATURE: Feedback and log upload**
- ENTRY: `HOME.Feedback.LPFeedbackDialogViewController` (QML `Qml\Feedback\LPFeedbackDialog.qml`), opened from `WiiMHome._openFeedbackDialogFromSideBar` and `LPDeviceSearchingViewController._openFeedbackDialogFromQml` (observed `WiiMHome.outline.txt:309-316`, `:407`).
- MODULES: `LPClientFramework.LPFeedback.*` (`LPFeedbackManager`, `LPFeedbackApiClient`, `LPFeedbackStsClient`, `LPLkp1Signer`, `LPFeedbackS3Uploader`, `LPSigV4Signer`, `LPFeedbackLogPackager`, `LPFirmwareLogCollector`, `LPFeedbackDraftStore`, `LPFeedbackPreferences`, `LPFeedbackEventTrack`, `LPFeedbackModels`, `LPFeedbackConfig`), `LPClientFramework.util.aes` (not used here).
- DATA:
  - Work directories `userDataDir\Feedback\state` and `userDataDir\Feedback\work` (observed `LPFeedbackManager.py:89-103`).
  - Per-submission firmware logs `<logDir>\firmware\<submissionId>` (observed `LPFeedbackManager.py:373-387`).
  - Output `feedback.zip` (observed `LPFeedbackLogPackager.outline.txt:51`).
  - QSettings keys `feedback/email`, `feedback/draft/subject`, `feedback/draft/email`, `feedback/draft/description`, `feedback/draft/attachmentPaths`, `feedback/draft/updatedAt` (observed `LPFeedbackPreferences.py:8`, `LPFeedbackDraftStore.outline.txt:12-16`). Attachment copies in `feedback_draft_attachments` (observed `LPFeedbackDraftStore.outline.txt:11`).
  - Constants held in `LPFeedbackConfig.py:10-16`: `FRESHDESK_APP_ID`, `FRESHDESK_ACCESS_KEY`, `FRESHDESK_SECRET_KEY` (Freshdesk app credentials, identical to the three values in `LPEventTrack.py:49-51`), `FEEDBACK_AES_KEY` (16-byte AES key). Values not reproduced.
  - `FEEDBACK_DEFAULT_RECEIVER` names the default ticket receiver (`LPFeedbackConfig.py:18`).
- MECHANISM (`LPFeedbackManager.submit`, one independent thread and 15 s UI-unlock timer per submit):
  1. `creating_ticket`: Freshdesk create ticket, up to 3 attempts (observed `LPFeedbackManager.py:61-62`, `:238-251`).
  2. `collecting_firmware_logs`: for each discovered speaker, send `getsyslog` (or `getsyslog:ip:<slaveIp>` for offline slaves), wait 3 s (master or online slave) or 6 s (offline slave), then download `http://<ip>/data/sys.log` to `master-<name>-<ts>.log` or `slave-<master>-<slave>-<ts>.log` (observed `LPFirmwareLogCollector.outline.txt:29-40`; docstring `LPFirmwareLogCollector.py:4-11`, `:70-85`).
  3. `packing_logs`: copy app logs (newest first, max 20 files, max 7 days, max 20 MiB total), max 5 JPEG attachments (plain), firmware logs (plain); `.log` files are encrypted with AES-128-ECB PKCS7 with `FEEDBACK_AES_KEY` into an `AES` subfolder; then ZIP-deflate to `feedback.zip` (observed `LPFeedbackLogPackager.py:26-30`, `:49-63`, `:150-189`, `:192-209`).
  4. `requesting_sts`: POST to STS, retrieve temporary S3 credentials (up to 3 attempts, 20 s timeout) (observed `LPFeedbackStsClient.py:226-258`).
  5. `uploading_s3`: SigV4-signed PUT of the ZIP, 60 s timeout, up to 3 attempts (observed `LPFeedbackS3Uploader.py:25-52`; `LPFeedbackManager.py:255-268`).
  6. `updating_ticket`: Freshdesk PUT with the S3 download link and confirmation (observed `LPFeedbackApiClient.outline.txt:50-62`).
  - Timeout (15 s): UI shows success, pipeline continues in background (observed `LPFeedbackManager.py:61`, `:345-370`).
  - Subject over 200 chars is moved to description (observed `LPFeedbackManager.py:222-235`).
- PROTOCOL:
  - Freshdesk: base `https://freshdesk.linkplay.com/apiv1/freshdesk/wiim` (`FRESHDESK_API_HOST`, `LPFeedbackConfig.py:8`); `POST /tickets`, `PUT /tickets/%s` (observed `LPFeedbackApiClient.outline.txt:44`, `:62`). Auth via `LPAuthenticatedRequestClient`, same algorithm as the event tracker (observed `LPEventTrack.outline.txt:225`; inferred from that docstring).
  - STS: `POST https://api.linkplay.com/datav3/log/feedbackUpload` (`STS_ENDPOINT`, `LPFeedbackConfig.py:13`). Headers: `Content-Type: application/json`, `Authorization`, `X-Linkplay-Date`, `X-Linkplay-Uuid`, `X-Linkplay-Project`, `X-Linkplay-Origin`, `X-Linkplay-Content` (observed `LPLkp1Signer.outline.txt:29-35`). Body keys: `osType` "pc", `logType` "custom_feedback", `uuid` "unknow" (literal), `project` "WiiMHome", `formatVersion` "3", `confirmationID`, `ticketId` "-1", `logItem` (JSON string), `actionType` "feedback", `emailMetadata` (JSON string with base64 `message`, `subject`, `receivers`), `FILE_PATH`, `sdkVersion` (observed `LPFeedbackStsClient.py:240-252`, `:155-158`).
  - Lkp1 signature: `LKP1-HMAC-SHA256 Credential=linkplay/<scope>, SignedHeaders=host;x-linkplay-date;x-linkplay-origin;x-linkplay-project;x-linkplay-uuid, Signature=<hex>`. Signing key is an HMAC chain seeded from `'LKP1'+uuid` through date, origin, project, then `linkplay_request` (observed `LPLkp1Signer.py:55-86`). STS origin `pc`, project `WiiMHome` (`LPFeedbackConfig.py:14-15`).
  - STS response fields: `accessKey`, `secretKey`, `sessionToken`, `bucketName`, `bucketRegion`, `fileKey` (observed `LPFeedbackModels.outline.txt:72-75`).
  - S3: `PUT https://{bucketName}.s3.{bucketRegion}.amazonaws.com/{fileKey}`, `Content-Type: application/zip`, SigV4 with service `s3` and session token (observed `LPFeedbackS3Uploader.py:41-51`).
- EVIDENCE: observed as tagged. Inferred: `sessionToken` placed as `X-Amz-Security-Token` (names only).
- UNKNOWNS:
  - `LPFeedbackStsClient.py:23` (`_toBase64`) and `_buildEmailSubject`/`_buildLogItem` are pycdc placeholders (for example `''.encode`, `''.replace`), so the exact base64 inputs are not settled by the `.py`; the `.dis.txt` was not read for those functions.
  - `LPFeedbackEventTrack.py` is an empty file (0 bytes); event names taken from the outline.
  - Exact command URL template for `getsyslog` (`commonHttpGet`, module not located).
  - How the S3 `fileKey` and download URL are built beyond the STS response.
  - `LPFeedbackManager._runSubmission` body is incomplete in the `.py`; stage order is from the outline strings.

**FEATURE: Analytics and event tracking**
- ENTRY: `LPGlobalUI.eventTrack = LPEventTrack()` (module singleton, observed `LPGlobalUI.py:31`); flush worker starts lazily.
- MODULES: `LPClientFramework.LPEventTrack`, `LPClientFramework.LPDiscoveryTelemetry`, `LPClientFramework.LPFeedback.LPFeedbackEventTrack`, `LPClientFramework.LPUpdateCoordinator` (OTA events), `HOME.StreamService.WiiMRadio.utils.LPWiiMRadioDataProvider`.
- DATA: `cacheDir\event_track_queue.json` (queue; atomic write via `.tmp`), `cacheDir\event_track_debug_dump.jsonl` when `DEBUG_DUMP_TO_LOCAL_FILE` is set (observed `LPEventTrack.py:38-53`, `:217-227`, `:304-327`). `DEBUG_DUMP_TO_LOCAL_FILE = False` (observed `LPEventTrack.py:42`).
- MECHANISM:
  - Events are appended to the local queue; flush at `BATCH_SIZE` 10 or every `FLUSH_INTERVAL` 15 s; retries up to `MAX_RETRY_COUNT` 3 then dropped (observed `LPEventTrack.py:38-42`, `:202-216`, `:244-270`).
  - Default params: `app_ver`, `client_id`, `app_session_id`, `system`. `app_open` adds `country_code`, `language_code`, `script_code`, `locale_name`, `timezone` from `localeGeoContext()` (observed `LPEventTrack.py:159-182`).
  - Request signing: `hashedAppId` is SHA-256 of appKey plus appId (lower-case hex); `sign` is SHA-256 (upper-case hex) over secret plus a canonical string including accessKey, appId, nonce, timestamp, secretKey; `nonce` is 16 random alphanumerics; `timestamp` in ms (observed `LPEventTrack.py:59-156`).
- PROTOCOL: `POST https://api.linkplay.com/apiv1/mp/collect` (observed `LPEventTrack.py:45`). Headers: `Content-Type: application/json`, `accessKey`, `timestamp`, `nonce`, `sign`, `appId` (observed `LPEventTrack.py:73-78`). Body: `client_id` plus `events: [{name, params}]` (inferred from flush strings, `LPEventTrack.outline.txt:175-190`). `client_id` is set from `pcUUID` (inferred from import and call).
- Event names (observed `LPEventTrack.py:26-35`): `first_run`, `app_open`, `screen_view`, `button_click`, `db_index_create`, `beets_import_result`, `network_context_snapshot`, `device_discovery_report`, `device_discovery_failure`. Plus `feedback_exception`, `feedback_complete`, `feedback_log_collect` (observed `LPFeedbackEventTrack.outline.txt:20-22`) and `ota` for OTA events (observed `LPEventTrack.outline.txt:214-215`).
- Discovery telemetry fields named (observed `LPDiscoveryTelemetry.outline.txt:10-21`): `deviceIdHash`, `internet_ok`, `gateway_status`, `gateway_class`, `if_type`, `local_ip_valid`, `ssid_present`, `network_info_raw_ok`, `ssid`, `bssid`, `ip`, `gateway`. Whether `ssid`, `bssid`, `ip`, `gateway` are stripped by `_cleanContextForEvent` is not resolved.
- EVIDENCE: observed as tagged.
- UNKNOWNS: whether `_send_batch` adds other headers; `_cleanContextForEvent` behaviour.

**FEATURE: Crash handling**
- ENTRY: `__main_script__` module init (faulthandler, `sys.excepthook`) and Qt fatal handlers from `main()`.
- MODULES: `LPClientFramework.util.LPExceptionHandler`, `LPCrashDumper`, `LPNativeCrashHandler`, `LPNativeCrashHandler_win`, `LPNativeCrashHandler_mac`.
- DATA:
  - Python crashes: `cacheDir\crash\crash_<timestamp>.json` (observed `LPCrashDumper.outline.txt:28`). Fields: `crashTime`, `exceptionType`, `exceptionValue`, `traceback`, `environment` (observed `LPCrashDumper.outline.txt:42-47`). Rolling delete of old files (observed `LPCrashDumper.outline.txt:18`).
  - Native (Windows): `%APPDATA%\WiiMHome\crashes\` with `.dmp` and `.traceback.txt` (observed `LPNativeCrashHandler_win.outline.txt:82-86`, `:99`).
  - `crash_faulthandler.log` (observed `__main_script__.py:13`).
- MECHANISM:
  - `LPExceptionHandler.globalHandler` writes to the app log and, if a dumper was injected, to a crash file (observed `LPExceptionHandler.outline.txt:4`).
  - Windows: `SetUnhandledExceptionFilter` then `MiniDumpWriteDump`, then `faulthandler.dump_traceback` (observed `LPNativeCrashHandler_win.outline.txt:4`, `:40`).
  - Crash files feed the feedback ZIP via `cacheDir\crash`.
- PROTOCOL: none.
- EVIDENCE: observed as tagged.
- UNKNOWNS: `LPNativeCrashHandler.py` (`get_crash_dir` source) and `LPNativeCrashHandler_mac.py` not read; `LPCrashDumper` is not invoked from feedback packaging in the read code.

**FEATURE: Sleep prevention (hibernation)**
- ENTRY: user toggle `_preventSleepToggleClicked` in `LPMyMusicSettingViewController`; applied at startup when `preventSleepEnable` is set.
- MODULES: `LPClientFramework.LPHibernation` (`LPHibernationManager`, `LPWinHibernation`, `LPMacHibernation`), `LPGlobalUI`.
- DATA: `preventSleepEnable` in userconfig (inferred from names).
- MECHANISM:
  - `LPGlobalUI.hibernationManager = LPHibernationManager().instance()` at import (observed `LPGlobalUI.py:30`).
  - Windows: `kernel32.dll` calls via `preventSleep`, `keepDisplay`, `restoreState` (observed `LPHibernation.outline.txt:48-63`).
  - macOS: IOKit power assertions `PreventSystemSleep` and `PreventUserIdleDisplaySleep` (observed `LPHibernation.outline.txt:84-87`, `:100-114`).
  - Startup logs `wiimhome preventSleep is enable` and calls `preventSleep` (observed `WiiMHome.outline.txt:658-659`; `WiiMHome.dis.txt:6636-6656`).
- PROTOCOL: none.
- EVIDENCE: observed as tagged.
- UNKNOWNS: other callers of `preventSleep` (during playback?) were not found in the scope files.

**FEATURE: util/aes helper (AESCipher)**
- ENTRY: callers listed below; not user-visible itself.
- MODULES: `LPClientFramework.util.aes`; callers `LPCommonWidgets.dialog.LPLoginDialog`, `LPClientFramework.LPDataModel.UpnpDataModel.LPUpnpAsyncDataModel`, `LPClientFramework.LPStreamServiceDir.LPQobuzStreamService`.
- DATA: none.
- MECHANISM (all zero IV, AES-CBC, base64 output):
  - `encrypt(key, raw)`: key is the UTF-8 key string, zero-padded to block; used for the login password, key = `currentDevice.uuid[:16]` (observed `aes.py:13-25`; `LPLoginDialog.py:159-160`).
  - `encrypt2(key, raw)`: key is UUID bytes right-padded to 16 zero bytes; used for login code, key = `device.uuid[:16]` (observed `aes.py:29-50`; `LPUpnpAsyncDataModel.py:46-48`).
  - `decrypt2(key, raw)`: inverse; used to read the stored Qobuz `accessToken`, key = `currentDevice.uuid[:16]` (observed `aes.py:63-78`; `LPQobuzStreamService.py:310-312`).
  - Key material is the speaker's UUID prefix, which the app learns from discovery (inferred).
- PROTOCOL: none.
- EVIDENCE: observed as tagged. `aes.py:83` `__main__` holds a sample key and plaintext literal; not reproduced.
- UNKNOWNS: whether the `encrypt` output is sent over the network (not traced).

**FEATURE: Localisation**
- ENTRY: `LPGlobalUI.changeLocalize(lan)` called with `'en'` in `setupUI` (observed `WiiMHome.dis.txt:11476-11479`).
- MODULES: `LPGlobalUI`, `LPClientFramework.LPUtility`.
- DATA: `data\en.qm`, `data\zh.qm`; sources `data\en.ts` (407 `<message>` elements) and `data\zh.ts` (499 `<message>` elements), counted by grep.
- MECHANISM: loads `'%s.qm' % lan` from `appLocalDataPath()` into a `QTranslator`, removes the previous translator, installs the new one (observed `LPGlobalUI.outline.txt:362-365`).
- PROTOCOL: none.
- EVIDENCE: observed as tagged.
- UNKNOWNS: whether `zh` is ever selected at runtime. Only `'en'` is called in the read code.

## Not found

UI-named features in scope that could not be traced beyond class names or not read:
- Title bar `HOME.LPTitleBar` (only the QML title-bar callbacks were traced).
- Toasts module `HOME.LPToaster` (`LPGlobalUI.Toast` traced).
- Menu bar `HOME.Menu.LPMenuBarController`, search-more menu `LPSearchMoreMenuController`, `LPMenuBridge` (decompile `.err`).
- Sidebar list `HOME.SideBar.LPSideBarListView` and sidebar controllers' handlers.
- About dialog `HOME.LPAboutViewController`.
- Speaker firmware OTA: no speaker firmware-update command found in scope.
- Feedback dialog internals (`Qml\Feedback\LPFeedbackDialog.qml`).
- `LPSignalBus`, `LPPublicDefine`, `LPPalette`, `LPMenu\*`, `LPHttpServerManager`, `LPMediaHttpServer` (not read).
- `LPNativeCrashHandler.py` and `LPNativeCrashHandler_mac.py` (not read).

Searches tried for speaker OTA: `getUpgrade|checkUpgrade|upgradeFirmware|firmware_?[Uu]pdate|otaUpgrade|getNewVersion|upgradeStatus|UpgradeStatus|upgrade_status|getOta|ota_|OTA_` across `evidence\outline`; hits only in the updater files and `dev_ota_status` in `LPDiscoveryTelemetry`.

## Obstacles Encountered

- Many decompiled modules are incomplete (`.err` siblings, `# WARNING: Decompyle incomplete`), including `WiiMHome.py` setup paths, `LPGlobalUI.py` (cut at line 235), `LPWinSparkleUpdater.py` (cut at line 171), `LPFeedbackManager.py` (`_runSubmission`), and `LPEventTrack.py` (cut at line 253). Outline `.outline.txt`/`.dis.txt` used for those.
- `LPFeedbackEventTrack.py` is empty.
- Two Grep runs printed the Freshdesk and event-tracker constant values into tool output. They are in this session's transcript and should be treated as exposed; they are not reproduced here.
- `wiimhome-userconfig.json` was read by key-name pattern only, so nested keys are not fully resolved.
- Side effects: none. Read-only Glob, Grep and Read; no writes, no processes, no network.