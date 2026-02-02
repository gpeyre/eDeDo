"""
Système audio du jeu.

Génère et joue des sons programmatiquement avec numpy.
"""

from enum import Enum, auto
import numpy as np
import pygame


class SoundType(Enum):
    """Types de sons disponibles."""
    WALL_IMPACT = auto()
    PLATFORM_IMPACT = auto()
    JUMP = auto()
    DOUBLE_JUMP = auto()
    BALL_COLLISION = auto()
    LIFE_LOST = auto()  # Son fun pour perte de vie


class AudioManager:
    """Gère la génération et la lecture des sons."""

    def __init__(self, enabled: bool = True, master_volume: float = 0.7):
        self.enabled = enabled
        self.master_volume = master_volume
        self.sounds: dict[SoundType, pygame.mixer.Sound] = {}
        self._sample_rate = 22050

        if self.enabled:
            self._init_mixer()
            self._generate_sounds()

    def _init_mixer(self):
        """Initialise le mixer Pygame."""
        pygame.mixer.init(frequency=self._sample_rate, size=-16, channels=1)

    def _generate_sounds(self):
        """Génère tous les sons du jeu."""
        self.sounds[SoundType.WALL_IMPACT] = self._create_wall_impact()
        self.sounds[SoundType.PLATFORM_IMPACT] = self._create_platform_impact()
        self.sounds[SoundType.JUMP] = self._create_jump()
        self.sounds[SoundType.DOUBLE_JUMP] = self._create_double_jump()
        self.sounds[SoundType.BALL_COLLISION] = self._create_ball_collision()
        self.sounds[SoundType.LIFE_LOST] = self._create_life_lost()

    def _create_sound(self, samples: np.ndarray) -> pygame.mixer.Sound:
        """Crée un son Pygame à partir d'un tableau numpy."""
        # Normaliser et convertir en 16-bit
        samples = np.clip(samples, -1, 1)
        samples = (samples * 32767).astype(np.int16)
        return pygame.mixer.Sound(samples)

    def _create_wall_impact(self) -> pygame.mixer.Sound:
        """Son sourd basse fréquence pour impact mur (~150Hz)."""
        duration = 0.08
        t = np.linspace(0, duration, int(self._sample_rate * duration))

        # Onde sinusoïdale basse fréquence avec décroissance rapide
        freq = 150
        envelope = np.exp(-t * 40)
        samples = np.sin(2 * np.pi * freq * t) * envelope * 0.6

        return self._create_sound(samples)

    def _create_platform_impact(self) -> pygame.mixer.Sound:
        """Son plus doux moyenne fréquence pour impact plateforme (~250Hz)."""
        duration = 0.1
        t = np.linspace(0, duration, int(self._sample_rate * duration))

        # Ton plus doux avec harmoniques légères
        freq = 250
        envelope = np.exp(-t * 30)
        samples = (np.sin(2 * np.pi * freq * t) * 0.7 +
                   np.sin(2 * np.pi * freq * 2 * t) * 0.2) * envelope * 0.5

        return self._create_sound(samples)

    def _create_jump(self) -> pygame.mixer.Sound:
        """Sweep ascendant pour le saut (200→400Hz)."""
        duration = 0.12
        t = np.linspace(0, duration, int(self._sample_rate * duration))

        # Fréquence qui monte de 200 à 400 Hz
        freq_start, freq_end = 200, 400
        freq = freq_start + (freq_end - freq_start) * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self._sample_rate

        envelope = np.exp(-t * 15)
        samples = np.sin(phase) * envelope * 0.5

        return self._create_sound(samples)

    def _create_double_jump(self) -> pygame.mixer.Sound:
        """Sweep plus aigu avec harmoniques pour double saut (400→800Hz)."""
        duration = 0.15
        t = np.linspace(0, duration, int(self._sample_rate * duration))

        # Fréquence qui monte de 400 à 800 Hz
        freq_start, freq_end = 400, 800
        freq = freq_start + (freq_end - freq_start) * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self._sample_rate

        envelope = np.exp(-t * 12)
        # Ajouter des harmoniques pour un son plus riche
        samples = (np.sin(phase) * 0.6 +
                   np.sin(phase * 1.5) * 0.25 +
                   np.sin(phase * 2) * 0.15) * envelope * 0.5

        return self._create_sound(samples)

    def _create_ball_collision(self) -> pygame.mixer.Sound:
        """Pop rapide pour collision entre boules (~300Hz)."""
        duration = 0.06
        t = np.linspace(0, duration, int(self._sample_rate * duration))

        # Son court et percutant
        freq = 300
        envelope = np.exp(-t * 60)
        samples = np.sin(2 * np.pi * freq * t) * envelope * 0.5

        return self._create_sound(samples)

    def _create_life_lost(self) -> pygame.mixer.Sound:
        """Son fun descendant pour perte de vie (600→50Hz avec effet comique long)."""
        duration = 1.5  # Plus long pour la mort
        t = np.linspace(0, duration, int(self._sample_rate * duration))

        # Fréquence qui descend de 600 à 50 Hz (effet "oouuhhh" dramatique)
        freq_start, freq_end = 600, 50
        freq = freq_start + (freq_end - freq_start) * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self._sample_rate

        # Enveloppe avec léger vibrato pour effet comique
        envelope = np.exp(-t * 2) * (1 + 0.15 * np.sin(2 * np.pi * 6 * t))
        samples = np.sin(phase) * envelope * 0.7

        return self._create_sound(samples)

    def play(self, sound_type: SoundType, volume: float = 1.0):
        """
        Joue un son.

        Args:
            sound_type: Type de son à jouer
            volume: Volume relatif (0.0 à 1.0)
        """
        if not self.enabled or sound_type not in self.sounds:
            return

        sound = self.sounds[sound_type]
        final_volume = self.master_volume * min(1.0, max(0.0, volume))
        sound.set_volume(final_volume)
        sound.play()
