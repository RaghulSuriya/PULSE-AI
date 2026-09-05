# PULSE AI - Android Companion Module

The PULSE AI Android Companion is a lightweight native Android service that enables secure, user-authorized notification and SMS forwarding to your PULSE AI Attention Engine backend.

## Why an Android Companion is Required

Modern web browsers operate inside strict security sandboxes and cannot directly access a mobile device's SMS or notification stack. 
PULSE AI implements an authentic client-server architecture:

```
Android Device (NotificationListenerService)
    ↓ (Explicit User Permission)
Notification Normalization & Source Toggle
    ↓ (HTTPS POST)
PULSE Backend (/api/v1/mobile/notifications)
    ↓
AI Relevance & Actionability Classifier
    ↓
Task Generation & Daily Schedule Replanner
```

## Features

1. **Explicit Source Toggles:** User can choose which notification sources to enable (SMS, Bank alerts, Electricity bills, Recharge reminders, Delivery alerts).
2. **Selective Filtering:** Filters out private chat messages and non-actionable notification noise locally before transmission.
3. **Token Authorization:** Authenticates requests securely using JWT device tokens linked to your PULSE account.

## Setup & Installation

1. Import `/android-companion` project into Android Studio.
2. Build APK: `./gradlew assembleRelease`
3. Install on your Android device.
4. Launch app and tap **Grant Notification Listener Permission**.
5. Log in with your PULSE AI account or enter your Backend API URL.
