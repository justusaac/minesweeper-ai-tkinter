'''
This strategy looks for safe moves by comparing pairs of nearby tiles and seeing if all/none of one tile's neighboring mines are also neighboring the other tile.
If that fails its guessing method will be determined by the number of remaining mines.
If there are a lot of mines remaining, it wil guess by opening a tile that borders the fewest unknown tiles.
If there are a smaller amount of mines remaining, it will guess by opening the tile that has a mine in the fewest number of possible mine configurations.
This strategy is optimized a bit more for speed rather than win rate, so it can work well on larger boards.
'''
import itertools
from collections import Counter
from functools import cache

    
class MinesweeperAI:
    def __init__(self,game):
        self.game=game
        self.threshold = 10
    @cache
    def secondneighbors(self,r,c):
        return list(filter((lambda p: p[0]>=0 and p[1]>=0 and p[0]<self.game.h and p[1]<self.game.w), \
                           ((r+2,c-1),(r+2,c),(r+2,c+1),\
                    (r+1,c-2),                          (r+1,c+2),\
                    (r,c-2),                            (r,c+2),\
                    (r-1,c-2),                          (r-1,c+2),\
                            (r-2,c-1),(r-2,c),(r-2,c+1))))
    @cache
    def neighbors(self,r,c):
        return list(filter((lambda p: p[0]>=0 and p[1]>=0 and p[0]<self.game.h and p[1]<self.game.w), \
                           ((r+1,c-1),(r+1,c),(r+1,c+1),\
                            (r,c-1),          (r,c+1),\
                            (r-1,c-1),(r-1,c),(r-1,c+1))))

  
    def __iter__(self):
        h = self.game.h
        w = self.game.w
        board = self.game.board

        self.neighbors.cache_clear()
        self.secondneighbors.cache_clear()
        
        if not self.game.firstmove:
            choice = ((h//4)-1,(w//4)-1) if self.game.zero_start else (0,0)
            self.game.flip(*choice)
            yield
        
        while self.game.active:
            foundsomething = False
            
            #Unknown = Tiles not open or flagged
            unknown = set()
            #Frontier = All open tiles bordering an unknown tile
            frontier = set()
            #edge = All unknown tiles bordering an open tile
            edge = set()
            for r in range(h):
                for c in range(w):
                    if board[r][c] ==-1:
                        unknown.add((r,c))
                        for r2,c2 in self.neighbors(r,c):
                            if board[r2][c2] not in (-1,9):
                                edge.add((r,c))
                                break
                    elif board[r][c] !=9:
                        for r2,c2 in self.neighbors(r,c):
                            if board[r2][c2]==-1:
                                frontier.add((r,c))
                                break
           
            if len(unknown)==0:
                return
                    
                
                            
            #Check if all/none of a tile's unknown neighbors are mines               
            bestcandidates = []
            bestprob=1
            for r,c in frontier:
                tileno = board[r][c]
                if (tileno in (-1,9)):
                    continue
                hidden = 0
                for r2,c2 in self.neighbors(r,c):
                    if board[r2][c2] == 9:
                        tileno-=1
                    elif board[r2][c2] == -1:
                        hidden+=1
                if hidden==0:
                    continue
                ratio = tileno/hidden
                if ratio==0:
                    for r2,c2 in self.neighbors(r,c):
                        if board[r2][c2]==-1:
                            foundsomething=True
                            self.game.flip(r2,c2)
                            yield
                elif ratio==1:
                    for r2,c2 in self.neighbors(r,c):
                        if board[r2][c2]==-1:
                            foundsomething=True
                            self.game.flag(r2,c2)
                            yield
                elif not foundsomething and ratio<=bestprob:
                    if ratio<bestprob:
                        bestcandidates.clear()
                        bestprob=ratio
                    bestcandidates.extend(self.neighbors(r,c))
                        
                        
            if foundsomething:
                continue
            

            #Check pairs of open tiles to see if info can be revealed
            gen1 = (((r,c),n) for r,c in frontier for n in self.neighbors(r,c) if n in frontier)
            gen2 = (((r,c),n) for r,c in frontier for n in self.secondneighbors(r,c) if n in frontier)
            for gen in [gen1,gen2]:
                for loc1,loc2 in gen:
                    r1,c1 = loc1
                    r2,c2 = loc2
                    n1 = self.neighbors(r1,c1)
                    n2 = self.neighbors(r2,c2)
                    uniq1=[]
                    hidden1 = set()
                    flagged1 = 0
                    for r,c in n1:
                        match board[r][c]:
                            case 9:
                                flagged1+=1
                            case -1:
                                hidden1.add((r,c))
                                if (r,c) not in n2:
                                    uniq1.append((r,c))
                    
                    uniq2=[]
                    hidden2 = set()
                    flagged2 = 0
                    for r,c in n2:
                        match board[r][c]:
                            case 9:
                                flagged2+=1
                            case -1:
                                hidden2.add((r,c))
                                if (r,c) not in n1:
                                    uniq2.append((r,c))

                    unk1 = board[r1][c1]-flagged1
                    unk2 = board[r2][c2]-flagged2
                    
                    highest = float('-inf')
                    lowest = float('inf')
                    
                    alln = self.neighbors(r1,c1)+self.secondneighbors(r1,c1)
                    for comb in itertools.combinations(hidden1,unk1):
                        s = set(comb)
                        for n in alln:
                            if n not in frontier:
                                continue
                            r3,c3 = n
                            num = board[r3][c3]
                            neighb3 = self.neighbors(r3,c3)
                            unk3 = 0
                            for r4,c4 in neighb3:
                                match board[r4][c4]:
                                    case 9:
                                        num-=1
                                    case -1:
                                        if (r4,c4) in s:
                                            num-=1
                                        elif (r4,c4) not in hidden1:
                                            unk3+=1
                            if num<0 or num>unk3:
                                break
                        else:
                            i = len(s&hidden2)
                            highest = max(i,highest)
                            lowest = min(i,lowest)
                    if highest != float('-inf'):
                        if unk2==lowest:
                            for r0,c0 in uniq2:
                                if board[r0][c0]==-1:
                                    foundsomething=True
                                    self.game.flip(r0,c0)
                                    yield
                        if unk2-highest == len(uniq2):
                            for r0,c0 in uniq2:
                                if board[r0][c0]==-1:
                                    foundsomething=True
                                    self.game.flag(r0,c0)
                                    yield
                if foundsomething:
                    break
                                
              
            if foundsomething:
                continue
            if len(frontier)==0:
                bestcandidates=unknown
            elif self.game.minecount<=self.threshold:
                #Graph search to identify disjointed regions
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
                        for z in self.neighbors(*curr):
                            if z in frontier:
                                frontierss.add(z)
                                for x in self.neighbors(*z):
                                    if x in edge and x not in visited:
                                        visited.add(x)
                                        stack.append(x)
                    subsets.append(subset)
                    frontiersubsets.append(frontierss)

                occurses = []
                lenses = []
                for edgess,frontierss in zip(subsets,frontiersubsets):
                    #limited depth search to enumerate all possible configurations
                    target=min(self.game.minecount,len(edgess))
                    occurs = [Counter({x:0 for x in edgess}) for _ in range(target+1)]
                    lens = [0]*(target+1)
                    selected = set()
                    sneed = dict()
                    frees = dict()
                    for r,c in frontierss:
                        mines = board[r][c]
                        free=0
                        for r2,c2 in self.neighbors(r,c):
                            if board[r2][c2]==9:
                                mines-=1
                            elif board[r2][c2]==-1:
                                free+=1
                        sneed.update({(r,c):mines})
                        frees.update({(r,c):free})
                    def dfs(candidates):
                        nonlocal occur,lens,target,selected,sneed,frees
                        if len(selected)>target:
                            return
                        #Validate full combination
                        if not any(sneed.values()):
                            occurs[len(selected)].update(selected)
                            lens[len(selected)]+=1
                            return
                        if len(candidates)==0:
                            return
                        sneedbak = sneed.copy()
                        freesbak = frees.copy()
                        selbak = selected.copy()
                        #partial combination reduce search space
                        reduced = True
                        while reduced:
                            reduced=False
                            for elem in frontierss:
                                n = sneed[elem]
                                f = frees[elem]
                                
                                if n<0 or len(candidates.intersection(self.neighbors(*elem)))<n or \
                                   f<n or target-len(selected)<n:
                                    selected = selbak
                                    sneed = sneedbak
                                    frees = freesbak
                                    return
                                if n==0:
                                    for a in self.neighbors(*elem):
                                        if a in candidates:
                                            candidates.discard(a)
                                            reduced=True
                                            for b in self.neighbors(*a):
                                                if b not in frontierss:
                                                    continue
                                                frees[b]-=1
                                if f==n:
                                    add=(a for a in self.neighbors(*elem) if a in candidates)
                                    
                                    for a in add:
                                        selected.add(a)
                                        candidates.discard(a)
                                        reduced=True
                                        for b in self.neighbors(*a):
                                            if b not in frontierss:
                                                continue
                                            sneed[b]-=1
                                            frees[b]-=1
                        #check if valid already otherwise deepen search
                        if not any(sneed.values()):
                            occurs[len(selected)].update(selected)
                            lens[len(selected)]+=1
                            
                            selected = selbak
                            sneed = sneedbak
                            frees = freesbak
                            return
                        if len(selected)<target:
                            while candidates:
                                p = candidates.pop()
                                selected.add(p)
                                for b in self.neighbors(*p):
                                    if b in sneed:
                                        sneed[b]-=1
                                        frees[b]-=1
                                dfs(candidates.copy())
                                for b in self.neighbors(*p):
                                    if b in sneed:
                                        sneed[b]+=1
                                        frees[b]+=1
                                selected.remove(p)
                        selected = selbak
                        sneed = sneedbak
                        frees = freesbak
                        return
                    dfs(edgess.copy())
                    occurses.append(occurs)
                    lenses.append(lens)
                    
                #Put em together
                    
                noinfo = len(unknown)-len(edge)
                m=self.game.minecount
                
                occur= Counter({x:0 for x in edge})
                lens = [0]*(min(self.game.minecount,len(edge))+1)
                additions=0
                validlengths = [[i for i in range(len(lst)) if lst[i]] \
                                for lst in lenses]
                multipliers = [[0 for _ in lst] for lst in occurses]
                for comb in itertools.product(*validlengths):
                    t = sum(comb)
                    if t>m or m-t>noinfo:
                        continue
                    pro = 1
                    for i in range(len(comb)):
                        pro*=lenses[i][comb[i]]
                    additions+=pro
                    lens[t]+=pro
                    for i in range(len(comb)):
                        multipliers[i][comb[i]]+=pro/lenses[i][comb[i]]

                for i in range(len(occurses)):
                    for j in range(len(occurses[i])):
                        occur.update({x:int(y*multipliers[i][j]) \
                                      for x,y in occurses[i][j].items()})
                    
                
                #Figure out probability of all unknown tiles not in edge
                unkprob = 0
                if noinfo:
                    for i in range(len(lens)):
                        unkprob+=(lens[i]/additions)*((m-i)/noinfo)
                #Figure out safe moves from these probabilities
                bestprob = float('inf')
                bestcandidates = []
                for pt,prob in occur.items():
                    r,c = pt
                    if prob==additions:
                        if board[r][c]==-1:
                            foundsomething=True
                            self.game.flag(r,c)
                            yield
                    elif prob==0:
                        if board[r][c]==-1:
                            foundsomething=True
                            self.game.flip(r,c)
                            yield
                    elif foundsomething==False and prob<=bestprob:
                        if prob<bestprob:
                            bestprob=prob
                            bestcandidates=[]
                        bestcandidates.append((r,c))
                        
                
                if unkprob==1:
                    for r,c in set(unknown)-set(edge):
                        if board[r][c]==-1:
                            foundsomething=True
                            self.game.flag(r,c)
                            yield
                elif unkprob==0:
                    for r,c in set(unknown)-set(edge):
                        if board[r][c]==-1:
                            foundsomething=True
                            self.game.flip(r,c)
                            yield
                elif foundsomething==False and unkprob<(bestprob/additions):
                    bestcandidates = set(unknown)-set(edge)

            if foundsomething:
                continue
                
            #Guess
            
            bestn = 9
            bestpos = None
            for r,c in bestcandidates:
                if board[r][c]!=-1:
                    continue
                n = 0
                for r2,c2 in self.neighbors(r,c):
                    if board[r2][c2]==-1:
                        n+=1
                if n<bestn:
                    bestn=n
                    bestpos = (r,c)
            if bestpos:
                self.game.flip(*bestpos)
                yield

                    
                
            
                        
