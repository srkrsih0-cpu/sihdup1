// lib/screens/attendance_result_screen.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/components/custom_loading_indicator.dart';
import 'package:mobile_app/services/api_service.dart';

class AttendanceResultScreen extends StatefulWidget {
  final List<String> presentStudentsByAI;
  final Map<String, dynamic> classSchedule;

  const AttendanceResultScreen({
    super.key,
    required this.presentStudentsByAI,
    required this.classSchedule,
  });

  @override
  State<AttendanceResultScreen> createState() => _AttendanceResultScreenState();
}

class _AttendanceResultScreenState extends State<AttendanceResultScreen> {
  late Future<List<dynamic>> _classRosterFuture;
  Map<String, bool> attendanceStatus = {};
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final classId = widget.classSchedule['id'];
    _classRosterFuture = _loadClassRosterAndSetStatus(classId);
  }

  Future<List<dynamic>> _loadClassRosterAndSetStatus(int classId) async {
    final classRoster = await ApiService.getClassRoster(classId);
    for (var student in classRoster) {
      final studentName = student['name'] as String;
      attendanceStatus[studentName] = widget.presentStudentsByAI.contains(studentName);
    }
    return classRoster;
  }
  
  Future<void> _finalizeAttendance() async {
    setState(() { _isSaving = true; });
    final classId = widget.classSchedule['id'];
    final result = await ApiService.saveAttendance(classId, attendanceStatus);

    if (!mounted) return;

    if (result['success']) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Attendance Saved!'), backgroundColor: Colors.green));
      Navigator.of(context).popUntil((route) => route.isFirst);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${result['message']}')));
    }
    setState(() { _isSaving = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Review: ${widget.classSchedule['title'] ?? ''}"),
        centerTitle: true,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _classRosterFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const CustomLoadingIndicator();
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error loading roster: ${snapshot.error}"));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text("No students found in this class roster."));
          }

          final classRoster = snapshot.data!;
          int presentCount = attendanceStatus.values.where((status) => status == true).length;

          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Text(
                      "$presentCount / ${classRoster.length} Students Present",
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold, color: Theme.of(context).primaryColor),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  itemCount: classRoster.length,
                  itemBuilder: (context, index) {
                    final student = classRoster[index];
                    final studentName = student['name'] as String;
                    return Card(
                      child: SwitchListTile(
                        title: Text(studentName, style: const TextStyle(fontWeight: FontWeight.w500)),
                        subtitle: Text(student['college_id'] ?? 'N/A'),
                        value: attendanceStatus[studentName] ?? false,
                        onChanged: (bool newValue) {
                          setState(() {
                            attendanceStatus[studentName] = newValue;
                          });
                        },
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isSaving ? null : _finalizeAttendance,
                    child: _isSaving 
                      ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 3)) 
                      : const Text("Finalize Attendance"),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}