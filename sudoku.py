#based on http://newcoder.io/gui/
import argparse
from tkinter import Tk, Label, Canvas, Frame, Button, BOTH, TOP, BOTTOM, filedialog
from os import getcwd, path, listdir

BOARDS = []  # Available sudoku boards
MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board
FILES = [('Sudoku Files', '*.sudoku')]


class SudokuError(Exception):
    """
    An application specific error.
    """
    pass


def parse_arguments():
    """
    Parses arguments of the form:
        sudoku.py <board name>
    Where `board name` must be in the `BOARD` list
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help="Desired board name",
                            type=str,
                            choices=BOARDS,
                            required=True)

    # Creates a dictionary of keys = argument flag, and value = argument
    args = vars(arg_parser.parse_args())
    return args['board']


class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1

        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH)
        header_label = Label(self,
                             text="Welcome to Sudoku!",
                             font="Arial 18 bold")
        header_label.pack(fill=BOTH, side=TOP)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        save_button = Button(self,
                              text="Save Puzzle",
                              command=self.__save_puzzle)
        save_button.pack(fill=BOTH, side=BOTTOM)
        solve_button = Button(self,
                              text="Solve Puzzle",
                              command=self.__solve_puzzle)
        solve_button.pack(fill=BOTH, side=BOTTOM)
        clear_button = Button(self,
                              text="Clear answers",
                              command=self.__clear_answers)
        clear_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)
        self.canvas.bind("<Left>",self._left_key_pressed)
        self.canvas.bind("<Right>",self._right_key_pressed)
        self.canvas.bind("<Down>",self._down_key_pressed)
        self.canvas.bind("<Up>",self._up_key_pressed)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "sea green"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="green", tags="cursor"
            )

    def __draw_victory(self):
        # create a oval (which will be a circle)
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange"
        )
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(
            x, y,
            text="You win!", tags="victory",
            fill="white", font=("Arial", 32)
        )

    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = int((y - MARGIN) / SIDE), int((x - MARGIN) / SIDE)

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        #print(event) #DEBUG
        if self.row >= 0 and self.col >= 0 and self.game.start_puzzle[self.row][self.col] ==0:
            if event.keycode >=48 and event.keycode <= 57: #"1234567890"
                self.game.puzzle[self.row][self.col] = int(event.char)
                if self.game.check_win():
                    self.__draw_victory()
            if event.keycode == 46 or event.keycode == 8:
                self.game.puzzle[self.row][self.col] = 0
            self.__draw_puzzle()
            self.__draw_cursor()
    
    def _left_key_pressed(self, event):
        if self.game.game_over:
            return
        if (self.row >= 0 and self.col >= 1):
            self.col=self.col-1
            self.__draw_puzzle()
            self.__draw_cursor()

    def _right_key_pressed(self, event):
        if self.game.game_over:
            return
        if (self.row >= 0 and self.col >= 0 and self.col < 8):
            self.col=self.col+1
            self.__draw_puzzle()
            self.__draw_cursor()

    def _down_key_pressed(self, event):
        if self.game.game_over:
            return
        if (self.row >= 0 and self.col >= 0 and self.row < 8):
            self.row=self.row+1
            self.__draw_puzzle()
            self.__draw_cursor()

    def _up_key_pressed(self, event):
        if self.game.game_over:
            return
        if (self.row >= 1 and self.col >= 0):
            self.row=self.row-1
            self.__draw_puzzle()
            self.__draw_cursor()

    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_puzzle()
        
    def __solve_puzzle(self):
        self.game.solve_step()
        self.__draw_puzzle()
        
    def __save_puzzle(self):
        file = filedialog.asksaveasfile(filetypes=FILES, defaultextension=FILES)
        text=''
        for i in self.game.puzzle:
            text=text+''.join(map(str,i))+'\n'
        file.write(text)

class SudokuBoard(object):
    """
    Sudoku Board representation
    """
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    def __create_board(self, board_file):
        board = []
        for line in board_file:
            line = line.strip()
            if len(line) != 9:
                raise SudokuError(
                    "Each line in the sudoku puzzle must be 9 chars long."
                )
            board.append([])

            for c in line:
                if not c.isdigit():
                    raise SudokuError(
                        "Valid characters for a sudoku puzzle must be in 0-9"
                    )
                board[-1].append(int(c))

        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")
        return board


class SudokuGame(object):
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """
    def __init__(self, board_file):
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

    def check_win(self):
        for row in range(9):
            if not self.__check_row(row):
                return False
        for column in range(9):
            if not self.__check_column(column):
                return False
        for row in range(3):
            for column in range(3):
                if not self.__check_square(row, column):
                    return False
        self.game_over = True
        return True

    def __check_block(self, block):
        return set(block) == set(range(1, 10))

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])

    def __check_column(self, column):
        return self.__check_block(
            [self.puzzle[row][column] for row in range(9)]
        )

    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in range(row * 3, (row + 1) * 3)
                for c in range(column * 3, (column + 1) * 3)
            ]
        )
        
    def solve_step(self):
        while True:
            changes=self.__solve_single_candidates()
            changes=changes+self.__solve_scan_two_directions()
            if changes==0:
                break
        
    def __solve_scan_two_directions(self):
        changes=0
        for rbox in range(3):
            for cbox in range(3):
                alreadyInSquare=set(
                    [
                        self.puzzle[r][c]
                        for r in range(rbox * 3, (rbox + 1) * 3)
                        for c in range(cbox * 3, (cbox + 1) * 3)
                    ])
                if 0 not in alreadyInSquare: #Skip if no empty in square
                    continue
                alreadyInSquare.remove(0)
                notInSquare=set(range(1,10))-alreadyInSquare
                emptycols,emptyrows,empty=[],[],[]
                numEmpty=0
                for a in range(rbox * 3, rbox * 3 + 3):
                    for b in range(cbox * 3, cbox * 3 +3):
                        if self.puzzle[a][b]==0:
                            empty.append('%d,%d' % (a,b))
                            emptyrows.append(a)
                            emptycols.append(b)
                            numEmpty=numEmpty+1
                emptycols=set(emptycols)
                emptyrows=set(emptyrows)
                if numEmpty==1: #Solve only 1 missing
                    coords=empty[0].split(',')
                    self.puzzle[int(coords[0])][int(coords[1])]=notInSquare.pop()
                    changes=changes+1
                    continue
                for i in notInSquare:
                    potentials=empty.copy()
                    for r in emptyrows:
                        if i in self.puzzle[r]:
                            potentials = [x for x in potentials if not x.startswith('%d' % r)]
                    for c in emptycols:
                        if i in [x[c] for x in self.puzzle]:
                            potentials = [x for x in potentials if not x.endswith(',%d' % c)]
                    if len(potentials)==1:
                        coords=potentials[0].split(',')
                        self.puzzle[int(coords[0])][int(coords[1])]=i
                        changes=changes+1
        return changes
    
    def __solve_single_candidates(self):
        potentials=[1,2,3,4,5,6,7,8,9]
        changes=0
        #Single Candidates
        for r in range(9):
            for c in range(9):
                if self.puzzle[r][c]!=0:
                    continue
                p=potentials.copy()
                #SameRow
                for a in range(9):
                    if a==c:
                        continue
                    #print('%d,%d:%d' % (r,a,self.puzzle[r][a])) #DEBUG
                    if self.puzzle[r][a]!=0:
                        try:
                            p.remove(self.puzzle[r][a])
                        except:
                            continue
                #SameCol
                for a in range(9):
                    if a==r:
                        continue
                    if self.puzzle[a][c]!=0:
                        try:
                            p.remove(self.puzzle[a][c])
                        except:
                            continue
                #SameBox
                rbox=int(r/3)
                cbox=int(c/3)
                for a in range(rbox * 3, rbox * 3 + 3):
                    for b in range(cbox * 3, cbox * 3 +3):
                        try:
                            p.remove(self.puzzle[a][b])
                        except:
                            continue
                if len(p)==1:
                    changes=changes+1
                    self.puzzle[r][c]=p[0]
        return changes


if __name__ == '__main__':
    BOARDS=listdir(path.join(getcwd(),"gameboards")) 
    for i in range(len(BOARDS)):
        BOARDS[i] = BOARDS[i].replace(".sudoku","")
    board_name = parse_arguments()

    with open(path.join(getcwd(),"gameboards",'%s.sudoku' % board_name), 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 120))
        root.mainloop()