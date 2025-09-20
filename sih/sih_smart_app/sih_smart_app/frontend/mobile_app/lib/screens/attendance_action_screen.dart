// lib/screens/attendance_action_screen.dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_app/components/custom_loading_indicator.dart';
import 'package:mobile_app/screens/attendance_result_screen.dart';
import 'package:mobile_app/services/api_service.dart';

class AttendanceActionScreen extends StatefulWidget {
  final Map<String, dynamic> classSchedule;

  const AttendanceActionScreen({super.key, required this.classSchedule});

  @override
  State<AttendanceActionScreen> createState() => _AttendanceActionScreenState();
}

class _AttendanceActionScreenState extends State<AttendanceActionScreen> {
  XFile? _image;
  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;

  Future<void> _pickImage() async {
    try {
      final XFile? photo = await _picker.pickImage(source: ImageSource.gallery, imageQuality: 80);
      if (photo != null) {
        setState(() { _image = photo; });
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error getting photo: $e')));
    }
  }

  Future<void> _submitAttendance() async {
    if (_image == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please select a photo first')));
      return;
    }
    setState(() { _isLoading = true; });
    try {
      final result = await ApiService.markAttendance(_image!);
      if (!mounted) return;
      if (result['success']) {
        final List<String> presentList = List<String>.from(result['data']['present']);
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => AttendanceResultScreen(
              presentStudentsByAI: presentList,
              classSchedule: widget.classSchedule,
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${result['message']}')));
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      if (mounted) {
        setState(() { _isLoading = false; });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.classSchedule['course_code'] ?? 'Attendance'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      widget.classSchedule['title'] ?? 'Unknown Class',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${widget.classSchedule['start_time']} - ${widget.classSchedule['end_time']}',
                      style: theme.textTheme.titleMedium,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Expanded(
              child: Container(
                clipBehavior: Clip.antiAlias,
                decoration: BoxDecoration(
                  color: Colors.black12,
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: _image == null
                    ? const Center(child: Icon(Icons.camera_alt_outlined, size: 60, color: Colors.white60))
                    : Image.file(File(_image!.path), fit: BoxFit.contain),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _pickImage,
              icon: const Icon(Icons.photo_library_outlined),
              label: Text(_image == null ? 'Select Photo' : 'Select Different Photo'),
              style: ElevatedButton.styleFrom(
                backgroundColor: _image == null ? theme.colorScheme.primary : Colors.grey[600],
              ),
            ),
            if (_image != null) ...[
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: _isLoading ? null : _submitAttendance,
                icon: _isLoading 
                  ? Container(
                      width: 24, height: 24, padding: const EdgeInsets.all(2.0),
                      child: const CircularProgressIndicator(color: Colors.white, strokeWidth: 3),
                    )
                  : const Icon(Icons.send_outlined),
                label: Text(_isLoading ? 'Processing...' : 'Submit Attendance'),
              ),
            ]
          ],
        ),
      ),
    );
  }
}