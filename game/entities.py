"""
Entités du jeu.

Définit les objets du jeu : boule, obstacles.
"""

import random
from dataclasses import dataclass, field
from .config import Config
from .physics import PhysicsEngine


@dataclass
class Ball:
    """La boule contrôlée par le joueur."""

    x: float
    y: float
    radius: float = Config.BALL_RADIUS
    vx: float = 0.0
    vy: float = 0.0
    on_ground: bool = False
    jumps_remaining: int = Config.MAX_JUMPS
    on_wall: int = 0  # -1 = mur gauche, 0 = pas sur mur, 1 = mur droit
    floating: bool = False  # Remplace wall_clinging
    energy: float = Config.MAX_ENERGY
    displayed_energy: float = Config.MAX_ENERGY  # Pour affichage smooth
    facing_direction: int = 1  # 1 = droite, -1 = gauche
    color: tuple = field(default_factory=lambda: Config.COLOR_BALL)
    walk_particle_timer: int = 0  # Pour particules de marche
    lives: int = 5  # Nombre de vies
    invincible_timer: int = 0  # Timer d'invincibilité après hit
    energy_usage_timer: int = 0  # Timer depuis dernière utilisation d'énergie

    def can_jump(self) -> bool:
        """Vérifie si la boule peut sauter."""
        return self.jumps_remaining > 0

    def is_double_jump(self) -> bool:
        """Vérifie si le prochain saut serait un double saut."""
        return not self.on_ground and self.jumps_remaining < Config.MAX_JUMPS

    def has_energy_for_double_jump(self) -> bool:
        """Vérifie si assez d'énergie pour double saut."""
        return self.energy >= Config.DOUBLE_JUMP_ENERGY_COST

    def move_left(self, speed: float = Config.BALL_SPEED):
        """Déplace la boule vers la gauche."""
        self.vx -= speed * 0.3
        self.facing_direction = -1

    def move_right(self, speed: float = Config.BALL_SPEED):
        """Déplace la boule vers la droite."""
        self.vx += speed * 0.3
        self.facing_direction = 1

    def jump(self, force: float = Config.JUMP_FORCE) -> bool:
        """
        Fait sauter la boule (double saut possible).

        Returns:
            True si c'est un double saut (pour l'animation)
        """
        is_double_jump = False

        if self.jumps_remaining > 0:
            # Détecter le double saut (pas au sol et pas le premier saut)
            is_double_jump = not self.on_ground and self.jumps_remaining < Config.MAX_JUMPS

            # Si c'est un double saut, consommer de l'énergie
            if is_double_jump:
                if self.energy >= Config.DOUBLE_JUMP_ENERGY_COST:
                    self.energy -= Config.DOUBLE_JUMP_ENERGY_COST
                    self.energy_usage_timer = 0  # Reset le timer
                else:
                    return False  # Pas assez d'énergie

            self.vy = force
            self.jumps_remaining -= 1
            self.on_ground = False

        return is_double_jump

    def start_floating(self):
        """Active le flottement si en l'air et assez d'énergie."""
        if not self.on_ground and self.energy > 0:
            self.floating = True
            self.energy_usage_timer = 0  # Reset le timer

    def stop_floating(self):
        """Désactive le flottement."""
        self.floating = False

    def update(
        self,
        physics: PhysicsEngine,
        obstacles: list['Obstacle']
    ) -> list[tuple[float, float, float, float, float]]:
        """
        Met à jour la position et vélocité de la boule.

        Returns:
            Liste des collisions: [(x, y, dir_x, dir_y, intensity), ...]
        """
        cfg = physics.config
        collisions = []

        # Sauvegarder la vélocité avant collision pour calculer l'intensité
        old_vx, old_vy = self.vx, self.vy

        # Réinitialiser l'état du mur
        self.on_wall = 0

        # Décrémenter le timer d'invincibilité
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # Incrémenter le timer d'utilisation d'énergie
        self.energy_usage_timer += 1

        # Régénération d'énergie: attendre 1s (60 frames) après dernière utilisation
        if self.energy_usage_timer >= 60 and self.energy < cfg.MAX_ENERGY:
            # Régénérer 60% par seconde = 36 énergie par seconde = 0.6 énergie par frame
            self.energy = min(cfg.MAX_ENERGY, self.energy + 0.6)

        # Interpolation smooth pour l'affichage
        if self.displayed_energy < self.energy:
            self.displayed_energy = min(self.energy, self.displayed_energy + 2)
        elif self.displayed_energy > self.energy:
            self.displayed_energy = max(self.energy, self.displayed_energy - 2)

        # Appliquer gravité (réduite si en flottement)
        if self.floating and not self.on_ground:
            # Consommer de l'énergie pour flotter
            if self.energy > 0:
                self.energy -= cfg.FLOAT_ENERGY_COST
                self.energy_usage_timer = 0  # Reset le timer
                self.vy += cfg.GRAVITY * cfg.FLOAT_GRAVITY_MULTIPLIER
            else:
                # Plus d'énergie, arrêter le flottement
                self.floating = False
                self.vy += cfg.GRAVITY
        else:
            self.vy += cfg.GRAVITY

        # Appliquer friction
        if self.on_ground:
            self.vx *= cfg.FRICTION

        # Limiter la vitesse horizontale strictement
        if self.vx > cfg.MAX_SPEED:
            self.vx = cfg.MAX_SPEED
        elif self.vx < -cfg.MAX_SPEED:
            self.vx = -cfg.MAX_SPEED

        # Mettre à jour position
        self.x += self.vx
        self.y += self.vy

        # Collision avec les murs
        old_x, old_y = self.x, self.y
        self.x, self.y, self.vx, self.vy, self.on_ground, self.on_wall = \
            physics.check_wall_collision(
                self.x, self.y, self.radius, self.vx, self.vy
            )

        # Détecter collision mur
        if self.x != old_x or (self.y != old_y and self.on_ground):
            speed = (old_vx ** 2 + old_vy ** 2) ** 0.5
            if speed > 3:  # Seuil minimum pour créer des particules
                # Direction opposée au mouvement
                if self.x != old_x:  # Collision horizontale
                    dir_x = 1 if old_vx < 0 else -1
                    dir_y = 0
                    collisions.append((self.x, self.y, dir_x, dir_y, speed / 5))
                if self.on_ground and old_vy > 2:  # Collision sol
                    collisions.append((self.x, self.y, 0, -1, speed / 5))

        # Collision avec les obstacles
        for obs in obstacles:
            old_x, old_y = self.x, self.y
            # Sauvegarder la position de l'obstacle avant collision
            old_obs_x = obs.x if hasattr(obs, 'min_x') else None  # Plateforme mobile

            self.x, self.y, self.vx, self.vy, hit, on_top = \
                physics.check_rect_collision(
                    self.x, self.y, self.radius,
                    self.vx, self.vy,
                    obs.x, obs.y, obs.width, obs.height
                )
            if hit:
                # Particules uniquement si chute sur obstacle (pas collision latérale)
                if on_top and old_vy > 2:
                    speed = (old_vx ** 2 + old_vy ** 2) ** 0.5
                    collisions.append((
                        old_x, old_y, 0, -1, speed / 5
                    ))

                # Si c'est une plateforme mobile et qu'on est dessus, suivre son mouvement
                if on_top and hasattr(obs, 'min_x'):  # C'est une MovingPlatform
                    # Calculer le déplacement de la plateforme depuis le dernier frame
                    platform_dx = obs.speed * obs.direction
                    self.x += platform_dx  # Suivre la plateforme

            if on_top:
                self.on_ground = True

        # Reset des sauts quand au sol
        if self.on_ground:
            self.jumps_remaining = cfg.MAX_JUMPS
            self.floating = False

            # Particules de fumée en marchant
            if abs(self.vx) > 0.5:  # Si en mouvement
                self.walk_particle_timer += 1
                if self.walk_particle_timer >= 8:  # Toutes les 8 frames
                    self.walk_particle_timer = 0
                    # Petite particule de fumée derrière
                    collisions.append((
                        self.x - self.vx * 2,  # Derrière la boule
                        self.y + self.radius * 0.8,  # Près du sol
                        0, -0.3, 0.3  # Très petite intensité
                    ))

        # Particules de friction contre les murs (comme au sol)
        if self.on_wall != 0 and abs(self.vy) > 1:  # Si glisse contre un mur
            self.walk_particle_timer += 1
            if self.walk_particle_timer >= 6:  # Un peu plus fréquent que au sol
                self.walk_particle_timer = 0
                # Particule sur le côté du mur
                wall_x = self.x + self.radius * self.on_wall  # Position du mur
                collisions.append((
                    wall_x,
                    self.y,
                    -self.on_wall, 0, 0.4  # Direction opposée au mur
                ))

        return collisions


@dataclass
class Obstacle:
    """Un obstacle rectangulaire statique."""

    x: float
    y: float
    width: float
    height: float
    color: tuple = field(default_factory=lambda: Config.COLOR_OBSTACLE)

    def update(self):
        """Met à jour l'obstacle (pour sous-classes)."""
        pass

    @classmethod
    def create_platform(cls, x: float, y: float, width: float) -> 'Obstacle':
        """Crée une plateforme (obstacle horizontal fin)."""
        return cls(x=x, y=y, width=width, height=20)

    @classmethod
    def create_block(cls, x: float, y: float, size: float) -> 'Obstacle':
        """Crée un bloc carré."""
        return cls(x=x, y=y, width=size, height=size)


@dataclass
class AIBall:
    """Une boule contrôlée par l'IA."""

    x: float
    y: float
    radius: float = Config.AI_BALL_RADIUS
    vx: float = 0.0
    vy: float = 0.0
    color: tuple = field(default_factory=lambda: Config.AI_BALL_COLOR_1HP)
    hp: int = 1  # Points de vie
    max_hp: int = 1  # HP initiaux (pour déterminer la taille)
    on_ground: bool = False
    shoot_timer: int = 0  # Timer pour tirer

    def update_color(self):
        """Met à jour la couleur selon les HP actuels."""
        if self.hp >= 3:
            self.color = Config.AI_BALL_COLOR_3HP
        elif self.hp == 2:
            self.color = Config.AI_BALL_COLOR_2HP
        else:
            self.color = Config.AI_BALL_COLOR_1HP

    @property
    def mass(self) -> float:
        """Masse proportionnelle au rayon."""
        return self.radius ** 2

    def update(self, physics: PhysicsEngine, obstacles: list['Obstacle']):
        """Met à jour la boule IA avec comportement variant selon la couleur/HP."""
        cfg = physics.config

        # Appliquer gravité
        self.vy += cfg.GRAVITY

        # Appliquer friction au sol
        if self.on_ground:
            self.vx *= cfg.FRICTION

        # Comportements différents selon max_hp (déterminé par la couleur initiale)
        if self.max_hp == 1:  # Bleu - Rapide, saute souvent et haut
            movement_chance = 0.04  # 4% de chance (2x plus actif)
            jump_chance = 0.025  # 2.5% de chance (2.5x plus de sauts)
            speed_multiplier = 1.5  # 50% plus rapide
            jump_force = cfg.JUMP_FORCE * 0.85  # Sauts plus hauts
        elif self.max_hp == 2:  # Violet - Moyennement rapide, saute moyennement
            movement_chance = 0.025  # 2.5% de chance
            jump_chance = 0.015  # 1.5% de chance
            speed_multiplier = 1.0  # Vitesse normale
            jump_force = cfg.JUMP_FORCE * 0.7  # Sauts moyens
        else:  # Rouge (3 HP) - Lent, saute peu et bas
            movement_chance = 0.015  # 1.5% de chance (moins actif)
            jump_chance = 0.008  # 0.8% de chance (peu de sauts)
            speed_multiplier = 0.6  # 40% plus lent
            jump_force = cfg.JUMP_FORCE * 0.5  # Sauts bas

        # Mouvement aléatoire occasionnel
        if random.random() < movement_chance:
            self.vx += random.uniform(-cfg.AI_BALL_SPEED * speed_multiplier,
                                     cfg.AI_BALL_SPEED * speed_multiplier)

        # Saut aléatoire si au sol
        if self.on_ground and random.random() < jump_chance:
            self.vy = jump_force

        # Limiter la vitesse horizontale selon le type
        max_speed = cfg.AI_BALL_SPEED * 2 * speed_multiplier
        self.vx = max(-max_speed, min(max_speed, self.vx))

        # Mettre à jour position
        self.x += self.vx
        self.y += self.vy

        # Collision avec les murs
        self.x, self.y, self.vx, self.vy, self.on_ground, _ = \
            physics.check_wall_collision(
                self.x, self.y, self.radius, self.vx, self.vy
            )

        # Collision avec les obstacles
        for obs in obstacles:
            self.x, self.y, self.vx, self.vy, hit, on_top = \
                physics.check_rect_collision(
                    self.x, self.y, self.radius,
                    self.vx, self.vy,
                    obs.x, obs.y, obs.width, obs.height
                )
            if on_top:
                self.on_ground = True

    @classmethod
    def create_random(cls, config: Config, index: int) -> 'AIBall':
        """Crée une boule IA à une position aléatoire avec couleur et HP aléatoires."""
        wall = config.WALL_THICKNESS
        margin = config.AI_BALL_RADIUS + 10

        # Choisir aléatoirement les HP initiaux (1, 2 ou 3)
        hp = random.randint(1, 3)

        # Déterminer rayon et couleur selon HP
        if hp == 3:
            ball_radius = config.AI_BALL_RADIUS_3HP
            color = config.AI_BALL_COLOR_3HP
        elif hp == 2:
            ball_radius = config.AI_BALL_RADIUS_2HP
            color = config.AI_BALL_COLOR_2HP
        else:
            ball_radius = config.AI_BALL_RADIUS_1HP
            color = config.AI_BALL_COLOR_1HP

        return cls(
            x=random.uniform(wall + ball_radius + 10, config.WINDOW_WIDTH - wall - ball_radius - 10),
            y=random.uniform(wall + ball_radius + 10, config.WINDOW_HEIGHT // 2),
            radius=ball_radius,
            vx=random.uniform(-2, 2),
            vy=0,
            color=color,
            hp=hp,
            max_hp=hp
        )


@dataclass
class EnemyBullet:
    """Une bulle tirée par un ennemi."""

    x: float
    y: float
    radius: float = 6
    vx: float = 0.0
    vy: float = 0.0
    color: tuple = (150, 200, 255)
    active: bool = True

    def update(self, config: Config):
        """Met à jour la position de la bulle."""
        self.x += self.vx
        self.y += self.vy

        # Désactiver si hors écran
        wall = config.WALL_THICKNESS
        if (self.x < wall - self.radius or self.x > config.WINDOW_WIDTH - wall + self.radius or
            self.y < wall - self.radius or self.y > config.WINDOW_HEIGHT - wall + self.radius):
            self.active = False

    def check_collision(self, ball_x: float, ball_y: float, ball_radius: float) -> bool:
        """Vérifie la collision avec une boule."""
        distance = ((self.x - ball_x) ** 2 + (self.y - ball_y) ** 2) ** 0.5
        return distance < self.radius + ball_radius


@dataclass
class HeartPickup:
    """Un coeur qui tombe du haut pour regagner une vie."""

    x: float
    y: float
    size: float = 15
    vy: float = 2  # Vitesse de chute
    active: bool = True

    def update(self, config: Config):
        """Met à jour la position du coeur."""
        self.y += self.vy

        # Désactiver si hors écran
        if self.y > config.WINDOW_HEIGHT:
            self.active = False

    def check_collision(self, ball_x: float, ball_y: float, ball_radius: float) -> bool:
        """Vérifie la collision avec le joueur."""
        distance = ((self.x - ball_x) ** 2 + (self.y - ball_y) ** 2) ** 0.5
        return distance < self.size + ball_radius


@dataclass
class Missile:
    """Un missile tiré par le joueur."""

    x: float
    y: float
    width: float = Config.MISSILE_WIDTH
    height: float = Config.MISSILE_HEIGHT
    speed: float = Config.MISSILE_SPEED
    direction: int = 1  # 1 = droite, -1 = gauche
    color: tuple = field(default_factory=lambda: Config.MISSILE_COLOR)
    active: bool = True
    charged: bool = False  # Missile chargé ou non

    def update(self, config: Config):
        """Met à jour la position du missile."""
        self.x += self.speed * self.direction

        # Les missiles chargés traversent les murs, les normaux non
        if not self.charged:
            wall = config.WALL_THICKNESS
            if self.x < wall or self.x > config.WINDOW_WIDTH - wall:
                self.active = False
            if self.y < wall or self.y > config.WINDOW_HEIGHT - wall:
                self.active = False
        else:
            # Désactiver le missile chargé seulement s'il sort complètement de l'écran
            if self.x + self.width < 0 or self.x > config.WINDOW_WIDTH:
                self.active = False
            if self.y + self.height < 0 or self.y > config.WINDOW_HEIGHT:
                self.active = False

    def check_collision(self, ball_x: float, ball_y: float, ball_radius: float) -> bool:
        """Vérifie la collision avec une boule."""
        # Point le plus proche du rectangle au centre de la boule
        closest_x = max(self.x, min(ball_x, self.x + self.width))
        closest_y = max(self.y, min(ball_y, self.y + self.height))

        # Distance entre le point le plus proche et le centre de la boule
        distance_x = ball_x - closest_x
        distance_y = ball_y - closest_y
        distance_squared = distance_x * distance_x + distance_y * distance_y

        return distance_squared < (ball_radius * ball_radius)

    def check_obstacle_collision(self, obstacle) -> bool:
        """Vérifie la collision avec un obstacle."""
        # Rectangle vs Rectangle
        return (self.x < obstacle.x + obstacle.width and
                self.x + self.width > obstacle.x and
                self.y < obstacle.y + obstacle.height and
                self.y + self.height > obstacle.y)


@dataclass
class MovingPlatform(Obstacle):
    """Une plateforme qui se déplace horizontalement."""

    min_x: float = 0
    max_x: float = 0
    speed: float = Config.MOVING_PLATFORM_SPEED
    direction: int = 1  # 1 = droite, -1 = gauche
    color: tuple = field(default_factory=lambda: Config.COLOR_MOVING_PLATFORM)

    def update(self):
        """Déplace la plateforme."""
        self.x += self.speed * self.direction

        # Inverser la direction aux limites
        if self.x <= self.min_x:
            self.x = self.min_x
            self.direction = 1
        elif self.x + self.width >= self.max_x:
            self.x = self.max_x - self.width
            self.direction = -1

    @classmethod
    def create(
        cls,
        x: float,
        y: float,
        width: float,
        travel_distance: float,
        speed: float = Config.MOVING_PLATFORM_SPEED
    ) -> 'MovingPlatform':
        """
        Crée une plateforme mobile.

        Args:
            x: Position X initiale
            y: Position Y
            width: Largeur de la plateforme
            travel_distance: Distance totale de déplacement
            speed: Vitesse de déplacement
        """
        return cls(
            x=x,
            y=y,
            width=width,
            height=20,
            min_x=x,
            max_x=x + travel_distance,
            speed=speed
        )


@dataclass
class Door:
    """Une porte qui apparaît quand on a vaincu assez d'ennemis."""

    x: float
    y: float
    width: float = 60
    height: float = 80
    color: tuple = (255, 215, 0)  # Or
    active: bool = False  # La porte n'est active que quand assez d'ennemis sont vaincus

    def check_collision(self, ball_x: float, ball_y: float, ball_radius: float) -> bool:
        """Vérifie si le joueur touche la porte."""
        if not self.active:
            return False

        # Point le plus proche du rectangle au centre de la boule
        closest_x = max(self.x, min(ball_x, self.x + self.width))
        closest_y = max(self.y, min(ball_y, self.y + self.height))

        # Distance entre le point le plus proche et le centre de la boule
        distance_x = ball_x - closest_x
        distance_y = ball_y - closest_y
        distance_squared = distance_x * distance_x + distance_y * distance_y

        return distance_squared < (ball_radius * ball_radius)
