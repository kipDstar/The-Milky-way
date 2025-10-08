import 'package:flutter/material.dart';

/// Application constants
class AppConstants {
  // API Configuration
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1', // Android emulator localhost
  );
  
  // Sync Configuration
  static const int syncIntervalMinutes = 30;
  static const int maxOfflineDeliveries = 1000;
  static const int syncBatchSize = 100;
  
  // Validation Limits
  static const double minDeliveryLiters = 0.1;
  static const double maxDeliveryLiters = 200.0;
  
  // UI Constants
  static const double defaultPadding = 16.0;
  static const double defaultRadius = 8.0;
}

/// Application colors
class AppColors {
  static const Color primary = Color(0xFF2E7D32); // Green
  static const Color secondary = Color(0xFF1B5E20); // Dark Green
  static const Color accent = Color(0xFFFFA726); // Orange
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFFC107);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);
  
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color divider = Color(0xFFBDBDBD);
}

/// Quality grades
enum QualityGrade {
  A('A'),
  B('B'),
  C('C'),
  rejected('Rejected');
  
  final String value;
  const QualityGrade(this.value);
}

/// Sync status
enum SyncStatus {
  synced('synced'),
  pending('pending'),
  conflict('conflict');
  
  final String value;
  const SyncStatus(this.value);
}
