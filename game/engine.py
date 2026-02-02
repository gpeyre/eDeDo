"""
Moteur de jeu principal.

Gère la boucle de jeu, les entrées et la coordination des composants.
"""

from enum import Enum, auto
import random
import pygame
from .config import Config
from .physics import PhysicsEngine
from .entities import Ball, Obstacle, MovingPlatform, AIBall, Missile, EnemyBullet, HeartPickup, Door
from .particles import ParticleSystem
from .renderer import Renderer
from .audio import AudioManager, SoundType


class GameState(Enum):
    """États possibles du jeu."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class GameEngine:
    """Moteur de jeu principal orchestrant tous les composants."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.running = False
        self.clock = None
        self.screen = None
        self.renderer = None
        self.physics = None
        self.ball = None
        self.obstacles = []
        self.ai_balls = []
        self.missiles = []
        self.enemy_bullets = []  # Bulles tirées par les ennemis
        self.heart_pickups = []  # Coeurs qui tombent
        self.heart_spawn_timer = 0
        self.game_over_timer = 0  # Timer pour animation game over
        self.audio = None
        self.state = GameState.MENU
        self.selected_color_index = 0
        self.pause_menu_index = 0  # 0 = Reprendre, 1 = Menu
        self.spawn_timer = 0
        self.missile_charging = False
        self.missile_charge_timer = 0
        self.fire_cooldown = 0  # Cooldown pour tir automatique
        self.space_key_hold_timer = 0  # Timer pour F maintenu
        self.was_grounded_during_charge = False  # Pour savoir si on était au sol pendant la charge
        self.joystick = None  # Manette
        self.enemies_defeated = 0  # Compteur d'ennemis vaincus
        self.door = None  # La porte vers le prochain niveau
        self.current_level = 1  # Niveau actuel

    def init(self):
        """Initialise Pygame et les composants du jeu."""
        pygame.init()
        pygame.display.set_caption(self.config.TITLE)

        self.screen = pygame.display.set_mode(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen, self.config)
        self.physics = PhysicsEngine(self.config)
        self.particles = ParticleSystem(self.config)
        self.audio = AudioManager(
            enabled=self.config.AUDIO_ENABLED,
            master_volume=self.config.AUDIO_MASTER_VOLUME
        )

        # Initialiser la manette si disponible
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Manette détectée: {self.joystick.get_name()}")

    def _create_level(self):
        """Crée le niveau avec la boule et les obstacles."""
        cfg = self.config

        # Position initiale de la boule (tout en haut, tombe) avec couleur sélectionnée
        selected_color = cfg.PLAYER_BALL_COLORS[self.selected_color_index]
        self.ball = Ball(
            x=cfg.WINDOW_WIDTH // 2,
            y=cfg.WALL_THICKNESS + cfg.BALL_RADIUS + 5,
            color=selected_color
        )

        # Générer obstacles aléatoirement
        self.obstacles = []

        # Toujours une plateforme en bas au centre (spawn safe)
        self.obstacles.append(
            Obstacle.create_platform(250, 450, 300)
        )

        # Nombre aléatoire de plateformes statiques (3-6)
        num_static = random.randint(3, 6)
        for _ in range(num_static):
            x = random.randint(cfg.WALL_THICKNESS + 50, cfg.WINDOW_WIDTH - cfg.WALL_THICKNESS - 200)
            y = random.randint(150, 400)
            width = random.randint(80, 180)
            self.obstacles.append(Obstacle.create_platform(x, y, width))

        # Nombre aléatoire de plateformes mobiles (2-4)
        num_moving = random.randint(2, 4)
        for _ in range(num_moving):
            x = random.randint(cfg.WALL_THICKNESS + 50, cfg.WINDOW_WIDTH - cfg.WALL_THICKNESS - 200)
            y = random.randint(100, 350)
            width = random.randint(100, 160)
            travel = random.randint(150, 300)
            speed = random.uniform(1.5, 3.0)
            self.obstacles.append(
                MovingPlatform.create(x, y, width, travel, speed)
            )

        # Quelques blocs (1-3)
        num_blocks = random.randint(1, 3)
        for _ in range(num_blocks):
            x = random.randint(cfg.WALL_THICKNESS + 50, cfg.WINDOW_WIDTH - cfg.WALL_THICKNESS - 100)
            y = random.randint(100, 300)
            size = random.randint(40, 70)
            self.obstacles.append(Obstacle.create_block(x, y, size))

        # Créer les boules IA
        self.ai_balls = [
            AIBall.create_random(cfg, i)
            for i in range(cfg.AI_BALL_COUNT)
        ]

        # Créer la porte (en haut à droite, initialement inactive)
        self.door = Door(
            x=cfg.WINDOW_WIDTH - cfg.WALL_THICKNESS - 80,
            y=cfg.WALL_THICKNESS + 20
        )

    def handle_events(self):
        """Gère les événements Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    self._handle_menu_keydown(event.key)
                else:
                    self._handle_game_keydown(event.key)
            elif event.type == pygame.KEYUP:
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.ball.stop_floating()
            # Gestion manette
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.state == GameState.PLAYING:
                    if event.button == 0:  # Bouton A = saut
                        self._handle_game_keydown(pygame.K_UP)
                    elif event.button == 7:  # Bouton Start = pause
                        self.state = GameState.PAUSED
                        self.pause_menu_index = 0
                elif self.state == GameState.PAUSED:
                    if event.button == 0:  # A = sélectionner option pause
                        if self.pause_menu_index == 0:  # Reprendre
                            self.state = GameState.PLAYING
                        else:  # Retour menu
                            self.state = GameState.MENU
                    elif event.button == 7:  # Start = reprendre directement
                        self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER:
                    # N'importe quel bouton après les 2 premières secondes
                    if self.game_over_timer >= 120:
                        self.state = GameState.MENU
                        self.game_over_timer = 0
                elif self.state == GameState.MENU:
                    if event.button == 0:  # A = sélectionner
                        self._handle_menu_keydown(pygame.K_RETURN)
            elif event.type == pygame.JOYBUTTONUP:
                if self.state == GameState.PLAYING:
                    if event.button == 1:  # Bouton B relâché = stop float
                        self.ball.stop_floating()
            elif event.type == pygame.JOYHATMOTION:
                if self.state == GameState.MENU:
                    if event.value[1] == 1:  # D-pad haut
                        self._handle_menu_keydown(pygame.K_UP)
                    elif event.value[1] == -1:  # D-pad bas
                        self._handle_menu_keydown(pygame.K_DOWN)
                    elif event.value[0] == -1:  # D-pad gauche
                        self._handle_menu_keydown(pygame.K_LEFT)
                    elif event.value[0] == 1:  # D-pad droite
                        self._handle_menu_keydown(pygame.K_RIGHT)
                elif self.state == GameState.PAUSED:
                    if event.value[1] == 1:  # D-pad haut
                        self.pause_menu_index = 0
                    elif event.value[1] == -1:  # D-pad bas
                        self.pause_menu_index = 1
            elif event.type == pygame.JOYAXISMOTION:
                # Stick analogique pour menu
                if self.state == GameState.MENU and event.axis == 0:  # Axe horizontal
                    if event.value < -0.5:  # Gauche
                        self._handle_menu_keydown(pygame.K_LEFT)
                    elif event.value > 0.5:  # Droite
                        self._handle_menu_keydown(pygame.K_RIGHT)

    def _handle_menu_keydown(self, key):
        """Gère les touches du menu."""
        cfg = self.config
        num_colors = len(cfg.PLAYER_BALL_COLORS)

        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_LEFT:
            self.selected_color_index = (self.selected_color_index - 1) % num_colors
        elif key == pygame.K_RIGHT:
            self.selected_color_index = (self.selected_color_index + 1) % num_colors
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._start_game()

    def _handle_game_keydown(self, key):
        """Gère les touches du jeu."""
        if key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif key == pygame.K_UP:
            # Vérifier si un saut est possible et quel type
            can_jump = self.ball.can_jump()
            will_be_double = self.ball.is_double_jump()

            # Effectuer le saut
            is_double_jump = self.ball.jump()

            # Jouer le son approprié si le saut a été effectué
            if is_double_jump:
                self.audio.play(SoundType.DOUBLE_JUMP)
                self.particles.spawn_double_jump(
                    self.ball.x, self.ball.y, self.ball.radius
                )
            elif can_jump and not will_be_double:
                # Saut simple effectué
                self.audio.play(SoundType.JUMP)
        elif key == pygame.K_r:
            self._create_level()  # Reset
            self.particles.clear()

    def _start_game(self):
        """Démarre le jeu avec la couleur sélectionnée."""
        self._create_level()
        self.particles.clear()
        self.missiles = []
        self.spawn_timer = 0
        self.enemies_defeated = 0  # Reset le compteur
        self.current_level = 1  # Reset le niveau
        self.state = GameState.PLAYING

    def _fire_missile(self, direction: int):
        """Tire un missile dans la direction donnée."""
        # Vérifier si assez d'énergie
        if self.ball.energy < self.config.MISSILE_ENERGY_COST:
            return  # Pas assez d'énergie

        # Consommer l'énergie
        self.ball.energy -= self.config.MISSILE_ENERGY_COST
        self.ball.energy_usage_timer = 0  # Reset le timer

        # Position de départ du missile (à côté de la boule)
        offset_x = (self.ball.radius + self.config.MISSILE_WIDTH / 2) * direction
        missile = Missile(
            x=self.ball.x + offset_x,
            y=self.ball.y - self.config.MISSILE_HEIGHT / 2,
            direction=direction,
            charged=False
        )
        self.missiles.append(missile)

    def _fire_charged_missile(self, direction: int):
        """Tire un missile chargé."""
        # Si on n'était PAS au sol pendant la charge, consommer l'énergie maintenant
        if not self.was_grounded_during_charge:
            if self.ball.energy < self.config.CHARGED_MISSILE_COST:
                return  # Pas assez d'énergie
            self.ball.energy -= self.config.CHARGED_MISSILE_COST
            self.ball.energy_usage_timer = 0  # Reset le timer
        # Sinon l'énergie a déjà été consommée progressivement

        # Position de départ du missile chargé
        offset_x = (self.ball.radius + self.config.CHARGED_MISSILE_WIDTH / 2) * direction
        missile = Missile(
            x=self.ball.x + offset_x,
            y=self.ball.y - self.config.CHARGED_MISSILE_HEIGHT / 2,
            width=self.config.CHARGED_MISSILE_WIDTH,
            height=self.config.CHARGED_MISSILE_HEIGHT,
            speed=self.config.CHARGED_MISSILE_SPEED,
            direction=direction,
            color=self.config.CHARGED_MISSILE_COLOR,
            charged=True
        )
        self.missiles.append(missile)
        self.audio.play(SoundType.JUMP, 1.0)  # Son de tir

    def handle_input(self):
        """Gère les entrées clavier et manette continues."""
        keys = pygame.key.get_pressed()

        # Gestion manette
        joy_left = False
        joy_right = False
        joy_float = False
        joy_fire = False

        if self.joystick:
            # Stick analogique gauche (axe 0 = horizontal)
            axis_x = self.joystick.get_axis(0)
            if axis_x < -0.3:  # Seuil de déclenchement
                joy_left = True
            elif axis_x > 0.3:
                joy_right = True

            # D-pad (chapeau)
            if self.joystick.get_numhats() > 0:
                hat = self.joystick.get_hat(0)
                if hat[0] < 0:
                    joy_left = True
                elif hat[0] > 0:
                    joy_right = True

            # Boutons : A (0) = saut, B (1) = float, X (2) = tir
            if self.joystick.get_button(1):  # B
                joy_float = True
            if self.joystick.get_button(2):  # X
                joy_fire = True

        # Mouvement
        if keys[pygame.K_LEFT] or keys[pygame.K_a] or joy_left:
            self.ball.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] or joy_right:
            self.ball.move_right()
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or joy_float:
            self.ball.start_floating()

        # Espace maintenu ou bouton manette : tir automatique OU charge
        if keys[pygame.K_SPACE] or joy_fire:
            self.space_key_hold_timer += 1

            # Si maintenu assez longtemps (30 frames = 0.5s), commencer la charge
            if self.space_key_hold_timer >= 30 and not self.missile_charging:
                self.missile_charging = True
                self.missile_charge_timer = 0
                self.was_grounded_during_charge = self.ball.on_ground
                self.fire_cooldown = 0  # Reset cooldown
            # Sinon, tir automatique rapide
            elif not self.missile_charging and self.space_key_hold_timer < 30:
                if self.fire_cooldown <= 0:
                    self._fire_missile(self.ball.facing_direction)
                    self.fire_cooldown = 15
        else:
            # F relâché
            if self.missile_charging and self.missile_charge_timer >= self.config.CHARGED_MISSILE_CHARGE_TIME:
                # Tirer le missile chargé
                self._fire_charged_missile(self.ball.facing_direction)
            self.missile_charging = False
            self.missile_charge_timer = 0
            self.space_key_hold_timer = 0

    def update(self):
        """Met à jour l'état du jeu."""
        # Si game over, continuer l'animation
        if self.state == GameState.GAME_OVER:
            self.game_over_timer += 1
            self.particles.update()  # Continuer l'animation des particules
            return

        # Décrémenter le cooldown de tir
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        # Gérer la charge du missile
        if self.missile_charging:
            self.missile_charge_timer += 1

            # Consommer l'énergie progressivement SEULEMENT si au sol pendant la charge
            if self.was_grounded_during_charge:
                energy_per_frame = self.config.CHARGED_MISSILE_COST / self.config.CHARGED_MISSILE_CHARGE_TIME
                self.ball.energy -= energy_per_frame
                self.ball.energy_usage_timer = 0  # Reset le timer

                # Arrêter la charge si plus d'énergie
                if self.ball.energy <= 0:
                    self.ball.energy = 0
                    self.missile_charging = False
                    self.missile_charge_timer = 0

        # Mettre à jour les obstacles (plateformes mobiles)
        for obs in self.obstacles:
            obs.update()

        # Mettre à jour la boule et récupérer les collisions
        collisions = self.ball.update(self.physics, self.obstacles)

        # Vérifier si mort (0 vie)
        if self.ball.lives <= 0:
            self.state = GameState.GAME_OVER
            self.game_over_timer = 0
            # Son de mort (réutiliser le son de perte de vie mais plus grave)
            self.audio.play(SoundType.LIFE_LOST, 1.0)
            # Grande explosion de particules
            for _ in range(30):
                angle = random.uniform(0, 2 * 3.14159)
                speed = random.uniform(2, 8)
                self.particles.spawn_directional(
                    self.ball.x, self.ball.y,
                    speed * (angle % 1), speed * ((angle + 1) % 1), 5.0
                )
            return  # Arrêter la mise à jour

        # Créer des particules et jouer sons pour chaque collision
        for x, y, dir_x, dir_y, intensity in collisions:
            self.particles.spawn_directional(x, y, dir_x, dir_y, intensity)
            # Son différent selon le type de collision
            if dir_y == -1:  # Impact sur plateforme/sol
                self.audio.play(SoundType.PLATFORM_IMPACT, min(1.0, intensity))
            else:  # Impact sur mur
                self.audio.play(SoundType.WALL_IMPACT, min(1.0, intensity))

        # Mettre à jour les missiles et créer des trainées
        for missile in self.missiles:
            # Créer une petite trainée
            if random.random() < 0.3:  # 30% de chance par frame
                self.particles.spawn_missile_trail(
                    missile.x + missile.width / 2,
                    missile.y + missile.height / 2
                )
            missile.update(self.config)

            # Vérifier collision avec obstacles
            for obstacle in self.obstacles:
                if missile.check_obstacle_collision(obstacle):
                    missile.active = False
                    # Si missile chargé, créer une explosion
                    if missile.charged:
                        self.particles.spawn_explosion(
                            missile.x + missile.width / 2,
                            missile.y + missile.height / 2,
                            2.0
                        )
                        self.audio.play(SoundType.BALL_COLLISION, 1.0)
                    break

        # Retirer les missiles inactifs
        self.missiles = [m for m in self.missiles if m.active]

        # Vérifier les collisions missile-ennemi
        enemies_to_remove = []
        missiles_to_remove = []
        for missile in self.missiles[:]:  # Copie de la liste pour itération sûre
            if not missile.active:
                continue

            # Si missile chargé, vérifier explosion de zone
            if missile.charged:
                explosion_x = missile.x + missile.width / 2
                explosion_y = missile.y + missile.height / 2
                for ai_ball in self.ai_balls[:]:
                    # Distance entre missile et ennemi
                    dist_x = ai_ball.x - explosion_x
                    dist_y = ai_ball.y - explosion_y
                    distance = (dist_x * dist_x + dist_y * dist_y) ** 0.5

                    if distance < self.config.CHARGED_MISSILE_EXPLOSION_RADIUS:
                        if ai_ball not in enemies_to_remove:
                            enemies_to_remove.append(ai_ball)
                            self.particles.spawn_enemy_destruction(
                                ai_ball.x, ai_ball.y, ai_ball.color
                            )

                # Si collision directe avec missile chargé, le détruire
                for ai_ball in self.ai_balls[:]:
                    if missile.check_collision(ai_ball.x, ai_ball.y, ai_ball.radius):
                        if missile not in missiles_to_remove:
                            missiles_to_remove.append(missile)
                        # Grande explosion
                        self.particles.spawn_explosion(explosion_x, explosion_y, 3.0)
                        self.audio.play(SoundType.BALL_COLLISION, 1.0)
                        break
            else:
                # Missile normal - réduit les HP
                for ai_ball in self.ai_balls[:]:
                    if missile.check_collision(ai_ball.x, ai_ball.y, ai_ball.radius):
                        # Réduire les HP
                        ai_ball.hp -= 1
                        ai_ball.update_color()  # Mettre à jour la couleur selon les nouveaux HP

                        if missile not in missiles_to_remove:
                            missiles_to_remove.append(missile)

                        # Si HP à 0, détruire l'ennemi
                        if ai_ball.hp <= 0:
                            if ai_ball not in enemies_to_remove:
                                enemies_to_remove.append(ai_ball)
                            # Effet de destruction avec la couleur de l'ennemi
                            self.particles.spawn_enemy_destruction(
                                ai_ball.x, ai_ball.y, ai_ball.color
                            )
                            self.audio.play(SoundType.BALL_COLLISION, 0.8)
                        else:
                            # Juste un petit effet de hit
                            self.particles.spawn_directional(
                                ai_ball.x, ai_ball.y, 0, 0, 2.0
                            )
                            self.audio.play(SoundType.BALL_COLLISION, 0.4)
                        break

        # Retirer les ennemis et missiles touchés
        for ball in enemies_to_remove:
            if ball in self.ai_balls:
                self.ai_balls.remove(ball)
                self.enemies_defeated += 1  # Incrémenter le compteur
        for missile in missiles_to_remove:
            if missile in self.missiles:
                self.missiles.remove(missile)

        # Activer la porte si assez d'ennemis vaincus
        if self.enemies_defeated >= self.config.ENEMIES_TO_WIN:
            self.door.active = True

        # Spawn d'ennemis si moins de 6
        if len(self.ai_balls) < self.config.ENEMY_MAX_COUNT:
            self.spawn_timer += 1
            if self.spawn_timer >= self.config.ENEMY_SPAWN_INTERVAL:
                self.spawn_timer = 0
                # Spawner un nouvel ennemi en haut avec HP aléatoires
                wall = self.config.WALL_THICKNESS
                hp = random.randint(1, 3)

                # Déterminer rayon et couleur selon HP
                if hp == 3:
                    ball_radius = self.config.AI_BALL_RADIUS_3HP
                    color = self.config.AI_BALL_COLOR_3HP
                elif hp == 2:
                    ball_radius = self.config.AI_BALL_RADIUS_2HP
                    color = self.config.AI_BALL_COLOR_2HP
                else:
                    ball_radius = self.config.AI_BALL_RADIUS_1HP
                    color = self.config.AI_BALL_COLOR_1HP

                margin = ball_radius + 10
                new_enemy = AIBall(
                    x=random.uniform(wall + margin, self.config.WINDOW_WIDTH - wall - margin),
                    y=wall + margin,
                    radius=ball_radius,
                    vx=random.uniform(-2, 2),
                    vy=0,
                    color=color,
                    hp=hp,
                    max_hp=hp
                )
                self.ai_balls.append(new_enemy)

        # Mettre à jour les boules IA et les faire tirer
        for ai_ball in self.ai_balls:
            ai_ball.update(self.physics, self.obstacles)

            # Timer de tir
            ai_ball.shoot_timer += 1
            if ai_ball.shoot_timer >= random.randint(120, 240):  # Tir toutes les 2-4 secondes
                ai_ball.shoot_timer = 0
                # Tirer à gauche et à droite
                bullet_speed = 4
                self.enemy_bullets.append(EnemyBullet(
                    x=ai_ball.x, y=ai_ball.y, vx=-bullet_speed, vy=0
                ))
                self.enemy_bullets.append(EnemyBullet(
                    x=ai_ball.x, y=ai_ball.y, vx=bullet_speed, vy=0
                ))

        # Mettre à jour les bulles ennemies
        for bullet in self.enemy_bullets:
            bullet.update(self.config)

        # Retirer les bulles inactives
        self.enemy_bullets = [b for b in self.enemy_bullets if b.active]

        # Collision missiles joueur vs bulles ennemies (annulation mutuelle)
        missiles_to_remove_collision = []
        bullets_to_remove_collision = []
        for missile in self.missiles[:]:
            for bullet in self.enemy_bullets[:]:
                # Vérifier collision missile-bulle
                dx = missile.x + missile.width / 2 - bullet.x
                dy = missile.y + missile.height / 2 - bullet.y
                distance = (dx * dx + dy * dy) ** 0.5

                if distance < bullet.radius + max(missile.width, missile.height) / 2:
                    # Collision ! Détruire les deux
                    if missile not in missiles_to_remove_collision:
                        missiles_to_remove_collision.append(missile)
                    if bullet not in bullets_to_remove_collision:
                        bullets_to_remove_collision.append(bullet)
                    # Petites particules
                    self.particles.spawn_directional(
                        bullet.x, bullet.y, 0, 0, 1.5
                    )
                    self.audio.play(SoundType.BALL_COLLISION, 0.3)
                    break

        # Retirer missiles et bulles qui se sont annulés
        for missile in missiles_to_remove_collision:
            if missile in self.missiles:
                self.missiles.remove(missile)
        for bullet in bullets_to_remove_collision:
            if bullet in self.enemy_bullets:
                self.enemy_bullets.remove(bullet)

        # Collision bulles ennemies avec joueur
        bullets_to_remove = []
        for bullet in self.enemy_bullets:
            if bullet.check_collision(self.ball.x, self.ball.y, self.ball.radius):
                if self.ball.invincible_timer <= 0:
                    # Perte d'une vie
                    self.ball.lives -= 1
                    self.ball.invincible_timer = 90  # 1.5 secondes d'invincibilité
                    # Son fun de perte de vie
                    self.audio.play(SoundType.LIFE_LOST, 0.8)
                    # Particules
                    self.particles.spawn_directional(
                        self.ball.x, self.ball.y, 0, 0, 3.0
                    )
                bullets_to_remove.append(bullet)

        for bullet in bullets_to_remove:
            if bullet in self.enemy_bullets:
                self.enemy_bullets.remove(bullet)

        # Spawn de coeurs si < 5 vies
        if self.ball.lives < 5:
            self.heart_spawn_timer += 1
            if self.heart_spawn_timer >= 300:  # Toutes les 5 secondes
                self.heart_spawn_timer = 0
                wall = self.config.WALL_THICKNESS
                heart_x = random.uniform(wall + 50, self.config.WINDOW_WIDTH - wall - 50)
                self.heart_pickups.append(HeartPickup(x=heart_x, y=wall + 20))

        # Mettre à jour les coeurs
        for heart in self.heart_pickups:
            heart.update(self.config)

        # Collision coeurs avec joueur
        hearts_to_remove = []
        for heart in self.heart_pickups:
            if heart.check_collision(self.ball.x, self.ball.y, self.ball.radius):
                if self.ball.lives < 5:
                    self.ball.lives += 1
                    self.audio.play(SoundType.DOUBLE_JUMP, 0.6)  # Son joyeux
                hearts_to_remove.append(heart)

        for heart in hearts_to_remove:
            if heart in self.heart_pickups:
                self.heart_pickups.remove(heart)

        # Retirer coeurs inactifs
        self.heart_pickups = [h for h in self.heart_pickups if h.active]

        # Collisions entre boules IA
        for i, ball1 in enumerate(self.ai_balls):
            for ball2 in self.ai_balls[i + 1:]:
                result = self.physics.check_ball_collision(
                    ball1.x, ball1.y, ball1.radius, ball1.vx, ball1.vy, ball1.mass,
                    ball2.x, ball2.y, ball2.radius, ball2.vx, ball2.vy, ball2.mass
                )
                if result[8]:  # Collision occurred
                    ball1.x, ball1.y, ball1.vx, ball1.vy = result[0:4]
                    ball2.x, ball2.y, ball2.vx, ball2.vy = result[4:8]
                    # Particules de collision
                    mid_x = (ball1.x + ball2.x) / 2
                    mid_y = (ball1.y + ball2.y) / 2
                    speed = ((ball1.vx - ball2.vx) ** 2 + (ball1.vy - ball2.vy) ** 2) ** 0.5
                    self.particles.spawn_ball_collision(mid_x, mid_y, speed / 5)
                    # Son de collision
                    self.audio.play(SoundType.BALL_COLLISION, min(1.0, speed / 10))

        # Collision entre joueur et boules IA avec détection directionnelle
        enemies_to_remove_collision = []
        for ai_ball in self.ai_balls:
            # Calculer la distance avant collision
            dx = ai_ball.x - self.ball.x
            dy = ai_ball.y - self.ball.y
            distance = (dx * dx + dy * dy) ** 0.5

            # Vérifier s'il y a collision
            if distance < self.ball.radius + ai_ball.radius:
                # Sauvegarder l'ancienne vitesse Y du joueur pour détecter le saut
                old_ball_vy = self.ball.vy

                # Détection directionnelle: saut sur la tête si le joueur tombe (vy > 2) et vient d'en haut
                jumping_on_head = old_ball_vy > 2 and self.ball.y < ai_ball.y

                if jumping_on_head:
                    # Saut sur la tête: retirer 1 HP à l'ennemi
                    ai_ball.hp -= 1
                    ai_ball.update_color()

                    # Faire rebondir le joueur
                    self.ball.vy = -8  # Petit rebond

                    # Particules de hit
                    self.particles.spawn_directional(
                        ai_ball.x, ai_ball.y, 0, 0, 3.0
                    )
                    self.audio.play(SoundType.BALL_COLLISION, 0.6)

                    # Si HP à 0, détruire l'ennemi
                    if ai_ball.hp <= 0:
                        if ai_ball not in enemies_to_remove_collision:
                            enemies_to_remove_collision.append(ai_ball)
                            self.enemies_defeated += 1  # Incrémenter le compteur
                        self.particles.spawn_enemy_destruction(
                            ai_ball.x, ai_ball.y, ai_ball.color
                        )
                        self.audio.play(SoundType.BALL_COLLISION, 0.8)
                else:
                    # Collision latérale: le joueur perd une vie si pas invincible
                    if self.ball.invincible_timer <= 0:
                        self.ball.lives -= 1
                        self.ball.invincible_timer = 90  # 1.5 secondes d'invincibilité
                        self.audio.play(SoundType.LIFE_LOST, 0.8)
                        self.particles.spawn_directional(
                            self.ball.x, self.ball.y, 0, 0, 3.0
                        )

                    # Appliquer la physique normale de collision
                    result = self.physics.check_ball_collision(
                        self.ball.x, self.ball.y, self.ball.radius,
                        self.ball.vx, self.ball.vy, self.ball.radius ** 2,
                        ai_ball.x, ai_ball.y, ai_ball.radius,
                        ai_ball.vx, ai_ball.vy, ai_ball.mass
                    )
                    if result[8]:  # Collision occurred
                        self.ball.x, self.ball.y, self.ball.vx, self.ball.vy = result[0:4]
                        ai_ball.x, ai_ball.y, ai_ball.vx, ai_ball.vy = result[4:8]
                        # Particules de collision
                        mid_x = (self.ball.x + ai_ball.x) / 2
                        mid_y = (self.ball.y + ai_ball.y) / 2
                        speed = ((self.ball.vx - ai_ball.vx) ** 2 + (self.ball.vy - ai_ball.vy) ** 2) ** 0.5
                        self.particles.spawn_ball_collision(mid_x, mid_y, speed / 4)

        # Retirer les ennemis tués par saut sur la tête
        for ball in enemies_to_remove_collision:
            if ball in self.ai_balls:
                self.ai_balls.remove(ball)

        # Vérifier collision avec la porte
        if self.door.check_collision(self.ball.x, self.ball.y, self.ball.radius):
            # Passer au niveau suivant
            self.current_level += 1
            self._create_level()
            self.particles.clear()
            self.missiles = []
            self.enemy_bullets = []
            self.heart_pickups = []
            self.enemies_defeated = 0  # Reset le compteur pour le nouveau niveau
            self.spawn_timer = 0
            # Jouer un son de victoire
            self.audio.play(SoundType.DOUBLE_JUMP, 1.0)

        # Mettre à jour les particules
        self.particles.update()

    def render(self):
        """Dessine tous les éléments du jeu."""
        self.renderer.clear()
        self.renderer.draw_walls()
        self.renderer.draw_door(self.door)
        self.renderer.draw_obstacles(self.obstacles)
        self.renderer.draw_ai_balls(self.ai_balls)
        self.renderer.draw_enemy_bullets(self.enemy_bullets)
        self.renderer.draw_heart_pickups(self.heart_pickups)
        self.renderer.draw_missiles(self.missiles)
        self.renderer.draw_particles(self.particles)
        charge_percent = self.missile_charge_timer / self.config.CHARGED_MISSILE_CHARGE_TIME if self.missile_charging else 0.0
        self.renderer.draw_ball(self.ball, self.missile_charging, charge_percent)
        self.renderer.draw_hud(self.ball, len(self.ai_balls), self.missile_charging, self.missile_charge_timer, self.enemies_defeated, self.current_level)
        pygame.display.flip()

    def render_pause(self):
        """Dessine le menu de pause."""
        # Dessiner le jeu en arrière-plan
        self.renderer.clear()
        self.renderer.draw_walls()
        self.renderer.draw_door(self.door)
        self.renderer.draw_obstacles(self.obstacles)
        self.renderer.draw_ai_balls(self.ai_balls)
        self.renderer.draw_enemy_bullets(self.enemy_bullets)
        self.renderer.draw_heart_pickups(self.heart_pickups)
        self.renderer.draw_missiles(self.missiles)
        self.renderer.draw_particles(self.particles)
        charge_percent = self.missile_charge_timer / self.config.CHARGED_MISSILE_CHARGE_TIME if self.missile_charging else 0.0
        self.renderer.draw_ball(self.ball, self.missile_charging, charge_percent)
        self.renderer.draw_hud(self.ball, len(self.ai_balls), self.missile_charging, self.missile_charge_timer, self.enemies_defeated, self.current_level)

        # Overlay semi-transparent
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.renderer.screen.blit(overlay, (0, 0))

        # Texte "PAUSE"
        font_big = pygame.font.Font(None, 100)
        font_medium = pygame.font.Font(None, 50)

        pause_text = font_big.render("PAUSE", True, (200, 200, 255))
        text_rect = pause_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, 150))
        self.renderer.screen.blit(pause_text, text_rect)

        # Options du menu
        options = ["Reprendre", "Menu"]
        y_start = self.config.WINDOW_HEIGHT // 2 - 30

        for i, option in enumerate(options):
            if i == self.pause_menu_index:
                color = (255, 255, 100)  # Jaune si sélectionné
                text = f"> {option} <"
            else:
                color = (200, 200, 200)  # Gris sinon
                text = option

            option_text = font_medium.render(text, True, color)
            text_rect = option_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, y_start + i * 60))
            self.renderer.screen.blit(option_text, text_rect)

        pygame.display.flip()

    def render_game_over(self):
        """Dessine l'écran de game over."""
        # Fond sombre
        self.renderer.clear()

        # Dessiner les éléments du jeu en arrière-plan (figés)
        self.renderer.draw_walls()
        self.renderer.draw_obstacles(self.obstacles)
        self.renderer.draw_ai_balls(self.ai_balls)
        self.renderer.draw_particles(self.particles)

        # Afficher "GAME OVER" seulement après 2 secondes d'animation
        if self.game_over_timer >= 120:  # Après 2 secondes
            # Overlay sombre
            overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.renderer.screen.blit(overlay, (0, 0))

            # Texte "GAME OVER"
            font_big = pygame.font.Font(None, 100)
            font_small = pygame.font.Font(None, 40)

            game_over_text = font_big.render("GAME OVER", True, (255, 50, 50))
            text_rect = game_over_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT // 2 - 50))
            self.renderer.screen.blit(game_over_text, text_rect)

            # Texte retour au menu ou appuyer sur un bouton
            return_text = font_small.render("Appuyez sur un bouton...", True, (200, 200, 200))
            text_rect2 = return_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT // 2 + 50))
            self.renderer.screen.blit(return_text, text_rect2)

        pygame.display.flip()

    def render_menu(self):
        """Dessine le menu de sélection."""
        cfg = self.config
        self.renderer.draw_menu(
            self.selected_color_index,
            cfg.PLAYER_BALL_COLORS,
            cfg.PLAYER_BALL_NAMES
        )
        pygame.display.flip()

    def run(self):
        """Lance la boucle de jeu principale."""
        self.init()
        self.running = True

        while self.running:
            self.handle_events()

            if self.state == GameState.MENU:
                self.render_menu()
            elif self.state == GameState.PAUSED:
                self.render_pause()
            elif self.state == GameState.GAME_OVER:
                self.update()  # Continue l'animation
                self.render_game_over()
            else:
                self.handle_input()
                self.update()
                self.render()

            self.clock.tick(self.config.FPS)

        pygame.quit()
