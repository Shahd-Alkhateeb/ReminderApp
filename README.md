# Daymark

A local-first Android reminder assistant, starting with medication and daily reminders. It is a scheduling tool only and does not provide medical advice.

## Current stage

Phase 4: a Kivy reminder screen with local SQLite storage, add/edit/delete, enable/disable, and weekly recurrence. Reliable background scheduling, Android notifications, and voice input remain to be implemented and tested.

## Requirements

- Python 3.11 on Windows for the local Kivy development environment
- Kivy 2.3.1

Activate the Python 3.11 environment where Kivy is installed, then install the project dependencies:

```powershell
& "$env:USERPROFILE\kivy_env\Scripts\Activate.ps1"
python -m pip install -r requirements-dev.txt
python -m app.main
```

## Tests

Run the test suite with:

```powershell
python -m pytest
```

The reminder model, form parsing, service, and SQLite repository are covered by pytest.

## Android phone build

The Windows Kivy environment runs the desktop app, but Buildozer requires Linux. Install WSL 2 with Ubuntu from an elevated PowerShell window, then restart Windows:

```powershell
wsl --install -d Ubuntu
```

In Ubuntu, install the Android build tools and build outside `/mnt/c` (the Linux filesystem is much faster and avoids file permission issues):

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
	autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
	libtinfo6 cmake libffi-dev libssl-dev build-essential
mkdir -p ~/projects/daymark
PROJECT="/mnt/c/Users/FIX 11/ReminderApp"
cp -r "$PROJECT/app" "$PROJECT/main.py" "$PROJECT/buildozer.spec" ~/projects/daymark/
cd ~/projects/daymark
python3 -m venv .buildozer-venv
source .buildozer-venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install buildozer
buildozer android debug
```

The first build downloads the Android SDK/NDK and may take several minutes. Copy the resulting APK to Windows Downloads, then transfer it to the phone:

```bash
cp bin/*.apk "/mnt/c/Users/FIX 11/Downloads/"
```

Open the APK on the phone and allow installation from that file manager when Android asks. The current Android config targets 64-bit ARM phones.

The APK currently provides local reminder management only. Background scheduling, Android notifications, and microphone speech recognition are not implemented yet, so reminders will not alert while the app is closed.