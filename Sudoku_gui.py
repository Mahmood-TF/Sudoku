import random
import time
import json
import numpy as np
from tkinter import *
from tkinter.ttk import *
import Sudoku_solver as gss

random.seed(time.time())

class SudokuGUI(Frame):

    def __init__(self, master, file):

        Frame.__init__(self, master)
        if master:
            master.title("SudokuGUI")

        self.grid = [[0 for x in range(9)] for y in range(9)]
        self.locked = []
        self.easy, self.hard = [], []
        self.load_db(file)
        self.make_grid()
        self.bframe = Frame(self)
        #bframe = Frame(self)

        # select game difficult level
        self.lvVar = StringVar()
        self.lvVar.set("")
        difficult_level = ["Easy","Hard"]
        Label(self.bframe, text="Please select difficult level:", font="Times 18 underline").pack(anchor=S)
        for l in difficult_level:
            Radiobutton(self.bframe, text=l, width=20, variable=self.lvVar, value=l).pack(anchor=S)
        # generate new game
        self.ng = Button(self.bframe, text='Generate New Game', width=20, command=self.new_game).pack(anchor=S)
        # solver
        self.sg = Button(self.bframe, text='Solver', width=20, command=self.solver).pack(anchor=S)

        self.bframe.pack(side='bottom', fill='x', expand='1')
        self.pack()
        
    def rgb(self, red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)
    
    def load_db (self, file):
        with open(file) as f:
            data = json.load(f)
        self.easy = data['Easy']
        self.hard = data['Hard']
