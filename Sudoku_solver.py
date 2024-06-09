import numpy as np
import random
import operator

random.seed()

Nd = 9  

class Population(object):
    """ A set of candidate solutions to the Sudoku puzzle.
    These candidates are also known as the chromosomes in the population. """

    def __init__(self):
        self.candidates = []


    def seed(self, Nc, given):
        self.candidates = []

        # Determine the legal values that each square can take.
        helper = Candidate()
        helper.values = [[[] for j in range(0, Nd)] for i in range(0, Nd)]
        for row in range(0, Nd):
            for column in range(0, Nd):
                for value in range(1, 10):
                    if ((given.values[row][column] == 0) and not (given.is_column_duplicate(column, value) or given.is_block_duplicate(row, column, value) or given.is_row_duplicate(row, value))):
                        # Value is available.
                        helper.values[row][column].append(value)
                    elif given.values[row][column] != 0:
                        # Given/known value from file.
                        helper.values[row][column].append(given.values[row][column])
                        break

        # Seed a new population.
        for p in range(0, Nc):
            g = Candidate()
            for i in range(0, Nd):  # New row in candidate.
                row = np.zeros(Nd)

                # Fill in the givens.
                for j in range(0, Nd):  # New column j value in row i.

                    # If value is already given, don't change it.
                    if given.values[i][j] != 0:
                        row[j] = given.values[i][j]
                    # Fill in the gaps using the helper board.
                    elif given.values[i][j] == 0:
                        row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j]) - 1)]

                # There must be no duplicates in the row.
                ii = 0
                while len(list(set(row))) != Nd:
                    ii += 1
                    if ii > 500000:
                        return 0
                    for j in range(0, Nd):
                        if given.values[i][j] == 0:
                            row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j]) - 1)]

                g.values[i] = row
            self.candidates.append(g)
        # Compute the fitness of all candidates in the population.
        self.update_fitness()


        return 1

    def update_fitness(self):
        """ Update fitness of every candidate/chromosome. """
        for candidate in self.candidates:

            candidate.update_fitness()
    def sort(self):
        """ Sort the population based on fitness. """
        self.candidates = sorted(self.candidates, key=operator.attrgetter('fitness'))



class Candidate(object):
    """ A candidate solutions to the Sudoku puzzle. """

    def __init__(self):
        self.values = np.zeros((Nd, Nd))
        self.fitness = None


    def update_fitness(self):
        """ The fitness of a candidate solution is determined by how close it is to being the actual solution to the puzzle.
        The actual solution (i.e. the 'fittest') is defined as a 9x9 grid of numbers in the range [1, 9]
        where each row, column and 3x3 block contains the numbers [1, 9] without any duplicates;
        if there are any duplicates then the fitness will be lower. """

        column_count = np.zeros(Nd)
        block_count = np.zeros(Nd)
        column_sum = 0
        block_sum = 0

        self.values = self.values.astype(int)
        # For each column....
        for j in range(0, Nd):
            for i in range(0, Nd):
                column_count[self.values[i][j] - 1] += 1

            for k in range(len(column_count)):
                if column_count[k] == 1:
                    column_sum += (1/Nd)/Nd
            column_count = np.zeros(Nd)

        # For each block...
        for i in range(0, Nd, 3):
            for j in range(0, Nd, 3):
                block_count[self.values[i][j] - 1] += 1
                block_count[self.values[i][j + 1] - 1] += 1
                block_count[self.values[i][j + 2] - 1] += 1

                block_count[self.values[i + 1][j] - 1] += 1
                block_count[self.values[i + 1][j + 1] - 1] += 1
                block_count[self.values[i + 1][j + 2] - 1] += 1

                block_count[self.values[i + 2][j] - 1] += 1
                block_count[self.values[i + 2][j + 1] - 1] += 1
                block_count[self.values[i + 2][j + 2] - 1] += 1

                # duplicate
                for k in range(len(block_count)):
                    if block_count[k] == 1:
                        block_sum += (1/Nd)/Nd
                block_count = np.zeros(Nd)

        # Calculate overall fitness.
        if int(column_sum) == 1 and int(block_sum) == 1:
            fitness = 1.0
        else:
            fitness = column_sum * block_sum

        self.fitness = fitness

