import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() => runApp(const WolofApp());

class WolofApp extends StatelessWidget {
  const WolofApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Wolof Services',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF00853F)),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
