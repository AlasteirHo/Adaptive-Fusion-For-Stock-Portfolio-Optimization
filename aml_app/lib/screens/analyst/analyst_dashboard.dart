import 'package:flutter/material.dart';
import '../../services/supabase_service.dart';
import '../../models/transaction.dart';

class AnalystDashboard extends StatefulWidget {
  const AnalystDashboard({super.key});

  @override
  State<AnalystDashboard> createState() => _AnalystDashboardState();
}

class _AnalystDashboardState extends State<AnalystDashboard> {
  List<Transaction> _flaggedTransactions = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadFlaggedTransactions();
  }

  Future<void> _loadFlaggedTransactions() async {
    setState(() => _isLoading = true);
    try {
      final transactions = await SupabaseService.getFlaggedTransactions();
      setState(() {
        _flaggedTransactions = transactions;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading transactions: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analyst Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadFlaggedTransactions,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _flaggedTransactions.isEmpty
              ? const Center(
                  child: Text(
                    'No flagged transactions',
                    style: TextStyle(fontSize: 18),
                  ),
                )
              : ListView.builder(
                  itemCount: _flaggedTransactions.length,
                  padding: const EdgeInsets.all(16),
                  itemBuilder: (context, index) {
                    final transaction = _flaggedTransactions[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        title: Text(
                          'Transaction: ${transaction.transactionId.substring(0, 16)}...',
                          style: const TextStyle(fontFamily: 'monospace'),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 4),
                            Text('Amount: ${transaction.amount?.toStringAsFixed(8) ?? 'N/A'} BTC'),
                            Text('Score: ${(transaction.predictionScore ?? 0).toStringAsFixed(2)}'),
                            Text('Label: ${transaction.predictedLabel ?? 'Unknown'}'),
                          ],
                        ),
                        trailing: ElevatedButton(
                          onPressed: () => _showReviewDialog(transaction),
                          child: const Text('Review'),
                        ),
                        isThreeLine: true,
                      ),
                    );
                  },
                ),
    );
  }

  void _showReviewDialog(Transaction transaction) {
    String selectedLabel = 'illicit';
    String selectedConfidence = 'medium';
    final notesController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Review Transaction'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('ID: ${transaction.transactionId.substring(0, 20)}...'),
              const SizedBox(height: 16),
              const Text('Manual Label:'),
              DropdownButton<String>(
                value: selectedLabel,
                isExpanded: true,
                items: const [
                  DropdownMenuItem(value: 'illicit', child: Text('Illicit')),
                  DropdownMenuItem(value: 'licit', child: Text('Licit')),
                ],
                onChanged: (value) {
                  setState(() => selectedLabel = value!);
                },
              ),
              const SizedBox(height: 16),
              const Text('Confidence:'),
              DropdownButton<String>(
                value: selectedConfidence,
                isExpanded: true,
                items: const [
                  DropdownMenuItem(value: 'high', child: Text('High')),
                  DropdownMenuItem(value: 'medium', child: Text('Medium')),
                  DropdownMenuItem(value: 'low', child: Text('Low')),
                ],
                onChanged: (value) {
                  setState(() => selectedConfidence = value!);
                },
              ),
              const SizedBox(height: 16),
              TextField(
                controller: notesController,
                decoration: const InputDecoration(
                  labelText: 'Notes',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              try {
                await SupabaseService.submitReview(
                  transactionId: transaction.transactionId,
                  analystId: 'analyst_001', // TODO: Get from auth
                  manualLabel: selectedLabel,
                  confidence: selectedConfidence,
                  notes: notesController.text,
                );
                
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Review submitted successfully')),
                  );
                  _loadFlaggedTransactions(); // Refresh list
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
            },
            child: const Text('Submit'),
          ),
        ],
      ),
    );
  }
}