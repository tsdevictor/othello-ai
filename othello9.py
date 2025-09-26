import sys; args = sys.argv[1:]

# TODO: iterative deepening
# TODO: stability when surrounded by enemy
# TODO: frontier

class Strategy:
    def __init__(self):
        self.logging = True
        self.opening_book = OPENING_BOOK

    def best_strategy(self, brd, tkn, best_move, still_running, time_limit):
        if brd + tkn in self.opening_book: best_move.value = self.opening_book[brd + tkn]
        elif still_running.value:
            best_move.value = max(findMoves(brd, tkn), key=lambda m: rateMove(brd, tkn, m))
            best_move.value = quickMove(brd, tkn)
        return best_move.value


def findMoves(brd, tkn):
    key = brd + tkn
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


def makeMove(brd, tkn, mv):
    if mv < 0: return brd  # move was invalid or pass

    key = brd + tkn, mv
    if key in MAKE_MOVE: return MAKE_MOVE[key]

    brd_lst, enemy = [*brd], ENEMY[tkn]
    brd_lst[mv] = tkn

    for drt in NBRS_BY_DIRECTION[mv]:  # check for captures in each direction (north, northeast, east, etc.)
        to_flip = []                   # track positions that will be captured (a.k.a, flipped)
        for pos in drt:                # check each neighbor of mv in the current direction
            if brd_lst[pos] == '.': break                      # no captures will be made in this direction
            if brd_lst[pos] == enemy: to_flip.append(pos)      # potential capture
            if brd_lst[pos] == tkn:                            # flip all captured positions
                for f in to_flip: brd_lst[f] = tkn
                break

    brd = ''.join(brd_lst)      # turn board back into string (for immutability)
    MAKE_MOVE[key] = brd
    return brd


def isTknLine(brd, tkn, positions):  # used to check for stability
    for pos in positions:
        if brd[pos] != tkn: return False
    return True


def board_eval(brd, tkn):  # board evaluation heuristic
    key = brd + tkn
    if key in BOARD_EVAL: return BOARD_EVAL[key]

    score, enemy = 0, ENEMY[tkn]
    for i in range(64):
        if brd[i] == '.': continue

        # tkn is stable if it is connected to an edge in: (N or S) and (NE or SW) and (E or W) and (NW or SE) cardinal directions
        od = NBRS_OPPOSITE_DIRS[i]
        for d in DIRECTION_PAIRS:
            if not isTknLine(brd, brd[i], od[d[0]]) and not isTknLine(brd, brd[i], od[d[1]]): break
        else: score += 1.5 * (1 if brd[i] == tkn else -1)

        # for d in DIRECTION_PAIRS:
        #     if not od[d[0]] or not od[d[1]]: continue
        #     if brd[i] == tkn: score -= ({od[d[0]][0], od[d[1]][0]} == {'.', enemy}) * 1.8
        #     else: score += ({od[d[0]][0], od[d[1]][0]} == {'.', tkn}) * 1.8

    score += len(findMoves(brd, tkn)) - len(findMoves(brd, enemy))   # check for mobility: more moves is better

    for corner in CORNERS:
        if brd[corner] == tkn: score += 3
        elif brd[corner] == enemy: score -= 3

    BOARD_EVAL[key] = score
    return score


def midgame_ab(brd, tkn, lower, upper, depth, top=False):  # non-terminal alpha-beta pruning
    if depth == 0: return [board_eval(brd, tkn)]

    moves, enemy = findMoves(brd, tkn), ENEMY[tkn]
    if not moves:                                                    # pass
        if not findMoves(brd, enemy): return [board_eval(brd, tkn)]  # game over
        ab = midgame_ab(brd, enemy, -upper, -lower, depth - 1)
        return [-ab[0]] + ab[1:] + [-1]

    best = [TERMINAL_MIN]
    for mv in sorted(moves, key=lambda m: -rateMove(brd, tkn, m)):  # sort moves to improve chances of pruning
        new_brd = makeMove(brd, tkn, mv)
        ab = midgame_ab(new_brd, enemy, -upper, -lower, depth - 1)
        score = -ab[0]
        if score < lower: continue        # not a viable score
        if score > upper: return [score]  # score too high: prune this branch (enemy will never allow this state)
        best = [-ab[0]] + ab[1:] + [mv]
        lower = score + 1
        if top: print(f'The preferred move is: {best[-1]}')  # print every time there is a new best move (in case code gets cut off)

    return best


def terminal_ab(brd, tkn, lower, upper, top=False):  # alpha-beta pruning for negamax
    key = brd + tkn, lower, upper
    if key in TERMINAL_AB: return TERMINAL_AB[key]

    moves, enemy = findMoves(brd, tkn), ENEMY[tkn]
    if not moves:
        if not findMoves(brd, enemy): return [brd.count(tkn) - brd.count(enemy)]
        ab = terminal_ab(brd, enemy, -upper, -lower)
        best = [-ab[0]] + ab[1:] + [-1]
        TERMINAL_AB[key] = best
        return best

    best = [TERMINAL_MIN]
    for mv in sorted(moves, key=lambda m: -rateMove(brd, tkn, m)):
        new_brd = makeMove(brd, tkn, mv)
        ab = terminal_ab(new_brd, enemy, -upper, -lower)
        score = -ab[0]
        if score < lower: continue
        if score > upper: return [score]
        best = [-ab[0]] + ab[1:] + [mv]
        lower = score + 1
        if top: print(f'The preferred move is: {best[-1]}')

    TERMINAL_AB[key] = best
    return best


def rateMove(brd, tkn, mv):
    if mv in CORNERS: return 100  # corners valuable

    new_brd, od = makeMove(brd, tkn, mv), NBRS_OPPOSITE_DIRS[mv]
    for d in DIRECTION_PAIRS:
        if not isTknLine(new_brd, tkn, od[d[0]]) and not isTknLine(new_brd, tkn, od[d[1]]): break
    else: return 60  # value an acquired stable token

    if mv in CORNER_NBRS and CORNER_NBRS[mv] != tkn: return -100  # don't give enemy free corner

    return len(findMoves(new_brd, ENEMY[tkn])) * -2  # don't give enemy mobility


def quickMove(brd, tkn):
    if brd in OPENING_BOOK: return OPENING_BOOK[brd]

    moves = findMoves(brd, tkn)
    if len(moves) == 1: return moves[0]

    # return max(moves, key=lambda m: rateMove(brd, tkn, m))
    if brd.count('.') < HL: return terminal_ab(brd.lower(), tkn.lower(), TERMINAL_MIN, TERMINAL_MAX, True)[-1]
    else: return midgame_ab(brd.lower(), tkn.lower(), MIDGAME_MIN, MIDGAME_MAX, DEPTH)[-1]


def set_globals():
    # noinspection PyGlobalUndefined
    global HL, DEPTH, TERMINAL_MIN, TERMINAL_MAX, MIDGAME_MIN, MIDGAME_MAX, ENEMY
    global CORNERS, CORNER_NBRS, DIRECTION_PAIRS, NBRS_BY_DIRECTION, NBRS_OPPOSITE_DIRS  # lookup tables for positions and neighbors
    global FIND_MOVES, MAKE_MOVE, TERMINAL_AB, BOARD_EVAL, OPENING_BOOK

    HL, DEPTH = 22, 5
    TERMINAL_MIN, TERMINAL_MAX, MIDGAME_MIN, MIDGAME_MAX = -65, 65, -1000, 1000
    ENEMY = {'x': 'o', 'o': 'x', 'X': 'o', 'O': 'x'}

    CORNERS = (0, 7, 56, 63)
    CORNER_NBRS = {1: 0, 8: 0, 9: 0, 6: 7, 14: 7, 15: 7, 48: 56, 49: 56, 57: 56, 62: 63, 54: 63, 55: 63}
    DIRECTION_PAIRS = ((8, -8), (7, -7), (9, -9), (1, -1))

    NBRS_BY_DIRECTION = [[] for _ in range(64)]
    NBRS_OPPOSITE_DIRS = {}
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
            if pos not in NBRS_OPPOSITE_DIRS: NBRS_OPPOSITE_DIRS[pos] = {}
            NBRS_OPPOSITE_DIRS[pos][drt] = nbrs

    FIND_MOVES, MAKE_MOVE, TERMINAL_AB, BOARD_EVAL = {}, {}, {}, {}
    OPENING_BOOK = {
        '...........................ox......xo...........................': 37,
        '..........................xxx......xo...........................': 20,
        '..................o.......xox......xo...........................': 37,
        '..................ox......xxx......xo...........................': 20,
        '..................ox......oxx.....ooo...........................': 45,
        '..................ox.....xxxx.....ooo...........................': 20,
        '..................ox......oxx.....xoo....x......................': 20,
        '..................ox......oxx.....oxo......x....................': 20,
        '..................ox......oxx.....oox........x..................': 37,
        '..................ooo.....xxo......xo...........................': 45,
        '...........x......oxo.....xxo......xo...........................': 34,
        '.............x....oox.....xxo......xo...........................': 34,
        '..................ooo.....xxxx.....xo...........................': 34,
        '..................ooo.....xxo......xx........x..................': 44,
        '..................o.......xox......xx.......x...................': 34,
        '..................o.......xox......xxx..........................': 34,
        '....................o.....xxo......xo...........................': 45,
        '....................o.....xxxx.....xo...........................': 34,
        '....................o.....xoxx....ooo...........................': 44,
        '....................o.....xoxx....oox......x....................': 44,
        '....................o.....xxo......xxx..........................': 44,
        '....................o....oooo......xxx..........................': 21,
        '....................o.....xxo......xox......o...................': 29,
        '....................o.....xxo......xx........x..................': 44,
        '....................o.....xxo......xo.......ox..................': 37,
        '....................o.....xxo......xxx......ox..................': 46,
        '...................x.......xx......xo...........................': 20,
        '..................ox.......ox......xo...........................': 37,
        '..................ox.......ox......xx.......x...................': 20,
        '..................ox.......ox......xxx..........................': 20,
        '...................x.......xx.....ooo...........................': 45,
        '...................x.......xx.....oxo......x....................': 20,
        '...................xo......oo.....oxo......x....................': 37,
        '...................xo......oox....oxx......x....................': 37,
        '...................x.......xx.....oox.......x...................': 37,
        '...........o.......o.......ox.....oox.......x...................': 42,
        '...................x.......xx.....oooo......x...................': 43,
        '...................x.......xx.....oox........x..................': 37,
        '...................x.......xx.....oooo.......x..................': 44,
        '...................x.......xx.....ooxo......xx..................': 53,
        '...........................ox......xx.......x...................': 45,
        '...........................ooo.....xx.......x...................': 20,
        '..................x........xoo.....xx.......x...................': 52,
        '..................x.......oooo.....xx.......x...................': 19,
        '..................xx......oxoo.....xx.......x...................': 10,
        '...................x.......xoo.....xx.......x...................': 52,
        '...................x......oooo.....xx.......x...................': 37,
        '...................x.......xoo.....xo.......o.......o...........': 21,
        '....................x......oxo.....xx.......x...................': 43,
        '....................x......oxo.....oo......ox...................': 34,
        '....................x......xxo....xoo......ox...................': 26,
        '...........................ox......xo.......xo..................': 37,
        '..........................xxx......xo.......xo..................': 43,
        '...................x.......xx......xo.......xo..................': 43,
        '...........................ox......xxx......xo..................': 29,
        '...........................ox......oxx.....ooo..................': 54,
        '..................x........xx......oxx.....ooo..................': 19,
        '...........................ox.....xxxx.....ooo..................': 29,
        '...........................ox......oxx.....xoo....x.............': 29,
        '...........................ox......oxx.....oxo......x...........': 29,
        '...........................ooo.....xxo......xo..................': 54,
        '..................x........xoo.....xxo......xo..................': 26,
        '....................x......oxo.....xxo......xo..................': 43,
        '......................x....oox.....xxo......xo..................': 43,
        '...........................ooo.....xxxx.....xo..................': 43,
        '...........................ox......xxx..........................': 45,
        '...........................ox......oxx.....o....................': 34,
        '..................x........xx......oxx.....o....................': 38,
        '..................xo.......ox......oxx.....o....................': 26,
        '..................xo......xxx......oxx.....o....................': 17,
        '..........................xxx......oxx.....o....................': 38,
        '...................o......xox......oxx.....o....................': 44,
        '..........................xxx......oooo....o....................': 42,
        '...........................ox.....xxxx.....o....................': 29,
        '...........................ooo....xxox.....o....................': 20,
        '....................x......xoo....xxox.....o....................': 19,
        '...........................ox......xox.......o..................': 44,
        '..........................xxx......xox.......o..................': 29,
        '...................x.......xx......xox.......o..................': 29}


def parse_args():
    global HL, VERBOSE

    brd, tkn, move_sequence, VERBOSE = '.' * 27 + 'ox......xo' + '.' * 27, '', [], False
    for arg in args:
        arg = arg.lower()
        if {*arg}.issubset({'x', 'o', '.'}) and len(arg) == 64: brd = arg
        elif arg in 'xo': tkn = arg
        elif arg in 'Vv': VERBOSE = True
        else: move_sequence += [int(arg[i: i+2].replace('_', '0')) for i in range(0, len(arg), 2)]

    return brd, (tkn if tkn else ('o' if brd.count('.') % 2 else 'x')), move_sequence


def snapshot(brd, tkn, should_print, mv=-1):
    if should_print and mv != -1: print(f'{ENEMY[tkn]} plays to {mv}')
    moves = findMoves(brd, tkn)
    if not moves:
        tkn = ENEMY[tkn]
        moves = findMoves(brd, tkn)
    if should_print:
        print('\n'.join([''.join(['*' if r*8+c in moves else brd[r*8+c] if r*8+c != mv else brd[r*8+c].upper() for c in range(8)]) for r in range(8)]))
        print(f'{brd} {brd.count("x")}/{brd.count("o")}')
        if moves: print(f'Possible moves for {tkn}: {str(moves)[1:-1]}')
    return tkn


def main():
    brd, tkn, move_sequence = parse_args()

    tkn = snapshot(brd, tkn, VERBOSE or not move_sequence)
    for i, mv in enumerate(move_sequence):
        if mv < 0: continue
        brd = makeMove(brd, tkn, mv)
        tkn = snapshot(brd, ENEMY[tkn], VERBOSE or i == len(move_sequence) - 1, mv)

    moves = findMoves(brd, tkn)
    if not moves:
        tkn = ENEMY[tkn]
        moves = findMoves(brd, tkn)
    if moves: print(f'The preferred move is: {quickMove(brd, tkn)}')

    if brd.count('.') < HL:
        ab = terminal_ab(brd, tkn, TERMINAL_MIN, TERMINAL_MAX, True)
        print(f'Min score: {ab[0]}; move sequence: {ab[1:]}')


set_globals()
if __name__ == '__main__': main()


# Tristan Devictor, pd. 6, 2024
