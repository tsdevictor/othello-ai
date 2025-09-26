import sys; args = sys.argv[1:]


def quickMove(board, token):
    board, token = board.lower(), token.lower()
    moves = possible_moves(board, token)

    for corner in [0, 7, 56, 63]:
        if corner in moves: return corner
    for edge in [2, 3, 4, 5, 16, 24, 32, 40, 22, 29, 36, 43, 58, 59, 60, 61]:
        if edge in moves: return edge

    best_score = -999999
    for move in moves:
        score = len(possible_moves(board, token)) - len(possible_moves(board, ENEMY_TOKEN[token]))
        if score > best_score: best_score, best_move = score, move

    return best_move


def make_move(board, token, move):
    board, token, enemy = [*board.lower()], token.lower(), ENEMY_TOKEN[token]
    board[move] = token

    for direction in NEIGHBORS[move]:
        seen_positions = []
        for pos in direction:
            if board[pos] == '.': break
            if board[pos] == token:
                for sp in seen_positions:
                    board[sp] = token
                break
            seen_positions.append(pos)
    return ''.join(board), enemy


def possible_moves(board, token):
    board, token, enemy = board.lower(), token.lower(), ENEMY_TOKEN[token]
    moves = set()
    for pos in range(64):
        if board[pos] != token: continue
        for direction in NEIGHBORS[pos]:
            for i, move in enumerate(direction):
                if board[move] == token: break
                if board[move] == enemy: continue
                if board[move] == '.' and i != 0: moves.add(move)
                break

    return moves


def two_d_print(board, moves):
    print('\n'.join([''.join(['*' if r * BW + c in moves else board[r * BW + c] for c in range(BW)]) for r in range(BW)]))


def parse_args():
    # noinspection PyGlobalUndefined
    global POSITIONS, BOARD, TOKEN_TO_PLAY, MOVE_SEQUENCE

    POSITIONS = {(letter + str(i + 1)): (ord(letter) - ord('a')) + i * BW for i in range(BW) for letter in 'abcdefgh'}
    for i in range(BW * BW): POSITIONS[str(i)] = i

    BOARD = '.' * 27 + 'ox......xo' + '.' * 27
    TOKEN_TO_PLAY = ''
    MOVE_SEQUENCE = []
    for arg in args:
        arg = arg.lower()
        if len(arg) == 64: BOARD = arg
        elif arg in 'xo': TOKEN_TO_PLAY = arg
        elif '-' not in arg: MOVE_SEQUENCE.append(POSITIONS[arg])
    if not TOKEN_TO_PLAY: TOKEN_TO_PLAY = X if BOARD.count('.') % 2 == 0 else O


def set_globals():
    # noinspection PyGlobalUndefined
    global X, O, BW, ENEMY_TOKEN, DIRECTIONS, ROW_DIFF, COL_DIFF, POSITION_VALUE, NEIGHBORS

    X, O, BW = 'x', 'o', 8
    ENEMY_TOKEN = {X: O, O: X}
    DIRECTIONS = [-8, -7, 1, 9, 8, 7, -1, -9]
    ROW_DIFF = {-8: 1, 8: 1, -1: 0, 1: 0, -7: 1, 7: 1, -9: 1, 9: 1}
    COL_DIFF = {-8: 0, 8: 0, -1: 1, 1: 1, -7: 1, 7: 1, -9: 1, 9: 1}
    POSITION_VALUE = [99, -8, 8, 6, 6, 8, -8, 99,
                      -8, -24, -4, -3, -3, -4, -24, -8,
                      8, -4, 7, 4, 4, 7, -4, 8,
                      6, -3, 4, 0, 0, 4, -3, -6,
                      6, -3, 4, 0, 0, 4, -3, -6,
                      8, -4, 7, 4, 4, 7, -4, 8,
                      -8, -24, -4, -3, -3, -4, -24, -8,
                      99, -8, 8, 6, 6, 8, -8, 99]
    NEIGHBORS = []
    for pos in range(64):
        NEIGHBORS.append([])
        for direction in DIRECTIONS:
            nbrs, row_diff, col_diff = [], ROW_DIFF[direction], COL_DIFF[direction]
            for k in range(1, BW):
                move = pos + k * direction
                if move < 0 or move > 63 \
                   or abs(move % BW - pos % BW) != k * col_diff \
                   or abs(move // BW - pos // BW) != k * row_diff: break
                nbrs.append(move)
            NEIGHBORS[pos].append(nbrs)


def main():
    # noinspection PyGlobalUndefined
    global BOARD, TOKEN_TO_PLAY
    parse_args()

    moves = possible_moves(BOARD, TOKEN_TO_PLAY)
    two_d_print(BOARD, moves)
    print()
    print(f'{BOARD} {BOARD.lower().count(X)}/{BOARD.lower().count(O)}')
    if not moves:
        TOKEN_TO_PLAY = ENEMY_TOKEN[TOKEN_TO_PLAY]
        moves = possible_moves(BOARD, TOKEN_TO_PLAY)
        print(print(f'Possible moves for {TOKEN_TO_PLAY}: {str(moves)[1:-1]}'))
    else:
        print(f'Possible moves for {TOKEN_TO_PLAY}: {str(moves)[1:-1]}')

    for move in MOVE_SEQUENCE:
        print(f'{TOKEN_TO_PLAY} plays to {move}')
        BOARD, TOKEN_TO_PLAY = make_move(BOARD, TOKEN_TO_PLAY, move)
        moves = possible_moves(BOARD, TOKEN_TO_PLAY)
        two_d_print(BOARD, moves)
        print()
        print(f'{BOARD} {BOARD.lower().count(X)}/{BOARD.lower().count(O)}')
        if moves:
            print(f'Possible moves for {TOKEN_TO_PLAY}: {str(sorted(moves))[1:-1]}\n')
        else:
            TOKEN_TO_PLAY = ENEMY_TOKEN[TOKEN_TO_PLAY]
            moves = possible_moves(BOARD, TOKEN_TO_PLAY)
            if moves:
                print(f'Possible moves for {TOKEN_TO_PLAY}: {str(sorted(moves))[1:-1]}\n')
            else:
                print()

    moves = possible_moves(BOARD, TOKEN_TO_PLAY)
    if moves:
        myPref = quickMove(BOARD, TOKEN_TO_PLAY)
        print(f'The preferred move is: {myPref}')


set_globals()
if __name__ == '__main__': main()

# Tristan Devictor, pd. 6, 2024
