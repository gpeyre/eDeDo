# Contributing to eDeDo

First off, thank you for considering contributing to eDeDo! 🎮

## Code of Conduct

This project and everyone participating in it is governed by respect and kindness.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When you create a bug report, include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what you expected**
* **Include screenshots if possible**
* **Note your environment** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include comments in your code where necessary
* Update the README.md with details of changes if needed
* Test your changes thoroughly

## Development Setup

1. Fork the repo
2. Clone your fork
3. Install dependencies: `pip install -r requirements.txt`
4. Create a branch: `git checkout -b feature/my-feature`
5. Make your changes
6. Test your changes: `python -m game.main`
7. Commit: `git commit -m 'Add amazing feature'`
8. Push: `git push origin feature/my-feature`
9. Open a Pull Request

## Style Guidelines

### Python Style Guide

* Follow PEP 8
* Use type hints where applicable
* Maximum line length: 120 characters
* Use docstrings for classes and functions

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters
* Reference issues and pull requests after the first line

## Project Structure

```
game/
├── __init__.py       # Package initialization
├── main.py          # Entry point
├── config.py        # Configuration constants
├── engine.py        # Game engine
├── entities.py      # Game entities
├── physics.py       # Physics engine
├── renderer.py      # Rendering
├── particles.py     # Particle effects
└── audio.py         # Audio system
```

Thank you for contributing! 🎉
