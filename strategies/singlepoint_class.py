import random

class MinesweeperAI:
    def __init__(self,game):
        self.game=game
        self.tiles = [(r,c) for r in range(game.h) for c in range(game.w)]
        random.shuffle(self.tiles)
        
    def __iter__(self):
        board = self.game.board
        
        while self.game.active:
            foundsomething = False
            
            for r,c in self.tiles:
                tileno = board[r][c]
                if (tileno in (-1,9)):
                    continue
                hidden = 0
                for r2,c2 in self.game.neighbors(r,c):
                    if board[r2][c2] == 9:
                        tileno-=1
                    elif board[r2][c2] == -1:
                        hidden+=1
                if hidden==0:
                    continue
                
                ratio = tileno/hidden
                
                if ratio==0:
                    for r2,c2 in self.game.neighbors(r,c):
                        if board[r2][c2]==-1:
                            foundsomething=True
                            self.game.flip(r2,c2)
                            yield
                elif ratio==1:
                    for r2,c2 in self.game.neighbors(r,c):
                        if board[r2][c2]==-1:
                            foundsomething=True
                            self.game.flag(r2,c2)
                            yield
                        
                        
            if foundsomething:
                continue
            
            if not self.tiles:
                return
            r,c = self.tiles.pop()
            while self.game.board[r][c]!=-1:
                r,c = self.tiles.pop()
            self.game.flip(r,c)
            yield
        return
