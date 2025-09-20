// lib/screens/view_attendance_screen.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/components/custom_loading_indicator.dart';
import 'package:mobile_app/services/api_service.dart';

class ViewAttendanceScreen extends StatefulWidget {
  final Map<String, dynamic> classSchedule;

  const ViewAttendanceScreen({super.key, required this.classSchedule});

  @override
  State<ViewAttendanceScreen> createState() => _ViewAttendanceScreenState();
}

class _ViewAttendanceScreenState extends State<ViewAttendanceScreen> {
  late Future<List<dynamic>> _attendanceRecordFuture;

  @override
  void initState() {
    super.initState();
    _attendanceRecordFuture = ApiService.getAttendanceRecord(widget.classSchedule['id']);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Record: ${widget.classSchedule['title'] ?? ''}"),
        centerTitle: true,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _attendanceRecordFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const CustomLoadingIndicator();
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error: ${snapshot.error}"));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text("No attendance record found."));
          }

          final attendanceRecords = snapshot.data!;
          final presentStudents = attendanceRecords.where((r) => r['status'] == 'present').toList();
          final absentStudents = attendanceRecords.where((r) => r['status'] == 'absent').toList();

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _buildStatusSection(context, 'Present', presentStudents, Colors.green, Icons.check_circle),
              const SizedBox(height: 24),
              _buildStatusSection(context, 'Absent', absentStudents, Colors.red, Icons.cancel),
            ],
          );
        },
      ),
    );
  }

  Widget _buildStatusSection(BuildContext context, String title, List<dynamic> students, Color color, IconData icon) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$title (${students.length})',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold, color: color),
        ),
        const Divider(thickness: 1.5),
        if (students.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 16.0),
            child: Center(child: Text('None', style: TextStyle(color: Colors.grey))),
          )
        else
          ...students.map((student) => Card(
            margin: const EdgeInsets.symmetric(vertical: 4),
            child: ListTile(
              leading: Icon(icon, color: color),
              title: Text(student['student_name'] ?? 'Unknown'),
              subtitle: Text(student['college_id'] ?? 'N/A'),
            ),
          )),
      ],
    );
  }
}