import sys; args = sys.argv[1:]
import re
import random
import cProfile


MAKE_MOVE = {}
def makeMove(brd, tkn, move, lower=True):
    if lower: brd, tkn = [*brd.lower()], tkn.lower()
    key = (brd + tkn, move[0])
    if key in MAKE_MOVE: return MAKE_MOVE[key]
    brd = [*brd]

    brd[move[0]] = tkn
    for flip in move[1]:
        brd[flip] = tkn

    result = ''.join(brd)
    MAKE_MOVE[key] = result
    return result


MOVE_CACHE = {}
def findMoves(brd, tkn, lower=True):
    if lower: brd, tkn = brd.lower(), tkn.lower()

    key = brd + tkn
    if key in MOVE_CACHE:
        return MOVE_CACHE[key]

    enemy = ENEMY[tkn]

    psbl_moves = []
    for pos in range(64):
        if brd[pos] != '.': continue
        flipped = []
        add = False
        for direction in NBRS[pos]:
            seen = []
            if direction and brd[direction[0]] != enemy: continue
            for move in direction:
                if brd[move] == enemy:
                    seen.append(move)
                    continue
                if brd[move] == tkn:
                    add = True
                    flipped += seen
                break
        if add: psbl_moves.append((pos, flipped))

    MOVE_CACHE[key] = psbl_moves
    return psbl_moves


def negamax(brd, tkn):
    return negamax_recur(brd.lower(), tkn.lower())


NEGAMAX_CACHE = {}
def negamax_recur(brd, tkn):
    key = brd + tkn
    if key in NEGAMAX_CACHE: return NEGAMAX_CACHE[key]

    enemy = ENEMY[tkn]
    moves = findMoves(brd, tkn, False)
    if '.' not in brd or (not moves and not findMoves(brd, enemy, False)): return [brd.count(tkn)-brd.count(enemy)]
    if not moves:
        nm = negamax_recur(brd, enemy)
        best = [-nm[0]] + nm[1:] + [-1]
        NEGAMAX_CACHE[key] = best
        return best

    best_so_far = [-65]
    for mv in moves:
        new_brd = makeMove(brd, tkn, mv, False)
        nm = negamax_recur(new_brd, enemy)
        if -nm[0] > best_so_far[0]:
            best_so_far = [-nm[0]] + nm[1:] + [mv]

    NEGAMAX_CACHE[key] = best_so_far
    return best_so_far


def quickMove(brd, tkn, psbl_moves=0):
    brd, tkn, enemy = brd.lower(), tkn.lower(), ENEMY[tkn]

    if brd.count('.') < N: return negamax(brd, tkn)[-1]

    if not psbl_moves: psbl_moves = findMoves(brd, tkn, False)
    for move in psbl_moves:
        if move in CORNERS: return move
        new_brd = makeMove(brd, tkn, move, False)
        for edge_indices in EDGES:
            if move not in edge_indices: continue
            edge = ''.join([new_brd[i] for i in edge_indices])
            if len(set(edge[:edge_indices.index(move)+1])) == 1 or len(set(edge[edge_indices.index(move):])) == 1:
                return move

    ok_moves = [move for move in psbl_moves if not (move in ADJ_CORNERS and ADJ_CORNERS[move] != tkn)]
    return random.choice(ok_moves) if ok_moves else random.choice([*psbl_moves])


def two_d_print(brd, psbl_moves):
    print('\n'.join([''.join(['*' if r * 8 + c in psbl_moves else brd[r * 8 + c] for c in range(8)]) for r in range(8)]))


def parse_args():
    positions = {(letter + str(i + 1)): (ord(letter) - ord('a')) + i * 8 for i in range(8) for letter in 'abcdefgh'}
    for i in range(64): positions[str(i)] = i

    brd = '.' * 27 + 'ox......xo' + '.' * 27
    tkn = ''
    psbl_moves = []
    for arg in args:
        arg = arg.lower()
        if re.match('^[xo.]{64}$', arg): brd = arg
        elif arg in 'xo': tkn = arg
        elif '-' not in arg: psbl_moves += [int(arg[i:i+2]) if '_' not in arg[i:i+2] else int(arg[i+1:i+2]) for i in range(0, len(arg), 2)]
    if not tkn: tkn = 'x' if brd.count('.') % 2 == 0 else 'o'
    return brd, tkn, psbl_moves


def set_globals():
    # noinspection PyGlobalUndefined
    global ENEMY, EDGES, POSITION_VALUE, NBRS, CORNERS, ADJ_CORNERS, N, VERTICAL_REFLECT

    N = 10
    ENEMY = {'x': 'o', 'o': 'x', 'X': 'o', 'O': 'x'}
    EDGES = [[0, 1, 2, 3, 4, 5, 6, 7], [0, 8, 16, 24, 32, 40, 48, 56], [56, 57, 58, 59, 60, 61, 62, 63], [7, 15, 23, 31, 39, 47, 55, 63]]
    CORNERS = (0, 7, 56, 63)
    ADJ_CORNERS = {1: 0, 8: 0, 9: 0, 6: 7, 14: 7, 15: 7, 48: 56, 49: 56, 57: 56, 62: 63, 54: 63, 55: 63}
    POSITION_VALUE = [99, -8, 8, 6, 6, 8, -8, 99,
                      -8, -24, -4, -3, -3, -4, -24, -8,
                      8, -4, 7, 4, 4, 7, -4, 8,
                      6, -3, 4, 0, 0, 4, -3, -6,
                      6, -3, 4, 0, 0, 4, -3, -6,
                      8, -4, 7, 4, 4, 7, -4, 8,
                      -8, -24, -4, -3, -3, -4, -24, -8,
                      99, -8, 8, 6, 6, 8, -8, 99]

    row_diffs = {-8: 1, 8: 1, -1: 0, 1: 0, -7: 1, 7: 1, -9: 1, 9: 1}
    col_diffs = {-8: 0, 8: 0, -1: 1, 1: 1, -7: 1, 7: 1, -9: 1, 9: 1}
    NBRS = []
    for pos in range(64):
        NBRS.append([])
        for direction in [-8, -7, 1, 9, 8, 7, -1, -9]:
            nbrs, row_diff, col_diff = [], row_diffs[direction], col_diffs[direction]
            for k in range(1, 8):
                move = pos + k * direction
                if move < 0 or move > 63 \
                   or abs(move % 8 - pos % 8) != k * col_diff \
                   or abs(move // 8 - pos // 8) != k * row_diff: break
                nbrs.append(move)
            NBRS[pos].append(nbrs)


def time_test():
    import time
    start = time.process_time()
    print(negamax('oooo.oooooxxxxooxxoxxoxxxxxoooxxxxxooxxx.xxooox..ooo.xoxo....x.o', 'x'))
    print(time.process_time() - start)


def main():
    brd, tkn, move_sequence = parse_args()

    psbl_moves = findMoves(brd, tkn)
    two_d_print(brd, psbl_moves)
    print()
    x, o = 'x', 'o'
    print(f'{brd} {brd.lower().count(x)}/{brd.lower().count(o)}')
    if not psbl_moves:
        tkn = ENEMY[tkn]
        psbl_moves = findMoves(brd, tkn)
        print(print(f'Possible moves for {tkn}: {str([mv for mv, flipped in psbl_moves[1:-1]])}'))
    else: print(f'Possible moves for {tkn}: {str([mv for mv, flipped in psbl_moves[1:-1]])}')

    for move in move_sequence:
        print(f'{tkn} plays to {move}')
        brd, tkn = makeMove(brd, tkn, move), ENEMY[tkn]
        psbl_moves = findMoves(brd, tkn)
        two_d_print(brd, psbl_moves)
        print()
        print(f'{brd} {brd.lower().count(x)}/{brd.lower().count(o)}')
        if psbl_moves: print(f'Possible moves for {tkn}: {str([mv for mv, flipped in psbl_moves[1:-1]])}\n')
        else:
            tkn = ENEMY[tkn]
            psbl_moves = findMoves(brd, tkn)
            if psbl_moves: print(f'Possible moves for {tkn}: {str([mv for mv, flipped in psbl_moves[1:-1]])}\n')
            else: print()

    psbl_moves = findMoves(brd, tkn)
    if psbl_moves:
        print(f'The preferred move is: {quickMove(brd, tkn, psbl_moves)}')

    if brd.count('.') < N:
        nm = negamax(brd, tkn)
        print(f'Min score: {nm[0]}; move sequence: {nm[1:]}')


set_globals()
if __name__ == '__main__': cProfile.run('time_test()', sort='tottime')  # main()

# Tristan Devictor, pd. 6, 2024
