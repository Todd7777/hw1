import pygame
import chess
import chess.engine
import sys
import os
import math
from datetime import datetime

# Colors
DARK_SQUARE = (118, 150, 86)    # Forest green
LIGHT_SQUARE = (238, 238, 210)  # Cream
BG_COLOR = (49, 46, 43)         # Dark gray
ACCENT_COLOR = (255, 167, 25)   # Warm orange
TEXT_COLOR = (238, 238, 210)    # Cream
HIGHLIGHT_SELECTED = (246, 246, 105, 160)  # Yellow
HIGHLIGHT_MOVE = (187, 203, 43, 160)      # Light green
HIGHLIGHT_CAPTURE = (235, 97, 80, 160)    # Red
MENU_ACCENT = (72, 69, 64)      # Lighter gray for menu elements

piece_type_map = {
    'p': 'pawn',
    'r': 'rook',
    'n': 'knight',
    'b': 'bishop',
    'q': 'queen',
    'k': 'king'
}

class Button:
    def __init__(self, x, y, width, height, text, callback, color=ACCENT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.base_color = color
        self.hover = False
        self.animation_progress = 0.0
        self.ANIMATION_SPEED = 0.2
        
    def draw(self, screen, font):
        # Update hover animation
        target = 1.0 if self.hover else 0.0
        self.animation_progress += (target - self.animation_progress) * self.ANIMATION_SPEED
        
        # Create button surface with alpha
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Base color with hover effect
        base_color = tuple(min(c + 30 * self.animation_progress, 255) for c in self.base_color)
        
        # Draw button background with rounded corners
        pygame.draw.rect(button_surface, (*base_color, 230), 
                        button_surface.get_rect(), border_radius=8)
        
        # Add subtle gradient
        gradient = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = int(100 * (1 - i/self.rect.height))
            pygame.draw.line(gradient, (255, 255, 255, alpha), 
                           (0, i), (self.rect.width, i))
        button_surface.blit(gradient, (0, 0))
        
        # Draw border
        pygame.draw.rect(button_surface, (*self.base_color, 255), 
                        button_surface.get_rect(), 2, border_radius=8)
        
        # Draw text
        text_color = (255, 255, 255, 255)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=button_surface.get_rect().center)
        button_surface.blit(text_surface, text_rect)
        
        # Draw final button
        screen.blit(button_surface, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

class AnimatedPiece:
    def __init__(self, piece_type, color, start_pos, end_pos):
        self.piece_type = piece_type
        self.color = color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        self.progress = 0.0
        self.ANIMATION_SPEED = 0.08  # Slower, smoother animation
        
    def update(self):
        self.progress = min(1.0, self.progress + self.ANIMATION_SPEED)
        # Smooth easing function using cubic bezier
        t = self.progress
        # Use a smoother easing function for more natural movement
        ease = t * t * (3 - 2 * t) if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
        
        # Calculate current position with scaled coordinates
        self.current_pos = (
            self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * ease,
            self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * ease
        )
        return self.progress >= 1.0

class ChessGame:
    def __init__(self):
        pygame.init()
        
        # For testing in terminal mode
        self.terminal_mode = False
        
        # Set up display
        if not self.terminal_mode:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = pygame.display.get_surface().get_size()
            
            # Calculate scaling factors
            self.scale_x = self.width / 1200
            self.scale_y = self.height / 800
            self.scale = min(self.scale_x, self.scale_y)
            
            # Scale dimensions
            self.BOARD_SIZE = int(700 * self.scale)
            self.SQUARE_SIZE = self.BOARD_SIZE // 8
            self.SIDEBAR_WIDTH = int(300 * self.scale)
            self.BOARD_OFFSET = int(50 * self.scale)
        else:
            # Use default dimensions for terminal mode
            self.width = 1200
            self.height = 800
            self.scale = 1.0
            self.BOARD_SIZE = 700
            self.SQUARE_SIZE = self.BOARD_SIZE // 8
            self.SIDEBAR_WIDTH = 300
            self.BOARD_OFFSET = 50
        
        # Initialize game state
        self.board = chess.Board()
        self.selected_square = None
        self.valid_moves = []
        self.animated_pieces = []
        self.game_over = False
        self.winner = None
        self.player_color = chess.WHITE
        self.state = "MENU"
        self.computer_move_scheduled = False
        self.computer_thinking_start = 0
        
        # Load assets and initialize UI only if not in terminal mode
        if not self.terminal_mode:
            self.load_assets()
            self.init_ui()
        
        # Initialize Stockfish engine
        self.engine = None
        stockfish_paths = [
            "/opt/homebrew/bin/stockfish",
            "/usr/local/bin/stockfish",
            "stockfish"
        ]
        
        for path in stockfish_paths:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(path)
                break
            except Exception:
                continue
        
        self.clock = pygame.time.Clock()
        self.create_buttons()
    
    def create_buttons(self):
        """Create buttons with improved styling"""
        # Scale button dimensions
        button_width = int(220 * self.scale)
        button_height = int(50 * self.scale)
        spacing = int(20 * self.scale)
        
        # Menu buttons - centered
        center_x = self.width // 2
        start_y = self.height // 2
        
        self.menu_buttons = [
            Button(center_x - button_width//2, start_y,
                  button_width, button_height,
                  "Play vs Computer", self.start_vs_computer,
                  color=ACCENT_COLOR),
            Button(center_x - button_width//2, start_y + button_height + spacing,
                  button_width, button_height,
                  "Play with a Friend", self.start_vs_human,
                  color=MENU_ACCENT)
        ]
        
        # Game buttons - in sidebar
        sidebar_x = self.BOARD_SIZE + self.BOARD_OFFSET * 2
        self.game_buttons = [
            Button(sidebar_x, self.height - 150 * self.scale,  # Moved up to make room for restart
                  self.SIDEBAR_WIDTH - 20 * self.scale, button_height,
                  "Restart Game", self.restart_game,
                  color=ACCENT_COLOR),
            Button(sidebar_x, self.height - 100 * self.scale,
                  self.SIDEBAR_WIDTH - 20 * self.scale, button_height,
                  "Resign", self.resign,
                  color=HIGHLIGHT_CAPTURE[:3]),
            Button(sidebar_x, self.height - 50 * self.scale,
                  self.SIDEBAR_WIDTH - 20 * self.scale, button_height,
                  "Main Menu", self.show_menu,
                  color=MENU_ACCENT)
        ]
        
        # Game over buttons
        self.game_over_buttons = [
            Button(center_x - button_width//2, start_y + button_height + spacing,
                  button_width, button_height,
                  "Back to Menu", self.show_menu,
                  color=MENU_ACCENT)
        ]
    
    def init_ui(self):
        """Initialize UI components"""
        # Set up buttons
        button_width = self.SIDEBAR_WIDTH - 20 * self.scale
        button_height = 40 * self.scale
        spacing = 20 * self.scale
        
        # Menu buttons - centered
        center_x = self.width // 2
        start_y = self.height // 2
        
        self.menu_buttons = [
            Button(center_x - button_width//2, start_y,
                  button_width, button_height,
                  "Play vs Computer", self.start_vs_computer),
            Button(center_x - button_width//2, start_y + button_height + spacing,
                  button_width, button_height,
                  "Play with a Friend", self.start_vs_human)
        ]
        
        # Game buttons - in sidebar
        sidebar_x = self.BOARD_SIZE + self.BOARD_OFFSET * 2
        self.game_buttons = [
            Button(sidebar_x, self.height - 150 * self.scale,  # Moved up to make room for restart
                  self.SIDEBAR_WIDTH - 20 * self.scale, button_height,
                  "Restart Game", self.restart_game,
                  color=ACCENT_COLOR),
            Button(sidebar_x, self.height - 100 * self.scale,
                  self.SIDEBAR_WIDTH - 20 * self.scale, button_height,
                  "Resign", self.resign,
                  color=HIGHLIGHT_CAPTURE[:3]),
            Button(sidebar_x, self.height - 50 * self.scale,
                  self.SIDEBAR_WIDTH - 20 * self.scale, button_height,
                  "Main Menu", self.show_menu,
                  color=MENU_ACCENT)
        ]
        
        # Game over buttons
        self.game_over_buttons = [
            Button(center_x - button_width//2, self.height * 2//3,
                  button_width, button_height,
                  "Back to Menu", self.show_menu)
        ]
    
    def select_square(self, square):
        """Select a square on the board (for testing)"""
        self.selected_square = square
        self.valid_moves = [move for move in self.board.legal_moves if move.from_square == square]
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over message
        if self.winner == "computer":
            message = "Computer Wins!"
            submsg = "Better luck next time!"
        elif self.winner == "player":
            message = "Player Wins!"
            submsg = "Congratulations!"
        else:
            message = "Game Over"
            submsg = ""
            
        # Draw main message
        text = self.title_font.render(message, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(self.width//2, self.height//3))
        self.screen.blit(text, text_rect)
        
        # Draw submessage
        if submsg:
            subtext = self.font.render(submsg, True, ACCENT_COLOR)
            subtext_rect = subtext.get_rect(center=(self.width//2, self.height//3 + text_rect.height + 20))
            self.screen.blit(subtext, subtext_rect)
        
        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(self.screen, self.font)

    def draw_status(self):
        """Draw the game status"""
        # Draw sidebar background
        sidebar_x = self.BOARD_SIZE + self.BOARD_OFFSET * 2
        sidebar_rect = pygame.Rect(sidebar_x, self.BOARD_OFFSET, 
                                 self.SIDEBAR_WIDTH - self.BOARD_OFFSET, 
                                 self.BOARD_SIZE)
        
        # Draw status information
        y = sidebar_rect.top + 20
        
        # Draw player info with larger text
        playing_as = self.font.render("Playing as:", True, TEXT_COLOR)
        color = self.font.render("White" if self.player_color else "Black", True, ACCENT_COLOR)
        self.screen.blit(playing_as, (sidebar_x, y))
        self.screen.blit(color, (sidebar_x + playing_as.get_width() + 10, y))
        
        # Draw turn info
        y += int(50 * self.scale)
        turn_text = self.font.render("Turn:", True, TEXT_COLOR)
        turn_color = self.font.render("White" if self.board.turn else "Black", True, ACCENT_COLOR)
        self.screen.blit(turn_text, (sidebar_x, y))
        self.screen.blit(turn_color, (sidebar_x + turn_text.get_width() + 10, y))
        
        # Draw game status
        y += int(50 * self.scale)
        if self.board.is_checkmate():
            status = "Checkmate!"
        elif self.board.is_check():
            status = "Check!"
        elif self.board.is_stalemate():
            status = "Stalemate!"
        else:
            status = "In Progress"
        
        status_text = self.font.render("Status:", True, TEXT_COLOR)
        status_value = self.font.render(status, True, ACCENT_COLOR)
        self.screen.blit(status_text, (sidebar_x, y))
        self.screen.blit(status_value, (sidebar_x + status_text.get_width() + 10, y))
        
        # Draw game buttons
        self.draw_game_buttons()

    def draw_game_buttons(self):
        """Draw the game buttons (Restart, Resign, Main Menu)"""
        # Always show Restart and Main Menu buttons
        self.game_buttons[0].draw(self.screen, self.font)  # Restart Game
        
        # Only show Resign in a game that's not over
        if not self.game_over:
            self.game_buttons[1].draw(self.screen, self.font)  # Resign
            
        self.game_buttons[2].draw(self.screen, self.font)  # Main Menu

    def draw_menu(self):
        """Draw the main menu with improved design"""
        # Draw background
        self.screen.fill(BG_COLOR)
        
        # Calculate center positions
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Draw decorative chess pattern in the background
        pattern_size = 40
        pattern_alpha = 30  # Very subtle
        pattern_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for row in range(self.height // pattern_size + 1):
            for col in range(self.width // pattern_size + 1):
                if (row + col) % 2 == 0:
                    rect = pygame.Rect(col * pattern_size, row * pattern_size, 
                                     pattern_size, pattern_size)
                    pygame.draw.rect(pattern_surface, (*MENU_ACCENT, pattern_alpha), rect)
        self.screen.blit(pattern_surface, (0, 0))
        
        # Draw decorative line at the top
        line_height = 4
        gradient_height = 50
        for i in range(gradient_height):
            alpha = int(255 * (1 - i/gradient_height))
            pygame.draw.line(self.screen, (*ACCENT_COLOR, alpha),
                           (0, line_height + i), (self.width, line_height + i))
        
        # Draw title with shadow effect
        title = "Chess"
        shadow_offset = 3
        title_y = self.height // 3  # Moved down from 1/4 to 1/3
        
        # Draw shadow
        shadow_text = self.title_font.render(title, True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(center_x + shadow_offset, 
                                                 title_y + shadow_offset))
        self.screen.blit(shadow_text, shadow_rect)
        
        # Draw main text
        text = self.title_font.render(title, True, ACCENT_COLOR)
        title_rect = text.get_rect(center=(center_x, title_y))
        self.screen.blit(text, title_rect)
        
        # Draw subtitle
        subtitle = "Welcome to the Game"
        sub_text = self.font.render(subtitle, True, TEXT_COLOR)
        sub_rect = sub_text.get_rect(center=(center_x, title_y + 60))
        self.screen.blit(sub_text, sub_rect)
        
        # Draw decorative chess pieces (moved down)
        piece_size = int(80 * self.scale)
        piece_y = title_y + 120  # Moved below subtitle
        piece_spacing = 100 * self.scale
        
        pieces_to_draw = ['k', 'q', 'r']  # king, queen, rook
        total_width = len(pieces_to_draw) * piece_spacing
        start_x = center_x - total_width//2 + piece_spacing//2
        
        for i, piece in enumerate(pieces_to_draw):
            piece_key = f'{piece}{"w" if i % 2 == 0 else "b"}'
            if piece_key in self.piece_images:
                piece_img = pygame.transform.scale(self.piece_images[piece_key], 
                                                (piece_size, piece_size))
                x = start_x + i * piece_spacing - piece_size//2
                self.screen.blit(piece_img, (x, piece_y))
        
        # Draw buttons with improved styling (moved down)
        button_y = piece_y + piece_size + 50  # Position buttons below pieces
        for button in self.menu_buttons:
            # Update button position for centered layout
            button.rect.centerx = center_x
            button.rect.y = button_y
            button_y += button.rect.height + 20
            button.draw(self.screen, self.font)
        
        # Draw version and controls info
        version_text = "Press ESC to toggle fullscreen"
        version_surface = self.small_font.render(version_text, True, TEXT_COLOR)
        version_rect = version_surface.get_rect(center=(center_x, self.height - 30))
        self.screen.blit(version_surface, version_rect)
    
    def draw_board(self):
        # Create a surface for the entire board area including border
        total_board_size = self.BOARD_SIZE + self.BOARD_OFFSET * 2
        board_surface = pygame.Surface((total_board_size, total_board_size))
        board_surface.fill(BG_COLOR)  # Fill with background color
        
        # Draw the actual board centered on the surface
        for row in range(8):
            for col in range(8):
                x = col * self.SQUARE_SIZE + self.BOARD_OFFSET
                y = row * self.SQUARE_SIZE + self.BOARD_OFFSET
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(board_surface, color, 
                               (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
        
        # Draw coordinates with better positioning
        for i in range(8):
            # File labels (a-h)
            text = self.small_font.render(chess.FILE_NAMES[i], True, TEXT_COLOR)
            x = i * self.SQUARE_SIZE + self.BOARD_OFFSET + self.SQUARE_SIZE//2 - text.get_width()//2
            y = self.BOARD_SIZE + self.BOARD_OFFSET + 5  # Slightly offset from board
            board_surface.blit(text, (x, y))
            
            # Rank labels (1-8)
            text = self.small_font.render(str(8-i), True, TEXT_COLOR)
            x = 5  # Slightly offset from board
            y = i * self.SQUARE_SIZE + self.BOARD_OFFSET + self.SQUARE_SIZE//2 - text.get_height()//2
            board_surface.blit(text, (x, y))
        
        # Draw the board
        self.screen.blit(board_surface, (0, 0))
    
    def draw_pieces(self):
        # Create a surface for pieces that matches the board size
        total_board_size = self.BOARD_SIZE + self.BOARD_OFFSET * 2
        pieces_surface = pygame.Surface((total_board_size, total_board_size), pygame.SRCALPHA)
        
        # Draw regular pieces
        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at(chess.square(col, 7-row))
                if piece:
                    # Skip pieces that are being animated
                    animated = any(
                        ap.piece_type == piece.symbol().lower() and
                        ap.start_pos == (col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                                       row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2)
                        for ap in self.animated_pieces
                    )
                    if animated:
                        continue
                    
                    piece_type = piece.symbol().lower()
                    color = 'w' if piece.color else 'b'
                    piece_key = f'{piece_type}{color}'
                    piece_img = self.piece_images[piece_key]
                    
                    # Center piece in square
                    x = self.BOARD_OFFSET + col * self.SQUARE_SIZE + (self.SQUARE_SIZE - piece_img.get_width()) // 2
                    y = self.BOARD_OFFSET + row * self.SQUARE_SIZE + (self.SQUARE_SIZE - piece_img.get_height()) // 2
                    
                    pieces_surface.blit(piece_img, (x, y))
        
        # Draw animated pieces
        for animated_piece in self.animated_pieces:
            piece_key = f'{animated_piece.piece_type}{animated_piece.color}'
            piece_img = self.piece_images[piece_key]
            x = self.BOARD_OFFSET + animated_piece.current_pos[0] - piece_img.get_width() // 2
            y = self.BOARD_OFFSET + animated_piece.current_pos[1] - piece_img.get_height() // 2
            pieces_surface.blit(piece_img, (x, y))
        
        # Draw the pieces surface
        self.screen.blit(pieces_surface, (0, 0))
    
    def draw_highlights(self):
        if self.selected_square is not None:
            # Create a surface for highlights that matches the board size
            total_board_size = self.BOARD_SIZE + self.BOARD_OFFSET * 2
            highlight_surface = pygame.Surface((total_board_size, total_board_size), pygame.SRCALPHA)
            
            # Highlight selected square
            x = self.BOARD_OFFSET + chess.square_file(self.selected_square) * self.SQUARE_SIZE
            y = self.BOARD_OFFSET + (7 - chess.square_rank(self.selected_square)) * self.SQUARE_SIZE
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(s, HIGHLIGHT_SELECTED, s.get_rect())
            highlight_surface.blit(s, (x, y))
            
            # Show possible moves
            for move in self.valid_moves:
                x = self.BOARD_OFFSET + chess.square_file(move.to_square) * self.SQUARE_SIZE
                y = self.BOARD_OFFSET + (7 - chess.square_rank(move.to_square)) * self.SQUARE_SIZE
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                
                if self.board.piece_at(move.to_square):
                    pygame.draw.rect(s, HIGHLIGHT_CAPTURE, s.get_rect())
                else:
                    pygame.draw.circle(s, HIGHLIGHT_MOVE, 
                                    (self.SQUARE_SIZE//2, self.SQUARE_SIZE//2), 
                                    self.SQUARE_SIZE//6)
                highlight_surface.blit(s, (x, y))
            
            # Draw the highlights surface
            self.screen.blit(highlight_surface, (0, 0))
    
    def resign(self):
        """Resign the current game"""
        self.game_over = True
        self.winner = chess.BLACK if self.board.turn == chess.WHITE else chess.WHITE
    
    def show_menu(self):
        """Show the main menu"""
        self.state = "MENU"
        self.board.reset()
        self.selected_square = None
        self.valid_moves = []
        self.animated_pieces = []
        self.game_over = False
        self.winner = None
    
    def start_vs_computer(self):
        """Start a game against the computer"""
        # Check if engine is available first
        if not self.engine:
            try:
                self.init_engine()
            except Exception as e:
                print(f"Failed to initialize chess engine: {e}")
                return
            
            if not self.engine:
                print("Chess engine not available. Please install Stockfish to play against computer.")
                return

        self.state = "PLAYING"
        self.board.reset()
        self.selected_square = None
        self.valid_moves = []
        self.animated_pieces = []
        self.game_over = False
        self.winner = None
        self.player_color = chess.WHITE
        self.two_player_mode = False
        self.computer_move_scheduled = False
        self.computer_thinking_start = 0
        
        # Initialize Stockfish if not already done
        if not self.engine:
            self.init_engine()
    
    def start_vs_human(self):
        """Start a game against another human"""
        self.state = "PLAYING"
        self.board.reset()
        self.selected_square = None
        self.valid_moves = []
        self.animated_pieces = []
        self.game_over = False
        self.winner = None
        self.player_color = chess.WHITE
        self.two_player_mode = True
    
    def check_game_over(self):
        """Check if the game is over and set the winner accordingly"""
        if self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_insufficient_material():
            self.game_over = True
            if self.board.is_checkmate():
                # The side that made the last move won
                if self.board.turn == chess.WHITE:  # It's white's turn, so black won
                    self.winner = "computer" if self.player_color == chess.WHITE else "player"
                else:  # It's black's turn, so white won
                    self.winner = "player" if self.player_color == chess.WHITE else "computer"
            else:
                self.winner = None  # Draw

    def make_move(self, move):
        if move in self.board.legal_moves:
            # Check for pawn promotion
            piece = self.board.piece_at(move.from_square)
            if (piece and piece.piece_type == chess.PAWN and 
                ((piece.color and chess.square_rank(move.to_square) == 7) or
                 (not piece.color and chess.square_rank(move.to_square) == 0))):
                move.promotion = chess.QUEEN
            
            # Store piece info before the move
            piece = self.board.piece_at(move.from_square)
            from_square, to_square = move.from_square, move.to_square
            
            # Calculate start and end positions
            start_pos = (
                chess.square_file(from_square) * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                (7 - chess.square_rank(from_square)) * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            )
            end_pos = (
                chess.square_file(to_square) * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                (7 - chess.square_rank(to_square)) * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            )
            
            # Create animation
            self.animated_pieces.append(
                AnimatedPiece(piece.symbol().lower(), 
                            'w' if piece.color else 'b',
                            start_pos, end_pos)
            )
            
            # Make the move
            self.board.push(move)
            
            # Check for game over immediately after the move
            self.check_game_over()

    def make_computer_move(self):
        """Make a move for the computer player"""
        if not self.engine:
            print("Chess engine not available")
            self.game_over = True
            self.winner = "player"  # Computer forfeits if engine is not available
            return
        
        try:
            # Set a reasonable time limit for the engine
            result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
            if result.move:
                self.make_move(result.move)
                self.computer_move_scheduled = False
                self.computer_thinking_start = 0
        except chess.engine.EngineTerminatedError:
            print("Chess engine has terminated unexpectedly")
            self.engine = None
            self.game_over = True
            self.winner = "player"
        except Exception as e:
            print(f"Error making computer move: {e}")
            self.game_over = True
            self.winner = "player"
    
    def init_engine(self):
        """Initialize the chess engine"""
        stockfish_paths = [
            "/opt/homebrew/bin/stockfish",
            "/usr/local/bin/stockfish",
            "stockfish"
        ]
        
        for path in stockfish_paths:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(path)
                print(f"Successfully initialized chess engine at: {path}")
                return
            except Exception as e:
                print(f"Failed to initialize engine at {path}: {e}")
                continue
        
        print("Could not initialize chess engine. Please make sure Stockfish is installed.")
    
    def start_game(self, two_player):
        self.state = "PLAYING"
        self.board.reset()
        self.two_player_mode = two_player
        self.player_color = True  # White
        self.selected_square = None
        self.valid_moves = []
        self.animated_pieces = []
        self.game_over = False
        self.winner = None
        self.computer_move_scheduled = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_over and (self.two_player_mode or self.board.turn == self.player_color):
                x, y = event.pos
                file = (x - self.BOARD_OFFSET) // self.SQUARE_SIZE
                rank = 7 - ((y - self.BOARD_OFFSET) // self.SQUARE_SIZE)
                
                if 0 <= file < 8 and 0 <= rank < 8:
                    square = chess.square(file, rank)
                    
                    if self.selected_square is None:
                        piece = self.board.piece_at(square)
                        if piece and piece.color == self.board.turn:
                            self.selected_square = square
                            self.valid_moves = [
                                move for move in self.board.legal_moves
                                if move.from_square == square
                            ]
                    else:
                        move = chess.Move(self.selected_square, square)
                        if move in self.valid_moves:
                            # Check for promotion
                            if (self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                                ((self.board.turn and chess.square_rank(move.to_square) == 7) or
                                 (not self.board.turn and chess.square_rank(move.to_square) == 0))):
                                move.promotion = chess.QUEEN
                            self.make_move(move)
                        
                        self.selected_square = None
                        self.valid_moves = []

    def load_assets(self):
        """Load game assets"""
        # Set up custom fonts with scaled sizes
        font_path = pygame.font.match_font('arial')
        self.title_font = pygame.font.Font(font_path, int(48 * self.scale))
        self.font = pygame.font.Font(font_path, int(24 * self.scale))
        self.small_font = pygame.font.Font(font_path, int(18 * self.scale))
        
        # Load and scale piece images
        self.piece_images = {}
        piece_size = int(self.SQUARE_SIZE * 0.85)
        color_map = {'w': 'white', 'b': 'black'}
        
        for piece in 'rnbqkp':
            for color in 'wb':
                try:
                    # Map piece symbols to full names
                    piece_name = piece_type_map[piece]
                    color_name = color_map[color]
                    img_path = f'pieces/{color_name}_{piece_name}.png'
                    
                    if not os.path.exists(img_path):
                        raise FileNotFoundError(f"Missing piece image: {img_path}")
                    
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.scale(img, (piece_size, piece_size))
                    # Store with short names for internal use
                    self.piece_images[f'{piece}{color}'] = img
                except Exception as e:
                    print(f"Error loading piece image: {e}")
                    pygame.quit()
                    sys.exit(1)

    def __del__(self):
        if hasattr(self, 'engine') and self.engine:
            try:
                self.engine.quit()
            except Exception:
                pass

    def run(self):
        while True:
            self.clock.tick(60)
            self.screen.fill(BG_COLOR)
            
            current_time = pygame.time.get_ticks()
            
            # Handle events first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.engine:
                        try:
                            self.engine.quit()
                        except Exception:
                            pass
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # ESC to toggle fullscreen
                        if self.screen.get_flags() & pygame.FULLSCREEN:
                            self.screen = pygame.display.set_mode((1200, 800))
                        else:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        self.width, self.height = self.screen.get_size()
                        self.scale_x = self.width / 1200
                        self.scale_y = self.height / 800
                        self.scale = min(self.scale_x, self.scale_y)
                        self.create_buttons()  # Recreate buttons with new scaling
                
                if self.game_over:
                    for button in self.game_over_buttons:
                        button.handle_event(event)
                elif self.state == "MENU":
                    for button in self.menu_buttons:
                        button.handle_event(event)
                elif self.state == "PLAYING":
                    for button in self.game_buttons:
                        button.handle_event(event)
                    
                    if not self.game_over:
                        self.handle_event(event)
            
            # Update animations
            for piece in self.animated_pieces[:]:
                if piece.update():
                    self.animated_pieces.remove(piece)
            
            # Draw current state
            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "PLAYING":
                self.draw_board()
                self.draw_pieces()
                self.draw_highlights()
                self.draw_status()
                
                # Make computer move if it's computer's turn
                if (not self.game_over and not self.two_player_mode and 
                    self.board.turn != self.player_color and not self.animated_pieces):
                    if not self.computer_move_scheduled:
                        self.computer_move_scheduled = True
                        self.computer_thinking_start = current_time
                        self.make_computer_move()
                    # Add timeout protection
                    elif current_time - self.computer_thinking_start > 1000:  # 5 second timeout
                        print("Computer move timed out")
                        self.computer_move_scheduled = False
                        self.computer_thinking_start = 0
                        self.game_over = True
                        self.winner = "player"
                
                if self.game_over:
                    self.draw_game_over()
            
            pygame.display.flip()

    def restart_game(self):
        """Restart the current game"""
        self.board.reset()
        self.selected_square = None
        self.valid_moves = []
        self.animated_pieces = []
        self.game_over = False
        self.winner = None
        # Keep the same game mode (vs computer or vs friend)
        if not self.two_player_mode:
            self.player_color = chess.WHITE
            self.computer_move_scheduled = False
            self.computer_thinking_start = 0

if __name__ == "__main__":
    game = ChessGame()
    game.run()
