import sets
import sys

class TwoDimensionalField:
    def __init__(self, list, size_x):
        self.List = list
        self.SizeX = size_x

    def __getitem__(self, (i,j)):
        return self.List[j*self.SizeX+i]

    def __setitem__(self, (i,j), value):
        self.List[j*self.SizeX+i] = value

    def _size_y(self):
        return len(self.List) / self.SizeX
    size_y = property(_size_y)

    def _size_x(self):
        return self.SizeX
    size_x = property(_size_x)

    def __str__(self):
        def stringify(x):
            if isinstance(x, sets.Set):
                return ",".join([str(el) for el in x])
            else:
                return str(x)
        col_widths = [max([len(stringify(self[col, row])) for row in range(self.size_y)])
                      for col in range(self.SizeX)]

        lines = ["|".join([stringify(self[col, row]).ljust(col_widths[col]) for col in range(self.SizeX)])
            for row in range(self.size_y)]
        return "\n".join(lines)

    def copy(self):
        return TwoDimensionalField(self.List[:], self.SizeX)

    def keys(self):
        for row in range(self.size_y):
            for col in range(self.size_x):
                yield (col, row)

class SudokuField(TwoDimensionalField):
    def __init__(self, list=[None for i in range(9*9)]):
        TwoDimensionalField.__init__(self, list[:], 9)

    def copy(self):
        return SudokuField(self.List)

    def read(self, filename):
        lines = file(filename, "r").readlines()
        for j, line in enumerate(lines):
            for i, character in enumerate(line):
                try:
                    self[i,j] = int(character)
                except ValueError:
                    pass

    def _boxsize_y(self):
        return 3
    boxsize_y = property(_boxsize_y)

    def _boxsize_x(self):
        return 3
    boxsize_x = property(_boxsize_x)

def generate_unique_lists(field):
    # rows
    for row in range(field.size_y):
        yield [(col,row) for col in range(field.size_x)]

    # columns
    for col in range(field.size_x):
        yield [(col,row) for row in range(field.size_y)]

    # boxes
    for boxcol in range(0, field.size_x / field.boxsize_x):
        for boxrow in range(0, field.size_y / field.boxsize_y):
            yield [(boxcol*field.boxsize_x + col,
                    boxrow*field.boxsize_y + row) 
                    for row in range(field.boxsize_y)
                    for col in range(field.boxsize_x)]

def replace_none_by_full_sets(field):
    for index in field.keys():
        if field[index] is None:
            field[index] = sets.Set(range(1,10))

def eliminate_simple(field):
    did_something = False
    for unique_list in generate_unique_lists(field):
        givens = sets.Set([field[index]
                for index in unique_list
                if isinstance(field[index], int)])
        for index in unique_list:
            if isinstance(field[index], sets.Set):
                if len(givens & field[index]) > 0:
                    did_something = True
                field[index] -= givens
        for index in unique_list:
            try:
                if len(field[index]) == 1:
                    field[index] = list(field[index])[0]
            except TypeError:
                pass
    return did_something

def is_valid(field):
    for unique_list in generate_unique_lists(field):
        histogram = {}
        for index in unique_list:
            value = field[index]
            if not isinstance(value, int):
                continue

            if value in histogram:
                print "*** INVALID AT", index
                raw_input()
                return False
            else:
                histogram[value] = index
    return True
                
def count_possibilities(field):
    result = 1
    for index in field.keys():
        try:
            result *= len(field[index])
        except TypeError:
            pass
    return result

def all_equal(list):
    if not list:
        return True
    first = list[0]
    for i in list[1:]:
        if i != first:
            return False
    return True

def generate_subsets_with_n_members(member_list, n):
    if n == 0:
        yield sets.Set([])
    else:
        for index, el in enumerate(member_list):
            for rest in generate_subsets_with_n_members(member_list[(index+1):], n-1):
                yield sets.Set([el]) | rest

def eliminate_hist(field):
    for unique_list in generate_unique_lists(field):
        histogram = {}
        for index in unique_list:
            values = field[index]
            if isinstance(values, int):
                continue

            for value in values:
                if value in histogram:
                    histogram[value].add(index)
                else:
                    histogram[value] = sets.Set([index])

        for value, indices in histogram.iteritems():
            if len(indices) == 1:
                print indices
                field[list(indices)[0]] = value
                return True

        for n in range(2, field.SizeX):
            # indices of numbers with n or less occurrences 
            ion = {}
            for value, indices in histogram.iteritems():
                if len(indices) <= n:
                    ion[value] = histogram[value]

            for subset_size in range(n, 1+len(ion.keys())):
                for subset in generate_subsets_with_n_members(ion.keys(), subset_size):
                    indices_of_subset = sets.Set()
                    for el in subset:
                        indices_of_subset |= sets.Set(histogram[el])

                    if len(indices_of_subset) == subset_size:
                        did_something = False
                        for index_in_subset in indices_of_subset:
                            len_before = len(field[index_in_subset])
                            field[index_in_subset] &= subset
                            len_after = len(field[index_in_subset])
                            if len_before > len_after:
                                did_something = True
                        if did_something:
                            return True
               
    return False

if __name__ == "__main__":
    u = SudokuField()
    u.read("sudoku-example-2")
    #for unique_list in generate_unique_lists(u):
        #print unique_list
    #sys.exit()
    possibilities = u.copy()
    replace_none_by_full_sets(possibilities)
    while True:
        ds_simple = eliminate_simple(possibilities)
        print "AFTER SIMPLE:"
        print possibilities
        print count_possibilities(possibilities)
        ds_hist = eliminate_hist(possibilities)
        print "AFTER HIST:"
        print possibilities
        print count_possibilities(possibilities)
        if not (ds_simple or ds_hist):
            break

