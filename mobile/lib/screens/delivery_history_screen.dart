import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../models/delivery.dart';
import '../services/storage_service.dart';
import '../utils/constants.dart';

class DeliveryHistoryScreen extends StatefulWidget {
  const DeliveryHistoryScreen({super.key});

  @override
  State<DeliveryHistoryScreen> createState() => _DeliveryHistoryScreenState();
}

class _DeliveryHistoryScreenState extends State<DeliveryHistoryScreen> {
  List<Delivery> _deliveries = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDeliveries();
  }

  Future<void> _loadDeliveries() async {
    setState(() => _isLoading = true);
    
    final storage = Provider.of<StorageService>(context, listen: false);
    final deliveries = await storage.getRecentDeliveries(limit: 50);
    
    setState(() {
      _deliveries = deliveries;
      _isLoading = false;
    });
  }

  Color _getSyncStatusColor(String syncStatus) {
    switch (syncStatus) {
      case 'synced':
        return AppColors.success;
      case 'pending':
        return AppColors.warning;
      case 'conflict':
        return AppColors.error;
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadDeliveries,
      child: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _deliveries.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.inbox, size: 64, color: AppColors.textSecondary),
                      SizedBox(height: 16),
                      Text('No deliveries yet'),
                    ],
                  ),
                )
              : ListView.builder(
                  itemCount: _deliveries.length,
                  padding: const EdgeInsets.all(AppConstants.defaultPadding),
                  itemBuilder: (context, index) {
                    final delivery = _deliveries[index];
                    
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: _getSyncStatusColor(delivery.syncStatus).withOpacity(0.2),
                          child: Icon(
                            delivery.syncStatus == 'synced' 
                                ? Icons.cloud_done 
                                : Icons.cloud_upload,
                            color: _getSyncStatusColor(delivery.syncStatus),
                          ),
                        ),
                        title: Text(
                          '${delivery.farmerCode} - ${delivery.quantityLiters}L',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 4),
                            Text(
                              DateFormat('yyyy-MM-dd HH:mm').format(delivery.deliveryDate),
                            ),
                            Text('Grade: ${delivery.qualityGrade}'),
                            if (delivery.remarks != null && delivery.remarks!.isNotEmpty)
                              Text(
                                delivery.remarks!,
                                style: const TextStyle(fontStyle: FontStyle.italic),
                              ),
                          ],
                        ),
                        trailing: Chip(
                          label: Text(
                            delivery.syncStatus.toUpperCase(),
                            style: TextStyle(
                              color: _getSyncStatusColor(delivery.syncStatus),
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          backgroundColor: _getSyncStatusColor(delivery.syncStatus).withOpacity(0.1),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
