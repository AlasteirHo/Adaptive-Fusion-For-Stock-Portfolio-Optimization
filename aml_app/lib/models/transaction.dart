class Transaction {
  final String transactionId;
  final DateTime timestamp;
  final double? amount;
  final Map<String, dynamic>? features;
  final double? predictionScore;
  final String? predictedLabel;
  final String? modelVersion;
  final String status;
  final DateTime createdAt;

  Transaction({
    required this.transactionId,
    required this.timestamp,
    this.amount,
    this.features,
    this.predictionScore,
    this.predictedLabel,
    this.modelVersion,
    required this.status,
    required this.createdAt,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      transactionId: json['transaction_id'],
      timestamp: DateTime.parse(json['timestamp']),
      amount: json['amount']?.toDouble(),
      features: json['features'],
      predictionScore: json['prediction_score']?.toDouble(),
      predictedLabel: json['predicted_label'],
      modelVersion: json['model_version'],
      status: json['status'] ?? 'pending_review',
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'transaction_id': transactionId,
      'timestamp': timestamp.toIso8601String(),
      'amount': amount,
      'features': features,
      'prediction_score': predictionScore,
      'predicted_label': predictedLabel,
      'model_version': modelVersion,
      'status': status,
      'created_at': createdAt.toIso8601String(),
    };
  }
}