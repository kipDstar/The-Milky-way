import 'package:flutter/foundation.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'api_service.dart';
import 'storage_service.dart';
import '../models/delivery.dart';

class SyncService extends ChangeNotifier {
  final ApiService apiService;
  final StorageService storage;
  
  bool _isSyncing = false;
  int _pendingCount = 0;
  DateTime? _lastSyncTime;
  
  bool get isSyncing => _isSyncing;
  int get pendingCount => _pendingCount;
  DateTime? get lastSyncTime => _lastSyncTime;
  
  SyncService({
    required this.apiService,
    required this.storage,
  }) {
    _init();
  }
  
  Future<void> _init() async {
    await _updatePendingCount();
    
    // Listen to connectivity changes
    Connectivity().onConnectivityChanged.listen((result) {
      if (result != ConnectivityResult.none) {
        syncPendingDeliveries();
      }
    });
  }
  
  Future<void> _updatePendingCount() async {
    final pending = await storage.getPendingDeliveries();
    _pendingCount = pending.length;
    notifyListeners();
  }
  
  Future<bool> syncPendingDeliveries() async {
    if (_isSyncing) return false;
    
    _isSyncing = true;
    notifyListeners();
    
    try {
      // Check connectivity
      final connectivityResult = await Connectivity().checkConnectivity();
      if (connectivityResult == ConnectivityResult.none) {
        print('No internet connection. Sync aborted.');
        return false;
      }
      
      // Get pending deliveries
      final pendingDeliveries = await storage.getPendingDeliveries();
      if (pendingDeliveries.isEmpty) {
        _lastSyncTime = DateTime.now();
        return true;
      }
      
      print('Syncing ${pendingDeliveries.length} pending deliveries...');
      
      // Convert to JSON for API
      final deliveriesJson = pendingDeliveries.map((d) => d.toJson()).toList();
      
      // Send batch sync request
      final response = await apiService.syncBatchDeliveries(deliveriesJson);
      
      final results = response['results'] as List;
      
      // Update local database based on sync results
      for (final result in results) {
        final clientId = result['client_id'];
        final status = result['status'];
        
        if (status == 'created') {
          // Mark as synced and update with server ID
          await storage.updateDeliverySyncStatus(
            clientId,
            'synced',
            serverId: result['delivery_id'],
          );
        } else if (status == 'duplicate') {
          // Mark as synced (already exists on server)
          await storage.updateDeliverySyncStatus(
            clientId,
            'synced',
            serverId: result['delivery_id'],
          );
        } else if (status == 'error') {
          print('Sync error for $clientId: ${result['message']}');
          // Keep as pending for retry
        }
      }
      
      _lastSyncTime = DateTime.now();
      await _updatePendingCount();
      
      print('Sync completed successfully');
      return true;
    } catch (e) {
      print('Sync failed: $e');
      return false;
    } finally {
      _isSyncing = false;
      notifyListeners();
    }
  }
  
  Future<void> forceSyncNow() async {
    await syncPendingDeliveries();
  }
}
