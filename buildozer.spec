[app]
# App name and package
title = PLC Controller
package.name = plccontroller
package.domain = org.aryan
version = 1.0

# Source files
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Requirements
requirements = python3,kivy,umodbus

# Orientation & display
orientation = portrait
fullscreen = 0

# (Optional but recommended)
# Use SDL2 as graphics backend
android.arch = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1

# Android SDK/NDK settings
android.sdk = 34
android.ndk = 25b
android.ndk_api = 21
android.api = 34
android.minapi = 21
android.accept_sdk_license = True

# Enable automatic caching of Android packages (speeds up builds)
# Uncomment if you want faster rebuilds locally
# android.gradle_dependencies = com.android.tools.build:gradle:7.4.2
