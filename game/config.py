"""
Configuration du jeu.

Contient toutes les constantes et paramètres ajustables.
"""


class Config:
    """Configuration globale du jeu."""

    # Fenêtre
    PLAY_AREA_WIDTH = 1200
    PLAY_AREA_HEIGHT = 800
    SIDEBAR_WIDTH = 320
    BOTTOM_PANEL_HEIGHT = 140
    WINDOW_WIDTH = PLAY_AREA_WIDTH + SIDEBAR_WIDTH
    WINDOW_HEIGHT = PLAY_AREA_HEIGHT + BOTTOM_PANEL_HEIGHT
    FPS = 60
    TITLE = "eDeDo"
    ASSETS_DIR = "assets"
    BACKGROUND_IMAGE = "background.png"
    PLAYER_IMAGES = ["perso-1.png", "perso-2.png", "perso-3.png"]
    ENEMY_IMAGES = {
        1: "ennemi-1.png",
        2: "ennemi-2.png",
        3: "ennemi-3.png",
    }

    # Couleurs (RGB)
    COLOR_BACKGROUND = (30, 30, 40)
    COLOR_BALL = (255, 100, 100)
    COLOR_WALL = (100, 100, 120)
    COLOR_OBSTACLE = (80, 180, 80)

    # Physique
    GRAVITY = 0.5
    FRICTION = 0.92  # Friction au sol
    BOUNCE_FACTOR = 0.5  # Rebond sur les murs

    # Particules
    PARTICLE_COUNT = 12  # Nombre de particules par impact
    PARTICLE_SPEED_MIN = 2
    PARTICLE_SPEED_MAX = 6
    PARTICLE_LIFETIME = 30  # Frames
    PARTICLE_SIZE_MIN = 2
    PARTICLE_SIZE_MAX = 5
    PARTICLE_COLORS = [
        (255, 200, 100),  # Jaune-orange
        (255, 150, 50),   # Orange
        (255, 100, 50),   # Rouge-orange
        (255, 255, 150),  # Jaune clair
    ]

    # Boule
    BALL_RADIUS = 20
    PLAYER_SPRITE_SIZES = [
        (55, 65),   # perso-1 (x0.6)
        (71, 65),   # perso-2 (x0.6)
        (94, 61),   # perso-3 (x0.6)
    ]
    PLAYER_HITBOX_SIZES = [
        (55, 65),    # perso-1 (meme taille que sprite)
        (71, 65),    # perso-2 (meme taille que sprite)
        (94, 61),    # perso-3 (meme taille que sprite)
    ]
    BALL_SPEED = 5
    JUMP_FORCE = -12
    MAX_JUMPS = 2  # Double saut

    # Système d'énergie
    MAX_ENERGY = 100
    ENERGY_REGEN_RATE = 0.1  # 1 point tous les 10 frames au sol
    FLOAT_ENERGY_COST = 0.5  # Coût par frame de flottement (réduit)
    DOUBLE_JUMP_ENERGY_COST = 30  # Coût d'un double saut
    MISSILE_ENERGY_COST = 10  # Coût d'un missile
    FLOAT_GRAVITY_MULTIPLIER = 0.3  # Gravité réduite pendant le flottement

    # Limite de vitesse
    MAX_SPEED = 12  # Vitesse horizontale maximale de base
    MAX_SPEED_RAGE = 17  # Vitesse maximale quand rage à 100%
    SPEED_DECAY_RATE = 0.95  # Taux de réduction quand au-dessus de la limite
    AIR_CONTROL_FACTOR = 0.6  # Facteur de contrôle dans les airs (60% du contrôle au sol)

    # Plateformes - couleurs marron
    COLOR_PLATFORM_STATIC = (101, 67, 33)   # Marron foncé
    COLOR_PLATFORM_SLOW = (139, 90, 43)     # Marron moyen
    COLOR_PLATFORM_FAST = (205, 133, 63)    # Marron clair
    COLOR_PLATFORM_FRAGILE = (120, 180, 210)  # Bleu-gris pour plateformes fragiles
    MOVING_PLATFORM_SPEED_SLOW = 1.0
    MOVING_PLATFORM_SPEED_FAST = 3.5
    FRAGILE_PLATFORM_BREAK_DELAY = 20  # Frames sur la plateforme avant qu'elle casse
    FRAGILE_PLATFORM_RESPAWN_TIME = 180  # Frames avant réapparition (3 secondes)

    # Salle secrète
    SECRET_HOLE_HALF_HEIGHT = 45

    # Boules IA
    AI_BALL_RADIUS = 14
    ENEMY_SPRITE_SIZES = {
        1: (53, 46),   # x0.6
        2: (60, 50),   # x0.6
        3: (67, 56),   # x0.6
    }
    ENEMY_HITBOX_SIZES = {
        1: (53, 46),  # meme taille que sprite
        2: (60, 50),  # meme taille que sprite
        3: (67, 56),  # meme taille que sprite
    }
    AI_BALL_COUNT = 3
    # Couleurs des ennemis selon HP
    AI_BALL_COLOR_1HP = (100, 150, 255)  # Bleu pour 1 HP
    AI_BALL_COLOR_2HP = (200, 100, 255)  # Violet pour 2 HP
    AI_BALL_COLOR_3HP = (255, 80, 80)    # Rouge pour 3 HP

    # Rayon selon HP initial
    AI_BALL_RADIUS_1HP = 12
    AI_BALL_RADIUS_2HP = 15
    AI_BALL_RADIUS_3HP = 18
    AI_BALL_SPEED = 3
    BALL_BOUNCE_FACTOR = 0.9  # Rebond entre boules

    # Animation double saut
    DOUBLE_JUMP_PARTICLE_COUNT = 16
    DOUBLE_JUMP_PARTICLE_COLORS = [
        (200, 220, 255),  # Blanc-bleu
        (150, 200, 255),  # Bleu clair
        (100, 180, 255),  # Bleu
    ]

    # Murs (épaisseur)
    WALL_THICKNESS = 20

    # Audio
    AUDIO_ENABLED = True
    AUDIO_MASTER_VOLUME = 0.7

    # Couleurs de boule joueur (menu de sélection)
    PLAYER_BALL_COLORS = [
        (255, 150, 50),   # Orange
        (100, 255, 100),  # Vert
        (255, 50, 200),   # Fushia
    ]
    PLAYER_BALL_NAMES = ["Flash", "Medium", "Tank"]
    # Stats des personnages : (max_lives, speed_multiplier, jump_multiplier)
    PLAYER_STATS = [
        (4, 1.5, 1.2),   # Flash: 4 vies, très rapide (150%), saute plus haut (120%)
        (5, 1.0, 1.0),   # Medium: 5 vies, vitesse normale, saut normal
        (6, 0.7, 0.8),   # Tank: 6 vies, plus lent (70%), saute moins haut (80%)
    ]

    # Menu de bienvenue
    COLOR_MENU_BACKGROUND = (20, 20, 30)
    COLOR_MENU_TEXT = (220, 220, 220)
    COLOR_MENU_HIGHLIGHT = (255, 200, 100)

    # Missiles
    MISSILE_WIDTH = 15
    MISSILE_HEIGHT = 8
    MISSILE_SPEED = 18  # Augmenté pour aller plus vite
    MISSILE_COLOR = (255, 255, 50)  # Jaune vif

    # Missile chargé
    CHARGED_MISSILE_COST = 0  # Désactivé: la super attaque utilise la rage
    CHARGED_MISSILE_CHARGE_TIME = 0
    CHARGED_MISSILE_WIDTH = 60  # Beaucoup plus grand!
    CHARGED_MISSILE_HEIGHT = 35  # Beaucoup plus grand!
    CHARGED_MISSILE_SPEED = 15
    CHARGED_MISSILE_COLOR = (255, 100, 50)  # Orange/rouge
    CHARGED_MISSILE_EXPLOSION_RADIUS = 120  # Zone d'explosion plus grande aussi

    # Rage / super attaque
    RAGE_GAIN_PER_HIT = 10
    RAGE_SUPER_COST = 50

    # Spawn d'ennemis
    ENEMY_SPAWN_INTERVAL = 180  # Frames entre chaque spawn (3 secondes à 60 FPS)
    ENEMY_MAX_COUNT = 6  # Nombre maximum d'ennemis
    ENEMIES_TO_WIN = 10  # Nombre d'ennemis à vaincre pour débloquer la porte (réduit de 15 à 10)
