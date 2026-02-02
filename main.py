#!/usr/bin/env python3
"""
Bouncing Ball - Prototype de jeu vidéo

Un jeu simple où vous contrôlez une boule dans une pièce carrée.
La boule rebondit sur les murs et les obstacles, avec gravité réaliste.

Contrôles:
    - Flèches gauche/droite ou A/D : Déplacer la boule
    - Espace : Sauter
    - R : Recommencer le niveau
    - Echap : Quitter

Auteur: Generated with Claude
"""

from game import GameEngine


def main():
    """Point d'entrée principal du jeu."""
    engine = GameEngine()
    engine.run()


if __name__ == "__main__":
    main()
