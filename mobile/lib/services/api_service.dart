import 'package:dio/dio.dart';
import '../utils/constants.dart';
import 'storage_service.dart';

class ApiService {
  late final Dio _dio;
  final StorageService storage;
  
  ApiService({required this.storage}) {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));
    
    // Add interceptor for auth token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storage.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        print('API Error: ${error.response?.statusCode} - ${error.message}');
        return handler.next(error);
      },
    ));
  }
  
  // Authentication
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _dio.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
    return response.data;
  }
  
  // Farmers
  Future<Map<String, dynamic>> getFarmerByCode(String farmerCode) async {
    final response = await _dio.get('/farmers/$farmerCode');
    return response.data;
  }
  
  Future<List<dynamic>> searchFarmers(String query) async {
    final response = await _dio.get('/farmers', queryParameters: {
      'search': query,
      'limit': 20,
    });
    return response.data as List;
  }
  
  // Deliveries
  Future<Map<String, dynamic>> createDelivery(Map<String, dynamic> data) async {
    final response = await _dio.post('/deliveries', data: data);
    return response.data;
  }
  
  Future<Map<String, dynamic>> syncBatchDeliveries(List<Map<String, dynamic>> deliveries) async {
    final response = await _dio.post('/deliveries/sync/batch', data: deliveries);
    return response.data;
  }
  
  Future<List<dynamic>> getDeliveries({
    String? stationId,
    String? farmerId,
    DateTime? dateFrom,
    DateTime? dateTo,
  }) async {
    final queryParams = <String, dynamic>{};
    if (stationId != null) queryParams['station_id'] = stationId;
    if (farmerId != null) queryParams['farmer_id'] = farmerId;
    if (dateFrom != null) queryParams['date_from'] = dateFrom.toIso8601String().split('T')[0];
    if (dateTo != null) queryParams['date_to'] = dateTo.toIso8601String().split('T')[0];
    
    final response = await _dio.get('/deliveries', queryParameters: queryParams);
    return response.data as List;
  }
  
  // Reports
  Future<Map<String, dynamic>> getDailyReport(DateTime date, {String? stationId}) async {
    final queryParams = {
      'report_date': date.toIso8601String().split('T')[0],
    };
    if (stationId != null) queryParams['station_id'] = stationId;
    
    final response = await _dio.get('/reports/daily', queryParameters: queryParams);
    return response.data;
  }
  
  // Health check
  Future<bool> checkConnectivity() async {
    try {
      final response = await _dio.get('/health', options: Options(
        sendTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 5),
      ));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
