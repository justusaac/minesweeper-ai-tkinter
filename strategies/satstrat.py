import pysat.solvers
import pysat.card
import pysat.formula
import pysat.process
from collections import Counter
from functools import lru_cache

#This one needs to figure out all the flags for itself
#If the player flags a tile thats not really a mine it breaks

@lru_cache
def count_models(clauses,poolsize):
    with pysat.solvers.Solver(bootstrap_with=clauses) as solv:
        if not solv.solve():
            raise Exception('invalid board')
        count = 0
        points = Counter({x:0 for x in range(poolsize)})
        ispos = lambda x: x>0
        
        for elem in solv.enum_models():
            points.update(filter(ispos,elem))
            count+=1
    return [points,count]
            
                 
class MinesweeperAI:
    def __init__(self,game):
        self.game=game
        self.flags = set()
        self.threshold = 10


    def __iter__(self):
        h = self.game.h
        w = self.game.w
        board = self.game.board
        pool = pysat.formula.IDPool()
        
        if not self.game.firstmove:
            choice = ((h//4)-1,(w//4)-1) if self.game.zero_start else (0,0)
            self.game.flip(*choice)
            yield
        
        while self.game.active:
            foundsomething = False


            #Tiles not open or flagged
            unknown = set()
            #All open tiles bordering an unknown tile
            frontier = set()
            #Unknown tiles bordering frontier tiles
            edge = set()
            for r in range(h):
                for c in range(w):
                    if 1[r][c] in (-1,9) and (r,c) not in self.flags:
                        unknown.add((r,c))
                        for r2,c2 in self.game.neighbors(r,c):
                            if board[r2][c2] not in (-1,9):
                                edge.add((r,c))
                                break
                    elif board[r][c] not in (-1,9):
                        for r2,c2 in self.game.neighbors(r,c):
                            if board[r2][c2] in (-1,9) and \
                                 (r2,c2) not in self.flags:
                                frontier.add((r,c))
                                
            
            #Check if all/none of a tile's unknown neighbors are mines     
            for r,c in frontier:
                tileno = board[r][c]
                if (tileno in (-1,9)):
                    continue
                hidden = 0
                for r2,c2 in self.game.neighbors(r,c):
                    if (r2,c2) in self.flags:
                        tileno-=1
                    elif board[r2][c2] in (-1,9):
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
                        if board[r2][c2] in (-1,9):
                            foundsomething=True
                            self.flags.add((r2,c2))
                            if board[r2][c2]==-1:
                                self.game.flag(r2,c2)
                                yield
                        
            if foundsomething:
                continue

            #Graph search to identify disjointed regions
            minecount = 0
            if self.game.b-len(self.flags)<=self.threshold and \
               len(unknown)<=3*self.threshold:
                minecount = self.game.b-len(self.flags)
                subsets = [unknown]
                frontiersubsets=[frontier]
            else:
                visited = set()
                subsets = []
                frontiersubsets = []
                for elem in edge:
                    if elem in visited:
                        continue
                    stack = [elem]
                    subset = set()
                    frontierss = set()
                    while stack:
                        curr = stack.pop()
                        subset.add(curr)
                        for z in self.game.neighbors(*curr):
                            if z in frontier:
                                frontierss.add(z)
                                for x in self.game.neighbors(*z):
                                    if x in edge and x not in visited:
                                        visited.add(x)
                                        stack.append(x)
                    subsets.append(subset)
                    frontiersubsets.append(frontierss)
                    
            bestcandidates = []
            bestprob = 1
            for ss,fss in zip(subsets,frontiersubsets):
                pool.restart()
                clauses = []
                if minecount:
                    unk = [pool.id(x) for x in ss]
                    clauses.extend(pysat.card.CardEnc.equals\
                                   (unk,minecount,vpool=pool).clauses)
                for r,c in fss:
                    num = board[r][c]
                    unk=[]
                    for r2,c2 in self.game.neighbors(r,c):
                        if (r2,c2) in self.flags:
                            num-=1
                        elif board[r2][c2] in (-1,9):
                            unk.append(pool.id((r2,c2)))
                    f = pysat.card.CardEnc.equals(unk,num,vpool=pool)
                    clauses.extend(f)

                points,count = count_models(frozenset(map(tuple, clauses)),pool.id())
                
                for pt,ct in points.items():
                    obj = pool.obj(pt)
                    if not obj:
                        continue
                    r,c = obj
                    #print((obj,ct),end='')
                    if ct==0:
                        if board[r][c]==-1:
                            foundsomething=True
                            self.game.flip(*obj)
                            yield
                    if ct==count:
                        if board[r2][c2] in (-1,9):
                            self.flags.add(obj)
                            foundsomething=True
                            if board[r][c]==-1:
                                self.game.flag(*obj)
                                yield
                    if (not foundsomething) and ct/count <= bestprob\
                       and board[r][c]==-1:
                        if ct/count<bestprob:
                            bestcandidates=[]
                            bestprob=ct/count
                        bestcandidates.append(obj)
                #print(count)
                        
            #Edge case of no edge
            if len(frontier)==0:
                bestcandidates=unknown
                
                        
            #Guess somewhere where more info may be gained           
            if not foundsomething:
                if not bestcandidates:
                    raise Exception
                bestn = 9
                bestpos = (-1,-1)
                for r,c in bestcandidates:
                    if board[r][c]!=-1:
                        continue
                    n = 0
                    for r2,c2 in self.game.neighbors(r,c):
                        if board[r2][c2]==-1:
                            n+=1
                    if n<bestn:
                        bestn=n
                        bestpos = (r,c)
                if bestpos==(-1,-1):
                    return
                self.game.flip(*bestpos)
                yield
                continue
            
                        
                        
                
                
            
                        
                        
           
        
