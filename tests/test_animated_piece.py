import pytest
from chess_game import AnimatedPiece

def test_animated_piece_initialization():
    """Test animated piece initialization"""
    piece = AnimatedPiece('p', 'b', (0, 0), (100, 100))
    assert piece.piece_type == 'p'
    assert piece.color == 'b'
    assert piece.start_pos == (0, 0)
    assert piece.end_pos == (100, 100)
    assert piece.progress == 0.0

def test_animated_piece_update():
    """Test piece animation update"""
    piece = AnimatedPiece('p', 'b', (0, 0), (100, 100))
    piece.update()
    assert piece.progress > 0.0
    assert piece.progress <= 1.0
