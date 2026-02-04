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

    def check_wall_collision_ellipse(
        self,
        x: float,
        y: float,
        half_w: float,
        half_h: float,
        vx: float,
        vy: float
    ) -> tuple[float, float, float, float, bool, int]:
        """Collision murs/plafond/sol pour une hitbox elliptique."""
        cfg = self.config
        bounce = cfg.BOUNCE_FACTOR
        wall = cfg.WALL_THICKNESS

        on_ground = False
        on_wall = 0

        if x - half_w < wall:
            x = wall + half_w
            vx = -vx * bounce
            on_wall = -1

        if x + half_w > cfg.PLAY_AREA_WIDTH - wall:
            x = cfg.PLAY_AREA_WIDTH - wall - half_w
            vx = -vx * bounce
            on_wall = 1

        if y - half_h < wall:
            y = wall + half_h
            vy = -vy * bounce

        if y + half_h > cfg.PLAY_AREA_HEIGHT - wall:
            y = cfg.PLAY_AREA_HEIGHT - wall - half_h
            vy = 0
            on_ground = True

        return x, y, vx, vy, on_ground, on_wall

    def check_rect_collision_ellipse(
        self,
        x: float,
        y: float,
        half_w: float,
        half_h: float,
        vx: float,
        vy: float,
        rect_x: float,
        rect_y: float,
        rect_w: float,
        rect_h: float
    ) -> tuple[float, float, float, float, bool, bool]:
        """
        Collision ellipse vs rectangle axis-alignée.

        Retourne: (new_x, new_y, new_vx, new_vy, hit, on_top)
        """
        bounce = self.config.BOUNCE_FACTOR
        closest_x = max(rect_x, min(x, rect_x + rect_w))
        closest_y = max(rect_y, min(y, rect_y + rect_h))

        dx = x - closest_x
        dy = y - closest_y
        ndx = dx / max(half_w, 1e-6)
        ndy = dy / max(half_h, 1e-6)
        distance_sq = ndx * ndx + ndy * ndy

        if distance_sq < 1.0:
            distance = distance_sq ** 0.5 if distance_sq > 0 else 1e-6
            nx = ndx / distance
            ny = ndy / distance
            overlap = 1.0 - distance

            new_x = x + nx * overlap * half_w
            new_y = y + ny * overlap * half_h

            if abs(nx * half_w) > abs(ny * half_h):
                vx = -vx * bounce
            else:
                vy = 0

            on_top = ny < -0.5
            return new_x, new_y, vx, vy, True, on_top

        return x, y, vx, vy, False, False

    def check_ellipse_collision(
        self,
        x1: float, y1: float, hw1: float, hh1: float, vx1: float, vy1: float, m1: float,
        x2: float, y2: float, hw2: float, hh2: float, vx2: float, vy2: float, m2: float
    ) -> tuple[float, float, float, float, float, float, float, float, bool]:
        """Résout une collision approximative entre deux ellipses."""
        sx = max(hw1 + hw2, 1e-6)
        sy = max(hh1 + hh2, 1e-6)
        ndx = (x2 - x1) / sx
        ndy = (y2 - y1) / sy
        dist_sq = ndx * ndx + ndy * ndy

        if dist_sq < 1.0 and dist_sq > 0:
            dist = dist_sq ** 0.5
            nx = ndx / dist
            ny = ndy / dist
            overlap = 1.0 - dist

            # Séparation dans l'espace réel
            sep_x = nx * overlap * sx
            sep_y = ny * overlap * sy
            x1 -= sep_x * 0.5
            y1 -= sep_y * 0.5
            x2 += sep_x * 0.5
            y2 += sep_y * 0.5

            # Vitesse relative en espace réel
            real_nx = nx * sx
            real_ny = ny * sy
            n_len = (real_nx * real_nx + real_ny * real_ny) ** 0.5
            if n_len > 0:
                real_nx /= n_len
                real_ny /= n_len
                dvx = vx1 - vx2
                dvy = vy1 - vy2
                dvn = dvx * real_nx + dvy * real_ny

                if dvn > 0:
                    bounce = self.config.BALL_BOUNCE_FACTOR
                    total_mass = m1 + m2
                    factor1 = (2 * m2 / total_mass) * dvn * bounce
                    factor2 = (2 * m1 / total_mass) * dvn * bounce
                    vx1 -= factor1 * real_nx
                    vy1 -= factor1 * real_ny
                    vx2 += factor2 * real_nx
                    vy2 += factor2 * real_ny

            return x1, y1, vx1, vy1, x2, y2, vx2, vy2, True

        return x1, y1, vx1, vy1, x2, y2, vx2, vy2, False

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
        return self.check_wall_collision_ellipse(x, y, radius, radius, vx, vy)

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
        return self.check_rect_collision_ellipse(
            ball_x, ball_y, radius, radius, vx, vy, rect_x, rect_y, rect_w, rect_h
        )

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
        return self.check_ellipse_collision(
            x1, y1, r1, r1, vx1, vy1, m1,
            x2, y2, r2, r2, vx2, vy2, m2
        )
