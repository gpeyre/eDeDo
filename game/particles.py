"""
Système de particules.

Gère les effets visuels de particules pour les impacts.
"""

import random
import math
from dataclasses import dataclass, field
from .config import Config


@dataclass
class Particle:
    """Une particule individuelle."""

    x: float
    y: float
    vx: float
    vy: float
    lifetime: int
    max_lifetime: int
    size: float
    color: tuple

    def update(self, gravity: float = 0.2) -> bool:
        """
        Met à jour la particule.

        Returns:
            True si la particule est encore vivante, False sinon.
        """
        self.x += self.vx
        self.y += self.vy
        self.vy += gravity  # Légère gravité sur les particules
        self.vx *= 0.98  # Friction air
        self.lifetime -= 1
        return self.lifetime > 0

    @property
    def alpha(self) -> float:
        """Opacité basée sur la durée de vie restante."""
        return self.lifetime / self.max_lifetime

    @property
    def current_size(self) -> float:
        """Taille qui diminue avec le temps."""
        return self.size * self.alpha


class ParticleSystem:
    """Gestionnaire de toutes les particules."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.particles: list[Particle] = []

    def spawn_explosion(self, x: float, y: float, intensity: float = 1.0):
        """
        Crée une explosion de particules à une position donnée.

        Args:
            x: Position X de l'explosion
            y: Position Y de l'explosion
            intensity: Multiplicateur d'intensité (vitesse des impacts)
        """
        cfg = self.config
        count = int(cfg.PARTICLE_COUNT * min(intensity, 2.0))

        for _ in range(count):
            # Angle aléatoire
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(
                cfg.PARTICLE_SPEED_MIN,
                cfg.PARTICLE_SPEED_MAX
            ) * intensity

            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                lifetime=random.randint(
                    cfg.PARTICLE_LIFETIME // 2,
                    cfg.PARTICLE_LIFETIME
                ),
                max_lifetime=cfg.PARTICLE_LIFETIME,
                size=random.uniform(
                    cfg.PARTICLE_SIZE_MIN,
                    cfg.PARTICLE_SIZE_MAX
                ),
                color=random.choice(cfg.PARTICLE_COLORS)
            )
            self.particles.append(particle)

    def spawn_directional(
        self,
        x: float,
        y: float,
        direction_x: float,
        direction_y: float,
        intensity: float = 1.0
    ):
        """
        Crée des particules dans une direction spécifique.

        Args:
            x, y: Position de l'impact
            direction_x, direction_y: Direction normale de l'impact
            intensity: Force de l'impact
        """
        cfg = self.config
        count = int(cfg.PARTICLE_COUNT * min(intensity, 2.0))

        for _ in range(count):
            # Angle basé sur la direction avec dispersion
            base_angle = math.atan2(direction_y, direction_x)
            angle = base_angle + random.uniform(-0.8, 0.8)
            speed = random.uniform(
                cfg.PARTICLE_SPEED_MIN,
                cfg.PARTICLE_SPEED_MAX
            ) * intensity

            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                lifetime=random.randint(
                    cfg.PARTICLE_LIFETIME // 2,
                    cfg.PARTICLE_LIFETIME
                ),
                max_lifetime=cfg.PARTICLE_LIFETIME,
                size=random.uniform(
                    cfg.PARTICLE_SIZE_MIN,
                    cfg.PARTICLE_SIZE_MAX
                ),
                color=random.choice(cfg.PARTICLE_COLORS)
            )
            self.particles.append(particle)

    def update(self):
        """Met à jour toutes les particules et supprime les mortes."""
        self.particles = [p for p in self.particles if p.update()]

    def clear(self):
        """Supprime toutes les particules."""
        self.particles.clear()

    def spawn_double_jump(self, x: float, y: float, radius: float):
        """
        Crée un effet circulaire pour le double saut.

        Args:
            x, y: Position de la boule
            radius: Rayon de la boule
        """
        cfg = self.config
        count = cfg.DOUBLE_JUMP_PARTICLE_COUNT

        for i in range(count):
            # Répartition uniforme en cercle
            angle = (2 * math.pi * i) / count
            # Les particules partent vers l'extérieur et légèrement vers le bas
            speed = random.uniform(3, 5)

            particle = Particle(
                x=x + math.cos(angle) * radius,
                y=y + math.sin(angle) * radius,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed * 0.5 + 1,  # Légère tendance vers le bas
                lifetime=random.randint(15, 25),
                max_lifetime=25,
                size=random.uniform(3, 5),
                color=random.choice(cfg.DOUBLE_JUMP_PARTICLE_COLORS)
            )
            self.particles.append(particle)

    def spawn_ball_collision(self, x: float, y: float, intensity: float = 1.0):
        """
        Crée des particules pour collision entre boules.

        Args:
            x, y: Point de collision
            intensity: Force de l'impact
        """
        cfg = self.config
        count = int(8 * min(intensity, 2.0))

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 4) * intensity

            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                lifetime=random.randint(10, 20),
                max_lifetime=20,
                size=random.uniform(2, 4),
                color=random.choice([
                    (255, 255, 255),
                    (200, 220, 255),
                    (255, 220, 200),
                ])
            )
            self.particles.append(particle)

    def spawn_missile_trail(self, x: float, y: float):
        """
        Crée une trainée de particules pour un missile.

        Args:
            x, y: Position du missile
        """
        # Petite trainée de fumée jaune
        for _ in range(2):
            particle = Particle(
                x=x,
                y=y,
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-0.5, 0.5),
                lifetime=random.randint(8, 15),
                max_lifetime=15,
                size=random.uniform(2, 3),
                color=random.choice([
                    (255, 255, 100),
                    (255, 200, 50),
                    (255, 150, 0),
                ])
            )
            self.particles.append(particle)

    def spawn_enemy_destruction(self, x: float, y: float, color: tuple):
        """
        Crée une explosion de particules pour la destruction d'un ennemi.

        Args:
            x, y: Position de l'ennemi détruit
            color: Couleur de l'ennemi pour les particules
        """
        count = 20

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)

            # Mélanger la couleur de l'ennemi avec du blanc/jaune
            particle_color = random.choice([
                color,
                (255, 255, 255),
                (255, 255, 100),
                (min(255, color[0] + 100), min(255, color[1] + 100), min(255, color[2] + 100))
            ])

            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                lifetime=random.randint(15, 30),
                max_lifetime=30,
                size=random.uniform(2, 5),
                color=particle_color
            )
            self.particles.append(particle)
