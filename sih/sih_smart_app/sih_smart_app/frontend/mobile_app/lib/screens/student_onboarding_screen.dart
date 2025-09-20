// lib/screens/student_onboarding_screen.dart
import 'package:flutter/material.dart';
import 'package:mobile_app/screens/student_dashboard.dart';
import 'package:mobile_app/services/api_service.dart';

class StudentOnboardingScreen extends StatefulWidget {
  const StudentOnboardingScreen({super.key});

  @override
  State<StudentOnboardingScreen> createState() => _StudentOnboardingScreenState();
}

class _StudentOnboardingScreenState extends State<StudentOnboardingScreen> {
  bool _isLoading = false;
  String? _selectedCareerGoal;
  final Set<String> _selectedInterests = {};
  final Set<String> _selectedStrengths = {};
  final Set<String> _selectedWeaknesses = {};

  final List<String> _careerGoals = ['Software Engineer', 'Data Scientist', 'Doctor', 'Civil Engineer', 'Researcher'];
  final List<String> _subjectOptions = ['Physics', 'Chemistry', 'Maths', 'Biology', 'Computer Science', 'History'];
  final List<String> _interestOptions = ['Coding', 'Reading', 'Sports', 'Music', 'Art', 'Robotics'];

  Future<void> _saveProfile() async {
    if (_selectedCareerGoal == null || _selectedInterests.isEmpty || _selectedWeaknesses.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please fill out all required fields.'), backgroundColor: Colors.red));
      return;
    }
    setState(() { _isLoading = true; });
    final profileData = {
      'career_goal': _selectedCareerGoal,
      'interests': _selectedInterests.join(','),
      'strengths': _selectedStrengths.join(','),
      'weak_subjects': _selectedWeaknesses.join(','),
    };
    final result = await ApiService.saveStudentProfile(profileData);
    if (!mounted) return;
    if (result['success']) {
      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const StudentDashboard()));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${result['message']}')));
    }
     setState(() { _isLoading = false; });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("Welcome!", style: theme.textTheme.headlineLarge?.copyWith(fontWeight: FontWeight.bold)),
              Text("Let's set up your profile to personalize your experience.", style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey[600])),
              const SizedBox(height: 32),
              DropdownButtonFormField<String>(
                value: _selectedCareerGoal,
                hint: const Text('Select your future career goal'),
                decoration: const InputDecoration(border: OutlineInputBorder()),
                items: _careerGoals.map((goal) => DropdownMenuItem(value: goal, child: Text(goal))).toList(),
                onChanged: (value) => setState(() => _selectedCareerGoal = value),
              ),
              const SizedBox(height: 24),
              _buildChipSelector("Your Interests", _interestOptions, _selectedInterests),
              _buildChipSelector("Your Strengths (Subjects)", _subjectOptions, _selectedStrengths),
              _buildChipSelector("Your Weaknesses (Subjects)", _subjectOptions, _selectedWeaknesses),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _saveProfile,
                  child: _isLoading 
                    ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 3)) 
                    : const Text('Save and Continue'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChipSelector(String title, List<String> options, Set<String> selectedSet) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8.0,
          children: options.map((option) {
            final isSelected = selectedSet.contains(option);
            return ChoiceChip(
              label: Text(option),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  if (selected) { selectedSet.add(option); } 
                  else { selectedSet.remove(option); }
                });
              },
            );
          }).toList(),
        ),
        const SizedBox(height: 24),
      ],
    );
  }
}