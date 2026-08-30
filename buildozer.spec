[app]

# (str) Title of your application
title = My Application

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# 注意：若有用到其他套件（如 requests、numpy 等），請加在後面
requirements = python3,kivy

# (str) Custom source folders for requirements
# Change to 1 if your app, requirements or recipes require code to be compiled
# for device target
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Presumed orientation of the application
# Valid values are: landscape, sensorLandscape, portrait or sensorPortrait
# orientation = portrait

# -----------------------------------------------------------------------------
# Android specific
# -----------------------------------------------------------------------------

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required. 21 = Android 5.0
android.minapi = 21

# (str) Android NDK version to use (鎖定穩定版 25b，避免抓到 r28c 路徑報錯)
android.ndk = 25b

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup of application data
android.allow_backup = True

# -----------------------------------------------------------------------------
# Buildozer specific
# -----------------------------------------------------------------------------

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable)
warn_on_root = 1
