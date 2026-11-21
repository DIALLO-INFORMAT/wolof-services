import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _controller = TextEditingController();
  final _historique = <_Message>[];
  bool _chargement = false;

  Future<void> _envoyer(String texte) async {
    final t = texte.trim();
    if (t.isEmpty || _chargement) return;
    setState(() {
      _historique.add(_Message(t, estUtilisateur: true));
      _chargement = true;
      _controller.clear();
    });

    try {
      final rep = await ApiService.demanderTexte(t);
      setState(() {
        _historique.add(
          _Message(rep['texte']?.toString() ?? '—', estUtilisateur: false),
        );
      });
    } catch (e) {
      setState(() {
        _historique.add(_Message('Erreur : $e', estUtilisateur: false));
      });
    } finally {
      setState(() => _chargement = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🇸🇳 Wolof Services'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // ---- Boutons de démonstration ----
          Padding(
            padding: const EdgeInsets.all(8),
            child: Wrap(
              spacing: 8,
              children: [
                ActionChip(
                  label: const Text('🌤️ Météo Dakar'),
                  onPressed: () => _envoyer('météo Dakar'),
                ),
                ActionChip(
                  label: const Text('🌾 Prix du riz'),
                  onPressed: () => _envoyer('prix du riz à Dakar'),
                ),
                ActionChip(
                  label: const Text('💊 Pharmacie'),
                  onPressed: () => _envoyer('pharmacie de garde'),
                ),
              ],
            ),
          ),

          // ---- Historique ----
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _historique.length,
              itemBuilder: (context, i) {
                final m = _historique[i];
                return Align(
                  alignment: m.estUtilisateur
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: m.estUtilisateur
                          ? Theme.of(context).colorScheme.primaryContainer
                          : Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(m.texte),
                  ),
                );
              },
            ),
          ),

          if (_chargement) const LinearProgressIndicator(),

          // ---- Saisie ----
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      onSubmitted: _envoyer,
                      decoration: const InputDecoration(
                        hintText: 'Xam-xam bi… (ex : météo Dakar)',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    icon: const Icon(Icons.mic),
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                            'Micro : activer Whisper côté backend (README étape 2)',
                          ),
                        ),
                      );
                    },
                  ),
                  IconButton.filled(
                    icon: const Icon(Icons.send),
                    onPressed: () => _envoyer(_controller.text),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Message {
  final String texte;
  final bool estUtilisateur;
  _Message(this.texte, {required this.estUtilisateur});
}
