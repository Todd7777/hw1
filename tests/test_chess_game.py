import pytest
import pygame
import chess
from chess_game import ChessGame

@pytest.fixture
def game(pygame_init, test_assets):
    """Create a game instance for testing"""
    # Create game instance with terminal mode
    game = ChessGame()
    game.terminal_mode = True
    game.state = "PLAYING"
    return game

def test_game_initialization(game):
    """Test game initialization"""
    assert game.board is not None
    assert game.selected_square is None
    assert game.valid_moves == []
    assert game.animated_pieces == []
    assert game.game_over == False

def test_piece_selection(game):
    """Test piece selection mechanics"""
    # Select white pawn at e2
    e2_square = chess.E2
    game.select_square(e2_square)
    
    assert game.selected_square == e2_square
    assert len(game.valid_moves) > 0  # Should have valid moves

def test_piece_movement(game):
    """Test piece movement mechanics"""
    # Move pawn from e2 to e4
    move = chess.Move(chess.E2, chess.E4)
    game.make_move(move)
    
    # Verify move was made
    piece = game.board.piece_at(chess.E4)
    assert piece is not None
    assert piece.piece_type == chess.PAWN
    assert piece.color == chess.WHITE

def test_pawn_promotion(game):
    """Test pawn promotion mechanics"""
    # Set up a position where white pawn is about to promote
    game.board.clear()
    game.board.set_piece_at(chess.B7, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.turn = chess.WHITE
    
    # Create a move with promotion
    move = chess.Move(chess.B7, chess.B8, promotion=chess.QUEEN)
    game.make_move(move)
    
    # Verify promotion to queen
    piece = game.board.piece_at(chess.B8)
    assert piece is not None
    assert piece.piece_type == chess.QUEEN
    assert piece.color == chess.WHITE
