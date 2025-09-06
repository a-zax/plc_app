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

# Android settings
android.sdk = 34
android.ndk = 25b
android.ndk_api = 21
android.api = 34
android.minapi = 21
android.accept_sdk_license = True
