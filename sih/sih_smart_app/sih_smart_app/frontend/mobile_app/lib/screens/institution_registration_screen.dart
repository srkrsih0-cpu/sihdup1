// lib/screens/institution_registration_screen.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/services/api_service.dart';
import 'package:mobile_app/screens/login_screen.dart';

class InstitutionRegistrationScreen extends StatefulWidget {
  const InstitutionRegistrationScreen({super.key});

  @override
  State<InstitutionRegistrationScreen> createState() => _InstitutionRegistrationScreenState();
}

class _InstitutionRegistrationScreenState extends State<InstitutionRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _institutionNameController = TextEditingController();
  final _adminNameController = TextEditingController();
  final _adminIdController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _isLoading = true; });

    final data = {
      "institution_name": _institutionNameController.text,
      "admin_name": _adminNameController.text,
      "admin_id": _adminIdController.text,
      "password": _passwordController.text,
    };

    final result = await ApiService.registerInstitution(data);

    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result['message'] ?? 'An error occurred'),
        backgroundColor: result['success'] ? Colors.green : Colors.red,
      ),
    );

    if (result['success']) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
    setState(() { _isLoading = false; });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text("Register Your Institution")),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32.0),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                Text('Join Smart Curriculum', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 32),
                TextFormField(controller: _institutionNameController, decoration: const InputDecoration(labelText: 'Institution Name', border: OutlineInputBorder()), validator: (v) => v!.isEmpty ? 'Required' : null),
                const SizedBox(height: 16),
                TextFormField(controller: _adminNameController, decoration: const InputDecoration(labelText: 'Administrator Name', border: OutlineInputBorder()), validator: (v) => v!.isEmpty ? 'Required' : null),
                const SizedBox(height: 16),
                TextFormField(controller: _adminIdController, decoration: const InputDecoration(labelText: 'Administrator Login ID', border: OutlineInputBorder()), validator: (v) => v!.isEmpty ? 'Required' : null),
                const SizedBox(height: 16),
                TextFormField(controller: _passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Administrator Password', border: OutlineInputBorder()), validator: (v) => v!.isEmpty ? 'Required' : null),
                const SizedBox(height: 32),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _register,
                    child: _isLoading ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white)) : const Text('Register'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}