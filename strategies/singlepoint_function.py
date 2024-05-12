'''
This strategy is the same as the other single point strategy but written as a function just to show that you can do that
'''
import random

def MinesweeperAI(game):
    tiles = [(r,c) for r in range(game.h) for c in range(game.w)]
    random.shuffle(tiles)
    board = game.board
    
    while game.active:
        foundsomething = False
        
        for r,c in tiles:
            tileno = board[r][c]
            if (tileno in (-1,9)):
                continue
            hidden = 0
            for r2,c2 in game.neighbors(r,c):
                if board[r2][c2] == 9:
                    tileno-=1
                elif board[r2][c2] == -1:
                    hidden+=1
            if hidden==0:
                continue
            
            ratio = tileno/hidden
            
            if ratio==0:
                for r2,c2 in game.neighbors(r,c):
                    if board[r2][c2]==-1:
                        foundsomething=True
                        game.flip(r2,c2)
                        yield
            elif ratio==1:
                for r2,c2 in game.neighbors(r,c):
                    if board[r2][c2]==-1:
                        foundsomething=True
                        game.flag(r2,c2)
                        yield
                    
                    
        if foundsomething:
            continue
        
        if not tiles:
            return
        r,c = tiles.pop()
        while game.board[r][c]!=-1:
            r,c = tiles.pop()
        game.flip(r,c)
        yield
    return
