[app]
title = Daymark
package.name = daymark
package.domain = org.daymark
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,txt
source.exclude_dirs = .git,.venv,tests,bin,build,__pycache__,.pytest_cache
version = 0.1.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1