import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/delivery.dart';

class StorageService {
  static Database? _database;
  final _secureStorage = const FlutterSecureStorage();
  
  Future<void> init() async {
    if (_database != null) return;
    
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, 'ddcpts.db');
    
    _database = await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        // Create deliveries table
        await db.execute('''
          CREATE TABLE deliveries (
            id TEXT PRIMARY KEY,
            client_id TEXT UNIQUE NOT NULL,
            farmer_code TEXT NOT NULL,
            station_id TEXT NOT NULL,
            officer_id TEXT,
            delivery_date TEXT NOT NULL,
            quantity_liters REAL NOT NULL,
            fat_content REAL,
            quality_grade TEXT NOT NULL,
            remarks TEXT,
            sync_status TEXT NOT NULL DEFAULT 'pending',
            recorded_at TEXT NOT NULL
          )
        ''');
        
        // Create farmers cache table
        await db.execute('''
          CREATE TABLE farmers (
            id TEXT PRIMARY KEY,
            farmer_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            station_id TEXT NOT NULL
          )
        ''');
        
        // Create index for faster queries
        await db.execute('CREATE INDEX idx_sync_status ON deliveries(sync_status)');
        await db.execute('CREATE INDEX idx_farmer_code ON farmers(farmer_code)');
      },
    );
  }
  
  Database get database {
    if (_database == null) {
      throw Exception('Database not initialized. Call init() first.');
    }
    return _database!;
  }
  
  // Secure token storage
  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
  }
  
  Future<String?> getToken() async {
    return await _secureStorage.read(key: 'auth_token');
  }
  
  Future<void> deleteToken() async {
    await _secureStorage.delete(key: 'auth_token');
  }
  
  // Delivery CRUD operations
  Future<int> saveDelivery(Delivery delivery) async {
    return await database.insert(
      'deliveries',
      {
        'id': delivery.id,
        'client_id': delivery.clientId,
        'farmer_code': delivery.farmerCode,
        'station_id': delivery.stationId,
        'officer_id': delivery.officerId,
        'delivery_date': delivery.deliveryDate.toIso8601String(),
        'quantity_liters': delivery.quantityLiters,
        'fat_content': delivery.fatContent,
        'quality_grade': delivery.qualityGrade,
        'remarks': delivery.remarks,
        'sync_status': delivery.syncStatus,
        'recorded_at': delivery.recordedAt.toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
  
  Future<List<Delivery>> getPendingDeliveries() async {
    final List<Map<String, dynamic>> maps = await database.query(
      'deliveries',
      where: 'sync_status = ?',
      whereArgs: ['pending'],
    );
    
    return maps.map((map) => Delivery.fromJson(_mapToDelivery(map))).toList();
  }
  
  Future<List<Delivery>> getRecentDeliveries({int limit = 50}) async {
    final List<Map<String, dynamic>> maps = await database.query(
      'deliveries',
      orderBy: 'recorded_at DESC',
      limit: limit,
    );
    
    return maps.map((map) => Delivery.fromJson(_mapToDelivery(map))).toList();
  }
  
  Future<int> updateDeliverySyncStatus(String clientId, String syncStatus, {String? serverId}) async {
    final data = {'sync_status': syncStatus};
    if (serverId != null) {
      data['id'] = serverId;
    }
    
    return await database.update(
      'deliveries',
      data,
      where: 'client_id = ?',
      whereArgs: [clientId],
    );
  }
  
  Future<int> deleteSyncedDeliveries({int olderThanDays = 30}) async {
    final cutoffDate = DateTime.now().subtract(Duration(days: olderThanDays));
    
    return await database.delete(
      'deliveries',
      where: 'sync_status = ? AND recorded_at < ?',
      whereArgs: ['synced', cutoffDate.toIso8601String()],
    );
  }
  
  // Farmer cache operations
  Future<int> cacheFarmer(Farmer farmer) async {
    return await database.insert(
      'farmers',
      {
        'id': farmer.id,
        'farmer_code': farmer.farmerCode,
        'name': farmer.name,
        'phone': farmer.phone,
        'station_id': farmer.stationId,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
  
  Future<Farmer?> getFarmerByCode(String farmerCode) async {
    final List<Map<String, dynamic>> maps = await database.query(
      'farmers',
      where: 'farmer_code = ?',
      whereArgs: [farmerCode],
      limit: 1,
    );
    
    if (maps.isEmpty) return null;
    return Farmer.fromJson(maps.first);
  }
  
  Future<List<Farmer>> searchFarmers(String query) async {
    final List<Map<String, dynamic>> maps = await database.query(
      'farmers',
      where: 'name LIKE ? OR farmer_code LIKE ?',
      whereArgs: ['%$query%', '%$query%'],
      limit: 20,
    );
    
    return maps.map((map) => Farmer.fromJson(map)).toList();
  }
  
  Map<String, dynamic> _mapToDelivery(Map<String, dynamic> dbMap) {
    return {
      'id': dbMap['id'],
      'client_generated_id': dbMap['client_id'],
      'farmer_code': dbMap['farmer_code'],
      'station_id': dbMap['station_id'],
      'officer_id': dbMap['officer_id'],
      'delivery_date': dbMap['delivery_date'],
      'quantity_liters': dbMap['quantity_liters'],
      'fat_content': dbMap['fat_content'],
      'quality_grade': dbMap['quality_grade'],
      'remarks': dbMap['remarks'],
      'sync_status': dbMap['sync_status'],
      'recorded_at': dbMap['recorded_at'],
    };
  }
}
