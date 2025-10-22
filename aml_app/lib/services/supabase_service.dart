import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/transaction.dart';
import '../config/supabase_config.dart';

class SupabaseService {
  static final SupabaseClient _supabase = Supabase.instance.client;

  // Get flagged transactions
  static Future<List<Transaction>> getFlaggedTransactions() async {
    try {
      final response = await _supabase
          .from('transactions')
          .select()
          .eq('status', 'pending_review')
          .order('prediction_score', ascending: false)
          .limit(50);

      return (response as List)
          .map((json) => Transaction.fromJson(json))
          .toList();
    } catch (e) {
      print('Error fetching flagged transactions: $e');
      rethrow;
    }
  }

  // Submit analyst review
  static Future<void> submitReview({
    required String transactionId,
    required String analystId,
    required String manualLabel,
    String? notes,
    String confidence = 'medium',
  }) async {
    try {
      // Insert review
      await _supabase.from('analyst_reviews').insert({
        'transaction_id': transactionId,
        'analyst_id': analystId,
        'manual_label': manualLabel,
        'notes': notes ?? '',
        'confidence': confidence,
      });

      // Update transaction status
      await _supabase
          .from('transactions')
          .update({'status': 'reviewed', 'updated_at': DateTime.now().toIso8601String()})
          .eq('transaction_id', transactionId);
    } catch (e) {
      print('Error submitting review: $e');
      rethrow;
    }
  }

  // Get dashboard statistics
  static Future<Map<String, dynamic>> getStatistics() async {
    try {
      final response = await _supabase.rpc('get_dashboard_stats');
      return response as Map<String, dynamic>;
    } catch (e) {
      print('Error fetching statistics: $e');
      return {
        'total_transactions': 0,
        'flagged_count': 0,
        'reviewed_count': 0,
        'avg_prediction_score': 0.0,
      };
    }
  }

  // Real-time subscription to flagged transactions
  static Stream<List<Transaction>> watchFlaggedTransactions() {
    return _supabase
        .from('transactions')
        .stream(primaryKey: ['transaction_id'])
        .eq('status', 'pending_review')
        .order('prediction_score', ascending: false)
        .map((data) => data.map((json) => Transaction.fromJson(json)).toList());
  }
}