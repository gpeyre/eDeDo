"""
Rendu graphique du jeu.

Gère l'affichage de tous les éléments visuels.
"""

import pygame
from pathlib import Path
from .config import Config
from .entities import Ball, Obstacle, FragilePlatform, AIBall, Missile
from .particles import ParticleSystem


class Renderer:
    """Gère le rendu graphique avec Pygame."""

    def __init__(self, screen: pygame.Surface, config: Config = None):
        self.screen = screen
        self.config = config or Config()
        self.background_image = None
        self.menu_background_image = None
        self.player_sprites = []
        self.enemy_sprites = {}
        self.heart_pickup_sprite = None
        self.heart_hud_sprite = None
        self.bullet_sprite = None
        self.bullet_super_sprite = None
        self.enemy_bullet_sprite = None
        self._load_assets()

    def _safe_load_scaled(self, path: Path, size: tuple[int, int]):
        """Charge et redimensionne une image PNG avec alpha."""
        try:
            image = pygame.image.load(str(path)).convert_alpha()
            return pygame.transform.smoothscale(image, size)
        except Exception:
            return None

    def _load_assets(self):
        """Charge les images (fond, persos, ennemis)."""
        cfg = self.config
        assets_dir = Path(cfg.ASSETS_DIR)

        self.background_image = self._safe_load_scaled(
            assets_dir / cfg.BACKGROUND_IMAGE,
            (cfg.PLAY_AREA_WIDTH, cfg.PLAY_AREA_HEIGHT)
        )
        self.menu_background_image = self._safe_load_scaled(
            assets_dir / cfg.MENU_BACKGROUND_IMAGE,
            (cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT)
        )

        self.player_sprites = []
        for index, image_name in enumerate(cfg.PLAYER_IMAGES):
            sprite = self._safe_load_scaled(
                assets_dir / image_name,
                cfg.PLAYER_SPRITE_SIZES[index]
            )
            self.player_sprites.append(sprite)

        self.enemy_sprites = {}
        for hp, image_name in cfg.ENEMY_IMAGES.items():
            self.enemy_sprites[hp] = self._safe_load_scaled(
                assets_dir / image_name,
                cfg.ENEMY_SPRITE_SIZES[hp]
            )

        self.heart_pickup_sprite = self._safe_load_scaled(
            assets_dir / cfg.HEART_IMAGE,
            cfg.HEART_PICKUP_SPRITE_SIZE
        )
        self.heart_hud_sprite = self._safe_load_scaled(
            assets_dir / cfg.HEART_IMAGE,
            cfg.HEART_HUD_SPRITE_SIZE
        )
        self.bullet_sprite = self._safe_load_scaled(
            assets_dir / cfg.BULLET_IMAGE,
            (36, 36)
        )
        self.bullet_super_sprite = self._safe_load_scaled(
            assets_dir / cfg.BULLET_SUPER_IMAGE,
            (72, 72)
        )
        self.enemy_bullet_sprite = self._safe_load_scaled(
            assets_dir / cfg.BULLET_ENEMY_IMAGE,
            cfg.ENEMY_BULLET_SPRITE_SIZE
        )

    def clear(self):
        """Efface l'écran avec la couleur de fond."""
        cfg = self.config
        self.screen.fill((24, 24, 30))
        pygame.draw.rect(
            self.screen,
            cfg.COLOR_BACKGROUND,
            (0, 0, cfg.PLAY_AREA_WIDTH, cfg.PLAY_AREA_HEIGHT)
        )
        pygame.draw.rect(
            self.screen,
            (32, 32, 42),
            (cfg.PLAY_AREA_WIDTH, 0, cfg.SIDEBAR_WIDTH, cfg.PLAY_AREA_HEIGHT)
        )
        pygame.draw.rect(
            self.screen,
            (28, 28, 36),
            (0, cfg.PLAY_AREA_HEIGHT, cfg.WINDOW_WIDTH, cfg.BOTTOM_PANEL_HEIGHT)
        )
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))

    def draw_walls(self):
        """Dessine les murs de la pièce."""
        cfg = self.config
        color = cfg.COLOR_WALL
        w = cfg.WALL_THICKNESS

        # Mur haut
        pygame.draw.rect(self.screen, color, (0, 0, cfg.PLAY_AREA_WIDTH, w))
        # Mur bas
        pygame.draw.rect(
            self.screen, color,
            (0, cfg.PLAY_AREA_HEIGHT - w, cfg.PLAY_AREA_WIDTH, w)
        )
        # Mur gauche
        pygame.draw.rect(self.screen, color, (0, 0, w, cfg.PLAY_AREA_HEIGHT))
        # Mur droit
        pygame.draw.rect(
            self.screen, color,
            (cfg.PLAY_AREA_WIDTH - w, 0, w, cfg.PLAY_AREA_HEIGHT)
        )

    def draw_secret_hole(self, side: int, y: float, is_open: bool):
        """Dessine le trou de la salle secrète sur un mur latéral."""
        if not is_open:
            return

        cfg = self.config
        hole_w = 12
        hole_h = cfg.SECRET_HOLE_HALF_HEIGHT * 2
        x = cfg.WALL_THICKNESS - hole_w // 2 if side == -1 else cfg.PLAY_AREA_WIDTH - cfg.WALL_THICKNESS - hole_w // 2
        rect = pygame.Rect(int(x), int(y - hole_h / 2), hole_w, hole_h)
        pygame.draw.rect(self.screen, (10, 10, 14), rect, border_radius=4)
        pygame.draw.rect(self.screen, (120, 170, 210), rect, 2, border_radius=4)

    def draw_ball(self, ball: Ball, missile_charging: bool = False, charge_percent: float = 0.0):
        """Dessine la boule."""
        sprite = None
        if 0 <= ball.character_index < len(self.player_sprites):
            sprite = self.player_sprites[ball.character_index]

        if sprite is not None:
            if ball.facing_direction < 0:
                sprite = pygame.transform.flip(sprite, True, False)
            sprite_rect = sprite.get_rect(center=(int(ball.x), int(ball.y)))
            self.screen.blit(sprite, sprite_rect)
        else:
            pygame.draw.ellipse(
                self.screen,
                ball.color,
                (
                    int(ball.x - ball.half_w),
                    int(ball.y - ball.half_h),
                    int(ball.hitbox_width),
                    int(ball.hitbox_height)
                )
            )

        # Effet de brillance supplémentaire quand chargé à 100%
        if missile_charging and charge_percent >= 1.0:
            # Aura brillante
            for i in range(3):
                alpha_radius = int(ball.visual_radius) + (i + 1) * 4
                import math
                pulse = abs(math.sin(pygame.time.get_ticks() / 100 + i))
                brightness = int(200 * pulse)
                pygame.draw.circle(
                    self.screen,
                    (brightness, brightness, brightness),
                    (int(ball.x), int(ball.y)),
                    alpha_radius,
                    2
                )

    def draw_obstacle(self, obstacle: Obstacle):
        """Dessine un obstacle."""
        if not obstacle.is_solid():
            return

        x, y, w, h = int(obstacle.x), int(obstacle.y), obstacle.width, obstacle.height

        # Remplir avec la couleur de base (marron selon le type)
        pygame.draw.rect(self.screen, obstacle.color, (x, y, w, h))

        # Bordure plus foncée
        r, g, b = obstacle.color
        border_color = (max(0, r - 30), max(0, g - 30), max(0, b - 30))
        pygame.draw.rect(self.screen, border_color, (x, y, w, h), 2)

        # Marquage visuel des plateformes fragiles (fissures)
        if isinstance(obstacle, FragilePlatform):
            crack_color = (240, 245, 255)
            pygame.draw.line(self.screen, crack_color, (x + 10, y + 6), (x + 25, y + h - 4), 2)
            pygame.draw.line(self.screen, crack_color, (x + w // 2 - 5, y + 4), (x + w // 2 + 6, y + h - 5), 2)
            pygame.draw.line(self.screen, crack_color, (x + w - 25, y + 5), (x + w - 10, y + h - 4), 2)

    def draw_obstacles(self, obstacles: list[Obstacle]):
        """Dessine tous les obstacles."""
        for obs in obstacles:
            self.draw_obstacle(obs)

    def draw_ai_ball(self, ball: AIBall):
        """Dessine une boule IA."""
        sprite = self.enemy_sprites.get(ball.enemy_type)
        if sprite is not None:
            sprite = pygame.transform.smoothscale(sprite, (int(ball.sprite_width), int(ball.sprite_height)))
            if ball.facing_direction < 0:
                sprite = pygame.transform.flip(sprite, True, False)
            rect = sprite.get_rect(center=(int(ball.x), int(ball.y)))
            self.screen.blit(sprite, rect)
        else:
            pygame.draw.ellipse(
                self.screen,
                ball.color,
                (
                    int(ball.x - ball.half_w),
                    int(ball.y - ball.half_h),
                    int(ball.hitbox_width),
                    int(ball.hitbox_height)
                )
            )

    def draw_ai_balls(self, ai_balls: list[AIBall]):
        """Dessine toutes les boules IA."""
        for ball in ai_balls:
            self.draw_ai_ball(ball)

    def draw_missile(self, missile: Missile):
        """Dessine un missile avec sprite."""
        sprite_base = self.bullet_super_sprite if missile.charged else self.bullet_sprite
        if sprite_base is not None:
            sprite = pygame.transform.smoothscale(sprite_base, (int(missile.width), int(missile.height)))
            if missile.direction < 0:
                sprite = pygame.transform.flip(sprite, True, False)
            self.screen.blit(sprite, (int(missile.x), int(missile.y)))
            return

        # Fallback simple
        color = (180, 220, 255) if missile.charged else (255, 80, 80)
        pygame.draw.ellipse(self.screen, color, (int(missile.x), int(missile.y), int(missile.width), int(missile.height)))

    def draw_missiles(self, missiles: list[Missile]):
        """Dessine tous les missiles."""
        for missile in missiles:
            self.draw_missile(missile)

    def draw_enemy_bullet(self, bullet):
        """Dessine une bulle ennemie."""
        if self.enemy_bullet_sprite is not None:
            rect = self.enemy_bullet_sprite.get_rect(center=(int(bullet.x), int(bullet.y)))
            self.screen.blit(self.enemy_bullet_sprite, rect)
            return

        pygame.draw.circle(self.screen, bullet.color, (int(bullet.x), int(bullet.y)), bullet.radius)

    def draw_enemy_bullets(self, bullets: list):
        """Dessine toutes les bulles ennemies."""
        for bullet in bullets:
            self.draw_enemy_bullet(bullet)

    def draw_heart_pickup(self, heart):
        """Dessine un coeur power-up."""
        if self.heart_pickup_sprite is not None:
            rect = self.heart_pickup_sprite.get_rect(center=(int(heart.x), int(heart.y)))
            self.screen.blit(self.heart_pickup_sprite, rect)
            return

        # Fallback simple si l'image n'est pas dispo
        pygame.draw.circle(self.screen, (255, 100, 100), (int(heart.x), int(heart.y)), int(heart.size))

    def draw_heart_pickups(self, hearts: list):
        """Dessine tous les coeurs power-up."""
        for heart in hearts:
            self.draw_heart_pickup(heart)

    def draw_door(self, door):
        """Dessine la porte vers le prochain niveau."""
        # Ne dessiner que si la porte est active
        if not door.active:
            return

        # Porte active: or brillant avec effet de pulse
        import math
        pulse = abs(math.sin(pygame.time.get_ticks() / 300))
        brightness = 200 + int(55 * pulse)
        door_color = (brightness, brightness - 20, 0)

        # Rectangle de la porte
        pygame.draw.rect(
            self.screen,
            door_color,
            (int(door.x), int(door.y), door.width, door.height)
        )

        # Bordure
        border_color = (255, 255, 200)
        pygame.draw.rect(
            self.screen,
            border_color,
            (int(door.x), int(door.y), door.width, door.height),
            3
        )

        # Poignée
        handle_x = int(door.x + door.width * 0.75)
        handle_y = int(door.y + door.height * 0.5)
        pygame.draw.circle(
            self.screen,
            border_color,
            (handle_x, handle_y),
            5
        )

    def draw_particles(self, particle_system: ParticleSystem):
        """Dessine toutes les particules."""
        for p in particle_system.particles:
            # Couleur avec fondu basé sur l'alpha
            alpha = p.alpha
            color = (
                int(p.color[0] * alpha),
                int(p.color[1] * alpha),
                int(p.color[2] * alpha)
            )
            size = max(1, int(p.current_size))
            pygame.draw.circle(
                self.screen,
                color,
                (int(p.x), int(p.y)),
                size
            )

    def draw_hud(self, ball: Ball, enemy_count: int = 0, enemies_defeated: int = 0, current_level: int = 1, rage: float = 0.0):
        """Affiche les informations à l'écran."""
        font = pygame.font.Font(None, 22)

        # Instructions en bas (hors aire de jeu)
        cmd_y_1 = self.config.PLAY_AREA_HEIGHT + 22
        cmd_y_2 = self.config.PLAY_AREA_HEIGHT + 50
        text1 = font.render(
            "Fleches/WASD: Bouger | Haut/Z/K: Sauter | Shift: Flotter | Espace: Tirer",
            True, (200, 200, 200)
        )
        self.screen.blit(text1, (16, cmd_y_1))

        text2 = font.render(
            "Super Orage: touche Y (rage 100%) | Manette: Stick, A saut, B float, X tir, Start pause",
            True, (170, 210, 255)
        )
        self.screen.blit(text2, (16, cmd_y_2))

        info_x = self.config.PLAY_AREA_WIDTH + 38
        title_font = pygame.font.Font(None, 30)
        info_title = title_font.render("Infos Joueur", True, (235, 235, 235))
        self.screen.blit(info_title, (info_x, 16))

        energy_bar_width = 160
        energy_bar_height = 20
        energy_x = info_x
        energy_y = 60

        pygame.draw.rect(self.screen, (60, 60, 60), (energy_x, energy_y, energy_bar_width, energy_bar_height))
        energy_percent = ball.displayed_energy / self.config.MAX_ENERGY
        current_width = int(energy_bar_width * energy_percent)

        if energy_percent > 0.6:
            energy_color = (100, 200, 255)
        elif energy_percent > 0.3:
            energy_color = (255, 200, 100)
        else:
            energy_color = (255, 100, 100)

        pygame.draw.rect(self.screen, energy_color, (energy_x, energy_y, current_width, energy_bar_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (energy_x, energy_y, energy_bar_width, energy_bar_height), 2)
        energy_text = font.render(f"Energie: {int(ball.displayed_energy)}", True, (180, 180, 180))
        self.screen.blit(energy_text, (energy_x, energy_y - 20))

        # Rage bar
        rage_percent = max(0.0, min(1.0, rage / 100.0))
        rage_bar_width = 160
        rage_bar_height = 20
        rage_x = info_x
        rage_y = energy_y + 44
        pygame.draw.rect(self.screen, (60, 60, 60), (rage_x, rage_y, rage_bar_width, rage_bar_height))
        rage_fill = int(rage_bar_width * rage_percent)

        if rage >= 100:
            import math
            t = pygame.time.get_ticks() / 180
            rage_color = (
                int(127 + 127 * math.sin(t)),
                int(127 + 127 * math.sin(t + 2.1)),
                int(127 + 127 * math.sin(t + 4.2))
            )
        elif rage >= 50:
            blink = (pygame.time.get_ticks() // 180) % 2
            rage_color = (255, 230, 80) if blink else (180, 150, 40)
        else:
            rage_color = (180, 90, 200)

        pygame.draw.rect(self.screen, rage_color, (rage_x, rage_y, rage_fill, rage_bar_height))
        pygame.draw.rect(self.screen, (220, 220, 220), (rage_x, rage_y, rage_bar_width, rage_bar_height), 2)
        rage_text = font.render(f"Rage: {int(rage)}%", True, (200, 200, 200))
        self.screen.blit(rage_text, (rage_x, rage_y - 20))

        jumps_text = font.render(f"Sauts: {ball.jumps_remaining}/{self.config.MAX_JUMPS}", True, (180, 180, 180))
        self.screen.blit(jumps_text, (energy_x, rage_y + 34))

        # Speed bar (s'agrandit à 100% rage)
        speed_bar_width = 220 if rage >= 100 else 150
        speed_bar_height = 16
        speed_x = energy_x
        speed_y = rage_y + 68
        active_max_speed = self.config.MAX_SPEED_RAGE if rage >= 100 else self.config.MAX_SPEED
        speed_ratio = min(1.0, abs(ball.vx) / max(active_max_speed, 1e-6))
        pygame.draw.rect(self.screen, (60, 60, 60), (speed_x, speed_y, speed_bar_width, speed_bar_height))
        pygame.draw.rect(self.screen, (120, 240, 140), (speed_x, speed_y, int(speed_bar_width * speed_ratio), speed_bar_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (speed_x, speed_y, speed_bar_width, speed_bar_height), 2)
        speed_text = font.render(f"Vitesse: {abs(ball.vx):.1f}/{active_max_speed}", True, (180, 180, 180))
        self.screen.blit(speed_text, (speed_x, speed_y + 20))

        enemies_text = font.render(f"Ennemis: {enemy_count}", True, (180, 180, 180))
        self.screen.blit(enemies_text, (energy_x, speed_y + 50))

        defeated_text = font.render(f"Vaincus: {enemies_defeated}/{self.config.ENEMIES_TO_WIN}", True, (255, 215, 0))
        self.screen.blit(defeated_text, (energy_x, speed_y + 76))

        level_text = font.render(f"Niveau: {current_level}", True, (150, 255, 150))
        self.screen.blit(level_text, (energy_x, speed_y + 102))

        if ball.rage_boost_active:
            immune_text = font.render("Rage max: Immunite collision", True, (255, 220, 120))
            self.screen.blit(immune_text, (energy_x, speed_y + 128))

        if ball.floating:
            float_text = font.render("FLOTTE", True, (150, 150, 255))
            self.screen.blit(float_text, (energy_x, speed_y + 154))

        heart_size = self.config.HEART_HUD_SPRITE_SIZE[0]
        heart_spacing = heart_size + 4
        start_x = energy_x + 15
        start_y = speed_y + 206

        hearts_label = font.render("Vies:", True, (220, 220, 220))
        self.screen.blit(hearts_label, (energy_x, start_y - 26))

        for i in range(ball.max_lives):
            heart_x = start_x + i * heart_spacing
            heart_y = start_y
            if self.heart_hud_sprite is not None:
                icon = self.heart_hud_sprite
                if i >= ball.lives:
                    icon = self.heart_hud_sprite.copy()
                    icon.fill((100, 100, 100, 190), special_flags=pygame.BLEND_RGBA_MULT)
                rect = icon.get_rect(center=(heart_x, heart_y))
                self.screen.blit(icon, rect)
            else:
                heart_color = (255, 50, 50) if i < ball.lives else (80, 80, 80)
                pygame.draw.circle(self.screen, heart_color, (heart_x - heart_size // 4, heart_y), heart_size // 3)
                pygame.draw.circle(self.screen, heart_color, (heart_x + heart_size // 4, heart_y), heart_size // 3)
                pygame.draw.polygon(self.screen, heart_color, [
                    (heart_x - heart_size // 2, heart_y),
                    (heart_x + heart_size // 2, heart_y),
                    (heart_x, heart_y + heart_size // 2)
                ])

    def draw_welcome(self):
        """Dessine l'écran de bienvenue avec explications."""
        cfg = self.config
        self.screen.fill(cfg.COLOR_MENU_BACKGROUND)

        # Titre du jeu
        title_font = pygame.font.Font(None, 90)
        title = title_font.render("eDeDo", True, (255, 200, 100))
        title_rect = title.get_rect(center=(cfg.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Sous-titre
        subtitle_font = pygame.font.Font(None, 32)
        subtitle = subtitle_font.render("Un platformer d'action rapide", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(cfg.WINDOW_WIDTH // 2, 130))
        self.screen.blit(subtitle, subtitle_rect)

        # Section: But du jeu
        section_font = pygame.font.Font(None, 36)
        text_font = pygame.font.Font(None, 24)

        y_pos = 180

        # But du jeu
        goal_title = section_font.render("🎯 But du jeu:", True, (255, 215, 0))
        self.screen.blit(goal_title, (50, y_pos))
        y_pos += 40

        goal_lines = [
            "• Battez les ennemis en sautant sur leur tête ou en tirant des pommes",
            f"• Vainquez {cfg.ENEMIES_TO_WIN} ennemis pour débloquer la porte vers le niveau suivant",
            "• Gérez votre énergie pour le double saut, le flottement et les tirs",
            f"• Collectez des coeurs pour récupérer vos vies (max {max(stats[0] for stats in cfg.PLAYER_STATS)})"
        ]
        for line in goal_lines:
            text = text_font.render(line, True, (180, 180, 180))
            self.screen.blit(text, (70, y_pos))
            y_pos += 28

        y_pos += 15

        # Contrôles Clavier
        controls_title = section_font.render("⌨️  Contrôles Clavier:", True, (100, 200, 255))
        self.screen.blit(controls_title, (50, y_pos))
        y_pos += 40

        keyboard_controls = [
            "Flèches/WASD: Déplacer  |  Haut/Z/K: Sauter (double saut)",
            "Shift: Flotter  |  Espace: Tirer  |  Super orage: Y manette (rage 100%)",
            "ESC: Pause  |  R: Recommencer le niveau"
        ]
        for line in keyboard_controls:
            text = text_font.render(line, True, (180, 180, 180))
            self.screen.blit(text, (70, y_pos))
            y_pos += 28

        y_pos += 15

        # Contrôles Manette
        gamepad_title = section_font.render("🎮 Contrôles Manette:", True, (100, 255, 150))
        self.screen.blit(gamepad_title, (50, y_pos))
        y_pos += 40

        gamepad_controls = [
            "Stick/D-pad: Déplacer  |  A: Sauter  |  B: Flotter",
            "X: Tirer  |  Y: Super orage (rage pleine)  |  Start: Pause"
        ]
        for line in gamepad_controls:
            text = text_font.render(line, True, (180, 180, 180))
            self.screen.blit(text, (70, y_pos))
            y_pos += 28

        # Message pour continuer (clignotant)
        import math
        pulse = abs(math.sin(pygame.time.get_ticks() / 500))
        alpha = int(150 + 105 * pulse)
        continue_font = pygame.font.Font(None, 36)
        continue_text = continue_font.render("Appuyez sur Entrée ou un bouton pour continuer", True, (alpha, alpha, alpha))
        continue_rect = continue_text.get_rect(center=(cfg.WINDOW_WIDTH // 2, cfg.WINDOW_HEIGHT - 40))
        self.screen.blit(continue_text, continue_rect)

    def draw_menu(self, selected_index: int, colors: list[tuple], names: list[str]):
        """
        Dessine l'écran de menu de sélection de couleur.

        Args:
            selected_index: Index de la couleur sélectionnée
            colors: Liste des couleurs disponibles
            names: Liste des noms des couleurs
        """
        cfg = self.config

        # Fond menu (wellcome.png en version pale si dispo)
        self.screen.fill(cfg.COLOR_MENU_BACKGROUND)
        if self.menu_background_image:
            self.screen.blit(self.menu_background_image, (0, 0))
            pale = pygame.Surface((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT), pygame.SRCALPHA)
            pale.fill((255, 255, 255, 120))
            self.screen.blit(pale, (0, 0))
            contrast = pygame.Surface((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT), pygame.SRCALPHA)
            contrast.fill((15, 20, 28, 70))
            self.screen.blit(contrast, (0, 0))
        elif self.background_image:
            bg = pygame.transform.smoothscale(self.background_image, (cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
            self.screen.blit(bg, (0, 0))
            overlay = pygame.Surface((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 12, 18, 120))
            self.screen.blit(overlay, (0, 0))

        # Titre
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("eDeDo", True, cfg.COLOR_MENU_TEXT)
        title_rect = title.get_rect(center=(cfg.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Sous-titre
        subtitle_font = pygame.font.Font(None, 36)
        subtitle = subtitle_font.render("Choisissez votre personnage", True, cfg.COLOR_MENU_TEXT)
        subtitle_rect = subtitle.get_rect(center=(cfg.WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)

        spacing = 280
        start_x = cfg.WINDOW_WIDTH // 2 - (len(names) - 1) * spacing // 2
        slot_y = 390

        for i, name in enumerate(names):
            slot_x = start_x + i * spacing
            sprite = self.player_sprites[i] if i < len(self.player_sprites) else None
            sprite_w, sprite_h = cfg.PLAYER_SPRITE_SIZES[i]
            display_w = sprite_w * 2
            display_h = sprite_h * 2

            if i == selected_index:
                highlight_rect = pygame.Rect(
                    int(slot_x - display_w / 2 - 16),
                    int(slot_y - display_h / 2 - 16),
                    display_w + 32,
                    display_h + 32
                )
                pygame.draw.rect(self.screen, cfg.COLOR_MENU_HIGHLIGHT, highlight_rect, 4, border_radius=16)

            if sprite:
                sprite = pygame.transform.smoothscale(sprite, (display_w, display_h))
                sprite_rect = sprite.get_rect(center=(slot_x, slot_y))
                self.screen.blit(sprite, sprite_rect)
            else:
                pygame.draw.ellipse(
                    self.screen,
                    colors[i],
                    (int(slot_x - display_w / 2), int(slot_y - display_h / 2), display_w, display_h)
                )

            name_font = pygame.font.Font(None, 30)
            name_text = name_font.render(name, True, cfg.COLOR_MENU_TEXT)
            name_rect = name_text.get_rect(center=(slot_x, slot_y + display_h // 2 + 30))
            self.screen.blit(name_text, name_rect)

            stats_font = pygame.font.Font(None, 22)
            max_lives, speed_mult, jump_mult = cfg.PLAYER_STATS[i]
            stats_text = stats_font.render(
                f"{max_lives} PV | Vit: {int(speed_mult*100)}% | Saut: {int(jump_mult*100)}%",
                True,
                (180, 180, 180)
            )
            stats_rect = stats_text.get_rect(center=(slot_x, slot_y + display_h // 2 + 56))
            self.screen.blit(stats_text, stats_rect)

        instr_font = pygame.font.Font(None, 30)
        instructions = ["< / > : Changer de personnage", "Entree / Espace : Jouer"]
        for idx, text_line in enumerate(instructions):
            instr = instr_font.render(text_line, True, (190, 190, 190))
            instr_rect = instr.get_rect(center=(cfg.WINDOW_WIDTH // 2, 640 + idx * 35))
            self.screen.blit(instr, instr_rect)

    def draw_highscores(self, highscores: list, current_score: int):
        """
        Dessine l'écran des meilleurs scores.

        Args:
            highscores: Liste des meilleurs scores triés
            current_score: Score de la partie qui vient de se terminer
        """
        cfg = self.config

        # Fond
        self.screen.fill(cfg.COLOR_MENU_BACKGROUND)

        # Titre
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("MEILLEURS SCORES", True, cfg.COLOR_MENU_TEXT)
        title_rect = title.get_rect(center=(cfg.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Score actuel
        score_font = pygame.font.Font(None, 48)
        current_text = score_font.render(
            f"Votre score : {current_score} ennemis",
            True,
            cfg.COLOR_MENU_HIGHLIGHT
        )
        current_rect = current_text.get_rect(center=(cfg.WINDOW_WIDTH // 2, 150))
        self.screen.blit(current_text, current_rect)

        # Liste des highscores
        list_font = pygame.font.Font(None, 36)
        start_y = 220
        spacing = 40

        for i, score in enumerate(highscores[:10]):
            # Couleur différente si c'est le score actuel
            if score == current_score and i < 10:
                color = cfg.COLOR_MENU_HIGHLIGHT
                text = f"{i+1}. {score} ennemis  ← NOUVEAU!"
            else:
                color = cfg.COLOR_MENU_TEXT
                text = f"{i+1}. {score} ennemis"

            score_text = list_font.render(text, True, color)
            score_rect = score_text.get_rect(center=(cfg.WINDOW_WIDTH // 2, start_y + i * spacing))
            self.screen.blit(score_text, score_rect)

        # Instructions
        instr_font = pygame.font.Font(None, 28)
        instr = instr_font.render("Appuyez sur un bouton pour continuer...", True, (150, 150, 150))
        instr_rect = instr.get_rect(center=(cfg.WINDOW_WIDTH // 2, 550))
        self.screen.blit(instr, instr_rect)
