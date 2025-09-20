// lib/screens/login_screen.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/screens/admin_dashboard.dart';
import 'package:mobile_app/screens/institution_registration_screen.dart';
import 'package:mobile_app/screens/student_dashboard.dart';
import 'package:mobile_app/screens/student_onboarding_screen.dart';
import 'package:mobile_app/screens/teacher_dashboard.dart';
import 'package:mobile_app/services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _collegeIdController = TextEditingController();
  final _passwordController = TextEditingController();
  String _selectedRole = 'student';
  bool _isLoading = false;

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _isLoading = true; });

    final result = await ApiService.login(_collegeIdController.text, _passwordController.text, _selectedRole);
    if (!mounted) return;

    if (result['success']) {
      final role = result['data']['role'];
      if (role == 'admin') {
        Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const AdminDashboard()));
      } else if (role == 'teacher') {
        Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const TeacherDashboard()));
      } else if (role == 'student') {
        final bool profileCompleted = result['data']['profile_completed'] ?? false;
        if (profileCompleted) {
          Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const StudentDashboard()));
        } else {
          Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const StudentOnboardingScreen()));
        }
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result['message'] ?? 'Login Failed!')));
    }
    setState(() { _isLoading = false; });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.school_outlined, size: 80, color: theme.primaryColor),
                const SizedBox(height: 20),
                Text('Smart Curriculum', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text('Sign in or register your institution', style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey[600])),
                const SizedBox(height: 40),
                TextFormField(controller: _collegeIdController, decoration: const InputDecoration(labelText: 'Login ID', prefixIcon: Icon(Icons.person_outline), border: OutlineInputBorder()), validator: (v) => v!.isEmpty ? 'Please enter your ID' : null),
                const SizedBox(height: 20),
                TextFormField(controller: _passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline), border: OutlineInputBorder()), validator: (v) => v!.isEmpty ? 'Please enter your password' : null),
                const SizedBox(height: 20),
                DropdownButtonFormField<String>(
                  value: _selectedRole,
                  onChanged: (String? newValue) { setState(() { _selectedRole = newValue!; }); },
                  items: <String>['student', 'teacher', 'admin'].map<DropdownMenuItem<String>>((String value) {
                    return DropdownMenuItem<String>(value: value, child: Text(value[0].toUpperCase() + value.substring(1)));
                  }).toList(),
                  decoration: const InputDecoration(labelText: 'Role', prefixIcon: Icon(Icons.switch_account_outlined), border: OutlineInputBorder()),
                ),
                const SizedBox(height: 30),
                SizedBox(width: double.infinity, child: ElevatedButton(onPressed: _isLoading ? null : _login, child: _isLoading ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 3)) : const Text('Login'))),
                const SizedBox(height: 20),
                TextButton(
                  onPressed: () {
                    Navigator.push(context, MaterialPageRoute(builder: (context) => const InstitutionRegistrationScreen()));
                  },
                  child: const Text('Register a new Institution'),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}