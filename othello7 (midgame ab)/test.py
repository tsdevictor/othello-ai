import sys; args = sys.argv[1:]
import re


MAKE_MOVE = {}
def makeMove(brd, tkn, mv):
    if mv < 0: return brd  # move was invalid or pass

    key = brd + tkn, mv    # caching
    if key in MAKE_MOVE: return MAKE_MOVE[key]

    brd, enemy = [*brd], ENEMY[tkn]
    brd[mv] = tkn

    for drt in NBRS_BY_DIRECTION[mv]:  # check for captures in each direction (north, northeast, east, etc.)
        to_flip = []                   # track positions that will be captured (a.k.a, flipped)
        for pos in drt:                # check each neighbor of mv in the current direction
            if brd[pos] == '.': break                      # no captures will be made in this direction
            if brd[pos] == enemy: to_flip.append(pos)      # potential capture
            if brd[pos] == tkn:                            # flip all captured positions
                for f in to_flip: brd[f] = tkn
                break

    result = ''.join(brd)      # turn board back into string (for immutability)
    MAKE_MOVE[key] = result
    return result


FIND_MOVES = {}
def findMoves(brd, tkn):
    key = brd + tkn    # caching
    if key in FIND_MOVES: return FIND_MOVES[key]

    moves, enemy = [], ENEMY[tkn]
    for cdt in range(64):               # loop through "candidate moves" (entire board)
        if brd[cdt] != '.': continue    # must play to open position
        valid = False
        for drt in NBRS_BY_DIRECTION[cdt]:     # check for cdt validity by looking at every direction around cdt
            if brd[drt[0]] != enemy: continue  # if adjacent pos isn't an enemy tkn, this cdt cannot be valid
            for pos in drt:                    # check each nbr in current direction
                if brd[pos] == enemy: continue   # adjacent line of enemy tokens
                if brd[pos] == tkn:              # enemy tokens will be surrounded, so cdt is valid
                    moves.append(cdt)
                    valid = True
                break
            if valid: break    # if cdt was already valid in one direction, no need to check other directions

    FIND_MOVES[key] = moves
    return moves


TERMINAL_AB = {}
def alphabeta(brd, tkn, lower, upper, top=False):  # alpha-beta pruning for negamax
    key = brd + tkn, lower, upper     # caching
    if key in TERMINAL_AB: return TERMINAL_AB[key]

    moves, enemy = findMoves(brd, tkn), ENEMY[tkn]

    if not moves:  # pass
        if not findMoves(brd, enemy): return [brd.count(tkn) - brd.count(enemy)]  # game over
        ab = alphabeta(brd, enemy, -upper, -lower)                                # recur
        best = [-ab[0]] + ab[1:] + [-1]  # track current score and move sequence
        TERMINAL_AB[key] = best
        return best

    best = [TERMINAL_MIN]
    for mv in sorted(moves, key=lambda m: -rateMove(brd, tkn, m)):  # sort moves to improve chances of pruning
        new_brd = makeMove(brd, tkn, mv)
        ab = alphabeta(new_brd, enemy, -upper, -lower)  # recur
        score = -ab[0]
        if score < lower: continue  # not a viable score
        if score > upper: return [score]  # score too high: prune this branch (enemy will never allow this state)
        best = [-ab[0]] + ab[1:] + [mv]
        lower = score + 1
        if top: print(f'The preferred move is: {best[-1]}')  # print every time there is a new best move (in case code gets cut off)

    TERMINAL_AB[key] = best
    return best


BOARD_EVAL = {}
def board_eval(brd, tkn):  # board evaluation heuristic
    key = brd + tkn
    if key in BOARD_EVAL: return BOARD_EVAL[key]

    score, enemy = 0, ENEMY[tkn]
    for i in range(64):
        if brd[i] == '.': continue

        # checking for stability: +1.5 for each of my stable tkns, -1.5 for each stable enemy tkn
        # tkn is stable if it is connected to an edge in:
        #   (north or south) and (northeast or southwest) and (east or west) and (northwest or southeast)
        if brd[i] == tkn:
            od = OPPOSITE_DIRECTIONAL_NBR_PAIRS[i]
            for d in DIRECTION_PAIRS:
                if not isTknLine(brd, tkn, od[d[0]]) and not isTknLine(brd, tkn, od[d[1]]): break
            else: score += 1.5
        else:
            od = OPPOSITE_DIRECTIONAL_NBR_PAIRS[i]  # opposite directions
            for d in DIRECTION_PAIRS:  # stable tkn
                if not isTknLine(brd, enemy, od[d[0]]) and not isTknLine(brd, enemy, od[d[1]]): break
            else: score -= 1.5

    score += len(findMoves(brd, tkn)) - len(findMoves(brd, enemy))   # check for mobility: more moves is better

    BOARD_EVAL[key] = score
    return score


def midgame_ab(brd, tkn, lower, upper, depth, top=False):  # non-terminal alpha-beta pruning
    if depth == 0: return [board_eval(brd, tkn)]  # reached end of depth

    moves, enemy = findMoves(brd, tkn), ENEMY[tkn]
    if not moves:
        if not findMoves(brd, enemy): return [board_eval(brd, tkn)]
        ab = midgame_ab(brd, enemy, -upper, -lower, depth - 1)
        return [-ab[0]] + ab[1:] + [-1]

    best = [TERMINAL_MIN]
    for mv in sorted(moves, key=lambda m: -rateMove(brd, tkn, m)):
        new_brd = makeMove(brd, tkn, mv)
        ab = midgame_ab(new_brd, enemy, -upper, -lower, depth - 1)
        score = -ab[0]
        if score < lower: continue
        if score > upper: return [score]
        best = [-ab[0]] + ab[1:] + [mv]
        lower = score + 1
        if top: print(f'The preferred move is: {best[-1]}')

    return best


def isTknLine(brd, tkn, positions):  # used to check for stability
    for pos in positions:
        if brd[pos] != tkn: return False
    return True


def rateMove(brd, tkn, mv):
    if mv in CORNERS: return 100  # corners valuable

    new_brd = makeMove(brd, tkn, mv)
    for edge in POS_TO_EDGE[mv]:
        if isTknLine(new_brd, tkn, edge[0]) or isTknLine(new_brd, tkn, edge[1]): return 50  # my edge impregnable by enemy

    # check if mv yields stable tkns
    od = OPPOSITE_DIRECTIONAL_NBR_PAIRS[mv]
    for d in DIRECTION_PAIRS:
        if not isTknLine(new_brd, tkn, od[d[0]]) and not isTknLine(new_brd, tkn, od[d[1]]): break
    else: return 30

    if mv in CORNER_NBRS and CORNER_NBRS[mv] != tkn: return -100  # don't give enemy free corner

    enemy = ENEMY[tkn]
    return -len(findMoves(new_brd, enemy)) * 2  # don't give enemy mobility


def quickMove(brd, tkn):
    global HL
    if not brd:
        HL = int(tkn)
        return

    moves = findMoves(brd, tkn)
    return max(moves, key=lambda m: rateMove(brd, tkn, m))
    # call terminal or mid-game alphabeta
    # if brd.count('.') < HL: return alphabeta(brd.lower(), tkn.lower(), TERMINAL_MIN, TERMINAL_MAX, True)[-1]
    # else: return midgame_ab(brd.lower(), tkn.lower(), MIDGAME_MIN, MIDGAME_MAX, DEPTH)[-1]


def set_globals():
    # noinspection PyGlobalUndefined
    global VERBOSE, HL, DEPTH, ENEMY, TERMINAL_MIN, TERMINAL_MAX, MIDGAME_MIN, MIDGAME_MAX

    # lookup tables for neighboring positions
    global POS_TO_EDGE, CORNERS, CORNER_NBRS, DIRECTION_PAIRS
    global NBRS_BY_DIRECTION, OPPOSITE_DIRECTIONAL_NBR_PAIRS

    VERBOSE = False
    HL, DEPTH = 13, 5
    ENEMY = {'x': 'o', 'o': 'x', 'X': 'o', 'O': 'x'}
    TERMINAL_MIN, TERMINAL_MAX = -65, 65
    MIDGAME_MIN, MIDGAME_MAX = -1000, 1000

    edges = (0, 1, 2, 3, 4, 5, 6, 7), (0, 8, 16, 24, 32, 40, 48, 56), (56, 57, 58, 59, 60, 61, 62, 63), (7, 15, 23, 31, 39, 47, 55, 63)
    POS_TO_EDGE = {i: ((edge[:edge.index(i) + 1], edge[edge.index(i):]) for edge in edges if i in edge) for i in range(64)}

    CORNERS = (0, 7, 56, 63)
    CORNER_NBRS = {1: 0, 8: 0, 9: 0, 6: 7, 14: 7, 15: 7, 48: 56, 49: 56, 57: 56, 62: 63, 54: 63, 55: 63}
    DIRECTION_PAIRS = ((8, -8), (7, -7), (9, -9), (1, -1))

    NBRS_BY_DIRECTION = [[] for _ in range(64)]
    OPPOSITE_DIRECTIONAL_NBR_PAIRS = {}
    row_diffs = {-8: 1, 8: 1, -1: 0, 1: 0, -7: 1, 7: 1, -9: 1, 9: 1}
    col_diffs = {-8: 0, 8: 0, -1: 1, 1: 1, -7: 1, 7: 1, -9: 1, 9: 1}
    for pos in range(64):
        for drt in [8, -8, 7, -7, 1, -1, 9, -9]:
            nbrs, rd, cd = [], row_diffs[drt], col_diffs[drt]
            for dist in range(1, 8):  # distance
                mv = pos + dist * drt
                if not 0 <= mv < 64 or abs(mv % 8 - pos % 8) != dist * cd or abs(mv // 8 - pos // 8) != dist * rd: break
                nbrs.append(mv)
            if nbrs: NBRS_BY_DIRECTION[pos].append(nbrs)
            if pos not in OPPOSITE_DIRECTIONAL_NBR_PAIRS: OPPOSITE_DIRECTIONAL_NBR_PAIRS[pos] = {}
            OPPOSITE_DIRECTIONAL_NBR_PAIRS[pos][drt] = nbrs


def parse_args():
    global HL, VERBOSE

    positions = {(letter + str(i + 1)): (ord(letter) - ord('a')) + i * 8 for i in range(8) for letter in 'abcdefgh'}
    for i in range(64): positions[str(i)] = i

    brd, tkn, move_sequence = '.' * 27 + 'ox......xo' + '.' * 27, '', []

    for arg in args:
        arg = arg.lower()
        if re.match('^[xo.]{64}$', arg): brd = arg
        elif arg in 'xo': tkn = arg
        elif 'HL' in arg or 'hl' in arg: HL = int(arg[2:].strip())
        elif arg in 'Vv': VERBOSE = True
        else:
            try: move_sequence += [int(arg[i:i + 2]) if '_' not in arg[i:i + 2] else int(arg[i + 1:i + 2]) for i in range(0, len(arg), 2)]
            except ValueError: move_sequence += [positions[arg]]

    if not tkn: tkn = 'x' if brd.count('.') % 2 == 0 else 'o'
    return brd, tkn, move_sequence


def snapshot(brd, tkn, should_print, mv=-1):
    x, o = 'x', 'o'
    moves = findMoves(brd, tkn)
    if not moves:
        tkn = ENEMY[tkn]
        moves = findMoves(brd, tkn)
    if should_print:
        to_print = '\n'.join([''.join(['*' if r * 8 + c in moves else brd[r * 8 + c] if r * 8 + c != mv else brd[r*8+c].upper() for c in range(8)]) for r in range(8)])
        print(to_print)
        print()
        print(f'{brd} {brd.count(x)}/{brd.count(o)}')
        if moves: print(f'Possible moves for {tkn}: {str(moves)[1:-1]}')
        print()
    return tkn


def main():
    brd, tkn, move_sequence = parse_args()

    tkn = snapshot(brd, tkn, VERBOSE or not move_sequence)
    for i, mv in enumerate(move_sequence):
        if mv < 0: continue
        should_print = VERBOSE or i == len(move_sequence) - 1
        if should_print: print(f'{tkn} plays to {mv}')
        brd = makeMove(brd, tkn, mv)
        tkn = snapshot(brd, ENEMY[tkn], should_print, mv=mv)

    moves = findMoves(brd, tkn)
    if not moves:
        tkn = ENEMY[tkn]
        moves = findMoves(brd, tkn)
    if moves: print(f'The preferred move is: {quickMove(brd, tkn)}')

    if brd.count('.') < HL:
        ab = alphabeta(brd.lower(), tkn.lower(), TERMINAL_MIN, TERMINAL_MAX, True)
        print(f'Min score: {ab[0]}; move sequence: {ab[1:]}')


set_globals()
if __name__ == '__main__': main()


# TODO:
#  improve quickMove so that alpha-beta pruning has better move ordering
#  use board symmetries for keys in caching (rotate, flip, etc.)
#  cache rateMove / avoid re-computation of move rating


# Tristan Devictor, pd. 6, 2024
