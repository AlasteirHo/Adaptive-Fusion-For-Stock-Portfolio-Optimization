import 'package:flutter/material.dart';
import 'analyst/analyst_dashboard.dart';
import 'guest/guest_dashboard.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bitcoin AML Detection'),
        centerTitle: true,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.security,
                size: 100,
                color: Colors.blue,
              ),
              const SizedBox(height: 40),
              const Text(
                'Bitcoin AML Detection System',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              const Text(
                'Select your role to continue',
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 40),
              
              // Analyst Button
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const AnalystDashboard()),
                  );
                },
                icon: const Icon(Icons.admin_panel_settings),
                label: const Text('Analyst Interface'),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(250, 60),
                  textStyle: const TextStyle(fontSize: 18),
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Guest Button
              OutlinedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const GuestDashboard()),
                  );
                },
                icon: const Icon(Icons.visibility),
                label: const Text('Guest View'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(250, 60),
                  textStyle: const TextStyle(fontSize: 18),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}