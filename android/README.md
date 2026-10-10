# Android WebView wrapper for publishing to the Play Store

This repository is a Python/Flask dashboard, not an Android app. To make it downloadable from Google Play, the recommended path is to keep the Flask server running on a hosted backend and wrap the web app in a small Android `WebView` shell.

## Recommended deployment flow

1. Deploy the Flask app to a public host or server.
2. Point the Android app to the hosted URL.
3. Build a signed Android package (AAB/APK).
4. Upload it to Google Play Console.

## Project skeleton

The Android wrapper project lives in:

- `android/ViewerWebWrapper/`

It contains a minimal Kotlin app with:

- a single `MainActivity`
- a `WebView` that loads a hosted URL
- `INTERNET` permission
- configuration for a Play Store release build

## Important note

The Flask app itself should not be published directly to the Play Store. Google Play distributes Android packages, not Python processes.

The Android app is just the shell that displays the dashboard URL.

## How to use the wrapper

1. Host the dashboard at a public URL such as `https://your-domain.example.com`.
2. Open `android/ViewerWebWrapper/app/src/main/java/com/example/viewerwebwrapper/MainActivity.kt`.
3. Replace the placeholder URL with the live app URL.
4. Open the project in Android Studio and build a release bundle.
5. Upload the signed AAB to Play Console.
