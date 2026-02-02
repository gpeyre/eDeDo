"""
Setup script pour créer un exécutable macOS avec py2app.

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame', 'numpy', 'game'],
    'iconfile': None,  # Ajoutez le chemin vers une icône .icns si disponible
    'plist': {
        'CFBundleName': 'eDeDo',
        'CFBundleDisplayName': 'eDeDo',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.ededo.game',
        'NSHumanReadableCopyright': 'Copyright © 2024 eDeDo Team',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='eDeDo',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
