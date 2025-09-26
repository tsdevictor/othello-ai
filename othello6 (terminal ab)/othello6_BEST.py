# TODO:
#  improve quickMove so that alpha beta has better move ordering
#  use board symmetries for keys in caching (rotate, flip, etc.)
#  cache rateMove / avoid re-computation of move rating

import sys; args = sys.argv[1:]
import re
import random


MAKE_MOVE = {}
def makeMove(brd, tkn, mv):
    if mv < 0: return brd  # pass or invalid

    key = brd + tkn, mv
    if key in MAKE_MOVE: return MAKE_MOVE[key]

    enemy = ENEMY[tkn]
    brd = [*brd]
    brd[mv] = tkn

    for drt in POS_TO_NBR[mv]:  # loop through each direction
        to_flip = []            # track tkns to flip
        for pos in drt:
            if brd[pos] == '.': break
            if brd[pos] == enemy: to_flip.append(pos)
            if brd[pos] == tkn:
                for t in to_flip: brd[t] = tkn
                break

    result = ''.join(brd)
    MAKE_MOVE[key] = result
    return result


MOVE_CACHE = {}
def findMoves(brd, tkn):
    key = brd + tkn
    if key in MOVE_CACHE: return MOVE_CACHE[key]

    enemy = ENEMY[tkn]
    moves = []
    for cdt in range(64):  # candidate moves
        if brd[cdt] != '.': continue
        valid = False      # bool: was move valid (don't check for validity after mv was already valid in one direction)
        for drt in POS_TO_NBR[cdt]:  # loop through each direction
            if brd[drt[0]] != enemy: continue
            for pos in drt:  # check each position in current direction
                if brd[pos] == enemy: continue
                if brd[pos] == tkn:
                    moves.append(cdt)
                    valid = True
                break
            if valid: break

    MOVE_CACHE[key] = moves
    return moves


def alphabeta(brd, tkn):  # alpha-beta pruning for negamax
    return alphabeta_recur(brd.lower(), tkn.lower(), -65, 65, True)


TERMINAL_AB = {}
def alphabeta_recur(brd, tkn, lower, upper, top=False):
    key = brd + tkn, lower, upper
    if key in TERMINAL_AB: return TERMINAL_AB[key]

    enemy = ENEMY[tkn]
    moves = findMoves(brd, tkn)
    if not moves:
        if not findMoves(brd, enemy): return [brd.count(tkn) - brd.count(enemy)]
        ab = alphabeta_recur(brd, enemy, -upper, -lower)
        best = [-ab[0]] + ab[1:] + [-1]
        TERMINAL_AB[key] = best
        return best

    best = [-65]
    for mv in sorted(moves, key=lambda x: -rateMove(brd, tkn, x)):
        new_brd = makeMove(brd, tkn, mv)
        ab = alphabeta_recur(new_brd, enemy, -upper, -lower)
        score = -ab[0]
        if score < lower: continue
        if score > upper: return [score]
        best = [-ab[0]] + ab[1:] + [mv]
        lower = score + 1
        if top: print(f'Min score: {best[0]}; move sequence: {best[1:]}')

    TERMINAL_AB[key] = best
    return best


def isTknLine(brd, tkn, positions):  # check for stability
    for pos in positions:
        if brd[pos] != tkn: return False
    return True


def rateMove(brd, tkn, mv):
    if mv in CORNERS: return 100
    new_brd = makeMove(brd, tkn, mv)
    for edge in POS_TO_EDGE[mv]:
        if isTknLine(new_brd, tkn, edge[0]) or isTknLine(new_brd, tkn, edge[1]): return 50
    od = DIRECTION_TO_NBR[mv]  # opposite directions
    for d in OPPOSITE_DIRECTIONS:  # stable tkn
        if not isTknLine(new_brd, tkn, od[d[0]]) and not isTknLine(new_brd, tkn, od[d[1]]): break
    else: return 40
    if mv in ADJ_CORNERS and ADJ_CORNERS[mv] != tkn: return -20
    return 0


def quickMove(brd, tkn):
    global HL
    if not brd:
        HL = int(tkn)
        return

    if brd.count('.') < HL: return alphabeta(brd, tkn)[-1]

    brd, tkn = brd.lower(), tkn.lower()
    moves = findMoves(brd, tkn)

    for corner in CORNERS:
        if corner in moves: return corner
    for mv in moves:
        new_brd = makeMove(brd, tkn, mv)
        for edge in POS_TO_EDGE[mv]:
            if isTknLine(new_brd, tkn, edge[0]) or isTknLine(new_brd, tkn, edge[1]): return mv
        od = DIRECTION_TO_NBR[mv]  # opposite directions
        for d in OPPOSITE_DIRECTIONS:  # stable tkn
            if not isTknLine(new_brd, tkn, od[d[0]]) and not isTknLine(new_brd, tkn, od[d[1]]): break
        else: return mv

    ok_moves = [mv for mv in moves if not (mv in ADJ_CORNERS and ADJ_CORNERS[mv] != tkn)]
    return random.choice(ok_moves) if ok_moves else random.choice([*moves])


def set_globals():
    # noinspection PyGlobalUndefined
    global HL, ENEMY, POS_TO_EDGE, CORNERS, ADJ_CORNERS, POS_TO_NBR, DIRECTION_TO_NBR, OPPOSITE_DIRECTIONS

    quickMove('', 1)
    ENEMY = {'x': 'o', 'o': 'x', 'X': 'o', 'O': 'x'}
    edges = (0, 1, 2, 3, 4, 5, 6, 7), (0, 8, 16, 24, 32, 40, 48, 56), (56, 57, 58, 59, 60, 61, 62, 63), (7, 15, 23, 31, 39, 47, 55, 63)
    POS_TO_EDGE = {i: ((edge[:edge.index(i) + 1], edge[edge.index(i):]) for edge in edges if i in edge) for i in range(64)}

    CORNERS = (0, 7, 56, 63)
    ADJ_CORNERS = {1: 0, 8: 0, 9: 0, 6: 7, 14: 7, 15: 7, 48: 56, 49: 56, 57: 56, 62: 63, 54: 63, 55: 63}
    OPPOSITE_DIRECTIONS = ((8, -8), (7, -7), (9, -9), (1, -1))

    POS_TO_NBR = [[] for _ in range(64)]
    DIRECTION_TO_NBR = {}
    row_diffs = {-8: 1, 8: 1, -1: 0, 1: 0, -7: 1, 7: 1, -9: 1, 9: 1}
    col_diffs = {-8: 0, 8: 0, -1: 1, 1: 1, -7: 1, 7: 1, -9: 1, 9: 1}
    for pos in range(64):
        for drt in [8, -8, 7, -7, 1, -1, 9, -9]:
            nbrs, rd, cd = [], row_diffs[drt], col_diffs[drt]
            for dist in range(1, 8):  # distance
                mv = pos + dist * drt
                if not 0 <= mv < 64 or abs(mv % 8 - pos % 8) != dist * cd or abs(mv // 8 - pos // 8) != dist * rd: break
                nbrs.append(mv)
            if nbrs: POS_TO_NBR[pos].append(nbrs)
            if pos not in DIRECTION_TO_NBR: DIRECTION_TO_NBR[pos] = {}
            DIRECTION_TO_NBR[pos][drt] = nbrs


def parse_args():
    global HL

    positions = {(letter + str(i + 1)): (ord(letter) - ord('a')) + i * 8 for i in range(8) for letter in 'abcdefgh'}
    for i in range(64): positions[str(i)] = i

    brd = '.' * 27 + 'ox......xo' + '.' * 27
    tkn = ''
    move_sequence = []

    for arg in args:
        arg = arg.lower()
        if re.match('^[xo.]{64}$', arg): brd = arg
        elif arg in 'xo': tkn = arg
        elif 'HL' in arg or 'hl' in arg: HL = int(arg[2:].strip())
        else:
            try: move_sequence += [int(arg[i:i + 2]) if '_' not in arg[i:i + 2] else int(arg[i + 1:i + 2]) for i in range(0, len(arg), 2)]
            except ValueError: move_sequence += [positions[arg]]
    if not tkn: tkn = 'x' if brd.count('.') % 2 == 0 else 'o'
    return brd, tkn, move_sequence


def snapshot(brd, tkn, mv=-1):
    x, o = 'x', 'o'
    moves = findMoves(brd, tkn)
    if not moves:
        tkn = ENEMY[tkn]
        moves = findMoves(brd, tkn)
    to_print = '\n'.join([''.join(['*' if r * 8 + c in moves else brd[r * 8 + c] if r * 8 + c != mv else brd[r*8+c].upper() for c in range(8)]) for r in range(8)])
    print(to_print)
    print()
    print(f'{brd} {brd.count(x)}/{brd.count(o)}')
    if moves: print(f'Possible moves for {tkn}: {str(moves)[1:-1]}')
    print()
    return tkn


def main():
    brd, tkn, move_sequence = parse_args()

    tkn = snapshot(brd, tkn)
    for mv in move_sequence:
        if mv < 0: continue  # pass or invalid
        else:
            print(f'{tkn} plays to {mv}')
            brd = makeMove(brd, tkn, mv)
            tkn = snapshot(brd, ENEMY[tkn], mv)

    moves = findMoves(brd, tkn)
    if not moves:
        tkn = ENEMY[tkn]
        moves = findMoves(brd, tkn)
    if moves: print(f'The preferred move is: {quickMove(brd, tkn)}')

    if brd.count('.') < HL:
        ab = alphabeta(brd, tkn)
        print(f'Min score: {ab[0]}; move sequence: {ab[1:]}')


set_globals()
if __name__ == '__main__': main()

# Tristan Devictor, pd. 6, 2024
