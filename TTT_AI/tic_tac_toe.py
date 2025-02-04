import streamlit as st
import numpy as np

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
            return True
    return False

def is_board_full(board):
    return " " not in board

def minimax(board, depth, is_maximizing):
    if check_winner(board, "X"):
        return -1
    if check_winner(board, "O"):
        return 1
    if is_board_full(board):
        return 0
    
    if is_maximizing:
        best_score = float("-inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = "O"
                score = minimax(board, depth + 1, False)
                board[i] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = "X"
                score = minimax(board, depth + 1, True)
                board[i] = " "
                best_score = min(score, best_score)
        return best_score

def get_ai_move(board):
    best_score = float("-inf")
    best_move = None
    
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            score = minimax(board, 0, False)
            board[i] = " "
            if score > best_score:
                best_score = score
                best_move = i
    
    return best_move

def main():
    st.title("Tic-Tac-Toe with AI")
    
    # Initialize session state
    if 'board' not in st.session_state:
        st.session_state.board = create_board()
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'winner' not in st.session_state:
        st.session_state.winner = None
    if 'game_mode' not in st.session_state:
        st.session_state.game_mode = None
        
    # Game mode selection
    if st.session_state.game_mode is None:
        st.write("Choose game mode:")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Player vs Player"):
                st.session_state.game_mode = "PVP"
        with col2:
            if st.button("Player vs AI"):
                st.session_state.game_mode = "AI"
        with col3:
            if st.button("AI vs AI"):
                st.session_state.game_mode = "AI_VS_AI"
        return

    # Reset button
    if st.button("Reset Game"):
        st.session_state.board = create_board()
        st.session_state.game_over = False
        st.session_state.winner = None
        st.session_state.game_mode = None
        st.rerun()

    # Display game mode
    st.write(f"Game Mode: {st.session_state.game_mode}")
    
    # Create the game board display
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        for i in range(0, 9, 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if st.session_state.board[idx] == " ":
                    if cols[j].button(" ", key=f"btn_{idx}", use_container_width=True):
                        if not st.session_state.game_over:
                            st.session_state.board[idx] = "X"
                            if check_winner(st.session_state.board, "X"):
                                st.session_state.winner = "X"
                                st.session_state.game_over = True
                            elif not is_board_full(st.session_state.board):
                                # AI move
                                if st.session_state.game_mode in ["AI", "AI_VS_AI"]:
                                    ai_move = get_ai_move(st.session_state.board)
                                    if ai_move is not None:
                                        st.session_state.board[ai_move] = "O"
                                        if check_winner(st.session_state.board, "O"):
                                            st.session_state.winner = "O"
                                            st.session_state.game_over = True
                            if is_board_full(st.session_state.board):
                                st.session_state.game_over = True
                            st.rerun()
                else:
                    cols[j].button(st.session_state.board[idx], key=f"btn_{idx}", use_container_width=True)

    # Display game status
    if st.session_state.game_over:
        if st.session_state.winner:
            st.success(f"Player {st.session_state.winner} wins!")
        else:
            st.info("It's a draw!")
    else:
        current_player = "X" if sum(x != " " for x in st.session_state.board) % 2 == 0 else "O"
        st.write(f"Current player: {current_player}")

if __name__ == "__main__":
    main() 