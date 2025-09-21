// lib/main.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/screens/admin_dashboard.dart';
import 'package:mobile_app/screens/login_screen.dart';
import 'package:mobile_app/screens/student_dashboard.dart';
import 'package:mobile_app/screens/teacher_dashboard.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  Future<String?> _getInitialRoute() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('user_role');
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OmniAttend - Smart Curriculum',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: FutureBuilder<String?>(
        future: _getInitialRoute(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(body: Center(child: CircularProgressIndicator()));
          }
          if (snapshot.hasData) {
            final role = snapshot.data;
            if (role == 'admin') return const AdminDashboard();
            if (role == 'teacher') return const TeacherDashboard();
            if (role == 'student') return const StudentDashboard();
          }
          return const LoginScreen();
        },
      ),
    );
  }
}