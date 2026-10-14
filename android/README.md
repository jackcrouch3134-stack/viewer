# Android wrapper for the Universal Earth Viewing System

This directory contains a minimal Android WebView shell that loads the
running Flask dashboard (default: `http://10.0.2.2:8000/` on the emulator,
or your machine's LAN IP on a device).

## Build the Android App Bundle (.aab)

Requires Android SDK + Gradle with access to Google Maven (dl.google.com):

```bash
cd android
gradle bundleRelease
# Output: app/build/outputs/bundle/release/app-release.aab
```

Then sign with `jarsigner`/`apksigner` or upload to Play Console.
