// lib/screens/admin_dashboard.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/components/ui_components.dart';
import 'package:mobile_app/screens/login_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_animate/flutter_animate.dart';

class AdminDashboard extends StatefulWidget {
  const AdminDashboard({super.key});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  int _selectedIndex = 0;

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Dashboard'),
        actions: [
          IconButton(
            onPressed: _logout, 
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: _buildDashboardContent(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.school),
            label: 'Institutions',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_tree),
            label: 'Branches',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_today),
            label: 'Semesters',
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardContent() {
    switch (_selectedIndex) {
      case 0:
        return _buildMainDashboard();
      case 1:
        return _buildInstitutionsScreen();
      case 2:
        return _buildBranchesScreen();
      case 3:
        return _buildSemestersScreen();
      default:
        return _buildMainDashboard();
    }
  }

  Widget _buildMainDashboard() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const AnimatedTextHeader(
            text: 'Welcome, Administrator!',
          )
              .animate()
              .fadeIn(duration: 300.ms),
          const SizedBox(height: 8),
          Text(
            'Manage your institution, students, and teachers',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.grey[600],
                ),
          )
              .animate(delay: 200.ms)
              .fadeIn(duration: 300.ms),
          const SizedBox(height: 32),
          GridView.count(
            crossAxisCount: 2,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              _buildDashboardCard(
                context,
                title: 'Institutions',
                subtitle: 'Manage institutions',
                icon: Icons.business,
                color: const Color(0xFF4A69FF),
                onTap: () {
                  setState(() {
                    _selectedIndex = 1;
                  });
                },
              ),
              _buildDashboardCard(
                context,
                title: 'Branches',
                subtitle: 'Manage branches',
                icon: Icons.account_tree,
                color: const Color(0xFF6C5CE7),
                onTap: () {
                  setState(() {
                    _selectedIndex = 2;
                  });
                },
              ),
              _buildDashboardCard(
                context,
                title: 'Semesters',
                subtitle: 'Manage semesters',
                icon: Icons.calendar_today,
                color: const Color(0xFF20BF6B),
                onTap: () {
                  setState(() {
                    _selectedIndex = 3;
                  });
                },
              ),
              _buildDashboardCard(
                context,
                title: 'Students',
                subtitle: 'Manage students',
                icon: Icons.person,
                color: const Color(0xFFFDCB6E),
                onTap: () {
                  // TODO: Implement student management
                },
              ),
              _buildDashboardCard(
                context,
                title: 'Teachers',
                subtitle: 'Manage teachers',
                icon: Icons.person_2,
                color: const Color(0xFFE17055),
                onTap: () {
                  // TODO: Implement teacher management
                },
              ),
              _buildDashboardCard(
                context,
                title: 'Subjects',
                subtitle: 'Manage subjects',
                icon: Icons.book,
                color: const Color(0xFFA29BFE),
                onTap: () {
                  // TODO: Implement subject management
                },
              ),
            ],
          )
              .animate(delay: 400.ms)
              .slideY(duration: 300.ms, begin: 1),
        ],
      ),
    );
  }

  Widget _buildDashboardCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16.0),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12.0),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 30,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    ).animate().scale(duration: 200.ms, curve: Curves.easeInOut);
  }

  Widget _buildInstitutionsScreen() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Institutions',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              GradientButton(
                onPressed: () {
                  // TODO: Implement add institution
                },
                text: 'Add Institution',
                icon: Icons.add,
              ),
            ],
          ),
          const SizedBox(height: 16),
          const EmptyStateWidget(
            title: 'No Institutions',
            message: 'No institutions have been added yet. Click the button above to add your first institution.',
            icon: Icons.business,
          ),
        ],
      ),
    );
  }

  Widget _buildBranchesScreen() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Branches',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              GradientButton(
                onPressed: () {
                  // TODO: Implement add branch
                },
                text: 'Add Branch',
                icon: Icons.add,
              ),
            ],
          ),
          const SizedBox(height: 16),
          const EmptyStateWidget(
            title: 'No Branches',
            message: 'No branches have been added yet. Click the button above to add your first branch.',
            icon: Icons.account_tree,
          ),
        ],
      ),
    );
  }

  Widget _buildSemestersScreen() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Semesters',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              GradientButton(
                onPressed: () {
                  // TODO: Implement add semester
                },
                text: 'Add Semester',
                icon: Icons.add,
              ),
            ],
          ),
          const SizedBox(height: 16),
          const EmptyStateWidget(
            title: 'No Semesters',
            message: 'No semesters have been added yet. Click the button above to add your first semester.',
            icon: Icons.calendar_today,
          ),
        ],
      ),
    );
  }
}