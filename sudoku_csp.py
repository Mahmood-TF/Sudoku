import random
import time
import json
import numpy as np
from tkinter import *
from tkinter.ttk import *

# Constraint Satisfaction Problem (CSP) Solver with Backtracking, MRV, and AC-3

class SudokuCSP:
    """
    A class to represent the Constraint Satisfaction Problem (CSP) solver for Sudoku using 
    Backtracking, Minimum Remaining Values (MRV), and AC-3 algorithms.
    """
    def __init__(self):
        """
        Initializes the SudokuCSP object with variables, domains, and neighbors.
        """
        self.variables = [(row, col) for row in range(9) for col in range(9)]
        self.domains = {var: list(range(1, 10)) for var in self.variables}
        self.neighbors = {var: set() for var in self.variables}
        for row in range(9):
            for col in range(9):
                for i in range(9):
                    self.neighbors[(row, col)].add((row, i))
                    self.neighbors[(row, col)].add((i, col))
                row_block, col_block = 3 * (row // 3), 3 * (col // 3)
                for r in range(row_block, row_block + 3):
                    for c in range(col_block, col_block + 3):
                        self.neighbors[(row, col)].add((r, c))
                self.neighbors[(row, col)].remove((row, col))

    def load(self, grid):
        """
        Loads the initial Sudoku grid and initializes the domains accordingly.

        Args:
            grid (list of list of int): 9x9 Sudoku grid.
        """
        self.grid = grid
        self.init_domains()

    def init_domains(self):
        """
        Refines the domains of each cell based on the initial Sudoku grid.
        """
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] != 0:
                    self.domains[(row, col)] = [self.grid[row][col]]

    def is_consistent(self, var, value, assignment):
        """
        Checks if assigning a value to a variable is consistent with the current assignment 
        and constraints.

        Args:
            var (tuple): Variable represented as (row, col).
            value (int): Value to assign to the variable.
            assignment (dict): Current assignment of variables.

        Returns:
            bool: True if the value is consistent, False otherwise.
        """
        for neighbor in self.neighbors[var]:
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True

    def select_unassigned_variable(self, assignment):
        """
        Selects the unassigned variable with the smallest domain using the MRV heuristic.

        Args:
            assignment (dict): Current assignment of variables.

        Returns:
            tuple: Unassigned variable with the smallest domain.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def order_domain_values(self, var, assignment):
        return self.domains[var]

    def ac3(self):
        """
        Implements the AC-3 (Arc Consistency 3) algorithm to enforce arc consistency across the CSP.

        Returns:
            bool: True if arc consistency is enforced, False if an inconsistency is found.
        """
        queue = [(var, neighbor) for var in self.variables for neighbor in self.neighbors[var]]
        while queue:
            (xi, xj) = queue.pop(0)
            if self.revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    return False
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def revise(self, xi, xj):
        """
        Revises the domain of xi based on the domain of xj, removing values from xi that have no 
        consistent counterpart in xj.

        Args:
            xi (tuple): Variable represented as (row, col).
            xj (tuple): Variable represented as (row, col).

        Returns:
            bool: True if a revision was made, False otherwise.
        """
        revised = False
        for x in self.domains[xi]:
            if all(x == y for y in self.domains[xj]):
                self.domains[xi].remove(x)
                revised = True
        return revised

    def backtrack(self, assignment):
        """
        Implements the backtracking search algorithm to find a solution to the CSP.

        Args:
            assignment (dict): Current assignment of variables.

        Returns:
            dict or None: Complete assignment if a solution is found, None otherwise.
        """
        if len(assignment) == len(self.variables):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            if self.is_consistent(var, value, assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result:
                    return result
                del assignment[var]
        return None

    def solve(self):
        self.ac3()
        return self.backtrack({})


class SudokuGUI(Frame):

    def __init__(self, master, file):
        Frame.__init__(self, master)
        if master:
            master.title("SudokuGUI")

        self.grid_values = [[0 for _ in range(9)] for _ in range(9)]
        self.locked = []
        self.easy, self.hard = [], []
        self.load_db(file)
        self.make_grid()
        self.bframe = Frame(self)

        self.lvVar = StringVar()
        self.lvVar.set("")
        difficult_level = ["Easy", "Hard"]
        Label(self.bframe, text="Please select difficult level:", font="Times 18 underline").pack(anchor=S)
        for l in difficult_level:
            Radiobutton(self.bframe, text=l, width=20, variable=self.lvVar, value=l).pack(anchor=S)
        self.ng = Button(self.bframe, text='Generate New Game', width=20, command=self.new_game).pack(anchor=S)
        self.sg = Button(self.bframe, text='Solver', width=20, command=self.solver).pack(anchor=S)

        self.bframe.pack(side='bottom', fill='x', expand='1')
        self.pack()

    def rgb(self, red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)

    def load_db(self, file):
        with open(file) as f:
            data = json.load(f)
        self.easy = data['Easy']
        self.hard = data['Hard']

    def new_game(self):
        level = self.lvVar.get()
        if level == "Easy":
            self.given = self.easy[random.randint(0, len(self.easy) - 1)]
        elif level == "Hard":
            self.given = self.hard[random.randint(0, len(self.hard) - 1)]
        else:
            self.given = [[0 for _ in range(9)] for _ in range(9)]
        self.grid_values = np.array(list(self.given)).reshape((9, 9)).astype(int)
        self.sync_board_and_canvas(initial=True)

    def solver(self):
        s = SudokuCSP()
        s.load(self.grid_values)
        start_time = time.time()
        solution = s.solve()
        if solution:
            self.grid_solution = [[0 for _ in range(9)] for _ in range(9)]
            for (row, col), value in solution.items():
                self.grid_solution[row][col] = value
            self.sync_board_and_canvas(initial=False)
            time_elapsed = '{0:6.2f}'.format(time.time() - start_time)
            str_print = f"Solution found\nTime elapsed: {time_elapsed}s"
        else:
            str_print = "No solution found, please try again"
        Label(self.bframe, text=str_print, relief="solid", justify=LEFT).pack()
        self.bframe.pack()

    def make_grid(self):
        (w, h) = (256, 256)
        c = Canvas(self, bg=self.rgb(128, 128, 128), width=2 * w, height=h)
        c.pack(side='top', fill='both', expand='1')

        self.rects = [[None for _ in range(18)] for _ in range(18)]
        self.handles = [[None for _ in range(18)] for _ in range(18)]
        rsize = w / 9
        guidesize = h / 3

        for y in range(18):
            for x in range(18):
                (xr, yr) = (x * guidesize, y * guidesize)
                if x < 3:
                    self.rects[y][x] = c.create_rectangle(xr, yr, xr + guidesize, yr + guidesize, width=4, fill='green')
                else:
                    self.rects[y][x] = c.create_rectangle(xr, yr, xr + guidesize, yr + guidesize, width=4, fill='gray')
                (xr, yr) = (x * rsize, y * rsize)
                r = c.create_rectangle(xr, yr, xr + rsize, yr + rsize)
                t = c.create_text(xr + rsize / 2, yr + rsize / 2)
                self.handles[y][x] = (r, t)

        self.canvas = c
        self.sync_board_and_canvas(initial=True)

    def sync_board_and_canvas(self, initial=True):
        """
        Synchronizes the board and the canvas, updating the GUI with the current grid values.

        Args:
            initial (bool): Whether to sync the initial grid values or the solution.
        """
        
        if initial:
            g = self.grid_values
            offset = 0
        else:
            g = self.grid_solution
            offset = 9

        for y in range(9):
            for x in range(9):
                if g[y][x] != 0:
                    self.canvas.itemconfig(self.handles[y][x + offset][1], text=str(g[y][x]))
                else:
                    self.canvas.itemconfig(self.handles[y][x + offset][1], text='')

if __name__ == "__main__":
    file = "sudoku_database.json"
    tk = Tk()
    gui = SudokuGUI(tk, file)
    gui.mainloop()