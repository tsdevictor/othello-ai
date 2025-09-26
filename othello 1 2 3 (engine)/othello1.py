import sys; args = sys.argv[1:]


def possible_moves(board, token_to_play):  # if pos in moves: break
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
    global BW, BOARD, TOKEN_TO_PLAY

    BW = 8
    BOARD = '.' * 27 + 'ox......xo' + '.' * 27
    TOKEN_TO_PLAY = False
    for arg in args:
        if len(arg) == 64: BOARD = arg
        elif arg in 'XxOo': TOKEN_TO_PLAY = arg
    if not TOKEN_TO_PLAY: TOKEN_TO_PLAY = 'x' if BOARD.count('.') % 2 == 0 else 'o'


def main():
    # noinspection PyGlobalUndefined
    global BOARD, TOKEN_TO_PLAY, MOVE_SEQUENCE
    set_globals()

    moves = possible_moves(BOARD, TOKEN_TO_PLAY)
    two_d_print(BOARD, moves)
    print()
    if moves: print(moves)
    else: print('No moves possible')


if __name__ == '__main__': main()


# Tristan Devictor, pd. 6, 2024
