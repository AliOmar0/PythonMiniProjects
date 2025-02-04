import random
import time
from typing import List, Tuple, Optional

class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.current_winner = None

    def print_board(self):
        for row in [self.board[i:i + 3] for i in range(0, 9, 3)]:
            print("| " + " | ".join(row) + " |")
            print("-" * 13)

    def print_board_nums(self):
        number_board = [[str(i + 1) for i in range(j * 3, (j + 1) * 3)] for j in range(3)]
        for row in number_board:
            print("| " + " | ".join(row) + " |")
            print("-" * 13)

    def available_moves(self) -> List[int]:
        return [i for i, spot in enumerate(self.board) if spot == " "]

    def empty_squares(self) -> bool:
        return " " in self.board

    def num_empty_squares(self) -> int:
        return self.board.count(" ")

    def make_move(self, square: int, letter: str) -> bool:
        if self.board[square] == " ":
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square: int, letter: str) -> bool:
        # Check row
        row_ind = square // 3
        row = self.board[row_ind * 3:(row_ind + 1) * 3]
        if all(spot == letter for spot in row):
            return True

        # Check column
        col_ind = square % 3
        column = [self.board[col_ind + i * 3] for i in range(3)]
        if all(spot == letter for spot in column):
            return True

        # Check diagonals
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all(spot == letter for spot in diagonal1):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all(spot == letter for spot in diagonal2):
                return True

        return False

class Player:
    def __init__(self, letter: str):
        self.letter = letter

    def get_move(self, game: TicTacToe) -> int:
        pass

class HumanPlayer(Player):
    def get_move(self, game: TicTacToe) -> int:
        valid_square = False
        val = None
        while not valid_square:
            square = input(f"{self.letter}'s turn. Input move (1-9): ")
            try:
                val = int(square) - 1
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print("Invalid square. Try again.")
        return val

class AIPlayer(Player):
    def __init__(self, letter: str, difficulty: str = 'hard'):
        super().__init__(letter)
        self.difficulty = difficulty

    def get_move(self, game: TicTacToe) -> int:
        if self.difficulty == 'easy':
            return random.choice(game.available_moves())
        
        if len(game.available_moves()) == 9:
            return random.choice(game.available_moves())
        
        return self.minimax(game, self.letter)['position']

    def minimax(self, state: TicTacToe, player: str) -> dict:
        max_player = self.letter
        other_player = 'O' if player == 'X' else 'X'

        if state.current_winner == other_player:
            return {
                'position': None,
                'score': 1 * (state.num_empty_squares() + 1) if other_player == max_player else -1 * (
                    state.num_empty_squares() + 1)
            }
        elif not state.empty_squares():
            return {'position': None, 'score': 0}

        if player == max_player:
            best = {'position': None, 'score': float('-inf')}
        else:
            best = {'position': None, 'score': float('inf')}

        for possible_move in state.available_moves():
            state.make_move(possible_move, player)
            sim_score = self.minimax(state, other_player)

            state.board[possible_move] = ' '
            state.current_winner = None
            sim_score['position'] = possible_move

            if player == max_player:
                if sim_score['score'] > best['score']:
                    best = sim_score
            else:
                if sim_score['score'] < best['score']:
                    best = sim_score

        return best

def play(game: TicTacToe, x_player: Player, o_player: Player, print_game: bool = True) -> Optional[str]:
    if print_game:
        game.print_board_nums()

    letter = 'X'
    while game.empty_squares():
        if letter == 'X':
            square = x_player.get_move(game)
        else:
            square = o_player.get_move(game)

        if game.make_move(square, letter):
            if print_game:
                print(f"\n{letter} makes a move to square {square + 1}")
                game.print_board()
                print()

            if game.current_winner:
                if print_game:
                    print(letter + ' wins!')
                return letter

            letter = 'O' if letter == 'X' else 'X'

        if print_game:
            time.sleep(0.8)

    if print_game:
        print('It\'s a tie!')
    return None

def main():
    while True:
        print("\nWelcome to Tic Tac Toe!")
        print("1. Player vs Player")
        print("2. Player vs AI")
        print("3. AI vs AI")
        print("4. Exit")
        
        choice = input("Select game mode (1-4): ")
        
        if choice == '4':
            break
            
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Please try again.")
            continue
            
        if choice == '1':
            x_player = HumanPlayer('X')
            o_player = HumanPlayer('O')
        elif choice == '2':
            player_letter = input("Choose your letter (X/O): ").upper()
            if player_letter not in ['X', 'O']:
                print("Invalid letter. Defaulting to X")
                player_letter = 'X'
            
            if player_letter == 'X':
                x_player = HumanPlayer('X')
                o_player = AIPlayer('O')
            else:
                x_player = AIPlayer('X')
                o_player = HumanPlayer('O')
        else:
            x_player = AIPlayer('X')
            o_player = AIPlayer('O')
            
        t = TicTacToe()
        play(t, x_player, o_player, print_game=True)
        
        play_again = input("\nWould you like to play again? (y/n): ")
        if play_again.lower() != 'y':
            break

if __name__ == '__main__':
    main() 