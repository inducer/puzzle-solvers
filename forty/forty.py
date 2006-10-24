import sys

def assemble_weight(weights, target):
    if len(weights) == 0:
        if target == 0:
            return []
        else:
            return None
    first_weight = weights[0]
    new_weights = weights[1:]

    for factor in [-1,0,1]:
        attempt = assemble_weight(new_weights, target+factor*first_weight)
        if attempt is not None:
            if factor:
                return [-factor*first_weight] + attempt
            else:
                return attempt
    return None


def try_config(weight_sum, weights):
    for i in range(0,weight_sum+1):
        if assemble_weight(weights, i) is None:
            #print "can't assemble %d with %s" % (i, weights)
            return False
    return True


def generate_tuples(sum, length, least=0):
    assert length >= 0
    if length == 0:
        yield []
    else:
        for i in range(least, sum+1):
            for base in generate_tuples(sum-i, length-1, i):
                yield [i] + base


def brute_force(weight_sum, weight_count, print_solution=False):
    for weights in generate_tuples(weight_sum, weight_count, least=1):
        if try_config(weight_sum, weights):
            print weights, "works for", weight_sum
            if print_solution:
                for i in range(0, weight_sum+1):
                    print "  %d: %s" % (i, assemble_weight(weights, i))
            return


brute_force(40, 4, True)
for s in range(30, 100):
    for n in range(3,7):
        print "checking", s, "with", n
        brute_force(s, n)
