// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:image_picker/image_picker.dart';

class ApiService {
  static const String _baseUrl = "http://10.0.2.2:5000/api";

  static Future<Map<String, dynamic>> registerInstitution(Map<String, String> data) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/register_institution'),
        headers: <String, String>{'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode(data),
      );
      final responseData = jsonDecode(response.body);
      if (response.statusCode == 201) {
        return {'success': true, 'message': responseData['message']};
      } else {
        return {'success': false, 'message': responseData['message'] ?? 'Registration failed'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Could not connect to server'};
    }
  }

  static Future<Map<String, dynamic>> login(String collegeId, String password, String role) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/login'),
        headers: <String, String>{'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode(<String, String>{'college_id': collegeId, 'password': password, 'role': role}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('user_role', data['role']);
        await prefs.setInt('user_id', data['user_id']);
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'message': 'Failed to login'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Could not connect to server'};
    }
  }

  static Future<Map<String, dynamic>> saveStudentProfile(Map<String, dynamic> profileData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getInt('user_id');
      if (userId == null) throw Exception('User not logged in');

      final response = await http.post(
        Uri.parse('$_baseUrl/student/$userId/profile'),
        headers: <String, String>{'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode(profileData),
      );
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'message': 'Failed to save profile'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Could not connect to server'};
    }
  }

  static Future<Map<String, dynamic>> getSmartRoutine() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getInt('user_id');
      if (userId == null) throw Exception('User not logged in');
      
      final response = await http.get(Uri.parse('$_baseUrl/student/$userId/smart_routine'));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load routine');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  static Future<List<dynamic>> getTeacherTimetable() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getInt('user_id');
      if (userId == null) throw Exception('User not logged in');
      final response = await http.get(Uri.parse('$_baseUrl/teacher/$userId/timetable/today'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load timetable');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }
  
  static Future<List<dynamic>> getClassRoster(int classId) async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/class/$classId/roster'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load class roster');
      }
    } catch (e) {
      throw Exception('Error fetching roster: $e');
    }
  }

  static Future<List<dynamic>> getAttendanceRecord(int classId) async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/class/$classId/attendance'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load attendance record');
      }
    } catch (e) {
      throw Exception('Error fetching attendance record: $e');
    }
  }

  static Future<Map<String, dynamic>> markAttendance(XFile imageFile) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$_baseUrl/mark_attendance'));
      request.files.add(await http.MultipartFile.fromPath('attendance_photo', imageFile.path));
      final response = await request.send();
      final responseData = await response.stream.bytesToString();
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(responseData)};
      } else {
        final errorBody = jsonDecode(responseData);
        return {'success': false, 'message': 'Server error: ${errorBody['message'] ?? 'Unknown error'}'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Could not connect to server'};
    }
  }

  static Future<Map<String, dynamic>> saveAttendance(int classId, Map<String, bool> attendanceData) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/save_attendance'),
        headers: <String, String>{'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode(<String, dynamic>{
          'class_id': classId,
          'attendance': attendanceData,
        }),
      );
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'message': 'Failed to save attendance'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Could not connect to server'};
    }
  }
}