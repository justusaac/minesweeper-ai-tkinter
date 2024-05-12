
# AI Minesweeper

## Playing Minesweeper
#### GUI
Running `MinesweeperGraphics.py` opens a Tk window that resembles the Minesweeper game. The board dimensions and game parameters can be modified from the `Settings` menu, along with the AI strategy that will be used and the layout of the board if you don't want it to be random.
The file defining the AI strategy to be imported will be searched for in the `/strategies` folder.
The file defining the board to import will be searched for in the `/boards` folder. Clearing the text entry for the board will make the board randomly generated.
These settings will be applied upon the start of a new game.

The current board can be exported with the `Export` button, which will also cause you to lose the current game if it is still going. If the game's first move has not been made, the configuration of mines will not yet have been generated, so instead all the tiles that have been flagged will be exported, which is an easy way to make a custom mine configuration. The way the boards are stored is also easily human interpretable so the files can be modified by hand.

#### AI simulation
Running `StrategyTest.py` will make an AI strategy play many games of Minesweeper without any graphics and report the win rate and time taken afterwards. The details of this simulation can be configured through the extra command line arguments: 
The name of a file will be interpreted as the file containing the AI strategy to be tested; 
A single integer will be used to determine the number of games to simulate; 
And three integers separated by 'x' will define the height, width, and number of mines for the game board. 

If an exception or keyboard interrupt occurs in the middle of the simulation, the current game board will be exported to `boards/StrategyTestBoard.txt` which can perhaps be imported to the MinesweeperGraphics game to make it easier to figure out what exactly happened.

## Creating AI strategies
The AI strategy will be instantiated like `iter(MinesweeperAI(self))`, where self is an instance of a MinesweeperGame, and the AI should move when `next()` is called on it. This means that it's name should be `MinesweeperAI`, and it could either be a function that contains the `yield` keyword or a class that defines the `__iter__` method that uses `yield`. The AI strategy should call the methods on the MinesweeperGame that is passed as its argument, the value that is yielded will be discarded; it's only there so that you can step 1 move at a time.

Useful methods and properties of MinesweeperGame objects for AI players:\
`MinesweeperGame.board : list[list[int]]`: a 2d array of integers representing the game's board in the following way:\
-1: a tile that has not yet been opened or flagged\
0-8: an opened tile with that number of neighboring mines\
9: an unopened tile that has been flagged\
Modifying this array is OK, it won't affect the functioning of the game.\
`MinesweeperGame.flip(row : int, column : int) -> int`: the tile at the (zero-indexed) row and column will be opened, and the number on the tile that was opened will be returned (or -1 if it didn't open a tile)\
`MinesweeperGame.flag(row : int, column : int) -> int`: the tile at the given row and column's flagged status will be toggled, and the boolean flagged status of the tile will be returned as an into (or -1 if it didn't affect a tile)\
The following properties are read-only:\
`MinesweeperGame.height : int`: the number of rows on the board\
`MinesweeperGame.width : int`: the number of columns on the board\
`MinesweeperGame.bombs : int`: the total number of mines on the board\
`MinesweeperGame.minecount : int`: the number of mines remaining that's displayed to the player which is the total number of mines minus the number of flagged (so it can be inaccurate)\
`MinesweeperGame.zero_start : bool`: whether the first move is guaranteed to open a tile containing a 0\
`MinesweeperGame.firstmove : bool`: whether the first move has been made yet\
`MinesweeperGame.active : bool`: whether the game has not ended yet\

You can check the files in the `/strategies` folder for some examples

