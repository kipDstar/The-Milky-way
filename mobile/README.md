# DDCPTS Mobile App

Flutter mobile application for dairy collection officers to record milk deliveries with offline-first capabilities.

## Features

- 📱 **Offline-First Architecture**: Record deliveries without internet connection
- 🔄 **Automatic Sync**: Background sync when connectivity is restored
- 👨‍🌾 **Farmer Management**: Quick farmer search and selection
- 📊 **Delivery History**: View recent deliveries with sync status
- 🔐 **Secure Authentication**: JWT-based auth with secure token storage

## Prerequisites

- Flutter SDK 3.0.0 or higher
- Dart SDK 3.0.0 or higher
- Android Studio / Xcode (for mobile development)
- Backend API running (see `../backend/README.md`)

## Getting Started

### 1. Install Dependencies

```bash
flutter pub get
```

### 2. Configure API Endpoint

The app uses `API_BASE_URL` environment variable. For development:

**Android Emulator:**
```bash
# 10.0.2.2 is the emulator's localhost
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

**iOS Simulator:**
```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

**Physical Device:**
```bash
# Use your machine's IP address
flutter run --dart-define=API_BASE_URL=http://192.168.1.100:8000/api/v1
```

### 3. Run the App

```bash
# Debug mode
flutter run

# Release mode (Android)
flutter run --release

# Release mode (iOS)
flutter run --release --no-codesign
```

## Project Structure

```
lib/
├── main.dart               # App entry point
├── models/                 # Data models
│   └── delivery.dart       # Delivery and Farmer models
├── services/               # Business logic services
│   ├── api_service.dart    # HTTP API client
│   ├── auth_service.dart   # Authentication
│   ├── storage_service.dart # SQLite local storage
│   └── sync_service.dart   # Offline sync logic
├── screens/                # UI screens
│   ├── login_screen.dart
│   ├── home_screen.dart
│   ├── delivery_entry_screen.dart
│   └── delivery_history_screen.dart
├── widgets/                # Reusable UI components
└── utils/                  # Constants and helpers
    └── constants.dart
```

## Offline Functionality

### How It Works

1. **Local Storage**: Deliveries are saved to SQLite database with `sync_status = 'pending'`
2. **Background Sync**: WorkManager schedules sync every 30 minutes when connected
3. **Manual Sync**: Tap the sync button to force immediate sync
4. **Conflict Resolution**: Server conflicts are detected and can be resolved manually

### Sync States

- **Pending** (⏰): Delivery waiting to be synced
- **Synced** (✅): Successfully synced to server
- **Conflict** (⚠️): Server conflict detected (requires manual resolution)

## Testing

### Unit Tests

```bash
flutter test
```

### Integration Tests

```bash
flutter test integration_test/
```

### Widget Tests

```bash
flutter test test/widget_test.dart
```

## Build for Production

### Android APK

```bash
flutter build apk --release --dart-define=API_BASE_URL=https://api.yourdomain.com/api/v1
```

### Android App Bundle (for Play Store)

```bash
flutter build appbundle --release --dart-define=API_BASE_URL=https://api.yourdomain.com/api/v1
```

### iOS

```bash
flutter build ios --release --dart-define=API_BASE_URL=https://api.yourdomain.com/api/v1
```

## Configuration

### Environment Variables

- `API_BASE_URL`: Backend API base URL (default: `http://10.0.2.2:8000/api/v1`)

### Build Configuration

Edit `pubspec.yaml` to update:
- App version: `version: 0.1.0+1`
- App name: `name: ddcpts_mobile`

## Demo Credentials

**Officer:**
- Email: `officer@ddcpts.test`
- Password: `Officer@123`

**Manager:**
- Email: `manager@ddcpts.test`
- Password: `Manager@123`

## Troubleshooting

### Cannot Connect to API

- **Android Emulator**: Use `10.0.2.2` instead of `localhost`
- **iOS Simulator**: Use `localhost` or `127.0.0.1`
- **Physical Device**: Use your computer's IP address (ensure same network)
- Check firewall settings allow connections to port 8000

### Sync Not Working

- Check internet connectivity
- Verify API endpoint is reachable
- Check background task permissions (Android 12+)
- Review logs with `flutter logs`

### Database Issues

```bash
# Clear app data
flutter clean
flutter pub get

# Reinstall app
flutter run --uninstall-only
flutter run
```

## Dependencies

Key packages used:
- `dio`: HTTP client
- `sqflite`: Local SQLite database
- `provider`: State management
- `flutter_secure_storage`: Secure token storage
- `workmanager`: Background sync tasks
- `connectivity_plus`: Network connectivity monitoring

## Contributing

See main repository CONTRIBUTING.md for guidelines.

## License

See main repository LICENSE file.
