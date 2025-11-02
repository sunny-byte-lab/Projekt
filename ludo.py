import random
import time

print("DONT PLAY THIS GAME =------error rrorrrorror")
# --- Game Configuration ---
PLAYER_COLORS = ['Red', 'Green', 'Yellow', 'Blue']
# Absolute board positions for each player's start
START_POSITIONS = {'Red': 0, 'Green': 13, 'Yellow': 26, 'Blue': 39}
# Absolute board positions that are safe
SAFE_POSITIONS = {0, 8, 13, 21, 26, 34, 39, 47}
# The main track has 52 squares (0-51)
TRACK_LENGTH = 52
# Home column path
HOME_PATH_LENGTH = 5
# Total steps to win
STEPS_TO_WIN = 51 + HOME_PATH_LENGTH + 1 # 51 on track, 5 in home, 1 to finish

# --- Piece Position States ---
# -1: In Yard
# 0-50: Main track (relative steps from start)
# 51-55: Home column (5 steps)
# 56: Finished (Home)

# --- Game State Variables ---
player_pieces = {}  # Will store positions of 4 pieces for each player
players = []
num_players = 0

# --- Helper Functions ---

def roll_dice():
    """Returns a random integer between 1 and 6."""
    # print("Rolling dice...")
    # time.sleep(1) # Dramatic effect
    return random.randint(1, 6)

def get_absolute_position(player, relative_pos):
    """Converts a player's relative position (0-50) to an absolute board square (0-51)."""
    if relative_pos < 0 or relative_pos > 50:
        return None  # Not on the main track
    
    start = START_POSITIONS[player]
    return (start + relative_pos) % TRACK_LENGTH

def get_player_at_abs_pos(abs_pos):
    """Checks if any player's piece is at a given absolute position."""
    occupants = []
    for player in players:
        for i, rel_pos in enumerate(player_pieces[player]):
            if get_absolute_position(player, rel_pos) == abs_pos:
                occupants.append((player, i)) # (player, piece_index)
    return occupants

def is_occupied_by_self(player, abs_pos):
    """Checks if a player already has a piece on a given absolute square."""
    for rel_pos in player_pieces[player]:
        if get_absolute_position(player, rel_pos) == abs_pos:
            return True
    return False

def check_for_capture(acting_player, abs_pos):
    """Checks for and performs a capture at a given absolute position."""
    if abs_pos in SAFE_POSITIONS:
        return # Cannot capture on a safe square

    occupants = get_player_at_abs_pos(abs_pos)
    for opponent, piece_index in occupants:
        if opponent != acting_player:
            # Capture!
            player_pieces[opponent][piece_index] = -1 # Send back to yard
            print(f"!!! {acting_player} captured {opponent}'s piece {piece_index + 1}!")
            # A capture grants an extra turn in some rules, but we'll stick to 6s for simplicity.

def get_movable_pieces(player, roll):
    """Returns a list of piece indices that can be moved given a dice roll."""
    movable = []
    pieces = player_pieces[player]

    for i, pos in enumerate(pieces):
        if pos == -1:  # Piece is in the yard
            if roll == 6:
                start_abs_pos = START_POSITIONS[player]
                # Check if start is blocked by own piece
                if not is_occupied_by_self(player, start_abs_pos):
                    movable.append(i)
        
        elif pos >= 0: # Piece is on the board
            new_pos = pos + roll
            if new_pos <= 56: # 56 is the 'Finished' state
                # Check for self-blockade only on main track
                if new_pos <= 50: # Moving on main track
                    abs_pos = get_absolute_position(player, new_pos)
                    if not is_occupied_by_self(player, abs_pos):
                        movable.append(i)
                else: # Moving in home column or finishing
                    movable.append(i)
                    
    return list(set(movable)) # Return unique indices

def make_move(player, piece_index, roll):
    """Moves the chosen piece and handles game logic (captures, finishing)."""
    current_pos = player_pieces[player][piece_index]
    
    if current_pos == -1 and roll == 6:
        # Move from yard to start
        new_pos = 0 
    else:
        new_pos = current_pos + roll

    # Check for overshooting home (e.g., needs 2, rolls 4)
    if new_pos > 56:
        print("Move not possible (overshot home).")
        return False # Should be pre-filtered by get_movable_pieces, but as a safeguard

    # Update piece position
    player_pieces[player][piece_index] = new_pos

    if new_pos == 56:
        print(f"*** {player}'s piece {piece_index + 1} is HOME! ***")
    
    # Check for capture (only if moving to a main track square)
    elif new_pos <= 50:
        abs_pos = get_absolute_position(player, new_pos)
        print(f"{player}'s piece {piece_index + 1} moves to square {abs_pos} (rel: {new_pos})")
        check_for_capture(player, abs_pos)
    
    elif new_pos > 50 and new_pos < 56:
        print(f"{player}'s piece {piece_index + 1} moves to home step {new_pos - 50}")
    
    return True

def check_for_win(player):
    """Checks if all 4 of a player's pieces are in the 'Finished' state (56)."""
    return all(pos == 56 for pos in player_pieces[player])

def display_board():
    """Prints a text summary of the current board state."""
    print("\n" + "="*30)
    print(" " * 10 + "LUDO BOARD")
    print("="*30)
    for player in players:
        yard_count = player_pieces[player].count(-1)
        home_count = player_pieces[player].count(56)
        
        print(f"\n--- {player} ({PLAYER_COLORS[players.index(player)]}) ---")
        print(f"  In Yard: {yard_count}")
        print(f"  Finished: {home_count}")
        
        active_pieces = []
        for i, pos in enumerate(player_pieces[player]):
            if 0 <= pos <= 50:
                abs_pos = get_absolute_position(player, pos)
                active_pieces.append(f"Piece {i+1} at [Sq {abs_pos}] (rel: {pos})")
            elif 51 <= pos <= 55:
                active_pieces.append(f"Piece {i+1} in [Home Col {pos-50}]")
        
        if active_pieces:
            for p_str in active_pieces:
                print(f"  * {p_str}")
        else:
            if yard_count + home_count < 4:
                print("  No active pieces on board.")
    print("="*30 + "\n")

# --- Main Game Setup ---

def setup_game():
    """Initializes the game, asks for number of players."""
    global num_players, players, player_pieces
    
    while True:
        try:
            num = int(input("Enter number of players (2-4): "))
            if 2 <= num <= 4:
                num_players = num
                break
            else:
                print("Invalid number. Please enter a value between 2 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    players = PLAYER_COLORS[:num_players]
    for player in players:
        player_pieces[player] = [-1, -1, -1, -1] # All 4 pieces in the yard
    
    print(f"Game starting with {num_players} players: {', '.join(players)}")

# --- Main Game Loop ---

def game_loop():
    """Runs the main turn-based game loop."""
    setup_game()
    
    current_player_index = 0
    winner = None
    
    while winner is None:
        player = players[current_player_index]
        
        display_board()
        print(f"--- {player}'s Turn ---")
        input("Press Enter to roll the dice...")
        
        roll = roll_dice()
        print(f"{player} rolled a {roll}!")
        
        movable_pieces = get_movable_pieces(player, roll)
        
        if not movable_pieces:
            print("No movable pieces.")
        else:
            # Get user choice
            choice = -1
            while True:
                print("Which piece to move?")
                for i, piece_idx in enumerate(movable_pieces):
                    pos = player_pieces[player][piece_idx]
                    desc = ""
                    if pos == -1:
                        desc = f"from yard to start (Sq {START_POSITIONS[player]})"
                    elif 0 <= pos <= 50:
                        desc = f"from [Sq {get_absolute_position(player, pos)}]"
                    elif 51 <= pos <= 55:
                        desc = f"from [Home Col {pos-50}]"
                    print(f"  {i+1}: Piece {piece_idx+1} ({desc})")
                
                try:
                    choice_input = input(f"Enter number (1-{len(movable_pieces)}): ")
                    choice_idx = int(choice_input) - 1
                    
                    if 0 <= choice_idx < len(movable_pieces):
                        piece_to_move = movable_pieces[choice_idx]
                        break # Valid choice
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            # Make the move
            make_move(player, piece_to_move, roll)
            
            # Check for win
            if check_for_win(player):
                winner = player
                break # Exit the while loop
        
        # Handle turn change
        if roll != 6:
            current_player_index = (current_player_index + 1) % num_players
        else:
            print("Rolled a 6! You get another turn.")
            # current_player_index stays the same
        
        time.sleep(1) # Pause for readability

    # Game Over
    print("\n" + "*"*30)
    print(" " * 10 + "GAME OVER!")
    print(f"Congratulations, {winner}! You won the game!")
    print("*"*30)
    display_board()


# --- Run the Game ---
if __name__ == "__main__":
    game_loop()