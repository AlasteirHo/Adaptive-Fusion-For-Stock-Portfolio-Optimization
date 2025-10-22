import 'package:flutter/material.dart';
import '../../services/supabase_service.dart';

class GuestDashboard extends StatefulWidget {
  const GuestDashboard({super.key});

  @override
  State<GuestDashboard> createState() => _GuestDashboardState();
}

class _GuestDashboardState extends State<GuestDashboard> {
  Map<String, dynamic>? _stats;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStatistics();
  }

  Future<void> _loadStatistics() async {
    setState(() => _isLoading = true);
    try {
      final stats = await SupabaseService.getStatistics();
      setState(() {
        _stats = stats;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Guest Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadStatistics,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _buildStatCard(
                    'Total Transactions',
                    _stats?['total_transactions']?.toString() ?? '0',
                    Icons.receipt,
                    Colors.blue,
                  ),
                  const SizedBox(height: 16),
                  _buildStatCard(
                    'Flagged as Illicit',
                    _stats?['flagged_count']?.toString() ?? '0',
                    Icons.flag,
                    Colors.red,
                  ),
                  const SizedBox(height: 16),
                  _buildStatCard(
                    'Reviewed',
                    _stats?['reviewed_count']?.toString() ?? '0',
                    Icons.check_circle,
                    Colors.green,
                  ),
                  const SizedBox(height: 16),
                  _buildStatCard(
                    'Avg Prediction Score',
                    _stats?['avg_prediction_score']?.toStringAsFixed(2) ?? '0.00',
                    Icons.analytics,
                    Colors.orange,
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Row(
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(width: 24),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    value,
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}