// lib/screens/student_dashboard.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/components/custom_loading_indicator.dart';
import 'package:mobile_app/screens/login_screen.dart';
import 'package:mobile_app/services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StudentDashboard extends StatefulWidget {
  const StudentDashboard({super.key});
  @override
  State<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends State<StudentDashboard> {
  late Future<Map<String, dynamic>> _routineFuture;

  @override
  void initState() {
    super.initState();
    _routineFuture = ApiService.getSmartRoutine();
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()));
  }
  
  Future<void> _refreshRoutine() async {
    setState(() {
      _routineFuture = ApiService.getSmartRoutine();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Daily Routine'),
        actions: [IconButton(icon: const Icon(Icons.logout), onPressed: _logout)],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshRoutine,
        child: FutureBuilder<Map<String, dynamic>>(
          future: _routineFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CustomLoadingIndicator();
            }
            if (snapshot.hasError) {
              return Center(child: Text('Error: ${snapshot.error}'));
            }
            if (!snapshot.hasData || snapshot.data!['routine'] == null || (snapshot.data!['routine'] as List).isEmpty) {
              return const Center(child: Text('No routine available for today.'));
            }
            
            final routineData = snapshot.data!;
            final routine = routineData['routine'] as List;
            
            return CustomScrollView(
              slivers: [
                SliverToBoxAdapter(
                  child: _buildHeader(context, routineData['branch'], routineData['semester']),
                ),
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      return _buildTimelineTile(
                        context,
                        routine[index],
                        isFirst: index == 0,
                        isLast: index == routine.length - 1
                      );
                    },
                    childCount: routine.length,
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
  
  Widget _buildHeader(BuildContext context, String branch, String semester) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Text(branch, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text(semester, style: Theme.of(context).textTheme.titleMedium),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildTimelineTile(BuildContext context, Map<String, dynamic> event, {bool isFirst = false, bool isLast = false}) {
    final bool isClass = event['type'] == 'class';
    final theme = Theme.of(context);
    
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            width: 50,
            child: Column(
              children: [
                if (!isFirst)
                  Expanded(child: Container(width: 2, color: Colors.grey[300])),
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: theme.scaffoldBackgroundColor,
                    border: Border.all(
                      color: isClass ? theme.primaryColor : Colors.orange,
                      width: 2
                    ),
                  ),
                  child: Icon(
                    isClass ? Icons.school_outlined : Icons.lightbulb_outline,
                    size: 20,
                    color: isClass ? theme.primaryColor : Colors.orange
                  ),
                ),
                if (!isLast)
                  Expanded(child: Container(width: 2, color: Colors.grey[300])),
              ],
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 8.0),
                  child: Text(
                    event['time'] ?? '',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)
                  ),
                ),
                Card(
                  margin: const EdgeInsets.only(top: 4, bottom: 20, right: 16),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          event['title'] ?? 'Untitled Event',
                          style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)
                        ),
                        const SizedBox(height: 4),
                        Text(
                          isClass ? "Scheduled Class" : "AI Recommended Task",
                          style: TextStyle(color: Colors.grey[600])
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}