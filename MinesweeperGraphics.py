from MinesweeperGame import *

from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import os.path

class MinesweeperGraphics(MinesweeperGame):
    colordict ={0:'#bbb',1:'#00f',2:'#090',3:'#e00',4:'#008',\
                5:'#800',6:'#088',7:'#000',8:'#888',9:'#000'}
    
    images = dict()
    
    def __init__(self, *args, **kwargs):

        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            tkinter.messagebox.showerror('Error',str(e)) 

        #used for ai autoplay
        self.afterid = None
        self.delay=0
        
        self.root = Tk()
        self.root.title('Mining Sweeper')
        self.root.resizable(False,False)

        #load assets or default text
        try:
            self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file=os.path.dirname(__file__)+'/assets/swag.png'))
        except Exception:
            pass
        #This needs to be a variable otherwise it will be garbage collected, breaking the whole program
        self.pixel = PhotoImage(width=0,height=0)
        try:
            self.images.update({'flag':{'image':PhotoImage(file=os.path.dirname(__file__)+'/assets/flag.png')}})
        except Exception:
            self.images.update({'flag':{'text':'F','fg':'#e00'}})
            
        try:
            self.images.update({'9':{'image':PhotoImage(file=os.path.dirname(__file__)+'/assets/9.png')}})
        except Exception:
            self.images.update({'9':{'text':'B'}})
        try:
            self.images.update({'9x':{'image':PhotoImage(file=os.path.dirname(__file__)+'/assets/9x.png')}})
        except Exception:
            self.images.update({'9x':{'text':'X','fg':'#e00'}})


            
       
        #The bar at the top
            
        self.counterstring = StringVar()
        self.counterstring.set(str(self._b))
        self.zfilllen=len(str(self._b))

        self.zerostart=IntVar()
        self.zerostart.set(self._zero_start)
        
        self.gameframe = Frame(self.root)
        self.gameframe.grid(row=1,padx=10,pady=(0,10),sticky='wn')
        self._initgameframe()        

        self.ctrlframe = Frame(self.root,bd=5)
        self.ctrlframe.grid(row=0,padx=5,sticky='news')
        self.bombcount = Label(self.ctrlframe,textvariable = self.counterstring,fg='#f00',font=('Consolas','18'),width='3')
        self.bombcount.grid(column=0,row=0,sticky='w',padx=1,pady=1)

        self.movebutton = Button(self.ctrlframe,text='AI Move',width='7',\
                                 command=self.aimove)
        self.movebutton.grid(column=1,row=0,sticky='w',padx=1,pady=1)

        self.autobutton = Button(self.ctrlframe,text='Autoplay',width='9',\
                                 command=self.aiautoplay)
        self.autobutton.grid(column=2,row=0,sticky='w',padx=1,pady=1)

        self.ngbutton = Button(self.ctrlframe,text='New game',command=self.newgame,width='8')
        self.ngbutton.grid(column=3,row=0,sticky='ew',padx=1,pady=1)

        self.setbutton = Button(self.ctrlframe,text='Settings',command=self._settings,width='8')
        self.setbutton.grid(column=4,row=0,sticky='e',padx=1,pady=1)

        
        #Settings popup
               
        self.popup = Toplevel(bd=4,relief='groove')
        self.popup.title('Settings')
        self.popup.resizable(False,False)
        self.popup.protocol('WM_DELETE_WINDOW', self._closepopup)
        self.popup.withdraw()
        self.popup.overrideredirect(True)

        self.setframe = Frame(self.popup,bd=5)
        self.setframe.grid()

        

        self.configframe = Frame(self.setframe,bd=4,relief='ridge')
        self.configframe.grid(row=0,column=0,sticky='news',padx=1,pady=1)

        self.heightvar = StringVar(self.root,str(self._h))
        self.widthvar = StringVar(self.root,str(self._w))
        self.bombvar = StringVar(self.root,str(self._b))
        self.delayvar = StringVar(self.root,str(self.delay))
        for var in [self.heightvar,self.widthvar,self.bombvar,self.delayvar]:
            var.trace('w',lambda *args,var=var: self._checkentry(var))
        self.heightentry = Entry(self.configframe,width=3,font='Consolas',textvariable=self.heightvar)
        self.widthentry = Entry(self.configframe,width=3,font='Consolas',textvariable=self.widthvar)
        self.bombentry = Entry(self.configframe,width=3,font='Consolas',textvariable=self.bombvar)
        
            
        self.hlabel = Label(self.configframe,text='Height:')
        self.hlabel.grid(row=0,column=0,sticky='w',padx=1,pady=1)
        self.heightentry.grid(row=0,column=1,sticky='w',padx=1,pady=1)
        
        self.wlabel = Label(self.configframe,text='Width:')
        self.wlabel.grid(row=1,column=0,sticky='w',padx=1,pady=1)
        self.widthentry.grid(row=1,column=1,sticky='w',padx=1,pady=1)
        
        self.blabel = Label(self.configframe,text='Mines:')
        self.blabel.grid(row=2,column=0,sticky='w',padx=1,pady=1)
        self.bombentry.grid(row=2,column=1,sticky='w',padx=1,pady=1)

        self.modecheck = Checkbutton(self.configframe,text='First move 0',\
                                     variable= self.zerostart)
        self.modecheck.grid(row=3,column=0,columnspan=2,sticky='w',padx=1,pady=1)

        self.aiframe = Frame(self.setframe,bd=4,relief='ridge')
        self.aiframe.grid(row=1,column=0,sticky='news',padx=1,pady=1)
        
        self.ailabel = Label(self.aiframe,text='AI File:')
        self.ailabel.grid(row=0,column=0,columnspan=2,sticky='w',padx=1,pady=1)
        self.aientry = Entry(self.aiframe,font='Consolas',width=16)
        self.aientry.grid(row=1,column=0,columnspan=2,sticky='news',padx=1,pady=1)
        self.aientry.insert(0,self._aifilename)

        self.delaylabel = Label(self.aiframe,text='Autoplay delay')
        self.delayentry = Entry(self.aiframe,width=3,font='Consolas',textvariable=self.delayvar)
        self.delaylabel.grid(row=2,column=0,sticky='w',padx=1,pady=1)
        self.delayentry.grid(row=2,column=1,sticky='w',padx=1,pady=1)

        self.impframe = Frame(self.setframe,bd=4,relief='ridge')
        self.impframe.grid(row=2,column=0,sticky='news',padx=1,pady=1)
        
        self.clearbtn = Button(self.impframe,text='Clear',command=self._clearimport)
        self.clearbtn.grid(row=0,column=1,sticky='w',padx=1,pady=1)
        self.exportbtn = Button(self.impframe,text='Export board',command=self.exportfile)
        self.exportbtn.grid(row=2,column=0,sticky='w',padx=1,pady=1,columnspan=2)
        self.importlabel=Label(self.impframe,text='Import from:')
        self.importlabel.grid(row=0,column=0,sticky='w',padx=1,pady=1)
        self.importentry = Entry(self.impframe,font='Consolas',width=16)
        self.importentry.grid(row=1,column=0,columnspan=2,sticky='news',padx=1,pady=1)
        self.importentry.insert(0,self._fromfile)

        self.closebtn = Button(self.setframe,text='Close',command=self._closepopup)
        self.closebtn.grid(row=3,column=0,sticky='w',padx=1,pady=1)
        
        
        mainloop()

    #Makes grid of blank tkinter buttons
    def _initgameframe(self, dim_change=True):
        if not dim_change:
            for r in reversed(range(self._h)):
                for c in range(self._w):
                    self.buttons[r][c].config(state='normal',relief='raised',
                                              bg='#ccc',text=' ',image=self.pixel)
            return
        
        gf = Frame(self.root,bg='#333',relief='ridge',bd=3)
        
        '''
        gf=self.gameframe
        for widget in gf.winfo_children():
            widget.destroy()
        '''
        self._setcounter(self._b)
        self.buttons = []
        for r in range(self._h):
            currrow = []
            for c in range(self._w):
                t = Button(gf,width=26,height=26,image=self.pixel,bd=4,\
                           bg='#ccc',activebackground='#bbb',compound='c',\
                           padx=0,pady=0,font=('Consolas','18'),\
                           command=(lambda r=r,c=c:self.flip(r,c)),text=' ')
                t.grid(column=c,row=r,sticky='news')
                t.bind("<Button-3>", (lambda event, r=r,c=c:self.flag(r,c)))
                t.bind("<Button-2>", (lambda event, r=r,c=c:self.flag(r,c)))
                currrow.append(t)
            self.buttons.append(currrow)
        
        self.gameframe.grid_forget()
        self.gameframe.destroy()
        
        self.gameframe=gf
        
        self.gameframe.grid(row=1,padx=10,pady=(0,10),sticky='wn')
        


    def flip(self,r,c):
        try:
            if ((n:=super().flip(r,c)) not in (-1,9)):
                self.buttons[r][c].config(state='disabled',relief='flat',bg='#bbb',\
                            disabledforeground=self.colordict.get(n),text=str(n))
        except Exception as e:
            
            tkinter.messagebox.showerror('Error',str(e)) 
            

    def flag(self,r,c):
        match super().flag(r,c):
            case 1:
                self.buttons[r][c].config(**self.images.get('flag'))
            case 0:
                self.buttons[r][c].config(text=' ',image=self.pixel)

    def _changecounter(self,delta):
        super()._changecounter(delta)
        self._updatecounterstring()

    def _setcounter(self,val):
        super()._setcounter(val)
        self._updatecounterstring()

    def _updatecounterstring(self):
        self.counterstring.set(str(self._counter).zfill(self.zfilllen))

    def _win(self):
        super()._win()
        timetaken = time.time()-self.starttime
        for i in range(len(self._grid)):
            row = self._grid[i]
            for j in range(len(row)):
                tile = row[j]
                if not tile.visible:
                    self.buttons[i][j].config(**self.images.get('flag'))
                else:
                    n = tile.getnumber()
                    self.buttons[i][j].config(state='disabled',relief='flat',bg='#bbb',\
                        disabledforeground=self.colordict.get(n),text=str(n))
        
        tkinter.messagebox.showinfo('Victory royale',\
                                    '{:.2f} seconds'.format(timetaken))

    def _lose(self,r,c):
        super()._lose(r,c)
        for i in range(len(self._grid)):
            row = self._grid[i]
            for j in range(len(row)):
                tile = row[j]
                tile.visible=True
                n = tile.getnumber()
                if (n==9) == (tile.flagged):
                    continue
                bgcol = '#bbb' if (i,j)!=(r,c) else '#f00'
                rel = 'raised' if (i,j)!=(r,c) else 'flat'
                t = '9x' if tile.flagged else '9'
                self.buttons[i][j].config(bg=bgcol,relief=rel,\
                            disabledforeground=self.colordict.get(n),**self.images.get(t))

    #aimove same as default
                
    def aiautoplay(self):
        if not (self._ai and self.active):
            return
        self.autobutton.config(command=self.stopautoplay,text='Pause')
            
        ogdelay = self.delay
        try:
            self.delay = float(self.delayvar.get().strip() or 0)
            if self.delay<0:
                raise Exception
        except Exception:
            self.delay=ogdelay
            tkinter.messagebox.showerror('Error','Bad delay')
            self.delayvar.set(str(ogdelay))
        for _ in self._ai:
            cont = IntVar(self.gameframe)
            self.afterid = (currafter := self.gameframe.after(max(1,int(self.delay*1000)),cont.set,1))
            self.gameframe.wait_variable(cont)
            if self.afterid!=currafter or not self.active:
                break
        
        self.stopautoplay()

    def stopautoplay(self):
        if self.afterid:
            self.gameframe.after_cancel(self.afterid)
            self.afterid = None
        self.autobutton.config(command=self.aiautoplay,text='Autoplay')

    def _checkentry(self,strvar):
        strvar.set(strvar.get()[:3]) #cat face
    def _clearimport(self):
        self.importentry.delete(0,'end')

    def exportfile(self,name='boards/MinesweeperGameBoard.txt'):
        name = tkinter.filedialog.asksaveasfilename(
            initialdir="./boards",
            title="Export Minesweeper board",
            defaultextension="txt"
        )
        if not name:
            return
        super().exportfile(name)
        self.importentry.delete(0,'end')
        self.importentry.insert(0,'/'.join(name.split('boards/')[1:]))

    #Reads in the new game settings from the relevant inputs
    def newgame(self):
        
        self.stopautoplay()
        ogh = self._h
        ogw = self._w
        ogb = self._b
        ogz = self._zero_start
        try:
            self._h = int(self.heightvar.get().strip())
            self._w = int(self.widthvar.get().strip())
            self._b = int(self.bombvar.get().strip())
            self._zero_start = self.zerostart.get()
            
            if self._b>(self._w*self._h)-(9 if self._zero_start else 1):
                raise Exception('Too many mines')
            if self._h<=0 or self._w<=0 or self._b<0:
                raise Exception('Bad dimensions')
        except Exception as e:
            self._h=ogh
            self._w=ogw
            self._b=ogb
            self._zero_start=ogz
            self.heightvar.set(str(ogh))
            self.widthvar.set(str(ogw))
            self.bombvar.set(str(ogb))
            tkinter.messagebox.showerror('Error',str(e))
        

        self.zfilllen=len(str(self._b))  

        dim_change = self._w!=ogw or self._h!=ogh
        self._initgameframe(dim_change)
        
        mod = self.aientry.get()
        if self._aifilename!=mod:
            try:
                self._aifilename=mod
                self._import_strategy()
                self._ai = iter(self._aimodule.MinesweeperAI(self))
            except Exception:
                self._aimodule = None
                self._aifilename=''
                self._ai = None
                if len(mod):
                    tkinter.messagebox.showerror('Error','AI file not found')
            
        self._fromfile = self.importentry.get().strip()

        super().newgame()

    def _generateboard(self,firstmove=None):
        super()._generateboard(firstmove)
        self.zfilllen=len(str(self._b))
        self._updatecounterstring()
    
    def _settings(self):
        xpos = self.root.winfo_rootx()+200
        ypos = self.root.winfo_rooty()+50
        self.popup.geometry(f'+{xpos}+{ypos}')
        self.popup.deiconify()
        self.popup.focus()

    def _closepopup(self):
        self.popup.withdraw()
      
if __name__ == '__main__':
    MinesweeperGraphics()
