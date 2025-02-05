import pytest
import pygame
import os

@pytest.fixture(scope="session")
def pygame_init():
    """Initialize pygame for testing with a dummy display"""
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))  # Create a tiny dummy display
    yield
    pygame.quit()

@pytest.fixture(scope="session")
def test_assets():
    """Verify test assets are available"""
    pieces_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pieces")
    assert os.path.exists(pieces_dir), "Pieces directory not found"
