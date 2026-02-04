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
    radius: float = Config.BALL_RADIUS  # Compat legacy (utilisé pour certains effets)
    hitbox_width: float = Config.PLAYER_HITBOX_SIZES[1][0]
    hitbox_height: float = Config.PLAYER_HITBOX_SIZES[1][1]
    character_index: int = 1
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
    max_lives: int = 5  # Nombre de vies maximum
    invincible_timer: int = 0  # Timer d'invincibilité après hit
    energy_usage_timer: int = 0  # Timer depuis dernière utilisation d'énergie
    speed_multiplier: float = 1.0  # Multiplicateur de vitesse (varie selon le personnage)
    jump_multiplier: float = 1.0  # Multiplicateur de force de saut (varie selon le personnage)
    aim_direction_y: int = 0  # Direction de visée verticale: -1 = haut, 0 = horizontal, 1 = bas
    rage_boost_active: bool = False

    @property
    def half_w(self) -> float:
        return self.hitbox_width / 2

    @property
    def half_h(self) -> float:
        return self.hitbox_height / 2

    @property
    def visual_radius(self) -> float:
        return max(self.half_w, self.half_h)

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
        # Appliquer moins de contrôle si en l'air + multiplicateur selon le personnage
        control_factor = Config.AIR_CONTROL_FACTOR if not self.on_ground else 1.0
        self.vx -= speed * 0.3 * control_factor * self.speed_multiplier
        self.facing_direction = -1

    def move_right(self, speed: float = Config.BALL_SPEED):
        """Déplace la boule vers la droite."""
        # Appliquer moins de contrôle si en l'air + multiplicateur selon le personnage
        control_factor = Config.AIR_CONTROL_FACTOR if not self.on_ground else 1.0
        self.vx += speed * 0.3 * control_factor * self.speed_multiplier
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

            self.vy = force * self.jump_multiplier
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
        current_max_speed = cfg.MAX_SPEED_RAGE if self.rage_boost_active else cfg.MAX_SPEED
        if self.vx > current_max_speed:
            self.vx = current_max_speed
        elif self.vx < -current_max_speed:
            self.vx = -current_max_speed

        # Mettre à jour position
        self.x += self.vx
        self.y += self.vy

        # Collision avec les murs
        old_x, old_y = self.x, self.y
        self.x, self.y, self.vx, self.vy, self.on_ground, self.on_wall = \
            physics.check_wall_collision_ellipse(
                self.x, self.y, self.half_w, self.half_h, self.vx, self.vy
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
            if not obs.is_solid():
                continue

            old_x, old_y = self.x, self.y

            self.x, self.y, self.vx, self.vy, hit, on_top = \
                physics.check_rect_collision_ellipse(
                    self.x, self.y, self.half_w, self.half_h,
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
                    obs.on_player_step()

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
                        self.y + self.half_h * 0.8,  # Près du sol
                        0, -0.3, 0.3  # Très petite intensité
                    ))

        # Particules de friction contre les murs (comme au sol)
        if self.on_wall != 0 and abs(self.vy) > 1:  # Si glisse contre un mur
            self.walk_particle_timer += 1
            if self.walk_particle_timer >= 6:  # Un peu plus fréquent que au sol
                self.walk_particle_timer = 0
                # Particule sur le côté du mur
                wall_x = self.x + self.half_w * self.on_wall  # Position du mur
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
    color: tuple = field(default_factory=lambda: Config.COLOR_PLATFORM_STATIC)

    def update(self):
        """Met à jour l'obstacle (pour sous-classes)."""
        pass

    def is_solid(self) -> bool:
        """Retourne True si l'obstacle participe aux collisions."""
        return True

    def on_player_step(self):
        """Hook appelé quand le joueur atterrit sur l'obstacle."""
        pass

    @classmethod
    def create_platform(cls, x: float, y: float, width: float) -> 'Obstacle':
        """Crée une plateforme statique (obstacle horizontal fin)."""
        return cls(x=x, y=y, width=width, height=20, color=Config.COLOR_PLATFORM_STATIC)

    @classmethod
    def create_block(cls, x: float, y: float, size: float) -> 'Obstacle':
        """Crée un bloc carré."""
        return cls(x=x, y=y, width=size, height=size)


@dataclass
class FragilePlatform(Obstacle):
    """Plateforme fragile qui casse temporairement au contact du joueur."""

    break_delay: int = Config.FRAGILE_PLATFORM_BREAK_DELAY
    respawn_time: int = Config.FRAGILE_PLATFORM_RESPAWN_TIME
    step_timer: int = 0
    broken: bool = False
    respawn_timer: int = 0
    stepped_this_frame: bool = False

    def update(self):
        """Met à jour la casse et la réapparition de la plateforme."""
        if self.broken:
            self.respawn_timer += 1
            if self.respawn_timer >= self.respawn_time:
                self.broken = False
                self.respawn_timer = 0
                self.step_timer = 0
            self.stepped_this_frame = False
            return

        if self.stepped_this_frame:
            self.step_timer += 1
        else:
            self.step_timer = 0

        if self.step_timer >= self.break_delay:
            self.broken = True
            self.respawn_timer = 0
            self.step_timer = 0

        self.stepped_this_frame = False

    def is_solid(self) -> bool:
        """La plateforme ne collabore pas aux collisions quand elle est cassée."""
        return not self.broken

    def on_player_step(self):
        """Démarre le compte à rebours de casse au premier contact."""
        if not self.broken:
            self.stepped_this_frame = True

    @classmethod
    def create(cls, x: float, y: float, width: float) -> 'FragilePlatform':
        """Crée une plateforme fragile."""
        return cls(
            x=x,
            y=y,
            width=width,
            height=20,
            color=Config.COLOR_PLATFORM_FRAGILE
        )


@dataclass
class AIBall:
    """Une boule contrôlée par l'IA."""

    x: float
    y: float
    radius: float = Config.AI_BALL_RADIUS
    hitbox_width: float = Config.ENEMY_HITBOX_SIZES[1][0]
    hitbox_height: float = Config.ENEMY_HITBOX_SIZES[1][1]
    vx: float = 0.0
    vy: float = 0.0
    color: tuple = field(default_factory=lambda: Config.AI_BALL_COLOR_1HP)
    hp: int = 1  # Points de vie
    max_hp: int = 1  # HP initiaux (pour déterminer la taille)
    on_ground: bool = False
    shoot_timer: int = 0  # Timer pour tirer
    facing_direction: int = 1  # 1 = droite, -1 = gauche

    def update_size(self):
        """Met à jour la hitbox selon le type d'ennemi (max_hp)."""
        if self.max_hp >= 3:
            self.radius = Config.AI_BALL_RADIUS_3HP
            self.hitbox_width, self.hitbox_height = Config.ENEMY_HITBOX_SIZES[3]
        elif self.max_hp == 2:
            self.radius = Config.AI_BALL_RADIUS_2HP
            self.hitbox_width, self.hitbox_height = Config.ENEMY_HITBOX_SIZES[2]
        else:
            self.radius = Config.AI_BALL_RADIUS_1HP
            self.hitbox_width, self.hitbox_height = Config.ENEMY_HITBOX_SIZES[1]

    @property
    def half_w(self) -> float:
        return self.hitbox_width / 2

    @property
    def half_h(self) -> float:
        return self.hitbox_height / 2

    @property
    def mass(self) -> float:
        """Masse proportionnelle au rayon."""
        return self.half_w * self.half_h

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
        if self.vx > 0.2:
            self.facing_direction = 1
        elif self.vx < -0.2:
            self.facing_direction = -1

        # Mettre à jour position
        self.x += self.vx
        self.y += self.vy

        # Collision avec les murs
        self.x, self.y, self.vx, self.vy, self.on_ground, _ = \
            physics.check_wall_collision_ellipse(
                self.x, self.y, self.half_w, self.half_h, self.vx, self.vy
            )

        # Collision avec les obstacles
        for obs in obstacles:
            if not obs.is_solid():
                continue

            self.x, self.y, self.vx, self.vy, hit, on_top = \
                physics.check_rect_collision_ellipse(
                    self.x, self.y, self.half_w, self.half_h,
                    self.vx, self.vy,
                    obs.x, obs.y, obs.width, obs.height
                )
            if on_top:
                self.on_ground = True

    @classmethod
    def create_random(cls, config: Config, index: int) -> 'AIBall':
        """Crée une boule IA à une position aléatoire avec couleur et HP aléatoires."""
        wall = config.WALL_THICKNESS

        # Choisir aléatoirement les HP initiaux (1, 2 ou 3)
        hp = random.randint(1, 3)

        # Déterminer rayon et couleur selon HP
        if hp == 3:
            ball_radius = config.AI_BALL_RADIUS_3HP
            color = config.AI_BALL_COLOR_3HP
            hitbox_w, hitbox_h = config.ENEMY_HITBOX_SIZES[3]
        elif hp == 2:
            ball_radius = config.AI_BALL_RADIUS_2HP
            color = config.AI_BALL_COLOR_2HP
            hitbox_w, hitbox_h = config.ENEMY_HITBOX_SIZES[2]
        else:
            ball_radius = config.AI_BALL_RADIUS_1HP
            color = config.AI_BALL_COLOR_1HP
            hitbox_w, hitbox_h = config.ENEMY_HITBOX_SIZES[1]

        initial_vx = random.uniform(-2, 2)
        return cls(
            x=random.uniform(wall + hitbox_w / 2 + 10, config.PLAY_AREA_WIDTH - wall - hitbox_w / 2 - 10),
            y=random.uniform(wall + hitbox_h / 2 + 10, config.PLAY_AREA_HEIGHT // 2),
            radius=ball_radius,
            hitbox_width=hitbox_w,
            hitbox_height=hitbox_h,
            vx=initial_vx,
            vy=0,
            color=color,
            hp=hp,
            max_hp=hp,
            facing_direction=1 if initial_vx >= 0 else -1
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
        if (self.x < wall - self.radius or self.x > config.PLAY_AREA_WIDTH - wall + self.radius or
            self.y < wall - self.radius or self.y > config.PLAY_AREA_HEIGHT - wall + self.radius):
            self.active = False

    def check_collision(self, ball_x: float, ball_y: float, half_w: float, half_h: float) -> bool:
        """Vérifie la collision avec une hitbox elliptique."""
        ndx = (self.x - ball_x) / max(half_w + self.radius, 1e-6)
        ndy = (self.y - ball_y) / max(half_h + self.radius, 1e-6)
        return ndx * ndx + ndy * ndy < 1.0

    def check_obstacle_collision(self, obstacle) -> bool:
        """Vérifie la collision avec un obstacle (plateforme)."""
        # Point le plus proche du rectangle au centre de la bulle
        closest_x = max(obstacle.x, min(self.x, obstacle.x + obstacle.width))
        closest_y = max(obstacle.y, min(self.y, obstacle.y + obstacle.height))

        # Distance entre le point le plus proche et le centre de la bulle
        distance_x = self.x - closest_x
        distance_y = self.y - closest_y
        distance_squared = distance_x * distance_x + distance_y * distance_y

        return distance_squared < (self.radius * self.radius)


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
        if self.y > config.PLAY_AREA_HEIGHT:
            self.active = False

    def check_collision(self, ball_x: float, ball_y: float, half_w: float, half_h: float) -> bool:
        """Vérifie la collision avec le joueur (ellipse approximative)."""
        ndx = (self.x - ball_x) / max(half_w + self.size, 1e-6)
        ndy = (self.y - ball_y) / max(half_h + self.size, 1e-6)
        return ndx * ndx + ndy * ndy < 1.0


@dataclass
class Missile:
    """Un missile tiré par le joueur."""

    x: float
    y: float
    width: float = Config.MISSILE_WIDTH
    height: float = Config.MISSILE_HEIGHT
    speed: float = Config.MISSILE_SPEED
    direction: int = 1  # 1 = droite, -1 = gauche
    direction_y: int = 0  # -1 = haut, 0 = horizontal, 1 = bas
    color: tuple = field(default_factory=lambda: Config.MISSILE_COLOR)
    active: bool = True
    charged: bool = False  # Missile chargé ou non

    def update(self, config: Config):
        """Met à jour la position du missile."""
        self.x += self.speed * self.direction
        if self.direction_y != 0:
            self.y += self.speed * self.direction_y

        # Les missiles chargés traversent les murs, les normaux non
        if not self.charged:
            wall = config.WALL_THICKNESS
            if self.x < wall or self.x > config.PLAY_AREA_WIDTH - wall:
                self.active = False
            if self.y < wall or self.y > config.PLAY_AREA_HEIGHT - wall:
                self.active = False
        else:
            # Désactiver le missile chargé seulement s'il sort complètement de l'écran
            if self.x + self.width < 0 or self.x > config.PLAY_AREA_WIDTH:
                self.active = False
            if self.y + self.height < 0 or self.y > config.PLAY_AREA_HEIGHT:
                self.active = False

    def check_collision(self, ball_x: float, ball_y: float, half_w: float, half_h: float) -> bool:
        """Vérifie la collision missile (rect) vs ellipse."""
        closest_x = max(self.x, min(ball_x, self.x + self.width))
        closest_y = max(self.y, min(ball_y, self.y + self.height))
        ndx = (ball_x - closest_x) / max(half_w, 1e-6)
        ndy = (ball_y - closest_y) / max(half_h, 1e-6)
        return ndx * ndx + ndy * ndy < 1.0

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
    speed: float = Config.MOVING_PLATFORM_SPEED_SLOW
    direction: int = 1  # 1 = droite, -1 = gauche
    color: tuple = field(default_factory=lambda: Config.COLOR_PLATFORM_SLOW)

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
        speed: float = Config.MOVING_PLATFORM_SPEED_SLOW,
        is_fast: bool = False
    ) -> 'MovingPlatform':
        """
        Crée une plateforme mobile.

        Args:
            x: Position X initiale
            y: Position Y
            width: Largeur de la plateforme
            travel_distance: Distance totale de déplacement
            speed: Vitesse de déplacement
            is_fast: Si True, plateforme rapide (sinon lente)
        """
        # Choisir couleur selon vitesse
        color = Config.COLOR_PLATFORM_FAST if is_fast else Config.COLOR_PLATFORM_SLOW
        return cls(
            x=x,
            y=y,
            width=width,
            height=20,
            min_x=x,
            max_x=x + travel_distance,
            speed=speed,
            color=color
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

    def check_collision(self, ball_x: float, ball_y: float, half_w: float, half_h: float) -> bool:
        """Vérifie si le joueur touche la porte."""
        if not self.active:
            return False

        closest_x = max(self.x, min(ball_x, self.x + self.width))
        closest_y = max(self.y, min(ball_y, self.y + self.height))
        ndx = (ball_x - closest_x) / max(half_w, 1e-6)
        ndy = (ball_y - closest_y) / max(half_h, 1e-6)
        return ndx * ndx + ndy * ndy < 1.0
