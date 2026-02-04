# eDeDo 🎮

Un jeu de plateforme 2D rapide où vous combattez des ennemis, collectez des power-ups et progressez à travers des niveaux générés procéduralement !

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Pygame Version](https://img.shields.io/badge/pygame-2.6.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Fonctionnalités du Jeu

- **Combat Dynamique** : Sautez sur la tête des ennemis pour les blesser, ou tirez-leur dessus avec des pommes
- **Variété d'Ennemis** : Trois types d'ennemis avec 1, 2 ou 3 PV (Bleu, Violet, Rouge)
- **Difficulté Progressive** : Battez 10 ennemis pour débloquer un portail vers le niveau suivant
- **Génération Procédurale** : Chaque niveau propose des plateformes et obstacles générés aléatoirement
- **Plateformes Fragiles** : Certaines plateformes bleutées se brisent sous vos pieds puis réapparaissent
- **Salle Secrète** : Un pan de mur cache une salle bonus avec un ennemi à vaincre pour gagner une vie
- **Système d'Énergie** : Gérez votre énergie pour les doubles sauts, le flottement et les tirs
- **Système de Rage** : Touchez les ennemis pour charger la rage et déclencher une super attaque orageuse
- **Système de Vies** : Chaque personnage a son propre maximum de vies, collectez des cœurs pour récupérer
- **Support Manette** : Support complet de manette avec contrôles intuitifs

## 🎮 Contrôles

### Clavier
- **Flèches / WASD** : Déplacer gauche/droite
- **Flèche Haut / Z / K** : Sauter (double saut disponible)
- **Shift** : Flotter (descente lente)
- **Espace** : Tirer des pommes (10 énergie)
- **C** : Super attaque orageuse (nécessite 50% de rage)
- **R** : Recommencer le niveau
- **Échap** : Menu pause

### Manette
- **Stick Gauche / D-Pad** : Déplacer
- **Bouton A** : Sauter
- **Bouton B** : Flotter
- **Bouton X** : Tirer
- **Bouton Y** : Super attaque
- **Start** : Menu pause

## 📋 Prérequis

- Python 3.9 ou supérieur
- Pygame 2.6.1
- NumPy (pour la génération audio)

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/yourusername/ededo.git
cd ededo
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez le jeu :
```bash
python main.py
```

## 🎲 Gameplay

1. **Choisissez Votre Couleur** : Sélectionnez la couleur de votre boule au départ
2. **Combattez les Ennemis** : Sautez sur leur tête ou tirez-leur dessus avec des pommes
3. **Gérez l'Énergie** : Votre énergie se régénère après 1 seconde sans l'utiliser (60%/s)
4. **Collectez des Cœurs** : Restaurez vos vies jusqu'au maximum de votre personnage
5. **Atteignez l'Objectif** : Battez 10 ennemis pour ouvrir le portail
6. **Progressez** : Entrez dans le portail pour générer un nouveau niveau

### Types d'Ennemis
- 🔵 **Bleu** (1 PV) : Petit et rapide
- 🟣 **Violet** (2 PV) : Force moyenne
- 🔴 **Rouge** (3 PV) : Grand et résistant

### Mécaniques de Combat
- **Saut sur la Tête** : Inflige 1 dégât à l'ennemi, rebond vers le haut
- **Collision Latérale** : Perte d'1 vie (avec invincibilité temporaire)
- **Tir** : Les projectiles de pomme infligent 1 dégât
- **Super Orage** : À 50% de rage, déclenchez une attaque massive

## 🏗️ Structure du Projet

```
ededo/
├── game/
│   ├── __init__.py
│   ├── config.py         # Configuration du jeu
│   ├── engine.py         # Moteur de jeu et boucle principale
│   ├── entities.py       # Entités du jeu (Ball, Enemy, etc.)
│   ├── physics.py        # Moteur physique
│   ├── renderer.py       # Système de rendu
│   ├── particles.py      # Effets de particules
│   └── audio.py          # Système audio
├── main.py               # Point d'entrée
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## 🛠️ Développement

### Lancement en Mode Développement
```bash
python main.py
```

### Création d'un Exécutable Standalone (macOS)

Pour des instructions détaillées sur la création d'un exécutable `.app` standalone pour macOS, consultez [BUILD_MAC_EXECUTABLE.md](BUILD_MAC_EXECUTABLE.md).

Démarrage rapide :
```bash
# Installer PyInstaller
pip install pyinstaller

# Construire l'app
pyinstaller eDeDo.spec
```

L'application sera créée dans `dist/eDeDo.app`.

### Style de Code
Le projet suit les directives de style PEP 8 avec des annotations de type lorsque applicable.

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une Pull Request.

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/NouvelleFonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrez une Pull Request

## 🎨 Crédits

- **Design & Développement du Jeu** : Arthur et Camille Giuchaoua
- **Audio** : Généré procéduralement avec NumPy
- **Graphismes** : Rendu programmatique avec Pygame

## 🐛 Problèmes Connus

Voir [todo.md](todo.md) pour les tâches de développement actuelles et les problèmes connus.

## 📧 Contact

Lien du Projet : [https://github.com/yourusername/ededo](https://github.com/yourusername/ededo)

---

Fait avec ❤️ et Python
