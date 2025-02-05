import pytest
import pygame
from chess_game import Button

def test_button_initialization():
    """Test button initialization"""
    def dummy_callback():
        pass
    
    button = Button(100, 200, 300, 50, "Test", dummy_callback)
    assert button.text == "Test"
    assert button.rect.x == 100
    assert button.rect.y == 200
    assert button.rect.width == 300
    assert button.rect.height == 50
    assert button.hover == False

def test_button_hover():
    """Test button hover state"""
    def dummy_callback():
        pass
    
    button = Button(100, 200, 300, 50, "Test", dummy_callback)
    
    # Mouse inside button
    button.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {'pos': (150, 225)}))
    assert button.hover == True
    
    # Mouse outside button
    button.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {'pos': (0, 0)}))
    assert button.hover == False
