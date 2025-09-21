// lib/screens/login_screen.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/components/ui_components.dart';
import 'package:mobile_app/screens/admin_dashboard.dart';
import 'package:mobile_app/screens/institution_registration_screen.dart';
import 'package:mobile_app/screens/student_dashboard.dart';
import 'package:mobile_app/screens/student_onboarding_screen.dart';
import 'package:mobile_app/screens/teacher_dashboard.dart';
import 'package:mobile_app/services/api_service.dart';
import 'package:flutter_animate/flutter_animate.dart';

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
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Login Failed!'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );
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
                Container(
                  padding: const EdgeInsets.all(24.0),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF4A69FF), Color(0xFF6C5CE7)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.school_outlined,
                    size: 60,
                    color: Colors.white,
                  ),
                )
                    .animate()
                    .scale(duration: 500.ms, curve: Curves.elasticOut),
                const SizedBox(height: 20),
                const AnimatedTextHeader(
                  text: 'OmniAttend',
                )
                    .animate(delay: 200.ms)
                    .fadeIn(duration: 300.ms),
                const SizedBox(height: 8),
                Text(
                  'AI-Powered Attendance & Learning',
                  style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey[600]),
                )
                    .animate(delay: 300.ms)
                    .fadeIn(duration: 300.ms),
                const SizedBox(height: 40),
                TextFormField(
                  controller: _collegeIdController,
                  decoration: const InputDecoration(
                    labelText: 'Login ID',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                  validator: (v) => v!.isEmpty ? 'Please enter your ID' : null,
                )
                    .animate(delay: 400.ms)
                    .slideX(duration: 300.ms, begin: -1),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Password',
                    prefixIcon: Icon(Icons.lock_outline),
                  ),
                  validator: (v) => v!.isEmpty ? 'Please enter your password' : null,
                )
                    .animate(delay: 500.ms)
                    .slideX(duration: 300.ms, begin: -1),
                const SizedBox(height: 20),
                Container(
                  decoration: BoxDecoration(
                    color: theme.cardTheme.color,
                    borderRadius: BorderRadius.circular(12.0),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.withOpacity(0.1),
                        spreadRadius: 1,
                        blurRadius: 5,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButtonFormField<String>(
                      value: _selectedRole,
                      onChanged: (String? newValue) {
                        setState(() {
                          _selectedRole = newValue!;
                        });
                      },
                      items: <String>['student', 'teacher', 'admin'].map<DropdownMenuItem<String>>((String value) {
                        return DropdownMenuItem<String>(
                          value: value,
                          child: Text(value[0].toUpperCase() + value.substring(1)),
                        );
                      }).toList(),
                      decoration: const InputDecoration(
                        labelText: 'Role',
                        prefixIcon: Icon(Icons.switch_account_outlined),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
                      ),
                    ),
                  ),
                )
                    .animate(delay: 600.ms)
                    .slideX(duration: 300.ms, begin: -1),
                const SizedBox(height: 30),
                SizedBox(
                  width: double.infinity,
                  child: GradientButton(
                    onPressed: _isLoading ? null : _login,
                    text: 'Login',
                    isLoading: _isLoading,
                  ),
                )
                    .animate(delay: 700.ms)
                    .slideX(duration: 300.ms, begin: -1),
                const SizedBox(height: 20),
                TextButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const InstitutionRegistrationScreen(),
                      ),
                    );
                  },
                  child: const Text('Register a new Institution'),
                )
                    .animate(delay: 800.ms)
                    .fadeIn(duration: 300.ms),
              ],
            ),
          ),
        ),
      ),
    );
  }
}