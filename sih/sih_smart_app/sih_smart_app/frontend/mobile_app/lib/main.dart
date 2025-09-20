// lib/main.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/screens/admin_dashboard.dart';
import 'package:mobile_app/screens/login_screen.dart';
import 'package:mobile_app/screens/student_dashboard.dart';
import 'package:mobile_app/screens/teacher_dashboard.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
      title: 'Smart Curriculum',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        primaryColor: const Color(0xFF4A69FF),
        scaffoldBackgroundColor: const Color(0xFFF4F6F8),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF4A69FF),
          background: const Color(0xFFF4F6F8),
          primary: const Color(0xFF4A69FF),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFF4F6F8),
          elevation: 0,
          iconTheme: IconThemeData(color: Colors.black87),
          titleTextStyle: TextStyle(
            color: Colors.black87,
            fontSize: 20,
            fontFamily: 'Inter',
            fontWeight: FontWeight.w600,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF4A69FF),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10.0),
            ),
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            )
          ),
        ),
        cardTheme: CardThemeData(
          elevation: 1.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12.0),
          ),
        ),
      ),
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