import sys;

args = sys.argv[1:]
# Mini moderator for Othello games in Dr. Gabor's AI
# Arguments to the script, in any order, are:
# Student Othello script file, token to start first game with, # of games
# Defaults are: Othello4.py, 'x', 1
# Sudent script file must define:
# quickMove(brd, tkn), findMoves(brd, tkn), and makeMove(brd, tkn, move)
# To use a different name, see:   # Import user's file here
# To change the args that findMoves or makeMove is called with, see playGame()
import random, re, time, os


def condense(transcript):
    # condenses a game transcript
    return ''.join([f"_{mv}"[-2:] for mv in transcript])


def playGame(quickMove, token, show=False):
    # plays a game between quickMove(brd, tkn) and Random
    # Uses student's findMoves(brd, tkn) function and
    #                makeMove(brd, tkn, mv)
    # If the function parameters are different, search for these functions
    # below and amend their calls/parameters as needed.
    # returns (ctOfToken, ctOfEnemyTkns, condensedGameXscript)

    brd = '.' * 27 + 'ox......xo' + '.' * 27  # Starting board
    tknToPlay = 'x'
    transcript = []  # Transcript of the game

    while True:
        # Determine who plays next (normally tknToPlay)
        if not (moves := findMoves(brd, tknToPlay)):
            tknToPlay = 'xo'[tknToPlay == 'x']  # Swap players if pass
            if not (moves := findMoves(brd, tknToPlay)): break
            transcript.append(-1)  # Note the pass

        # Determine the move
        if tknToPlay != token:
            mv = random.choice([*moves])  # Random's turn
        else:  # quickMove's turn
            try:
                mv = quickMove(brd, tknToPlay)
                if mv not in moves:
                    dt = ' '.join(aSCORES)  # tranche summary
                    print(f"Partial tranche summary: {dt}")
                    print(f"\nIllegal move {mv} as {token} in '{condense(transcript)}'")
                    exit()
            except Exception as err:
                dt = ' '.join(aSCORES)
                print(f"Partial tranche summary: {dt}")
                print(f"\nScript error as {token} in '{condense(transcript)}'")
                raise

        transcript.append(mv)

        # Make and show the move (3rd arg is move to make)
        brd = makeMove(brd, tknToPlay, mv)  # , moves

        # Prepare for next round
        brd = brd.lower()  # Just in case
        tknToPlay = 'xo'[tknToPlay == 'x']  # Switch to other side

    # Game is over:
    tknCt = brd.count(token)
    enemy = len(brd) - tknCt - brd.count('.')
    if show: print(f"\nScore: Me as {token=}: {tknCt} vs Enemy: {enemy}\n")
    xscript = [f"_{mv}"[-2:] for mv in transcript]
    if show: print(f"Game transcript: {''.join(xscript)}")
    return tknCt, enemy, ''.join(xscript)


# Parse args here
tkn, trnyCt, defFile = "x", 1, "Othello4"  # token, game count, users file name
for arg in args:
    if len(arg) == 1 and arg in "xXoO":
        tkn = arg.lower()
    elif re.search(r"^\d+$", arg):
        trnyCt = int(arg)  # Number of games to play
    else:
        defFile = arg[:-3] if arg.lower().endswith(".py") else arg

# Import user's file here
sys.argv = [defFile + '.py']  # else imported file sees sys.argv of caller
try:
    _tmp = __import__(defFile, globals=None, locals=None,
                      fromlist=['quickMove', 'findMoves', 'makeMove'], level=0)
    quickMove, findMoves, makeMove = _tmp.quickMove, _tmp.findMoves, _tmp.makeMove
except:
    print("Error on import")
    raise

SECSPERGAME = 90 # normal is .3
gamesperline = 1
WORSTGAMECT = 3  # Number of games to show
tourneyStart = time.process_time()
if trnyCt < 2:
    playGame(quickMove, tkn, True)  # Play a single game
else:
    res, worst, mine, tkns = [], [], 0, 0  # all game results, worst 3 games, my token total, all tokens total
    aSCORES = []
    for gameNum in range(1, trnyCt + 1):
        gameStart = time.process_time()
        pg = playGame(quickMove, tkn)  # returns [myTknCt, enemyTknCt, gameXscript]
        mine, tkns = mine + pg[0], tkns + pg[0] + pg[1]
        timeUsed = time.process_time() - gameStart
        res += [pg]  # Append played game to results
        scr = pg[0] - pg[1]  # Score
        if len(worst) < WORSTGAMECT or scr < worst[-1][0]:
            worst = sorted(worst + [(scr, gameNum, pg[0], tkn, pg[2])])[:WORSTGAMECT]
        aSCORES.append(f"{scr}")
        if not gameNum % gamesperline:  # print complete lines (of 25 games)
            dt = ' '.join(aSCORES[-gamesperline:])  # token differences
            print(f"{dt} Score so far: {100 * mine / tkns:.3g}% Time: {timeUsed}")
        if timeUsed > SECSPERGAME:
            print(f"\nLast game used {timeUsed:.4g}s => exit");
            exit()
        tkn = 'xo'[tkn == "x"]

    print("\n\nWorst games:")
    for wg in worst: print(f"Game {wg[1]} as {wg[3]}: {wg[0]}, {wg[-1]}")
    print(f"\nScore: {mine}/{tkns} => {100 * mine / tkns:.4g}%")
    print(f"Total time: {time.process_time() - tourneyStart:.4g}s")

# Csaba Gabor, p8, 10 Dec 2021