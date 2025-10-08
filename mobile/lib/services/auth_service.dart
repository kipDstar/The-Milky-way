import 'package:flutter/foundation.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthService extends ChangeNotifier {
  final ApiService apiService;
  final StorageService storage;
  
  String? _accessToken;
  String? _refreshToken;
  Map<String, dynamic>? _currentUser;
  
  AuthService({
    required this.apiService,
    required this.storage,
  });
  
  bool get isLoggedIn => _accessToken != null;
  Map<String, dynamic>? get currentUser => _currentUser;
  
  Future<bool> isAuthenticated() async {
    final token = await storage.getToken();
    if (token != null) {
      _accessToken = token;
      // TODO: Validate token and fetch user info
      return true;
    }
    return false;
  }
  
  Future<bool> login(String email, String password) async {
    try {
      final response = await apiService.login(email, password);
      
      _accessToken = response['access_token'];
      _refreshToken = response['refresh_token'];
      
      // Save token to secure storage
      if (_accessToken != null) {
        await storage.saveToken(_accessToken!);
      }
      
      // TODO: Decode JWT to get user info
      _currentUser = {
        'email': email,
      };
      
      notifyListeners();
      return true;
    } catch (e) {
      print('Login failed: $e');
      return false;
    }
  }
  
  Future<void> logout() async {
    _accessToken = null;
    _refreshToken = null;
    _currentUser = null;
    
    await storage.deleteToken();
    
    notifyListeners();
  }
}
