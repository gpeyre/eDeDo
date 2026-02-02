"""
Rendu graphique du jeu.

Gère l'affichage de tous les éléments visuels.
"""

import pygame
from .config import Config
from .entities import Ball, Obstacle, MovingPlatform, AIBall, Missile
from .particles import ParticleSystem


class Renderer:
    """Gère le rendu graphique avec Pygame."""

    def __init__(self, screen: pygame.Surface, config: Config = None):
        self.screen = screen
        self.config = config or Config()

    def clear(self):
        """Efface l'écran avec la couleur de fond."""
        self.screen.fill(self.config.COLOR_BACKGROUND)

    def draw_walls(self):
        """Dessine les murs de la pièce."""
        cfg = self.config
        color = cfg.COLOR_WALL
        w = cfg.WALL_THICKNESS

        # Mur haut
        pygame.draw.rect(self.screen, color, (0, 0, cfg.WINDOW_WIDTH, w))
        # Mur bas
        pygame.draw.rect(
            self.screen, color,
            (0, cfg.WINDOW_HEIGHT - w, cfg.WINDOW_WIDTH, w)
        )
        # Mur gauche
        pygame.draw.rect(self.screen, color, (0, 0, w, cfg.WINDOW_HEIGHT))
        # Mur droit
        pygame.draw.rect(
            self.screen, color,
            (cfg.WINDOW_WIDTH - w, 0, w, cfg.WINDOW_HEIGHT)
        )

    def draw_ball(self, ball: Ball, missile_charging: bool = False, charge_percent: float = 0.0):
        """Dessine la boule."""
        # Effet de charge : multicolore puis brille
        if missile_charging:
            if charge_percent >= 1.0:
                # Brille quand c'est prêt (blanc brillant qui pulse)
                import math
                pulse = abs(math.sin(pygame.time.get_ticks() / 100))
                brightness = 200 + int(55 * pulse)
                color = (brightness, brightness, brightness)
            else:
                # Multicolore pendant la charge
                # Mélange de couleurs qui change avec le temps
                import math
                t = pygame.time.get_ticks() / 200
                r = int(127 + 127 * math.sin(t))
                g = int(127 + 127 * math.sin(t + 2.1))
                b = int(127 + 127 * math.sin(t + 4.2))
                color = (r, g, b)
        elif ball.floating:
            color = (200, 200, 255)  # Bleuté quand en flottement
        else:
            color = ball.color

        pygame.draw.circle(
            self.screen,
            color,
            (int(ball.x), int(ball.y)),
            ball.radius
        )

        # Effet de brillance supplémentaire quand chargé à 100%
        if missile_charging and charge_percent >= 1.0:
            # Aura brillante
            for i in range(3):
                alpha_radius = ball.radius + (i + 1) * 3
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

        # Dessiner les yeux
        eye_offset_x = ball.radius * 0.35 * ball.facing_direction
        eye_offset_y = -ball.radius * 0.2
        eye_radius = ball.radius * 0.25  # Yeux plus gros

        # Position des deux yeux
        left_eye_x = int(ball.x + eye_offset_x - ball.radius * 0.2 * ball.facing_direction)
        right_eye_x = int(ball.x + eye_offset_x + ball.radius * 0.2 * ball.facing_direction)
        eye_y = int(ball.y + eye_offset_y)

        # Blanc des yeux
        pygame.draw.circle(self.screen, (255, 255, 255), (left_eye_x, eye_y), int(eye_radius * 1.2))
        pygame.draw.circle(self.screen, (255, 255, 255), (right_eye_x, eye_y), int(eye_radius * 1.2))

        # Pupilles (noires)
        pupil_offset = ball.radius * 0.08 * ball.facing_direction
        pygame.draw.circle(self.screen, (0, 0, 0),
                          (int(left_eye_x + pupil_offset), eye_y), int(eye_radius * 0.6))
        pygame.draw.circle(self.screen, (0, 0, 0),
                          (int(right_eye_x + pupil_offset), eye_y), int(eye_radius * 0.6))

    def draw_obstacle(self, obstacle: Obstacle):
        """Dessine un obstacle."""
        pygame.draw.rect(
            self.screen,
            obstacle.color,
            (int(obstacle.x), int(obstacle.y), obstacle.width, obstacle.height)
        )
        # Bordure (couleur différente pour plateforme mobile)
        if isinstance(obstacle, MovingPlatform):
            border_color = (140, 90, 50)
        else:
            border_color = (60, 140, 60)

        pygame.draw.rect(
            self.screen,
            border_color,
            (int(obstacle.x), int(obstacle.y), obstacle.width, obstacle.height),
            2
        )

    def draw_obstacles(self, obstacles: list[Obstacle]):
        """Dessine tous les obstacles."""
        for obs in obstacles:
            self.draw_obstacle(obs)

    def draw_ai_ball(self, ball: AIBall):
        """Dessine une boule IA."""
        # Corps de la boule
        pygame.draw.circle(
            self.screen,
            ball.color,
            (int(ball.x), int(ball.y)),
            ball.radius
        )
        # Effet de brillance
        highlight_pos = (
            int(ball.x - ball.radius * 0.25),
            int(ball.y - ball.radius * 0.25)
        )
        # Couleur de brillance plus claire
        highlight_color = (
            min(255, ball.color[0] + 80),
            min(255, ball.color[1] + 80),
            min(255, ball.color[2] + 80)
        )
        pygame.draw.circle(
            self.screen,
            highlight_color,
            highlight_pos,
            ball.radius // 4
        )
        # Contour
        pygame.draw.circle(
            self.screen,
            (
                max(0, ball.color[0] - 40),
                max(0, ball.color[1] - 40),
                max(0, ball.color[2] - 40)
            ),
            (int(ball.x), int(ball.y)),
            ball.radius,
            2
        )

        # Dessiner un sourire fun au lieu des HP
        # Yeux (deux petits cercles)
        eye_offset_x = ball.radius * 0.4
        eye_offset_y = -ball.radius * 0.25
        eye_radius = ball.radius * 0.15

        # Oeil gauche
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (int(ball.x - eye_offset_x), int(ball.y + eye_offset_y)),
            int(eye_radius)
        )
        # Pupille gauche
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            (int(ball.x - eye_offset_x), int(ball.y + eye_offset_y)),
            int(eye_radius * 0.5)
        )

        # Oeil droit
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (int(ball.x + eye_offset_x), int(ball.y + eye_offset_y)),
            int(eye_radius)
        )
        # Pupille droite
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            (int(ball.x + eye_offset_x), int(ball.y + eye_offset_y)),
            int(eye_radius * 0.5)
        )

        # Sourire (arc)
        mouth_y = int(ball.y + ball.radius * 0.3)
        mouth_width = int(ball.radius * 0.8)
        mouth_height = int(ball.radius * 0.4)
        mouth_rect = pygame.Rect(
            int(ball.x - mouth_width / 2),
            mouth_y - mouth_height,
            mouth_width,
            mouth_height
        )
        pygame.draw.arc(
            self.screen,
            (255, 255, 255),
            mouth_rect,
            3.14,  # pi (180 degrés)
            0,     # 0 degrés
            3      # épaisseur
        )

    def draw_ai_balls(self, ai_balls: list[AIBall]):
        """Dessine toutes les boules IA."""
        for ball in ai_balls:
            self.draw_ai_ball(ball)

    def draw_missile(self, missile: Missile):
        """Dessine un missile (pomme ou fraise)."""
        center_x = int(missile.x + missile.width / 2)
        center_y = int(missile.y + missile.height / 2)

        if missile.charged:
            # Fraise (gros missile)
            radius = int(missile.height / 2)

            # Corps de la fraise (rouge)
            pygame.draw.circle(self.screen, (220, 40, 40), (center_x, center_y), radius)

            # Points jaunes sur la fraise (graines)
            import math
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                seed_x = int(center_x + radius * 0.6 * math.cos(rad))
                seed_y = int(center_y + radius * 0.6 * math.sin(rad))
                pygame.draw.circle(self.screen, (255, 255, 150), (seed_x, seed_y), 2)

            # Feuilles vertes en haut
            leaf_y = center_y - radius
            pygame.draw.polygon(
                self.screen,
                (50, 150, 50),
                [
                    (center_x - radius // 2, leaf_y),
                    (center_x, leaf_y - radius // 3),
                    (center_x + radius // 2, leaf_y)
                ]
            )
        else:
            # Pomme (petit missile)
            radius = int(missile.height / 2)

            # Corps de la pomme (rouge vif)
            pygame.draw.circle(self.screen, (255, 50, 50), (center_x, center_y), radius)

            # Reflet blanc sur la pomme
            pygame.draw.circle(
                self.screen,
                (255, 200, 200),
                (center_x - radius // 3, center_y - radius // 3),
                radius // 3
            )

            # Tige (marron)
            stem_x = center_x
            stem_y = center_y - radius
            pygame.draw.line(
                self.screen,
                (100, 60, 20),
                (stem_x, stem_y),
                (stem_x, stem_y - radius // 2),
                2
            )

            # Feuille verte
            pygame.draw.ellipse(
                self.screen,
                (50, 200, 50),
                (stem_x, stem_y - radius // 2, radius // 2, radius // 3)
            )

    def draw_missiles(self, missiles: list[Missile]):
        """Dessine tous les missiles."""
        for missile in missiles:
            self.draw_missile(missile)

    def draw_enemy_bullet(self, bullet):
        """Dessine une bulle ennemie."""
        # Bulle semi-transparente
        pygame.draw.circle(
            self.screen,
            bullet.color,
            (int(bullet.x), int(bullet.y)),
            bullet.radius
        )
        # Reflet blanc
        pygame.draw.circle(
            self.screen,
            (220, 240, 255),
            (int(bullet.x - bullet.radius * 0.3), int(bullet.y - bullet.radius * 0.3)),
            bullet.radius // 3
        )
        # Contour
        pygame.draw.circle(
            self.screen,
            (100, 150, 200),
            (int(bullet.x), int(bullet.y)),
            bullet.radius,
            1
        )

    def draw_enemy_bullets(self, bullets: list):
        """Dessine toutes les bulles ennemies."""
        for bullet in bullets:
            self.draw_enemy_bullet(bullet)

    def draw_heart_pickup(self, heart):
        """Dessine un coeur power-up."""
        heart_size = heart.size
        heart_x = int(heart.x)
        heart_y = int(heart.y)

        # Coeur rouge brillant
        heart_color = (255, 100, 100)

        # Deux demi-cercles en haut
        pygame.draw.circle(self.screen, heart_color,
                         (heart_x - heart_size // 3, heart_y), heart_size // 2)
        pygame.draw.circle(self.screen, heart_color,
                         (heart_x + heart_size // 3, heart_y), heart_size // 2)
        # Triangle pointant vers le bas
        pygame.draw.polygon(self.screen, heart_color, [
            (heart_x - heart_size // 2, heart_y),
            (heart_x + heart_size // 2, heart_y),
            (heart_x, heart_y + heart_size)
        ])

        # Reflet blanc
        pygame.draw.circle(self.screen, (255, 200, 200),
                         (heart_x - heart_size // 4, heart_y - heart_size // 4),
                         heart_size // 4)

    def draw_heart_pickups(self, hearts: list):
        """Dessine tous les coeurs power-up."""
        for heart in hearts:
            self.draw_heart_pickup(heart)

    def draw_door(self, door):
        """Dessine la porte vers le prochain niveau."""
        if door.active:
            # Porte active: or brillant avec effet de pulse
            import math
            pulse = abs(math.sin(pygame.time.get_ticks() / 300))
            brightness = 200 + int(55 * pulse)
            door_color = (brightness, brightness - 20, 0)
        else:
            # Porte inactive: gris foncé
            door_color = (80, 80, 80)

        # Rectangle de la porte
        pygame.draw.rect(
            self.screen,
            door_color,
            (int(door.x), int(door.y), door.width, door.height)
        )

        # Bordure
        border_color = (255, 255, 200) if door.active else (50, 50, 50)
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

    def draw_hud(self, ball: Ball, enemy_count: int = 0, missile_charging: bool = False, charge_timer: int = 0, enemies_defeated: int = 0, current_level: int = 1):
        """Affiche les informations à l'écran."""
        font = pygame.font.Font(None, 22)

        # Instructions ligne 1 - Clavier
        text1 = font.render(
            "Fleches/WASD: Bouger | Espace: Tirer | Haut: Sauter | Shift: Flotter",
            True, (200, 200, 200)
        )
        self.screen.blit(text1, (10, self.config.WINDOW_HEIGHT - 55))

        # Instructions ligne 2 - Manette
        text2 = font.render(
            "Manette: Stick/D-pad: Bouger | A: Sauter | B: Flotter | X: Tirer | Start: Pause",
            True, (150, 200, 255)
        )
        self.screen.blit(text2, (10, self.config.WINDOW_HEIGHT - 30))

        # Barre de vitesse en haut à gauche
        speed_bar_width = 150
        speed_bar_height = 20
        speed_x = 20
        speed_y = 30

        # Fond de la barre
        pygame.draw.rect(
            self.screen,
            (60, 60, 60),
            (speed_x, speed_y, speed_bar_width, speed_bar_height)
        )

        # Vitesse actuelle
        current_speed = abs(ball.vx)
        speed_percent = min(1.0, current_speed / self.config.MAX_SPEED)
        current_width = int(speed_bar_width * speed_percent)

        # Couleur selon le niveau de vitesse
        if speed_percent > 0.8:
            speed_color = (255, 100, 100)  # Rouge (trop rapide)
        elif speed_percent > 0.5:
            speed_color = (255, 200, 100)  # Orange
        else:
            speed_color = (100, 255, 100)  # Vert

        pygame.draw.rect(
            self.screen,
            speed_color,
            (speed_x, speed_y, current_width, speed_bar_height)
        )

        # Bordure de la barre
        pygame.draw.rect(
            self.screen,
            (200, 200, 200),
            (speed_x, speed_y, speed_bar_width, speed_bar_height),
            2
        )

        # Ligne de limite max
        max_line_x = speed_x + speed_bar_width
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (max_line_x - 2, speed_y),
            (max_line_x - 2, speed_y + speed_bar_height),
            2
        )

        # Texte vitesse
        speed_text = font.render(f"Vitesse: {int(current_speed)}/{self.config.MAX_SPEED}", True, (180, 180, 180))
        self.screen.blit(speed_text, (speed_x, speed_y - 20))

        # Barre d'énergie
        energy_bar_width = 150
        energy_bar_height = 20
        energy_x = self.config.WINDOW_WIDTH - energy_bar_width - 20
        energy_y = 30

        # Fond de la barre
        pygame.draw.rect(
            self.screen,
            (60, 60, 60),
            (energy_x, energy_y, energy_bar_width, energy_bar_height)
        )

        # Énergie actuelle (affichage smooth)
        energy_percent = ball.displayed_energy / self.config.MAX_ENERGY
        current_width = int(energy_bar_width * energy_percent)

        # Couleur selon le niveau d'énergie
        if energy_percent > 0.6:
            energy_color = (100, 200, 255)  # Bleu
        elif energy_percent > 0.3:
            energy_color = (255, 200, 100)  # Orange
        else:
            energy_color = (255, 100, 100)  # Rouge

        pygame.draw.rect(
            self.screen,
            energy_color,
            (energy_x, energy_y, current_width, energy_bar_height)
        )

        # Bordure de la barre
        pygame.draw.rect(
            self.screen,
            (200, 200, 200),
            (energy_x, energy_y, energy_bar_width, energy_bar_height),
            2
        )

        # Texte énergie (affichage smooth)
        energy_text = font.render(f"Énergie: {int(ball.displayed_energy)}", True, (180, 180, 180))
        self.screen.blit(energy_text, (energy_x, energy_y - 20))

        # Indicateur de sauts restants
        jumps_text = font.render(
            f"Sauts: {ball.jumps_remaining}/{self.config.MAX_JUMPS}",
            True, (180, 180, 180)
        )
        self.screen.blit(jumps_text, (energy_x, energy_y + 30))

        # Nombre d'ennemis actifs
        enemies_text = font.render(
            f"Ennemis: {enemy_count}",
            True, (180, 180, 180)
        )
        self.screen.blit(enemies_text, (energy_x, energy_y + 55))

        # Compteur d'ennemis vaincus et niveau
        defeated_text = font.render(
            f"Vaincus: {enemies_defeated}/{self.config.ENEMIES_TO_WIN}",
            True, (255, 215, 0)  # Or
        )
        self.screen.blit(defeated_text, (energy_x, energy_y + 80))

        level_text = font.render(
            f"Niveau: {current_level}",
            True, (150, 255, 150)  # Vert clair
        )
        self.screen.blit(level_text, (energy_x, energy_y + 105))

        # Indicateur flottement
        if ball.floating:
            float_text = font.render("FLOTTE", True, (150, 150, 255))
            self.screen.blit(float_text, (energy_x, energy_y + 130))

        # Affichage des vies (coeurs) en haut à gauche
        heart_size = 25
        heart_spacing = 30
        start_x = 20
        start_y = 20

        for i in range(5):  # Toujours afficher 5 coeurs max
            heart_x = start_x + i * heart_spacing
            heart_y = start_y

            if i < ball.lives:
                # Coeur plein (rouge)
                heart_color = (255, 50, 50)
            else:
                # Coeur vide (gris)
                heart_color = (80, 80, 80)

            # Dessiner un coeur avec des cercles et un triangle
            # Deux demi-cercles en haut
            pygame.draw.circle(self.screen, heart_color,
                             (heart_x - heart_size // 4, heart_y), heart_size // 3)
            pygame.draw.circle(self.screen, heart_color,
                             (heart_x + heart_size // 4, heart_y), heart_size // 3)
            # Triangle pointant vers le bas
            pygame.draw.polygon(self.screen, heart_color, [
                (heart_x - heart_size // 2, heart_y),
                (heart_x + heart_size // 2, heart_y),
                (heart_x, heart_y + heart_size // 2)
            ])


    def draw_menu(self, selected_index: int, colors: list[tuple], names: list[str]):
        """
        Dessine l'écran de menu de sélection de couleur.

        Args:
            selected_index: Index de la couleur sélectionnée
            colors: Liste des couleurs disponibles
            names: Liste des noms des couleurs
        """
        cfg = self.config

        # Fond
        self.screen.fill(cfg.COLOR_MENU_BACKGROUND)

        # Titre
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("Bouncing Ball", True, cfg.COLOR_MENU_TEXT)
        title_rect = title.get_rect(center=(cfg.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Sous-titre
        subtitle_font = pygame.font.Font(None, 36)
        subtitle = subtitle_font.render(
            "Choisissez votre couleur", True, cfg.COLOR_MENU_TEXT
        )
        subtitle_rect = subtitle.get_rect(center=(cfg.WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)

        # Afficher les boules
        ball_radius = 40
        spacing = 150
        start_x = cfg.WINDOW_WIDTH // 2 - (len(colors) - 1) * spacing // 2
        ball_y = 300

        for i, (color, name) in enumerate(zip(colors, names)):
            ball_x = start_x + i * spacing

            # Cercle de sélection
            if i == selected_index:
                pygame.draw.circle(
                    self.screen,
                    cfg.COLOR_MENU_HIGHLIGHT,
                    (ball_x, ball_y),
                    ball_radius + 8,
                    4
                )

            # Boule
            pygame.draw.circle(
                self.screen,
                color,
                (ball_x, ball_y),
                ball_radius
            )

            # Dessiner les yeux pour le menu
            eye_offset_x = ball_radius * 0.35
            eye_offset_y = -ball_radius * 0.2
            eye_radius = ball_radius * 0.25  # Yeux plus gros

            # Position des deux yeux (regardent vers la droite)
            left_eye_x = int(ball_x + eye_offset_x - ball_radius * 0.2)
            right_eye_x = int(ball_x + eye_offset_x + ball_radius * 0.2)
            eye_y = int(ball_y + eye_offset_y)

            # Blanc des yeux
            pygame.draw.circle(self.screen, (255, 255, 255), (left_eye_x, eye_y), int(eye_radius * 1.2))
            pygame.draw.circle(self.screen, (255, 255, 255), (right_eye_x, eye_y), int(eye_radius * 1.2))

            # Pupilles - couleur différente selon la boule
            if i == 0:  # Rouge
                pupil_color = (100, 0, 0)
            elif i == 1:  # Bleu
                pupil_color = (0, 50, 100)
            else:  # Vert
                pupil_color = (0, 100, 50)

            pupil_offset = ball_radius * 0.08
            pygame.draw.circle(self.screen, pupil_color,
                              (int(left_eye_x + pupil_offset), eye_y), int(eye_radius * 0.6))
            pygame.draw.circle(self.screen, pupil_color,
                              (int(right_eye_x + pupil_offset), eye_y), int(eye_radius * 0.6))

            # Nom de la couleur
            name_font = pygame.font.Font(None, 28)
            name_text = name_font.render(name, True, cfg.COLOR_MENU_TEXT)
            name_rect = name_text.get_rect(center=(ball_x, ball_y + ball_radius + 25))
            self.screen.blit(name_text, name_rect)

        # Instructions
        instr_font = pygame.font.Font(None, 28)
        instructions = [
            "< / > : Changer de couleur",
            "Entree / Espace : Jouer"
        ]
        for i, text in enumerate(instructions):
            instr = instr_font.render(text, True, (150, 150, 150))
            instr_rect = instr.get_rect(
                center=(cfg.WINDOW_WIDTH // 2, 450 + i * 35)
            )
            self.screen.blit(instr, instr_rect)
