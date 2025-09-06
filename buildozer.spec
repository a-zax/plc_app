[app]
title = PLC Controller
package.name = plccontroller
package.domain = org.aryan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,umodbus
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

# Force stable Android SDK/NDK versions
android.sdk = 34
android.ndk = 25b
android.ndk_api = 21

# Android API levels
android.api = 34
android.minapi = 21

# Accept SDK licenses automatically
android.accept_sdk_license = True

# Explicit SDK/NDK paths (for CI/GitHub Actions)
# Set these paths to match where the workflow installs SDK/NDK
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-sdk/ndk/25.1.8937393

# Use SDL2 as graphics backend (recommended)
android.use_sdl2 = True
