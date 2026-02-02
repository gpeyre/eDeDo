# Générer un Exécutable Standalone pour macOS

Ce guide explique comment créer un exécutable standalone (`.app`) du jeu eDeDo pour macOS.

## Prérequis

- Python 3.9 ou supérieur
- Les dépendances du jeu installées (`pip install -r requirements.txt`)
- PyInstaller (`pip install pyinstaller`)

## Installation de PyInstaller

```bash
pip install pyinstaller
```

## Méthode 1 : Génération automatique avec PyInstaller

### Étape 1 : Créer le fichier spec

Créez un fichier `eDeDo.spec` à la racine du projet avec le contenu suivant :

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['numpy', 'pygame'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='eDeDo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Pas de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='eDeDo',
)

app = BUNDLE(
    coll,
    name='eDeDo.app',
    icon=None,  # Ajoutez un fichier .icns ici si vous avez une icône
    bundle_identifier='com.ededo.game',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
    },
)
```

### Étape 2 : Générer l'exécutable

```bash
pyinstaller eDeDo.spec
```

L'application `eDeDo.app` sera créée dans le dossier `dist/`.

## Méthode 2 : Commande en une ligne

Si vous préférez une approche plus simple :

```bash
pyinstaller --name="eDeDo" \
            --windowed \
            --onefile \
            --add-data "game:game" \
            main.py
```

**Note :** Cette méthode crée un exécutable unique mais peut être plus lent au démarrage.

## Méthode 3 : py2app (Alternative native macOS)

Une alternative spécifique à macOS est d'utiliser `py2app` :

### Installation

```bash
pip install py2app
```

### Créer le fichier setup.py

```python
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame', 'numpy'],
    'iconfile': None,  # Ajoutez le chemin vers une icône .icns
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Générer l'application

```bash
python setup.py py2app
```

L'application sera dans `dist/eDeDo.app`.

## Test de l'exécutable

1. Naviguez vers le dossier `dist/`
2. Double-cliquez sur `eDeDo.app` pour lancer le jeu
3. Si macOS bloque l'exécution (sécurité), allez dans :
   - Préférences Système > Sécurité et confidentialité
   - Cliquez sur "Ouvrir quand même"

## Distribution

Pour distribuer l'application :

1. Compressez le fichier `.app` en `.zip`
2. Ou créez un fichier `.dmg` pour une installation plus professionnelle :

```bash
hdiutil create -volname "eDeDo" -srcfolder dist/eDeDo.app -ov -format UDZO eDeDo.dmg
```

## Dépannage

### Erreur "module not found"
- Assurez-vous que toutes les dépendances sont dans `requirements.txt`
- Ajoutez les modules manquants dans `hiddenimports` du fichier spec

### L'application ne démarre pas
- Testez d'abord avec l'option `--console` pour voir les erreurs :
  ```bash
  pyinstaller --console main.py
  ```

### Problèmes de permissions
- Après la première exécution, vous devrez peut-être autoriser l'application dans les préférences système

## Taille de l'exécutable

L'exécutable peut être volumineux (~50-100 MB) car il inclut Python et toutes les bibliothèques.

Pour réduire la taille :
- Utilisez `--onefile` (plus lent au démarrage)
- Excluez les modules inutilisés
- Utilisez UPX pour compresser : `pip install pyinstaller[upx]`

## Notes

- L'exécutable généré ne fonctionne que sur macOS
- Pour Windows/Linux, répétez le processus sur ces plateformes
- Pour une distribution universelle, considérez une version web avec Pygame Web
