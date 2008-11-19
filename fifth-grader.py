from __future__ import division
import re

numbers = [5, 4, 2, 4, 3 ]
joiners = ["-", "+", "*", "/", "**", ""]
result = 126

def generate_nonnegative_integer_tuples_below(n, length):
    if length == 0:
        yield ()
    else:
        for i in range(n):
            for rest in generate_nonnegative_integer_tuples_below(n, length-1):
                yield (i,)+rest

def join_numbers(numbers, joiners, my_j_nrs):
    return "".join(
            str(numbers[i])+joiners[my_j_nrs[i]]
            for i in range(len(numbers)-1)) + str(numbers[-1])

def generate_paren_combinations(s, allow_whole=False):
    paren_spots = [(match.start(), match.end()) 
            for match in re.finditer(r"\b[0-9]+", s)]

    yield s

    for i, (opening_paren, _) in enumerate(paren_spots):
        if i == 0 and not allow_whole:
            # shouldn't parenthesize whole expr
            close_spots = paren_spots[i+1:-1]
        else:
            close_spots = paren_spots[i+1:]

        for _, closing_paren in close_spots:
            for in_paren in generate_paren_combinations(
                    s[opening_paren:closing_paren]):
                for post_paren in generate_paren_combinations(
                        s[closing_paren:], allow_whole=True):
                    yield s[:opening_paren] + "(" + in_paren + ")" + post_paren
                    yield s[:opening_paren] + "(-" + in_paren + ")" + post_paren

for my_j_nrs in generate_nonnegative_integer_tuples_below(
        len(joiners), length=len(numbers)-1):
    for s in generate_paren_combinations(
            join_numbers(numbers, joiners, my_j_nrs)):

        # evaluate with floats first to scout for overflows
        float_s = re.sub("([0-9]+)", "\\1.", s)

        try:
            eval(float_s)
        except ZeroDivisionError:
            pass
        except ValueError:
            # (-n)**(fraction)
            pass
        except OverflowError:
            # don't even try this with integers
            pass
        else:
            try:
                if eval(s) == result:
                    print s
            except ZeroDivisionError:
                pass
