### The Advanced Chess Game

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

## Introduction

It has always been my dream to build my own chess game, similar to the ones I play on platforms like CoolmathGames. To challenge myself and fine tune my programming skills, I decided to develop this project entirely by hand, which took approximately 40 hours to complete. I handled every aspect of the project, from designing the UI and implementing game logic to integrating Stockfish for an AI opponent, and embedding a legal move validator algorithm.

One of the most challenging parts was ensuring the smooth execution of the chess engine's API calls and animating piece movements to provide a professional feel. Implementing legal move validation, especially for checkmate detection, required significant effort. Handling edge cases, such as stalemates, insufficient material draws, and en passant captures, further complicated the logic.

To ensure robust game state management, I introduced precise tracking for computer move scheduling. Specifically, I implemented `self.computer_move_scheduled` to indicate when the engine is processing a move and `self.computer_thinking_start` to timestamp when the AI begins its calculation. This avoids unnecessary redundant calls and ensures moves are executed efficiently.

Another significant improvement was optimizing computer move execution by:
- Ensuring no animations are in progress before scheduling a move.
- Implementing a timeout to prevent the game from freezing if the engine fails to respond.
- Resetting scheduling flags once a move completes successfully.
- Implementing a condition where if the AI exceeds the time limit, the game ends in a player victory to prevent indefinite stalls.

State management was also improved to handle restarts and prevent unintended behavior. When starting a new game, all computer move flags are reset, animations are cleared, and the game board is properly reinitialized. I also ensured game-ending conditions properly lock the board state to prevent illegal moves after checkmate or stalemate.

By refining move validation, AI scheduling, and game state management, I created a fully functional chess experience that can be expanded and deployed in the future. Super excited to share this project with everyone!

## The Game

A sophisticated chess implementation featuring both player-vs-player and player-vs-computer gameplay modes. Built with Python and Pygame, this application combines classical chess rules with modern UI design and AI integration through the Stockfish chess engine.

## 🎮 Features

- **Dual Game Modes**
  - Play against Stockfish chess engine
  - Play with a friend locally
  - Real-time move validation

- **Improved UI/UX**
  - Smooth piece animations
  - Intuitive drag-and-drop interface
  - Legal move highlighting
  - Coordinate notation display
  - Game state indicators

- **Advanced Gameplay Features**
  - Full chess rule implementation
  - Support for special moves (castling, en passant, pawn promotion)
  - Move validation and check detection
  - Stalemate and checkmate detection
  - Game state persistence

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Stockfish chess engine
- Pygame library

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Todd7777/hw1.git
   cd hw1
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Stockfish chess engine:
   - **macOS**: `brew install stockfish`
   - **Linux**: `sudo apt-get install stockfish`
   - **Windows**: Download from [Stockfish's official website](https://stockfishchess.org/download/)

### Running the Game

```bash
python chess_game.py
```

## 🎯 How to Play

1. **Starting a Game**
   - Launch the application
   - Choose "Play vs Computer" or "Play with a Friend"
   - For computer games, you'll play as White

2. **Making Moves**
   - Click and drag pieces to valid squares
   - Valid moves are highlighted
   - Illegal moves are automatically prevented

3. **Game Controls**
   - ESC: Toggle fullscreen
   - Restart: Start a new game
   - Resign: Forfeit current game
   - Main Menu: Return to mode selection

## 🛠️ Technical Implementation

The game is built with a focus on:
- Clean, modular code architecture
- Efficient state management
- Responsive UI with smooth animations
- Robust error handling
- Comprehensive test coverage

Key components:
- Board state management using python-chess
- UI rendering with Pygame
- AI integration with Stockfish
- Event-driven architecture for game flow

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📞 Contact

For questions or feedback, please contact me at 240-506-9984.

## Acknowledgments

- Stockfish team for their powerful chess engine
- Pygame community for the graphics library
- Competitive chess community for inspiration and UI design ideas
