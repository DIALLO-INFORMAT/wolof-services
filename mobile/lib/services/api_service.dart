import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

/// Appels vers le backend Python.
class ApiService {
  /// ⚠️ REMPLACEZ par l'IP de votre ordinateur (ipconfig → Adresse IPv4)
  /// quand le téléphone n'est pas sur le même réseau que le PC.
  /// En émulateur Android, utilisez : http://10.0.2.2:8000
  static const String baseUrl = 'http://10.0.2.2:8000';

  /// Demande en TEXTE — fonctionne dès maintenant (sans Whisper).
  static Future<Map<String, dynamic>> demanderTexte(String texte) async {
    final rep = await http.post(
      Uri.parse('$baseUrl/ask'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'texte': texte}),
    );
    if (rep.statusCode != 200) {
      throw Exception('Erreur ${rep.statusCode} : ${rep.body}');
    }
    return jsonDecode(utf8.decode(rep.bodyBytes)) as Map<String, dynamic>;
  }

  /// Demande en VOIX — nécessite Whisper côté backend (README étape 2).
  static Future<Map<String, dynamic>> demanderVoix(File fichierAudio) async {
    final req = http.MultipartRequest('POST', Uri.parse('$baseUrl/ask/voix'))
      ..files.add(await http.MultipartFile.fromPath('audio', fichierAudio.path));
    final rep = await req.send();
    final corps = await http.Response.fromStream(rep);
    if (corps.statusCode != 200) {
      throw Exception('Erreur ${corps.statusCode} : ${corps.body}');
    }
    return jsonDecode(utf8.decode(corps.bodyBytes)) as Map<String, dynamic>;
  }
}
