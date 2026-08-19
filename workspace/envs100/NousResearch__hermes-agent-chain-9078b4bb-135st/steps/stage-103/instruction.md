**fix(windows): harden gateway scheduled task**

What does this PR do?
- Makes the Windows gateway Scheduled Task actually survive reboot/login by closing all three root causes in #45599, not just the schtasks-settings one.
- Creates the task from XML with a logon delay, StartWhenAvailable, battery-safe settings, no 72-hour execution limit, and a RestartOnFailure policy (root cause #2).
- Resolves the detached uv-venv pythonw in the generated wrapper so the launcher does not respawn a console python.exe (root cause #2c).
- Runs the task through a console-less `wscript.exe` -> `pythonw.exe` launcher instead of `cmd.exe`, so the logon-time `CTRL_CLOSE_EVENT` can no longer reap the gateway with `STATUS_CONTROL_C_EXIT` / `0xC000013A` (root cause #1 - the one that produced the reported `LastTaskResult` after every reboot). `RestartOnFailure` cannot catch `0xC000013A` (Windows treats it as a user cancel), so the console has to be eliminated at the source rather than retried.

Why the .vbs launcher
`wscript.exe` and `pythonw.exe` are both GUI-subsystem executables with no console, so the Scheduled Task action receives no console control events at logon. The `.vbs` sets `HERMES_HOME` / `PYTHONIOENCODING` / `HERMES_GATEWAY_DETACHED` / `VIRTUAL_ENV` / `PYTHONPATH` on the WScript.Shell process (chaining onto any runtime `PYTHONPATH`, mirroring the cmd wrapper's `;%PYTHONPATH%`) and `Run`s pythonw directly, window style 0, async. The `.cmd` wrapper is kept for the Startup-folder fallback and direct `/Run` paths, so this is a single, scoped change to the reboot path.

Related Issue