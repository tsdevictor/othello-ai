import sys; args = sys.argv[1:]


def make_move(board, token_to_play, move):
    board, token_to_play = board.lower(), token_to_play.lower()
    board = board[:move] + token_to_play + board[move+1:]

    for choice in [-8, -7, 1, 9, 8, 7, -1, -9]:
        pos = move + choice
        if pos < 0 or pos >= 64 or board[pos] == '.': continue

        if choice % 8 == 0: row_diff, col_diff = 1, 0
        elif choice == 1 or choice == -1: row_diff, col_diff = 0, 1
        else: row_diff, col_diff = 1, 1

        seen_positions = []
        for k in range(1, BW):
            if (pos := move + k * choice) < 0 or pos >= 64 \
                    or abs(pos % BW - move % BW) != k * col_diff \
                    or abs(pos // BW - move // BW) != k * row_diff \
                    or board[pos] == '.': break
            if board[pos] == token_to_play:
                for sp in seen_positions:
                    board = board[:sp] + token_to_play + board[sp+1:]
                break
            seen_positions.append(pos)

    return board, 'o' if token_to_play == 'x' else 'x'


def possible_moves(board, token_to_play):
    board, token_to_play = board.lower(), token_to_play.lower()
    moves = set()
    for i, tile in enumerate(board):
        if tile != token_to_play: continue

        for choice in [-8, -7, 1, 9, 8, 7, -1, -9]:
            pos = i + choice
            if pos < 0 or pos >= 64 or board[pos] in [token_to_play, '.']: continue

            if choice % 8 == 0: row_diff, col_diff = 1, 0
            elif choice == 1 or choice == -1: row_diff, col_diff = 0, 1
            else: row_diff, col_diff = 1, 1

            if abs(pos % BW - i % BW) != col_diff or abs(pos // BW - i // BW) != row_diff: continue

            for k in range(2, BW):
                if (pos := i + k * choice) < 0 or pos >= 64 \
                        or abs(pos % BW - i % BW) != k * col_diff \
                        or abs(pos // BW - i // BW) != k * row_diff \
                        or board[pos] == token_to_play: break
                if board[pos] == '.':
                    moves.add(pos)
                    break

    return moves


def two_d_print(board, moves):
    print('\n'.join([''.join(['*' if r * BW + c in moves else board[r * BW + c] for c in range(BW)]) for r in range(BW)]))


def set_globals():
    # noinspection PyGlobalUndefined
    global X, O, BW, POSITIONS, BOARD, TOKEN_TO_PLAY, MOVE

    X, O, BW = 'x', 'o', 8
    POSITIONS = {(letter + str(i + 1)): (ord(letter) - ord('a')) + i * BW for i in range(BW) for letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']}
    for i in range(BW * BW): POSITIONS[str(i)] = i

    BOARD = '.' * 27 + 'ox......xo' + '.' * 27
    TOKEN_TO_PLAY = False
    MOVE = []
    for arg in args:
        if len(arg) == 64: BOARD = arg
        elif arg in 'XxOo': TOKEN_TO_PLAY = arg
        else: MOVE = POSITIONS[arg.lower()]
    if not TOKEN_TO_PLAY: TOKEN_TO_PLAY = 'x' if BOARD.count('.') % 2 == 0 else 'o'


def main():
    # noinspection PyGlobalUndefined
    global BOARD, TOKEN_TO_PLAY
    set_globals()

    moves = possible_moves(BOARD, TOKEN_TO_PLAY)
    two_d_print(BOARD, moves)
    print()
    print(f'{BOARD} {BOARD.lower().count(X)}/{BOARD.lower().count(O)}')
    if moves: print(f'Possible moves for {TOKEN_TO_PLAY}: {str(moves)[1:-1]}')
    else: print('No moves possible')
    print()

    if MOVE or MOVE == 0:
        print(f'{TOKEN_TO_PLAY} plays to {MOVE}')
        BOARD, TOKEN_TO_PLAY = make_move(BOARD, TOKEN_TO_PLAY, MOVE)
        moves = possible_moves(BOARD, TOKEN_TO_PLAY)
        two_d_print(BOARD, moves)
        print()
        print(f'{BOARD} {BOARD.lower().count(X)}/{BOARD.lower().count(O)}')
        if moves: print(f'Possible moves for {TOKEN_TO_PLAY}: {str(sorted(moves))[1:-1]}\n')
        else: print('No moves possible\n')


if __name__ == '__main__': main()


# Tristan Devictor, pd. 6, 2024
