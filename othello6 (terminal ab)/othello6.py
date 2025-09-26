import sys; args = sys.argv[1:]
import re
import random


MAKE_MOVE = {}
def makeMove(brd, tkn, mv):
    key = brd + tkn, mv
    if key in MAKE_MOVE: return MAKE_MOVE[key]

    enemy = ENEMY[tkn]
    brd = [*brd]
    brd[mv] = tkn

    for drt in POS_TO_NBR[mv]:
        seen = []
        for pos in drt:
            if brd[pos] == '.': break
            if brd[pos] == enemy: seen.append(pos)
            if brd[pos] == tkn:
                for sp in seen: brd[sp] = tkn
                break

    result = ''.join(brd)
    MAKE_MOVE[key] = result
    return result


MOVE_CACHE = {}
def findMoves(brd, tkn):
    key = brd + tkn
    if key in MOVE_CACHE: return MOVE_CACHE[key]

    enemy = ENEMY[tkn]
    moves = set()

    for cdt in range(64):  # candidate
        if brd[cdt] != '.': continue
        valid = False
        for drt in POS_TO_NBR[cdt]:  # direction
            if brd[drt[0]] != enemy: continue
            for pos in drt:
                if brd[pos] == enemy: continue
                if brd[pos] == tkn:
                    moves.add(cdt)
                    valid = True
                break
            if valid: break

    MOVE_CACHE[key] = moves
    return moves


def alphabeta(brd, tkn):
    return alphabeta_recur(brd.lower(), tkn.lower(), -65, 65)  # , True)


# ALPHABETA_CACHE = {}
def alphabeta_recur(brd, tkn, lower, upper):  # , top=False):
    # key = brd + tkn  # , lower, upper
    # if key in ALPHABETA_CACHE: return ALPHABETA_CACHE[key]

    enemy = ENEMY[tkn]
    moves = findMoves(brd, tkn)
    if not moves:
        if not findMoves(brd, enemy): return [brd.count(tkn)-brd.count(enemy)]
        ab = alphabeta_recur(brd, enemy, -upper, -lower)
        best = [-ab[0]] + ab[1:] + [-1]
        # ALPHABETA_CACHE[key] = best
        return best

    best = [-65]
    for mv in moves:
        new_brd = makeMove(brd, tkn, mv)
        ab = alphabeta_recur(new_brd, enemy, -upper, -lower)
        score = -ab[0]
        if score < lower: continue
        if score > upper: return [score]
        best = [-ab[0]] + ab[1:] + [mv]
        lower = score + 1
        # if top: print(f'Min score: {best[0]}; move sequence: {best[1:]}')

    # ALPHABETA_CACHE[key] = best
    return best


def isTknLine(brd, tkn, positions):
    for pos in positions:
        if brd[pos] != tkn: return False
    return True


def quickMove(brd, tkn):
    # if brd.count('.') < HL: return alphabeta(brd, tkn)[-1]

    brd, tkn, enemy = brd.lower(), tkn.lower(), ENEMY[tkn]

    moves = findMoves(brd, tkn)
    for corner in CORNERS:
        if corner in moves: return corner
    for mv in moves:
        new_brd = makeMove(brd, tkn, mv)
        for edge in POS_TO_EDGE[mv]:
            tkns = [new_brd[i] for i in edge]
            index = edge.index(mv)
            if len(set(tkns[:index+1])) == 1 or len(set(tkns[index:])) == 1:
                return mv
        for d in OPPOSITE_DIRECTIONS:
            if not isTknLine(brd, tkn, DIRECTION_TO_NBR[mv][d[0]]) and not isTknLine(brd, tkn, DIRECTION_TO_NBR[mv][d[1]]): break
        else: return mv

    ok_moves = [mv for mv in moves if not (mv in ADJ_CORNERS and ADJ_CORNERS[mv] != tkn)]
    return random.choice(ok_moves) if ok_moves else random.choice([*moves])


def set_globals():
    # noinspection PyGlobalUndefined
    global HL, ENEMY, POS_TO_EDGE, CORNERS, ADJ_CORNERS, POSITION_VALUE, POS_TO_NBR, DIRECTION_TO_NBR, OPPOSITE_DIRECTIONS

    HL = 11
    ENEMY = {'x': 'o', 'o': 'x', 'X': 'o', 'O': 'x'}
    edges = [[0, 1, 2, 3, 4, 5, 6, 7], [0, 8, 16, 24, 32, 40, 48, 56], [56, 57, 58, 59, 60, 61, 62, 63], [7, 15, 23, 31, 39, 47, 55, 63]]
    POS_TO_EDGE = {i: [[e for e in edge] for edge in edges if i in edge] for i in range(64)}

    CORNERS = (0, 7, 56, 63)
    ADJ_CORNERS = {1: 0, 8: 0, 9: 0, 6: 7, 14: 7, 15: 7, 48: 56, 49: 56, 57: 56, 62: 63, 54: 63, 55: 63}
    OPPOSITE_DIRECTIONS = ((8, -8), (7, -7), (9, -9), (1, -1))
    POSITION_VALUE = [99, -8, 8, 6, 6, 8, -8, 99,
                      -8, -24, -4, -3, -3, -4, -24, -8,
                      8, -4, 7, 4, 4, 7, -4, 8,
                      6, -3, 4, 0, 0, 4, -3, -6,
                      6, -3, 4, 0, 0, 4, -3, -6,
                      8, -4, 7, 4, 4, 7, -4, 8,
                      -8, -24, -4, -3, -3, -4, -24, -8,
                      99, -8, 8, 6, 6, 8, -8, 99]

    POS_TO_NBR = [[] for _ in range(64)]
    DIRECTION_TO_NBR = {}
    row_diffs = {-8: 1, 8: 1, -1: 0, 1: 0, -7: 1, 7: 1, -9: 1, 9: 1}
    col_diffs = {-8: 0, 8: 0, -1: 1, 1: 1, -7: 1, 7: 1, -9: 1, 9: 1}
    for pos in range(64):
        for direction in [8, -8, 7, -7, 1, -1, 9, -9]:
            nbrs, row_diff, col_diff = [], row_diffs[direction], col_diffs[direction]
            for k in range(1, 8):
                move = pos + k * direction
                if move < 0 or move > 63 \
                   or abs(move % 8 - pos % 8) != k * col_diff \
                   or abs(move // 8 - pos // 8) != k * row_diff: break
                nbrs.append(move)
            if nbrs:
                POS_TO_NBR[pos].append(nbrs)
            if pos not in DIRECTION_TO_NBR:
                DIRECTION_TO_NBR[pos] = {}
            DIRECTION_TO_NBR[pos][direction] = nbrs


def snapshot(brd, tkn, psbl_moves):
    x, o = 'x', 'o'
    print('\n'.join([''.join(['*' if r * 8 + c in psbl_moves else brd[r * 8 + c] for c in range(8)]) for r in range(8)]))
    print()
    print(f'{brd} {brd.lower().count(x)}/{brd.lower().count(o)}')
    if psbl_moves:
        print(f'Possible moves for {tkn}: {str(sorted(psbl_moves))[1:-1]}\n')
    else:
        tkn = ENEMY[tkn]
        psbl_moves = findMoves(brd, tkn)
        if psbl_moves:
            print(f'Possible moves for {tkn}: {str(sorted(psbl_moves))[1:-1]}\n')
        else:
            print()


def parse_args():
    global HL, VERBOSE

    positions = {(letter + str(i + 1)): (ord(letter) - ord('a')) + i * 8 for i in range(8) for letter in 'abcdefgh'}
    for i in range(64): positions[str(i)] = i

    VERBOSE = True
    brd = '.' * 27 + 'ox......xo' + '.' * 27
    tkn = ''
    move_sequence = []

    for arg in args:
        arg = arg.lower()
        if re.match('^[xo.]{64}$', arg): brd = arg
        elif arg in 'xo': tkn = arg
        elif 'HL' in arg: HL = int(arg[2:].strip())
        elif arg in 'vV': VERBOSE = True
        elif '-' not in arg: move_sequence += [int(arg[i:i+2]) if '_' not in arg[i:i+2] else int(arg[i+1:i+2]) for i in range(0, len(arg), 2)]
    if not tkn: tkn = 'x' if brd.count('.') % 2 == 0 else 'o'
    return brd, tkn, move_sequence


def main():
    brd, tkn, move_sequence = parse_args()

    if VERBOSE:
        snapshot(brd, tkn, findMoves(brd, tkn))
        for mv in move_sequence:
            print(f'{tkn} plays to {mv}')
            brd, tkn = makeMove(brd, tkn, mv), ENEMY[tkn]
            snapshot(brd, tkn, findMoves(brd, tkn))

    moves = findMoves(brd, tkn)
    if moves:
        print(f'The preferred move is: {quickMove(brd, tkn)}')

    if brd.count('.') < HL:
        ab = alphabeta(brd, tkn)
        print(f'Min score: {ab[0]}; move sequence: {ab[1:]}')


def time_test():
    import time
    start = time.process_time()
    print(alphabeta('oooo.oooooxxxxooxxoxxoxxxxxoooxxxxxooxxx.xxooox..ooo.xoxo....x.o', 'x'))
    print(time.process_time() - start)


set_globals()
if __name__ == '__main__':
    main()

# Tristan Devictor, pd. 6, 2024
