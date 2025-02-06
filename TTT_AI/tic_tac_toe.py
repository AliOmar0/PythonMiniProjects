import streamlit as st
import numpy as np
import time

def init_styles():
    """Initialize custom CSS styles"""
    st.markdown("""
        <style>
        /* Container spacing */
        .main {
            padding: 2rem 1rem;
        }
        
        /* Game title */
        .game-title {
            text-align: center;
            color: #343a40;
            font-size: 48px;
            margin: 2rem 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Game mode selection */
        .mode-button {
            width: 100%;
            background-color: #2c3338;
            border: 2px solid #1a1d20;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 180px;
            display: flex !important;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            color: #ffffff;
        }
        
        .mode-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
            border-color: #3b9cff;
        }
        
        .mode-icon {
            font-size: 48px;
            margin-bottom: 1rem;
        }
        
        .mode-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .mode-desc {
            font-size: 14px;
            color: #a0a0a0;
            text-align: center;
        }
        
        /* Difficulty selector */
        .difficulty-selector {
            max-width: 400px;
            margin: 2rem auto;
            padding: 1.5rem;
            background-color: #2c3338;
            border: 2px solid #1a1d20;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        /* Game info and status */
        .game-info {
            text-align: center;
            font-size: 24px;
            margin: 1.5rem 0;
            color: #ffffff;
        }
        
        .game-status {
            text-align: center;
            font-size: 28px;
            padding: 1rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }
        
        /* Game board */
        .board-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 2rem auto;
            max-width: 360px;
        }
        
        .board-row {
            display: flex;
            justify-content: center;
            margin: 0.25rem 0;
        }
        
        /* Game cells */
        .stButton > button {
            all: unset;
            width: 100px;
            height: 100px;
            background-color: #2c3338;
            border: 3px solid #1a1d20;
            border-radius: 12px;
            font-size: 64px;
            font-weight: 900;
            line-height: 1;
            color: #6c757d;
            cursor: pointer;
            transition: all 0.2s;
            margin: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.3);
            background-color: #343a40;
        }
        
        .stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        .stButton > button:disabled {
            cursor: not-allowed;
            opacity: 1;
            background-color: #2c3338;
        }
        
        .stButton > button[data-value="X"] {
            color: #ff4d5f;
            text-shadow: 0 0 15px rgba(255, 77, 95, 0.4);
        }
        
        .stButton > button[data-value="O"] {
            color: #3b9cff;
            text-shadow: 0 0 15px rgba(59, 156, 255, 0.4);
        }
        
        /* Column spacing */
        div[data-testid="column"] {
            display: flex;
            justify-content: center;
            padding: 0.5rem;
        }
        
        /* Control buttons */
        div[data-testid="column"] > .stButton > button {
            margin: 0.5rem;
            height: auto;
            min-height: 50px;
        }
        
        /* Dark theme adjustments */
        .stApp {
            background-color: #1a1d20;
        }
        
        .stMarkdown {
            color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)

def create_board():
    return np.array([" "] * 9)

def check_winner(board, player):
    # Check rows, columns and diagonals
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]  # Diagonals
    ]
    
    for combo in winning_combinations:
        if all(board[i] == player for i in combo):
            return True, combo
    return False, None

def is_board_full(board):
    return " " not in board

def get_empty_squares(board):
    return [i for i, val in enumerate(board) if val == " "]

def minimax(board, depth, is_maximizing, player, alpha=float("-inf"), beta=float("inf")):
    """
    Minimax algorithm with alpha-beta pruning.
    player parameter indicates which AI is currently playing (X or O)
    """
    opponent = "O" if player == "X" else "X"
    
    # Check terminal states
    winner, _ = check_winner(board, player)
    if winner:
        return 1
    winner, _ = check_winner(board, opponent)
    if winner:
        return -1
    if is_board_full(board):
        return 0
    
    if is_maximizing:
        best_score = float("-inf")
        for i in get_empty_squares(board):
            board[i] = player
            score = minimax(board, depth + 1, False, player, alpha, beta)
            board[i] = " "
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = float("inf")
        for i in get_empty_squares(board):
            board[i] = opponent
            score = minimax(board, depth + 1, True, player, alpha, beta)
            board[i] = " "
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score

def get_ai_move(board, difficulty="hard", current_player="O"):
    """Get AI move based on difficulty and current player"""
    empty_squares = get_empty_squares(board)
    if not empty_squares:
        return None
        
    if difficulty == "easy":
        # Random move with 70% chance, smart move with 30% chance
        if np.random.random() < 0.7:
            return np.random.choice(empty_squares)
    elif difficulty == "medium":
        # Random move with 30% chance, smart move with 70% chance
        if np.random.random() < 0.3:
            return np.random.choice(empty_squares)
    
    # For hard difficulty or when not making a random move
    best_score = float("-inf")
    best_move = empty_squares[0]
    
    for i in empty_squares:
        board[i] = current_player
        score = minimax(board, 0, False, current_player)
        board[i] = " "
        if score > best_score:
            best_score = score
            best_move = i
    
    return best_move

def get_button_style(value, winning_cells=None, idx=None):
    """Get the style for a cell based on its value"""
    if winning_cells and idx in winning_cells:
        bg_color = "#28a745"  # Green for winning line
    else:
        bg_color = "#ffffff"  # White background
    
    color = {
        "X": "#dc3545",  # Red for X
        "O": "#007bff",  # Blue for O
        " ": "#6c757d"   # Gray for empty
    }.get(value, "#6c757d")
    
    return color

def render_game_mode_button(icon, title, description):
    return f"""
        <div class="game-mode-button">
            <div class="game-mode-icon">{icon}</div>
            <div class="game-mode-title">{title}</div>
            <div class="game-mode-desc">{description}</div>
        </div>
    """

def main():
    # Initialize session state
    if 'board' not in st.session_state:
        st.session_state.board = create_board()
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'winner' not in st.session_state:
        st.session_state.winner = None
    if 'winning_cells' not in st.session_state:
        st.session_state.winning_cells = None
    if 'game_mode' not in st.session_state:
        st.session_state.game_mode = None
    if 'current_player' not in st.session_state:
        st.session_state.current_player = "X"
    if 'ai_thinking' not in st.session_state:
        st.session_state.ai_thinking = False
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = "medium"
    
    # Initialize styles
    init_styles()
    
    # Title
    st.markdown('<h1 class="game-title">Tic-Tac-Toe with AI</h1>', unsafe_allow_html=True)
    
    # Game mode selection
    if st.session_state.game_mode is None:
        st.markdown('<p class="game-info">Choose your game mode:</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👥\nPlayer vs Player", 
                        key="pvp", 
                        use_container_width=True, 
                        help="Play against another player locally"):
                st.session_state.game_mode = "PVP"
                st.rerun()
                
        with col2:
            if st.button("🤖\nPlayer vs AI", 
                        key="ai", 
                        use_container_width=True,
                        help="Play against the AI with adjustable difficulty"):
                st.session_state.game_mode = "AI"
                st.rerun()
                
        with col3:
            if st.button("🤖 🤖\nAI vs AI", 
                        key="ai_vs_ai", 
                        use_container_width=True,
                        help="Watch two AI players play against each other"):
                st.session_state.game_mode = "AI_VS_AI"
                st.rerun()
        
        if st.session_state.game_mode == "AI":
            st.markdown('<div class="difficulty-selector">', unsafe_allow_html=True)
            st.markdown('<p class="game-info">Select AI Difficulty</p>', unsafe_allow_html=True)
            difficulty = st.select_slider(
                "",
                options=["easy", "medium", "hard"],
                value="medium",
                key="difficulty_slider"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.session_state.difficulty = difficulty
        return

    # Game controls
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 New Game", use_container_width=True, key="new_game"):
            st.session_state.board = create_board()
            st.session_state.game_over = False
            st.session_state.winner = None
            st.session_state.winning_cells = None
            st.session_state.game_mode = None
            st.session_state.current_player = "X"
            st.session_state.ai_thinking = False
            st.rerun()
    
    with col2:
        mode_text = {
            "PVP": "👥 Player vs Player",
            "AI": f"🤖 Player vs AI (Difficulty: {st.session_state.difficulty.title()})",
            "AI_VS_AI": "🤖 AI vs AI"
        }
        st.markdown(f'<p class="game-info">{mode_text[st.session_state.game_mode]}</p>', unsafe_allow_html=True)
    
    # Game status
    if not st.session_state.game_over:
        if st.session_state.ai_thinking:
            st.markdown('<p class="game-status" style="background-color: #2c3338; color: #3b9cff; border: 2px solid #1a1d20;">🤖 AI is thinking...</p>', unsafe_allow_html=True)
        else:
            current = "X" if st.session_state.current_player == "X" else "O"
            color = "#ff4d5f" if current == "X" else "#3b9cff"
            st.markdown(f'<p class="game-status" style="color: {color};">Current player: {current}</p>', unsafe_allow_html=True)
    
    # Game board
    st.markdown('<div class="board-container">', unsafe_allow_html=True)
    for i in range(0, 9, 3):
        st.markdown('<div class="board-row">', unsafe_allow_html=True)
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            with cols[j]:
                cell_value = st.session_state.board[idx]
                # In AI vs AI mode, all buttons should be disabled
                if st.session_state.game_mode == "AI_VS_AI":
                    st.button(cell_value if cell_value != " " else "", key=f"btn_{idx}", disabled=True)
                else:
                    if cell_value == " " and not st.session_state.game_over:
                        if st.button("", key=f"btn_{idx}"):
                            if not st.session_state.ai_thinking:
                                st.session_state.board[idx] = st.session_state.current_player
                                winner, winning_combo = check_winner(st.session_state.board, st.session_state.current_player)
                                
                                if winner:
                                    st.session_state.winner = st.session_state.current_player
                                    st.session_state.winning_cells = winning_combo
                                    st.session_state.game_over = True
                                elif is_board_full(st.session_state.board):
                                    st.session_state.game_over = True
                                else:
                                    if st.session_state.game_mode == "PVP":
                                        st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"
                                    elif st.session_state.game_mode == "AI":
                                        st.session_state.ai_thinking = True
                                st.rerun()
                    else:
                        st.button(cell_value, key=f"btn_{idx}", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI moves
    if not st.session_state.game_over and st.session_state.ai_thinking:
        time.sleep(0.5)
        ai_move = get_ai_move(st.session_state.board, st.session_state.difficulty)
        if ai_move is not None:
            st.session_state.board[ai_move] = "O"
            winner, winning_combo = check_winner(st.session_state.board, "O")
            if winner:
                st.session_state.winner = "O"
                st.session_state.winning_cells = winning_combo
                st.session_state.game_over = True
            elif is_board_full(st.session_state.board):
                st.session_state.game_over = True
            else:
                st.session_state.current_player = "X"
        st.session_state.ai_thinking = False
        st.rerun()
    
    # AI vs AI mode
    if st.session_state.game_mode == "AI_VS_AI" and not st.session_state.game_over:
        time.sleep(0.8)  # Slight delay for better visualization
        current_player = st.session_state.current_player  # "X" or "O"
        
        # Get move for current AI player
        ai_move = get_ai_move(st.session_state.board, "hard", current_player)
        
        if ai_move is not None:
            st.session_state.board[ai_move] = current_player
            winner, winning_combo = check_winner(st.session_state.board, current_player)
            if winner:
                st.session_state.winner = current_player
                st.session_state.winning_cells = winning_combo
                st.session_state.game_over = True
            elif is_board_full(st.session_state.board):
                st.session_state.game_over = True
            else:
                st.session_state.current_player = "O" if current_player == "X" else "X"
            st.rerun()
    
    # Game over status
    if st.session_state.game_over:
        if st.session_state.winner:
            color = "#ff4d5f" if st.session_state.winner == "X" else "#3b9cff"
            st.markdown(
                f'<p class="game-status" style="background-color: #2c3338; color: {color}; '
                f'border: 2px solid #1a1d20; font-size: 32px; font-weight: bold; '
                f'text-shadow: 0 0 10px {color}4d;">'
                f'🎉 Player {st.session_state.winner} wins! 🎉</p>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<p class="game-status" style="background-color: #2c3338; color: #ffd700; '
                'border: 2px solid #1a1d20; font-size: 32px; font-weight: bold; '
                'text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);">'
                '🤝 It\'s a draw! 🤝</p>',
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    st.set_page_config(page_title="Tic-Tac-Toe", layout="centered")
    main() 