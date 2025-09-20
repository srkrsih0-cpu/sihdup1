// lib/screens/teacher_dashboard.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/components/custom_loading_indicator.dart';
import 'package:mobile_app/screens/attendance_action_screen.dart';
import 'package:mobile_app/screens/login_screen.dart';
import 'package:mobile_app/screens/view_attendance_screen.dart';
import 'package:mobile_app/services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

// The class is now correctly named TeacherDashboard
class TeacherDashboard extends StatefulWidget {
  const TeacherDashboard({super.key});

  @override
  State<TeacherDashboard> createState() => _TeacherDashboardState();
}

class _TeacherDashboardState extends State<TeacherDashboard> {
  late Future<List<dynamic>> _timetableFuture;

  @override
  void initState() {
    super.initState();
    _timetableFuture = ApiService.getTeacherTimetable();
  }

  Future<void> _refreshTimetable() async {
    setState(() {
      _timetableFuture = ApiService.getTeacherTimetable();
    });
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const LoginScreen()), 
        (route) => false
    );
  }

  void _onClassTap(Map<String, dynamic> classItem) {
    final bool isAttendanceTaken = classItem['attendance_taken'] ?? false;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => isAttendanceTaken 
            ? ViewAttendanceScreen(classSchedule: classItem) 
            : AttendanceActionScreen(classSchedule: classItem),
      ),
    ).then((_) => _refreshTimetable());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Today's Schedule"),
        actions: [IconButton(icon: const Icon(Icons.logout), onPressed: _logout)],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshTimetable,
        child: FutureBuilder<List<dynamic>>(
          future: _timetableFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CustomLoadingIndicator();
            }
            if (snapshot.hasError) {
              return Center(child: Text('Error: Could not load schedule.'));
            }
            if (!snapshot.hasData || snapshot.data!.isEmpty) {
              return const Center(child: Text('No classes scheduled for today.'));
            }

            final classes = snapshot.data!;
            return ListView.builder(
              padding: const EdgeInsets.all(12.0),
              itemCount: classes.length,
              itemBuilder: (context, index) => _buildClassCard(context, classes[index]),
            );
          },
        ),
      ),
    );
  }

  Widget _buildClassCard(BuildContext context, Map<String, dynamic> classItem) {
    final bool isAttendanceTaken = classItem['attendance_taken'] ?? false;
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      child: InkWell(
        onTap: () => _onClassTap(classItem),
        borderRadius: BorderRadius.circular(12.0),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Column(
                children: [
                  Text(classItem['start_time'] ?? '', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: theme.primaryColor)),
                  const Text("to", style: TextStyle(color: Colors.grey)),
                  Text(classItem['end_time'] ?? '', style: TextStyle(color: Colors.grey[600])),
                ],
              ),
              const VerticalDivider(width: 32),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(classItem['title'] ?? 'No Title', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    const SizedBox(height: 4),
                    Text('${classItem['course_code'] ?? 'N/A'} • ${classItem['room'] ?? 'N/A'}', style: TextStyle(color: Colors.grey[700])),
                  ],
                ),
              ),
              Chip(
                avatar: Icon(isAttendanceTaken ? Icons.check_circle : Icons.pending_actions, color: isAttendanceTaken ? Colors.green : Colors.orange, size: 18),
                label: Text(isAttendanceTaken ? 'Completed' : 'Pending', style: const TextStyle(fontWeight: FontWeight.bold)),
                backgroundColor: isAttendanceTaken ? Colors.green.withOpacity(0.15) : Colors.orange.withOpacity(0.15),
                shape: const StadiumBorder(side: BorderSide(color: Colors.transparent)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}