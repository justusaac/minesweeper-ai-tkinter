from MinesweeperGame import *
import sys
import re

def test_strategy(n):
    succ = 0
    count = 0
    
    totaltime = 0
    args = [16,30,99,True,'goodstrategy.py']
    for a in sys.argv[1:]:
        if re.match(r'^[0-9]+x[0-9]+x[0-9]+$',a):
            args[:3] = map(int,a.split('x'))
        elif re.match(r'^[0-9]+$',a):
            n = int(a)
        elif re.match(r'^.+\.[a-zA-Z0-9]+$',a):
            args[4] = a
    print(f'Testing {args[4]} for {n} games on {args[0]}x{args[1]}x{args[2]} {"modern" if args[3] else "classic"} board')
    m = MinesweeperGame(*args)
    outfilename = 'boards/StrategyTestBoard.txt'
    try:
        for i in range(n):
            '''
            if i%1000==0:
                print(i)
                print('{:02d}:{:02d}:{:02d}'.format(\
                    *time.localtime(time.time())[3:6]))
            '''
            m.newgame()
            m.aiautoplay()
            totaltime+=(time.time()-m.starttime)
            succ+=m.victory
            count+=1
    except KeyboardInterrupt as k:
        print(str(k))
        m.exportfile(outfilename)
    except Exception as e:
        print(str(e))
        
        m.exportfile(outfilename)
    print('{} out of {} : {:.5%}'.format(succ,count,succ/count))
    print('{:.3f} seconds'.format(totaltime))
    

if __name__ == '__main__':
    test_strategy(100)
