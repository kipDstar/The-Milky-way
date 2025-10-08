import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../models/delivery.dart';
import '../services/storage_service.dart';
import '../services/sync_service.dart';
import '../utils/constants.dart';

class DeliveryEntryScreen extends StatefulWidget {
  const DeliveryEntryScreen({super.key});

  @override
  State<DeliveryEntryScreen> createState() => _DeliveryEntryScreenState();
}

class _DeliveryEntryScreenState extends State<DeliveryEntryScreen> {
  final _formKey = GlobalKey<FormState>();
  final _farmerCodeController = TextEditingController();
  final _quantityController = TextEditingController();
  final _fatContentController = TextEditingController();
  final _remarksController = TextEditingController();
  
  DateTime _selectedDate = DateTime.now();
  QualityGrade _selectedGrade = QualityGrade.B;
  Farmer? _selectedFarmer;
  bool _isLoading = false;

  @override
  void dispose() {
    _farmerCodeController.dispose();
    _quantityController.dispose();
    _fatContentController.dispose();
    _remarksController.dispose();
    super.dispose();
  }

  Future<void> _searchFarmer() async {
    final code = _farmerCodeController.text.trim();
    if (code.isEmpty) return;

    setState(() => _isLoading = true);

    final storage = Provider.of<StorageService>(context, listen: false);
    final farmer = await storage.getFarmerByCode(code);

    setState(() {
      _selectedFarmer = farmer;
      _isLoading = false;
    });

    if (farmer == null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Farmer $code not found'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  Future<void> _submitDelivery() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedFarmer == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please search and select a farmer first'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final delivery = Delivery(
      farmerCode: _selectedFarmer!.farmerCode,
      stationId: _selectedFarmer!.stationId,
      deliveryDate: _selectedDate,
      quantityLiters: double.parse(_quantityController.text),
      fatContent: _fatContentController.text.isNotEmpty 
          ? double.parse(_fatContentController.text) 
          : null,
      qualityGrade: _selectedGrade.value,
      remarks: _remarksController.text.isNotEmpty ? _remarksController.text : null,
      syncStatus: 'pending',
    );

    final storage = Provider.of<StorageService>(context, listen: false);
    final syncService = Provider.of<SyncService>(context, listen: false);

    await storage.saveDelivery(delivery);

    // Try immediate sync if online
    await syncService.syncPendingDeliveries();

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Delivery recorded successfully'),
          backgroundColor: AppColors.success,
        ),
      );

      // Clear form
      _formKey.currentState!.reset();
      _farmerCodeController.clear();
      _quantityController.clear();
      _fatContentController.clear();
      _remarksController.clear();
      setState(() {
        _selectedFarmer = null;
        _selectedGrade = QualityGrade.B;
        _selectedDate = DateTime.now();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Farmer search
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _farmerCodeController,
                    decoration: const InputDecoration(
                      labelText: 'Farmer Code',
                      prefixIcon: Icon(Icons.person_search),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Required';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _isLoading ? null : _searchFarmer,
                  child: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Search'),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Farmer info card
            if (_selectedFarmer != null)
              Card(
                color: AppColors.success.withOpacity(0.1),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _selectedFarmer!.name,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text('Phone: ${_selectedFarmer!.phone}'),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 16),

            // Date picker
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Delivery Date'),
              subtitle: Text(DateFormat('yyyy-MM-dd').format(_selectedDate)),
              trailing: const Icon(Icons.calendar_today),
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: _selectedDate,
                  firstDate: DateTime.now().subtract(const Duration(days: 7)),
                  lastDate: DateTime.now(),
                );
                if (date != null) {
                  setState(() => _selectedDate = date);
                }
              },
            ),
            const Divider(),

            // Quantity
            TextFormField(
              controller: _quantityController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                labelText: 'Quantity (Liters)',
                prefixIcon: Icon(Icons.local_drink),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) return 'Required';
                final quantity = double.tryParse(value);
                if (quantity == null) return 'Invalid number';
                if (quantity < AppConstants.minDeliveryLiters) {
                  return 'Minimum ${AppConstants.minDeliveryLiters}L';
                }
                if (quantity > AppConstants.maxDeliveryLiters) {
                  return 'Maximum ${AppConstants.maxDeliveryLiters}L';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            // Fat content
            TextFormField(
              controller: _fatContentController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                labelText: 'Fat Content (%) - Optional',
                prefixIcon: Icon(Icons.science),
              ),
              validator: (value) {
                if (value != null && value.isNotEmpty) {
                  final fat = double.tryParse(value);
                  if (fat == null) return 'Invalid number';
                  if (fat < 0 || fat > 20) return 'Must be 0-20%';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            // Quality grade
            DropdownButtonFormField<QualityGrade>(
              value: _selectedGrade,
              decoration: const InputDecoration(
                labelText: 'Quality Grade',
                prefixIcon: Icon(Icons.star),
              ),
              items: QualityGrade.values.map((grade) {
                return DropdownMenuItem(
                  value: grade,
                  child: Text(grade.value),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() => _selectedGrade = value);
                }
              },
            ),
            const SizedBox(height: 16),

            // Remarks
            TextFormField(
              controller: _remarksController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Remarks (Optional)',
                prefixIcon: Icon(Icons.note),
              ),
            ),
            const SizedBox(height: 32),

            // Submit button
            ElevatedButton(
              onPressed: _submitDelivery,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Record Delivery'),
            ),
          ],
        ),
      ),
    );
  }
}
