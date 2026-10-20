# CLAUDE.md

Router for this repo. Rules live one line each; the detail lives in the skill, rule file or doc that owns it.

## Project

Audio Star: a Windows desktop controller for WiiM/LinkPlay speakers (WPF on .NET 10) that replaces the WiiM Home app and plays YouTube, SoundCloud, Spotify, radio and local music on the speaker. The protocol was reverse engineered from WiiM Home.

```text
src/audio-start/
  AudioStar.slnx          solution
  AudioStar.Core/         shared contract: interfaces, records, settings, AppPaths
  AudioStar.Speakers/     discovery, UPnP SOAP and httpapi clients, playback, queue, presets
  AudioStar.Devices/      multiroom groups, device settings
  AudioStar.Library/      My Music (SQLite), media and stream-proxy server, DLNA, Home Share
  AudioStar.Sources/      YouTube and SoundCloud via yt-dlp, Spotify, radio-browser.info
  AudioStar.Desktop/      WPF shell, pages, tray, autostart, single instance
  AudioStar.Setup/        WiX v6 MSI
  AudioStar.*.Tests/      xUnit per library
  db/audiostar/deltas/    SQL delta scripts
  tools/                  firewall.ps1
evidence/                 WiiM Home extraction and live speaker replies, keys redacted
setup/                    AudioStar.msi
tasks/                    features.md, v1-plan.md, lessons.md
wiim-home-feature-map.md  protocol map with evidence pointers
```

## Where the detail lives

| Topic | Lives in |
| --- | --- |
| .NET, WPF and WiX, git history, reverse engineering | `~/.claude/skills/` dotnet-conventions, git-history-ops, windows-app-reverse-engineering |
| Desktop shell, styles, installer, UIA handles | `.claude/rules/desktop.md` |
| Reference view (YouTube page) | `.claude/rules/view-reference.md` |
| Libraries, speaker protocol, streams, sign-in, ports, data, tests | `.claude/rules/libraries.md` |
| WiiM Home protocol and evidence | `wiim-home-feature-map.md`, `evidence/` |
| Scope, what was verified live, corrections | `tasks/features.md`, `tasks/v1-plan.md`, `tasks/lessons.md` |

## Harness

Orchestration runs in the integrations-marketplace mods (`D:\git-projects\integrations-marketplace`), and the house rules in `~/.claude/CLAUDE.md` apply as they stand; this file repeats neither.

- `subagent-delegation-plugin`: routes work to the owning agent (owners in `.claude/rules/`), sends fact gathering to the Haiku fact-gatherer, bounds every brief, keeps the agent ledger.
- `learn-loop-plugin`: runs `claude-learn` once a session goes idle.
- `report-plugin`: starts a status cron when an agent or workflow runs long.
- `intent-guard-plugin`: holds destructive commands nobody asked for.
- `ask-check-plugin`: stops questions the conversation already settled and unrequested findings.
- `write-gate-plugin`: holds a writer's finish until the humanize and marketing-psychology passes ran.
- `harness-plugin`: guards this file's shape, halts a run on `AGENT_STOP`, redirects it with `STEER.md`; `fix-constitution` realigns the repo.

## Hard Rules

- **Read the code on disk, never commit history, to learn what the app has.** Features, sources and settings are what `src/` holds now, uncommitted work included; no `git log`, `git show` or commit diff as the inventory, in a brief or on the main thread.
- **Blockers only while a task runs.** Do the named task with the named tools and nothing beside it. Until it is done, the only message is one blocker line: what the task cannot proceed past without the user. No progress, findings, observations, options, offers, reminders, or gates you were told to respect.
- **Findings wait for completion.** The done reply is what changed and where, then at most a numbered list of `/create-issue` proposals, one line each, for high-severity defects or drastic code smells met on the way. Security is excluded. Anything not on that list is dropped: never asked, never offered, never repeated.
- **Git is not your issue**: never mention commit state, branches or the working tree, and never run a git command the task did not require.
- **No EF Core migrations**: schema changes are hand-written SQL delta scripts in `src/audio-start/db/audiostar/deltas/`.
- **WiiM Home secrets stay out**: never copy its embedded TLS certificate and key, LinkPlay cloud keys or other secrets into Audio Star; `evidence/` keeps them redacted (`windows-app-reverse-engineering`).
- **Verify the UI through UI Automation only**: never simulate mouse input, which can land in the owner's terminal. Capture the window with `PrintWindow`; screenshots are physical pixels at 150 percent scaling.
- **Running the app**: restarting is always allowed and interrupts what the owner's WiiM Amp (192.168.0.67) plays. The running `AudioStar.exe` locks `bin`: stop it, build the Desktop csproj, start it again.
- **Agent notation**: always refer to a subagent as `@<name> (<agent type>)`, e.g. `@queue-fix (dotnet expert)`. Never the bare name, never the type alone. Give every spawn an explicit name so both halves exist.
- **Shell**: Bash for shell operations; PowerShell only where Windows makes it unavoidable.
- Write clean code with no noise: no inline comments, no placeholder notes, no error handling in scripts unless asked.
- No experimental or test files in the repo root: use `.claude/experiments/` or the scratchpad.
- Internal links are relative; anchors are `#heading-name`; every code fence declares a language.
- If a quality check fails, fix the cause. Never bypass with `--no-verify`.

## Working Method

- **Plan first** for anything non-trivial (3+ steps or an architectural decision): write it to `tasks/todo.md`, check in, then track progress there.
- **Verify before reporting done.** Run the check, show the command and its output. A claim is not a receipt.
- **Review `tasks/lessons.md`** at session start; `claude-learn`'s `instruction-audit` gate prunes it and this file.
- **Simplicity first**: minimal diff, root causes over patches, no rewrite to fix a typo.
