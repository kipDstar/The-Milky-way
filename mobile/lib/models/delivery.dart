import 'package:uuid/uuid.dart';

class Delivery {
  final String? id; // Server-assigned ID
  final String clientId; // Client-generated UUID for offline sync
  final String farmerCode;
  final String stationId;
  final String? officerId;
  final DateTime deliveryDate;
  final double quantityLiters;
  final double? fatContent;
  final String qualityGrade;
  final String? remarks;
  final String syncStatus; // synced, pending, conflict
  final DateTime recordedAt;
  
  Delivery({
    this.id,
    String? clientId,
    required this.farmerCode,
    required this.stationId,
    this.officerId,
    required this.deliveryDate,
    required this.quantityLiters,
    this.fatContent,
    required this.qualityGrade,
    this.remarks,
    this.syncStatus = 'pending',
    DateTime? recordedAt,
  })  : clientId = clientId ?? const Uuid().v4(),
        recordedAt = recordedAt ?? DateTime.now();
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'client_generated_id': clientId,
      'farmer_code': farmerCode,
      'station_id': stationId,
      'officer_id': officerId,
      'delivery_date': deliveryDate.toIso8601String().split('T')[0], // Date only
      'quantity_liters': quantityLiters,
      'fat_content': fatContent,
      'quality_grade': qualityGrade,
      'remarks': remarks,
      'sync_status': syncStatus,
      'source': 'mobile',
    };
  }
  
  factory Delivery.fromJson(Map<String, dynamic> json) {
    return Delivery(
      id: json['id'],
      clientId: json['client_generated_id'] ?? json['client_id'],
      farmerCode: json['farmer_code'],
      stationId: json['station_id'],
      officerId: json['officer_id'],
      deliveryDate: DateTime.parse(json['delivery_date']),
      quantityLiters: (json['quantity_liters'] as num).toDouble(),
      fatContent: json['fat_content'] != null ? (json['fat_content'] as num).toDouble() : null,
      qualityGrade: json['quality_grade'],
      remarks: json['remarks'],
      syncStatus: json['sync_status'] ?? 'pending',
      recordedAt: json['recorded_at'] != null 
          ? DateTime.parse(json['recorded_at']) 
          : DateTime.now(),
    );
  }
  
  Delivery copyWith({
    String? id,
    String? syncStatus,
  }) {
    return Delivery(
      id: id ?? this.id,
      clientId: clientId,
      farmerCode: farmerCode,
      stationId: stationId,
      officerId: officerId,
      deliveryDate: deliveryDate,
      quantityLiters: quantityLiters,
      fatContent: fatContent,
      qualityGrade: qualityGrade,
      remarks: remarks,
      syncStatus: syncStatus ?? this.syncStatus,
      recordedAt: recordedAt,
    );
  }
}

class Farmer {
  final String id;
  final String farmerCode;
  final String name;
  final String phone;
  final String stationId;
  
  Farmer({
    required this.id,
    required this.farmerCode,
    required this.name,
    required this.phone,
    required this.stationId,
  });
  
  factory Farmer.fromJson(Map<String, dynamic> json) {
    return Farmer(
      id: json['id'],
      farmerCode: json['farmer_code'],
      name: json['name'],
      phone: json['phone'],
      stationId: json['station_id'],
    );
  }
}
