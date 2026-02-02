"""
Moteur physique du jeu.

Gère la gravité, les collisions et les rebonds.
"""

from dataclasses import dataclass
from .config import Config


@dataclass
class Vector2:
    """Vecteur 2D pour positions et vélocités."""
    x: float
    y: float

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)


class PhysicsEngine:
    """Moteur physique gérant gravité et collisions."""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def apply_gravity(self, velocity: Vector2) -> Vector2:
        """Applique la gravité à une vélocité."""
        return Vector2(velocity.x, velocity.y + self.config.GRAVITY)

    def apply_friction(self, velocity: Vector2, on_ground: bool) -> Vector2:
        """Applique la friction horizontale si au sol."""
        if on_ground:
            return Vector2(velocity.x * self.config.FRICTION, velocity.y)
        return velocity

    def check_wall_collision(
        self,
        x: float,
        y: float,
        radius: float,
        vx: float,
        vy: float
    ) -> tuple[float, float, float, float, bool, int]:
        """
        Vérifie et gère les collisions avec les murs.

        Returns:
            (new_x, new_y, new_vx, new_vy, on_ground, on_wall)
            on_wall: -1 = mur gauche, 0 = pas de mur, 1 = mur droit
        """
        cfg = self.config
        bounce = cfg.BOUNCE_FACTOR
        wall = cfg.WALL_THICKNESS

        on_ground = False
        on_wall = 0

        # Mur gauche
        if x - radius < wall:
            x = wall + radius
            vx = -vx * bounce
            on_wall = -1

        # Mur droit
        if x + radius > cfg.WINDOW_WIDTH - wall:
            x = cfg.WINDOW_WIDTH - wall - radius
            vx = -vx * bounce
            on_wall = 1

        # Plafond
        if y - radius < wall:
            y = wall + radius
            vy = -vy * bounce

        # Sol (pas de rebond)
        if y + radius > cfg.WINDOW_HEIGHT - wall:
            y = cfg.WINDOW_HEIGHT - wall - radius
            vy = 0  # Pas de rebond au sol
            on_ground = True

        return x, y, vx, vy, on_ground, on_wall

    def check_rect_collision(
        self,
        ball_x: float,
        ball_y: float,
        radius: float,
        vx: float,
        vy: float,
        rect_x: float,
        rect_y: float,
        rect_w: float,
        rect_h: float
    ) -> tuple[float, float, float, float, bool]:
        """
        Vérifie collision entre une boule et un rectangle.

        Returns:
            (new_vx, new_vy, collision_occurred, on_top)
        """
        bounce = self.config.BOUNCE_FACTOR

        # Trouver le point le plus proche du rectangle
        closest_x = max(rect_x, min(ball_x, rect_x + rect_w))
        closest_y = max(rect_y, min(ball_y, rect_y + rect_h))

        # Distance entre la boule et ce point
        dx = ball_x - closest_x
        dy = ball_y - closest_y
        distance_sq = dx * dx + dy * dy

        if distance_sq < radius * radius:
            # Collision détectée
            distance = distance_sq ** 0.5 if distance_sq > 0 else 0.001

            # Normaliser
            nx = dx / distance
            ny = dy / distance

            # Repousser la boule
            overlap = radius - distance
            new_x = ball_x + nx * overlap
            new_y = ball_y + ny * overlap

            # Réfléchir la vélocité (pas de rebond comme au sol)
            if abs(nx) > abs(ny):
                vx = -vx * bounce
            else:
                vy = 0  # Pas de rebond vertical, comme au sol

            on_top = ny < -0.5  # Sur le dessus de l'obstacle
            return new_x, new_y, vx, vy, True, on_top

        return ball_x, ball_y, vx, vy, False, False

    def check_ball_collision(
        self,
        x1: float, y1: float, r1: float, vx1: float, vy1: float, m1: float,
        x2: float, y2: float, r2: float, vx2: float, vy2: float, m2: float
    ) -> tuple[float, float, float, float, float, float, float, float, bool]:
        """
        Vérifie et résout la collision entre deux boules.

        Utilise la conservation de la quantité de mouvement.

        Returns:
            (x1, y1, vx1, vy1, x2, y2, vx2, vy2, collision_occurred)
        """
        dx = x2 - x1
        dy = y2 - y1
        distance_sq = dx * dx + dy * dy
        min_dist = r1 + r2

        if distance_sq < min_dist * min_dist and distance_sq > 0:
            distance = distance_sq ** 0.5

            # Vecteur normal
            nx = dx / distance
            ny = dy / distance

            # Séparer les boules
            overlap = min_dist - distance
            x1 -= nx * overlap * 0.5
            y1 -= ny * overlap * 0.5
            x2 += nx * overlap * 0.5
            y2 += ny * overlap * 0.5

            # Vitesse relative
            dvx = vx1 - vx2
            dvy = vy1 - vy2

            # Vitesse relative selon la normale
            dvn = dvx * nx + dvy * ny

            # Ne pas résoudre si les boules s'éloignent
            if dvn > 0:
                # Coefficient de restitution
                bounce = self.config.BALL_BOUNCE_FACTOR

                # Calcul des nouvelles vitesses (collision élastique avec masses)
                total_mass = m1 + m2
                factor1 = (2 * m2 / total_mass) * dvn * bounce
                factor2 = (2 * m1 / total_mass) * dvn * bounce

                vx1 -= factor1 * nx
                vy1 -= factor1 * ny
                vx2 += factor2 * nx
                vy2 += factor2 * ny

            return x1, y1, vx1, vy1, x2, y2, vx2, vy2, True

        return x1, y1, vx1, vy1, x2, y2, vx2, vy2, False
