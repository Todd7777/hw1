# Chess Game Test Suite

This directory contains a simplified test suite for the Chess Game application. The tests are designed to run in terminal mode without requiring a display, making them suitable for continuous integration environments.

## Test Structure

### 1. Game Tests (`test_chess_game.py`)
- Game initialization
- Piece selection
- Basic piece movement
- Pawn promotion

### 2. Button Tests (`test_button.py`)
- Button initialization
- Button hover state

### 3. Animation Tests (`test_animated_piece.py`)
- Piece animation initialization
- Animation updates

## Running Tests

1. Make sure you have the test dependencies installed:
```bash
pip install -r requirements-test.txt
```

2. Run the tests:
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_chess_game.py
```

## Test Environment

The tests use a dummy video driver to run in terminal mode without requiring a display. This is configured in `conftest.py` using:
```python
os.environ['SDL_VIDEODRIVER'] = 'dummy'
```

## Adding New Tests

When adding new tests:
1. Follow the existing test structure
2. Use the terminal mode flag when needed
3. Keep tests focused and simple
4. Test one feature at a time
5. Use meaningful assertions
