import random
import time
import importlib
import os
import os.path

class Tile:
    #9 is for bomb
    def __init__(self,number):
        self.visible=False
        self.flagged=False
        self.__number = number
    def flip(self):
        if not self.flagged:
            self.visible=True
    def getnumber(self):
        if self.visible:
            return self.__number
        if self.flagged:
            return 9
        return -1
      
class MinesweeperGame:
    def __init__(self,height=16,width=30,nbombs=99,zerog=True,\
                 default='dfsstrategy',fromfile=""):
        self._active=True
        self._h = height
        self._w = width
        self._b = nbombs
        self.board = [[-1 for _ in range(self._w)] for _ in range(self._h)]
        self._firstmove=False
        self._zero_start=zerog
        self._victory=False
        self._fromfile=fromfile
        self._tempgrid = [[Tile(0) for _ in range(self._w)] for _ in range(self._h)]
        self._counter = self._b
        self._starttime = 0
        try:
            self._aifilename = default
            self._import_strategy()
            self._ai = iter(self._aimodule.MinesweeperAI(self))
        except Exception as e:
            self._aimodule = None
            self._ai=None
            self._aifilename=''
            raise Exception('Bad AI File: '+str(e))
                
    def _import_strategy(self):
        self._aimodule = importlib.import_module('strategies.'+os.path.splitext(self._aifilename)[0])
       
    def _generateboard(self,firstmove=None):       
        self._firstmove=True
        height=self._h
        width=self._w
        nbombs=self._b
        exc = None
        if nbombs>(height*width)-(9 if self._zero_start else 1):
            exc = ValueError('Too many mines!')

        self._nsafe = (height*width)-nbombs

        temp = [[0]*width for _ in range(height)]
        neighbor = []
        if firstmove:
            neighbor = self.neighbors(*firstmove)
        points = [(r,c) for r in range(height) for c in range(width) \
                  if (r,c) !=firstmove and not (self._zero_start and ((r,c) in neighbor))]

        if self._fromfile:
            if '.' not in self._fromfile:
                self._fromfile+='.txt'
            pts=set()
            self._b=0
            try:
                with open('boards/'+self._fromfile) as fp:
                    lines = fp.readlines()
                for line in lines:
                    line = (line.strip())
                    if not line:
                        break
                    t = eval(line)
                    if len(t)!=2 or (type(t[0]) is not int) or (type(t[1]) is not int)\
                    or t[0]>=height or t[1]>=width or t[0]<0 or t[1]<0:
                        raise ValueError(t)
                    pts.add(tuple(t))
                    self._b+=1
                self._changecounter(self._b-nbombs)
            except Exception as e:
                pts = random.sample(points,k=nbombs)
                self._b=nbombs
                exc = e
        else:
            pts = random.sample(points,k=nbombs)
                
        for r,c in pts:
            temp[r][c]=9
            for r2,c2 in self.neighbors(r,c):
                temp[r2][c2]+=1
                
        self._nsafe = (height*width)-self._b
        
        self._grid = [[Tile(min(x,9)) for x in row] for row in temp]
        for r in range(len(self._tempgrid)):
            for c in range(len(self._tempgrid[r])):
                if self._tempgrid[r][c].flagged:
                    self._grid[r][c].flagged=True
        #self._tempgrid = [[Tile(0) for _ in range(self._w)] for _ in range(self._h)]
        self._starttime = time.time()
        if exc is not None:
            raise Exception('Bad board file: '+str(exc))
        
    def neighbors(self,r,c):
        return list(filter((lambda p: p[0]>=0 and p[1]>=0 and p[0]<self._h and p[1]<self._w), \
                           [(r+1,c-1),(r+1,c),(r+1,c+1),\
                            (r,c-1),          (r,c+1),\
                            (r-1,c-1),(r-1,c),(r-1,c+1)]))

    def flip(self,r,c):
        if self._firstmove == False:
            self._generateboard((r,c))
        if not self._active:
            return -1
        t = self._grid[r][c]
        if t.flagged or t.visible:
            return -1
        
        t.visible = True
        n = t.getnumber()
        if n==9:
            self._lose(r,c)
            return 9
        try:
            self.board[r][c]=n
        except Exception:
            pass
        
        
        self._nsafe-=1
        if self._nsafe==0:
            self._win()   
        if t.getnumber()==0:
            for r2,c2 in self.neighbors(r,c):
               self.flip(r2,c2)
        return n
                
    def flag(self,r,c):
        if (not self._active):
            return -1
        
        t = self._grid[r][c] if self._firstmove else self._tempgrid[r][c]
        if t.visible:
            return -1
        t.flagged = not t.flagged
        try:
            self.board[r][c] = 9 if t.flagged else -1
        except Exception:
            pass

        if t.flagged:
                
            self._changecounter(-1)
        else:
            self._changecounter(1)
        return int(t.flagged)
            
    def _changecounter(self,delta):
        self._counter+=delta

    def _setcounter(self,val):
        self._counter=val
            
    def _win(self):
        self._active=False
        self._victory=True
        self._setcounter(0)                    
        
    def _lose(self,r,c):
        self._active=False
                
    def aimove(self):
        if not (self._ai and self._active):
            return
        next(self._ai)

    def aiautoplay(self):
        if not (self._ai and self._active):
            return
        for _ in self._ai:
            if not self.active:
                break
    
  

    def exportfile(self,name='boards/MinesweeperGameBoard.txt'):
        
        if not os.path.isdir(os.path.dirname(name)):
           os.makedirs(os.path.dirname(name))
        
        g = self._grid if self._firstmove else self._tempgrid
        if self._firstmove and self._active:
            self._lose(-1,-1)
        with open(name,'w') as fp:
            for r in range(len(g)):
                for c in range(len(g[r])):
                    g[r][c].visible = True
                    if g[r][c].getnumber()==9 or (not self._firstmove and g[r][c].flagged):
                        fp.write('({},{})\n'.format(r,c))
            
            
    def newgame(self):
        if self._aimodule:
            self._ai = iter(self._aimodule.MinesweeperAI(self))
        self._setcounter(self._b)       
        self._firstmove=False
        self._active=True
        self._victory=False
        self.board = [[-1 for _ in range(self._w)] for _ in range(self._h)]
        self._tempgrid = [[Tile(0) for _ in range(self._w)] for _ in range(self._h)]

    @property
    def firstmove(self):
        return self._firstmove

    @property
    def minecount(self):
        return self._counter

    @property
    def h(self):
        return self._h
    @property
    def height(self):
        return self.h

    @property
    def w(self):
        return self._w
    @property
    def width(self):
        return self.w

    @property
    def b(self):
        return self._b
    def bombs(self):
        return self.b

    @property
    def active(self):
        return self._active

    @property
    def victory(self):
        return self._victory

    @property
    def starttime(self):
        return self._starttime

    @property
    def zero_start(self):
        return self._zero_start
    
        
   

          
        
