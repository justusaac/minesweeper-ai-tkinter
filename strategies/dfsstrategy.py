'''
This strategy calculates the probability of each hidden tile containing a mine, as well as each number.
This information is used to estimate the probability of making meaningful progress when guessing.
This also lets it find every tile that is safe to open.
It is more sophisticated than the other strategies I made/found, for Hard difficulty its win rate is about 45%.
With typical sized boards it is very rare but possible that it could take hours to make its guess.
With larger boards it gets more and more likely to be super slow, this strategy is not as well suited for those games.
'''
from collections import Counter
import itertools
from functools import cache
import copy

class MinesweeperAI:
    def __init__(self,game,guess=True):
        self.game=game
        self.threshold = 4000
        
    @cache
    def neighbors(self,r,c):
        return tuple(filter((lambda p: p[0]>=0 and p[1]>=0 and p[0]<self.game.h and p[1]<self.game.w),
                           ((r+1,c-1),(r+1,c),(r+1,c+1),
                            (r,c-1),          (r,c+1),
                            (r-1,c-1),(r-1,c),(r-1,c+1))))
    
    @cache
    def secondneighbors(self,r,c):
        return tuple(filter((lambda p: p[0]>=0 and p[1]>=0 and p[0]<self.game.h and p[1]<self.game.w),
                           ((r+2,c-1),(r+2,c),(r+2,c+1),
                    (r+1,c-2),                          (r+1,c+2),
                    (r,c-2),                            (r,c+2),
                    (r-1,c-2),                          (r-1,c+2),
                            (r-2,c-1),(r-2,c),(r-2,c+1))))
    
    
        
    def __iter__(self):
        h = self.game.h
        w = self.game.w
        board = self.game.board

        self.dead = set()

        self.neighbors.cache_clear()
        self.secondneighbors.cache_clear()
        
        if not self.game.firstmove:
            choice = (h//4,w//4) if self.game.zero_start else (0,0)
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

            #No info about any tile
            if len(edge)==0:
                if self.game.minecount==len(unknown):
                    for r,c in unknown:
                        if board[r][c]==-1:
                            self.game.flag(r,c)
                            yield
                else:
                    choice = self.pickguess(unknown)
                    self.game.flip(*choice)
                    yield
                continue
                             
            #Trivial search        
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
                        
            if foundsomething:
                continue
            
            #Local search
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
                
            doubleedges = set()
            occurses = []
            numberses = []
            lenses = []
            for edgess,frontierss in zip(subsets,frontiersubsets):
                #limited depth search to enumerate all possible configurations
                doubleedge = set()
                for elem in edgess:
                    for r,c in self.neighbors(*elem):
                        if board[r][c]==-1:
                            doubleedge.add((r,c))
                doubleedges.update(doubleedge)
                            
                target=min(self.game.minecount,len(edgess))
                occurs = [Counter({x:0 for x in edgess}) for _ in range(target+1)]
                numbers = [{x:[0]*9 for x in doubleedge} for _ in range(target+1)]
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
                        for elem in doubleedge:
                            if elem not in selected:
                                numbers[len(selected)][elem][len(selected.intersection(self.neighbors(*elem)))]+=1
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
                            if n<0 or len(candidates.intersection(self.neighbors(*elem)))<n or\
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
                        for elem in doubleedge:
                            if elem not in selected:
                                numbers[len(selected)][elem][len(selected.intersection(self.neighbors(*elem)))]+=1

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
                numberses.append(numbers)
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
            #Figure out safest moves from these probabilities
            bestprob = float('inf')
            bestpt = None
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
                elif foundsomething==False and prob<bestprob:
                    bestprob=prob
                    bestpt = pt

                    
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
            elif not foundsomething and unkprob<bestprob/additions:
                bestpt = self.pickguess(unknown)

            
            if foundsomething:
                continue

           
            #Make dead tile analysis
            
            def analyze_dead(pt):
                for r2,c2 in self.neighbors(*pt):
                    if board[r2][c2]==-1 and (r2,c2) not in edge:
                        return False
                for i in range(len(numberses)):
                    num = None
                    for j in range(len(numberses[i])):
                        if not multipliers[i][j]:
                            continue
                        lst = numberses[i][j].get(pt,())
                        for k in range(len(lst)):
                            if lst[k]>0:
                                if num is None:
                                    num=k
                                elif num!=lst[k]:
                                    return False
                return True
            
            for pt in unknown:
                if pt not in self.dead and analyze_dead(pt):
                    self.dead.add(pt)
                
            
            #Identify more 5050/forced guess situation and guess there
            
            for edgess,vlss in zip(subsets,validlengths):
                if len(vlss)>1:
                    #mine count will give more info later
                    continue
                bc =[]
                bestprob = float('inf')
                for pt in edgess:
                    
                    o = occur[pt]
                    if o<=bestprob:
                        if o<bestprob:
                            bc = []
                        bc.append(pt)
                        bestprob = o
                    for pt2 in self.neighbors(*pt):
                        if pt2 in unknown:
                            if not edgess<=set(itertools.chain((pt2,),self.neighbors(*pt2))):
                                break
                    else:
                        continue
                    break
                else:
                    #no more info coming
                    bestpos = self.pickguess(bc)
                    if bestpos:
                        foundsomething=True
                        self.game.flip(*bestpos)
                        yield

            if foundsomething:
                continue
            
            
                
            
            
            #Pick guess with decent safety and chance to be 0
            bestcandidates = set()
            target = (bestprob)*1.1
            for pt,prob in occur.items():
                if prob<=target:
                    bestcandidates.add(pt)
            if unkprob<=target/additions:
                bestcandidates.update(doubleedges.difference(edge))

            bestcandidates.difference_update(self.dead)
            #No tiles that gain any info, just have to guess the safest guess
            if not bestcandidates:
                
                if board[bestpt[0]][bestpt[1]]==-1:
                    self.game.flip(*bestpt)
                    yield
                    continue
                    
                
            
            choices = []
            for pt in bestcandidates:
                score = 1
                for i in range(len(numberses)):
                    tot = 0
                    for j in range(len(numberses[i])):
                        if lenses[i][j]>0:
                            tot+=numberses[i][j].get(pt,(0,))[0]\
                                  /lenses[i][j]*multipliers[i][j] 
                    score*=tot/sum(multipliers[i])
                        
                score*=(1-unkprob)**len(unknown.intersection(self.neighbors(*pt)))
                choices.append((pt,score,occur[pt]/additions or unkprob))
            #Combine safe percent and zero percent to create final score
            
            zero_weight = 0.88
            bestscore = max(map(lambda t: t[1]*zero_weight+\
                                                (1-t[2])*(1-zero_weight), choices))
            bestchoices = []
            bestscore = 0
            for t in choices:
                score= t[1]*zero_weight+(1-t[2])*(1-zero_weight)
                if score>=bestscore:
                    if score>bestscore:
                        bestscore = score
                        bestchoices.clear()
                    bestchoices.append(t[0])
            choice = self.pickguess(bestchoices)
            

            
            #Calculate probabilities of unknown tiles being 0
            unkchoices = []
            unkth = 0
            if unkprob<=target/additions:
                for i in range(1,8):
                    p = (1-unkprob)**i
                    sc =p*zero_weight+(1-unkprob)*(1-zero_weight)
                    if sc>bestscore:
                        unkth=i
                    else:
                        break
                if unkth>0:
                    bestn = 9
                    for r,c in unknown:
                        if (r,c) in doubleedges:
                            continue
                        n = 0
                        for r2,c2 in self.neighbors(r,c):
                            if board[r2][c2]==-1:
                                n+=1
                        if n<=unkth and n<=bestn and n>0:
                            if n<bestn:
                                unkchoices.clear()
                                bestn=n
                            unkchoices.append((r,c))
                        

            if unkchoices:
                choice = unkchoices[0]
            intersect1 = 0
            intersect2 = 0
            for elem in unkchoices:
                if intersect1==0:
                    l2 = len(doubleedges.intersection(self.secondneighbors(*elem)))
                    if l2>intersect2:
                        intersect2=l2
                        choice= elem
                l1 = len(doubleedges.intersection(self.neighbors(*elem)))
                if l1>intersect1:
                    intersect1=l1
                    choice= elem
            
            
            
            #Guess
            
            self.game.flip(*choice)
            yield
                        
    def pickguess(self,bestcandidates):
        bestn = 9
        bestpos = None
        for r,c in bestcandidates:
            if self.game.board[r][c]!=-1:
                continue
            n = 0
            for r2,c2 in self.neighbors(r,c):
                if self.game.board[r2][c2]==-1:
                    n+=1
            if n<bestn:
                bestn=n
                bestpos = (r,c)
        return bestpos                
                



        
