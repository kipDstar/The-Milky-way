import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:workmanager/workmanager.dart';

import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'services/storage_service.dart';
import 'services/sync_service.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'utils/constants.dart';

/// Background sync task callback
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    print("Background sync task started: $task");
    
    try {
      // Initialize services for background task
      final storage = StorageService();
      await storage.init();
      
      final apiService = ApiService(storage: storage);
      final syncService = SyncService(
        apiService: apiService,
        storage: storage,
      );
      
      // Perform sync
      await syncService.syncPendingDeliveries();
      
      return Future.value(true);
    } catch (e) {
      print("Background sync failed: $e");
      return Future.value(false);
    }
  });
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize background worker for sync
  await Workmanager().initialize(
    callbackDispatcher,
    isInDebugMode: false,
  );
  
  // Schedule periodic sync (every 30 minutes)
  await Workmanager().registerPeriodicTask(
    "delivery-sync",
    "syncPendingDeliveries",
    frequency: const Duration(minutes: 30),
    constraints: Constraints(
      networkType: NetworkType.connected,
    ),
  );
  
  runApp(const DDCPTSApp());
}

class DDCPTSApp extends StatelessWidget {
  const DDCPTSApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<StorageService>(
          create: (_) => StorageService()..init(),
        ),
        ProxyProvider<StorageService, ApiService>(
          update: (_, storage, __) => ApiService(storage: storage),
        ),
        ProxyProvider2<ApiService, StorageService, AuthService>(
          update: (_, api, storage, __) => AuthService(
            apiService: api,
            storage: storage,
          ),
        ),
        ProxyProvider2<ApiService, StorageService, SyncService>(
          update: (_, api, storage, __) => SyncService(
            apiService: api,
            storage: storage,
          ),
        ),
      ],
      child: MaterialApp(
        title: 'DDCPTS Mobile',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          primarySwatch: Colors.green,
          primaryColor: AppColors.primary,
          scaffoldBackgroundColor: Colors.white,
          appBarTheme: const AppBarTheme(
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
            elevation: 0,
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
          inputDecorationTheme: InputDecorationTheme(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 16,
            ),
          ),
        ),
        home: const AuthWrapper(),
      ),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context);
    
    return FutureBuilder<bool>(
      future: authService.isAuthenticated(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
        
        if (snapshot.data == true) {
          return const HomeScreen();
        }
        
        return const LoginScreen();
      },
    );
  }
}
