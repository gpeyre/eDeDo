# eDeDo 🎮

A fast-paced 2D platformer game where you battle enemies, collect power-ups, and progress through procedurally generated levels!

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Pygame Version](https://img.shields.io/badge/pygame-2.6.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Game Features

- **Dynamic Combat**: Jump on enemies' heads to damage them, or shoot them with apple projectiles
- **Enemy Variety**: Three types of enemies with 1, 2, or 3 HP (Blue, Purple, Red)
- **Progressive Difficulty**: Defeat 15 enemies to unlock a portal to the next level
- **Procedural Generation**: Each level features randomly generated platforms and obstacles
- **Energy System**: Manage your energy for double jumps, floating, and shooting
- **Lives System**: Start with 5 lives, collect hearts to recover
- **Controller Support**: Full gamepad support with intuitive controls

## 🎮 Controls

### Keyboard
- **Arrow Keys / WASD**: Move left/right
- **Up Arrow / Space**: Jump (double jump available)
- **Shift**: Float (slow descent)
- **Space (hold)**: Shoot apples / Charge super shot
- **R**: Restart level
- **Escape**: Pause menu

### Controller
- **Left Stick / D-Pad**: Move
- **Button A**: Jump
- **Button B**: Float
- **Button X**: Shoot / Charge
- **Start**: Pause menu

## 📋 Requirements

- Python 3.9 or higher
- Pygame 2.6.1
- NumPy (for audio generation)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ededo.git
cd ededo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python -m game.main
```

## 🎲 Gameplay

1. **Choose Your Color**: Select your ball color at the start
2. **Battle Enemies**: Jump on their heads or shoot them with apples
3. **Manage Energy**: Your energy regenerates after 1 second of not using it (30%/s)
4. **Collect Hearts**: Restore lives when you have less than 5
5. **Reach the Goal**: Defeat 15 enemies to open the portal
6. **Progress**: Enter the portal to generate a new level

### Enemy Types
- 🔵 **Blue** (1 HP): Small and quick
- 🟣 **Purple** (2 HP): Medium strength
- 🔴 **Red** (3 HP): Large and tough

### Combat Mechanics
- **Jump on Head**: Deal 1 damage to enemy, bounce upward
- **Side Collision**: Lose 1 life (with temporary invincibility)
- **Shooting**: Apple projectiles deal 1 damage
- **Charged Shot**: Hold to charge a powerful strawberry projectile

## 🏗️ Project Structure

```
ededo/
├── game/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── config.py         # Game configuration
│   ├── engine.py         # Game engine and main loop
│   ├── entities.py       # Game entities (Ball, Enemy, etc.)
│   ├── physics.py        # Physics engine
│   ├── renderer.py       # Rendering system
│   ├── particles.py      # Particle effects
│   └── audio.py          # Audio system
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## 🛠️ Development

### Running in Development Mode
```bash
python -m game.main
```

### Code Style
The project follows PEP 8 style guidelines with type hints where applicable.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🎨 Credits

- **Game Design & Development**: Your Team
- **Audio**: Procedurally generated using NumPy
- **Graphics**: Programmatic rendering with Pygame

## 🐛 Known Issues

See [todo.md](todo.md) for current development tasks and known issues.

## 📧 Contact

Project Link: [https://github.com/yourusername/ededo](https://github.com/yourusername/ededo)

---

Made with ❤️ and Python
