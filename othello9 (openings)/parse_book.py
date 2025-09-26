from othello9 import makeMove

print(int('03'))

positions = {(ltr + str(i + 1)): (ord(ltr) - ord('a')) + i * 8 for i in range(8) for ltr in 'abcdefgh'}

with open('othello9 (openings)/opening_book') as f:
    lines = [line.strip() for line in f]

all_sequences = [[positions[line[i: i + 2].lower()] for i in range(0, len(line), 2)] for line in lines]

book = {}
for sequence in all_sequences:
    brd, tkn = '.' * 27 + 'ox......xo' + '.' * 27, 'x'
    for move in sequence:
        book[brd] = move
        brd = makeMove(brd, tkn, move)
        tkn = 'x' if tkn == 'o' else 'o'

for key in book:
    print(f'\'{key}\': {book[key]}, ')
