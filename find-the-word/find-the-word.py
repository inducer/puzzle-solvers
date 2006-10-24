import sys
import random
import sets

if len(sys.argv) < 4:
    print "usage:%s wordlist xdim ydim" % sys.argv[0]
    sys.exit(1)

words = [line.strip().upper() for line in file(sys.argv[1], "r").readlines()]

letters = sets.Set()

for word in words:
    for letter in word:
        letters.add(letter)

letters = list(letters)
letters.sort()

x_size = int(sys.argv[2])
y_size = int(sys.argv[3])

field = [[None for x in range(x_size)] for y in range(y_size)]

def deep_copy(f):
    if isinstance(f, list):
        return [deep_copy(i) for i in f]
    else:
        return f

def print_field(field):
    for y in range(y_size):
        print " ".join([letter or "." for letter in field[y]])

for word in words:
    while True:
        x = random.randint(0,x_size-1)
        y = random.randint(0,y_size-1)
        dx, dy = random.choice([(1,0), (0,1), (1,1)])

        field_copy = deep_copy(field)

        failed = False
        for letter in word:
            if field_copy[y][x] is None or field_copy[y][x] == letter:
                field_copy[y][x] = letter
            else:
                failed = True
                break
            x += dx
            y += dy
            if x >= x_size or y >= y_size:
                failed = True
                break

        if failed:
            continue
        field = field_copy
        break

print_field(field)
print

for x in range(x_size):
    for y in range(y_size):
        if field[y][x] is None:
            field[y][x] = random.choice(letters)

print_field(field)

