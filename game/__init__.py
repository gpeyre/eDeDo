"""
Module principal du jeu.

Ce module contient tous les composants du jeu :
- config : Configuration et constantes
- physics : Moteur physique (gravité, collisions)
- entities : Entités du jeu (boule, obstacles)
- engine : Boucle de jeu principale
- renderer : Rendu graphique
"""

from .config import Config
from .engine import GameEngine

__all__ = ['Config', 'GameEngine']
