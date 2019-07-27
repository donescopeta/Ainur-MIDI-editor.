#!/usr/bin/python2.7
#import the pygame module, and the
#sys module for exiting the window we create
import pygame, sys
from threading import Thread as thread
import time
import queue as Queue
from multiprocessing import Process
from threading import Event,Timer
pygame.init()

#tasks
# note sstreaching
myfont = pygame.font.SysFont("LiberationSans-Regular", 20)
keycolors = 1,0,1,0,1,1,0,1,0,1,0,1
keynames = 'C','C#','D','D#','E','F','F#','G','G#','A','A#','H'
doubleSurface = lambda w,h,*y: [ pygame.surface.Surface((w, h),*y) for x in range(2) ]
keysurfaces = [ myfont.render(x, 1, (0,0,0)) for x in keynames ]
numbersurfaces = [ myfont.render(str(x), 1, (0,0,0)) for x in range(1,13) ]

class roll:
    def __init__(self):
        self.bottom = 0 #notes counted from botton
        self.scaleX = 1.0
        self.scaleY = 1.0
        self.displayHeight = 500
        self.displayWidth = 700
        self.gridsurface = None
        self.surface = None
        self.bottom = 0
        self.sybefore = self.scaleY
        self.sxbefore = self.scaleX

        self.rollHeight = self.displayHeight - 80
        self.resizing=False
        self.noteHeight = 20
        self.rollLeft = 50
        self.rollTop = 50
        self.rollWidth = self.displayWidth - self.rollLeft - 15

        self.rollrFrameRady = True
        self.XbarsBefore = 0
        self.XbarsBefore2 = 0
        self.XbarWidth = self.rollWidth * 0.25
        self.XbarScale = 1
        self.gridDensity = 0.25
        self.Rows = []
        self.Grid = []
        self.noteZones = []
        self.noteBuffer = set()
        #self.updateNotes = self.drawNotes

        self.dbNoteCreate = lambda x: None
        self.dbFetchNotes = lambda start,range: []

    def drawRows(self,surface):

        left, width = self.rollLeft, self.rollWidth
        noteHeight = self.noteHeight * self.scaleY
        toplim = -noteHeight

        a = width/self.noteHeight
        self.bottom += ( (1/self.sybefore) - (1/self.scaleY) )*a * 0.25
        bottom = self.bottom

        begin = self.rollHeight - (noteHeight*(1-bottom%1))

        #surface = pygame.surface.Surface((r.displayWidth, r.rollHeight))
        margin = (noteHeight-14) / 2

        #print "a:",a

        #print int(bottom)%12
        while begin > toplim:
            knth = int(bottom) % 12
            pygame.draw.rect(
                surface,
                [(keycolors[knth] or 0.8) * 255,] * 3,
                (left,begin,width,noteHeight)
            )
            if noteHeight > 15:
                surface.blit(keysurfaces[knth],(28, begin + margin))
            if knth == 11:
                surface.blit(numbersurfaces[int(bottom/12)],(8,begin+4))
                pygame.draw.line(surface, (0, 0, 0), (0, begin), (left, begin))
            #    if bottom / 12 >= 11: break
            yield begin,bottom
            begin -= noteHeight
            bottom+=1

        self.sybefore = self.scaleY


    def drawGrid(self,surface):
        barWidth = self.scaleX * self.XbarWidth
        a = self.rollHeight / barWidth

        self.XbarsBefore += ( (1/self.sxbefore) - (1/self.scaleX) ) * a * 0.25
        surface.fill(0)

        x = self.XbarsBefore

        width,height = surface.get_size()
        gridGap = barWidth * self.gridDensity
        ibegin = ( self.gridDensity - (x % 1) ) * barWidth

        yield x, ibegin
        #ibegin += gridGap

        x -= (x % 1)
        x += self.gridDensity

        while ibegin < self.rollWidth:
            #if self.rollWidth - ibegin > gridGap*2:
            #if not (x / 1):
            if not x % 1:
                label = myfont.render(str(int(x)),0,(0,0,0))
                surface.blit(label,(ibegin-(label.get_size()[0]*0.5),3))

            pygame.draw.line(surface, (0, 0, 0), (ibegin, 20), (ibegin, height))

            yield ibegin,x
            ibegin += gridGap
            #print ibegin, self.XbarsBefore,self.scaleX
            x += self.gridDensity
            self.sxbefore = self.scaleX

    def deleteNote(self,Note):
        self.noteBuffer.discard(Note)
    def selectNote(self): pass
    def strechNoteRight(self): pass
    def strechNoteLeft(self): pass

    def drawNotes(self,surface):

        bottom = self.bottom
        rollHeight = self.rollHeight
        barwidth = self.XbarWidth * self.scaleX
        x = self.XbarsBefore

        y = self.XbarsBefore2
        self.XbarsBefore2 = x
        #loading notes from database
        if int(x) != int(y):
            self.noteBuffer.update( self.dbFetchNotes(x - 1, self.rollHeight / barwidth + 2 ) )
            print("NOTES!!")
            for j in self.noteBuffer:
                print(j)

        noteheight = self.noteHeight * self.scaleY
        surface.fill(0)
        delete = set()
        #print(self.noteBuffer)
        for note in self.noteBuffer:
            begin,key,length = note
            xd = ( begin - x ) * barwidth
            l = length * barwidth
            k = rollHeight - ( ( key - bottom + 1 ) * noteheight )
            #print xd, k, rollHeight
            if xd < - barwidth or k < 0 or k > rollHeight or begin > x + self.displayHeight / barwidth + 1: 
                delete.add(note)
            else:
                yield xd, l + xd, k , k + noteheight, note
                pygame.draw.rect(surface,(180,0,0),(xd,k,l,noteheight))

        self.noteBuffer.difference_update(delete)
        if len(delete) : print('deleting',delete)

    def getNote(self,r):
        x, y = r
        x -= self.rollLeft
        y -= self.rollTop
        i = 0
        while True:
            try: x1, x2, y1, y2, note = self.noteZones[i]
            except: return False
            if y1 < y and y < y2 and x1 < x and x < x2:
                return note
            i += 1

    def getNotesInRectangle(px,py,sx,sy):
        x -= self.rollLeft
        y -= self.rollTop
        inXrange = lambda x: x > px and x < sx
        inYrange = lambda y: y > py and y < sy
        while True:
            try: x1, x2, y1, y2, note = self.noteZones[i]
            except: return
            if     ( inXrange(x1) or inXrange(x2) ) and \
                ( inXrange(y1) or inXrange(y2) ):
                yield note

    def display(self):
        pygame.init()
        #right
        self.rowsurface = doubleSurface(self.rollWidth + self.rollLeft, self.rollHeight)

        [ x.fill([180,]*3) for x in self.rowsurface ]

        self.gridsurface = doubleSurface(
            self.rollWidth,
            self.rollHeight + self.rollTop - 10,
            pygame.SRCALPHA, 32
        )

        self.notesSurface = doubleSurface(
            self.rollWidth,
            self.rollHeight,
            pygame.SRCALPHA, 32
        )

        #self.gridsurface.convert_alpha()
        #[ x.fill([180,]*3) for x in self.gridsurface ]
        #create a new drawing surface, width=300, height=300
        self.surface = pygame.display.set_mode((self.displayWidth,self.displayHeight))
        pygame.display.set_caption('Ainur Midi Editor ~ Mateusz Sokolowski')
        self.surface.fill([180,]*3)

    def updateNotes(self,surface):
        del self.noteZones[:]
        self.noteZones += self.drawNotes(surface)

    def updateRows(self,surface):
        self.rowsurface[1].fill([180,]*3)
        del self.Rows[:]
        self.Rows += self.drawRows(surface)

    def updateGrid(self,surface):
        del self.Grid[:]
        self.Grid += self.drawGrid(surface)

    def parseMouseVectorY(self,x,y):

        self.bottom += float(y) / (20 * self.scaleY)
        self.scaleY += float(x) / 100

        #self.bottom += self.scaleY * sbefore
        if self.scaleY < 0.2: self.scaleY = 0.2
        if self.scaleY > 1.7: self.scaleY = 1.7
        if self.bottom < 0: self.bottom = 0
        #print self.bottom,self.scaleY,x,y

    def parseMouseVectorX(self,x,y):
        self.XbarsBefore -= float(x) / 200
        self.scaleX += float(y) / ( 150 * self.scaleX )
        if self.scaleX < 0.2: self.scaleX = 0.2

    def noteCreate(self,key,begin):
        length = self.gridDensity
        n = (begin,int(key),length)
        self.noteBuffer.add(n)
        self.dbNoteCreate(n)

    def getGridCell(self,x,y):
        r = g = 0
        try:
            while self.Rows[r][0] > y : r += 1
            while self.Grid[g][0] < x : g += 1
        except: return []
        return self.Rows[r][1], self.Grid[g - 1][1]


    def getNoteFromClick(self,xy):
        x,y = xy
        n = self.getGridCell(x - self.rollLeft, y - self.rollTop)
        self.noteCreate(*n)
        self.updateNotes(self.notesSurface[0])

    def noteStreach(self,note,mag):
        g = 0
        start, key, ran = note
        x, y = mag
        x -= self.rollLeft
        y -= self.rollTop

        # additional sensivity
        x +=5

        g = sorted([ ( abs(g[0] - x) , g ) for g in self.Grid ], key = lambda x: x[0])
        
        r = g[0][1][1]

        print(r)

        if r < start:
            d = start - r
            start -= d
            ran += d
        elif r > start + ran:
            d = r -  (start + ran)
            ran += d
        else:
            rangeA = abs( r - start )
            rangeB = abs( r - (ran + start) )
            if rangeB < rangeA:
                 ran -= rangeB
            elif rangeA < rangeB:
                ran -= rangeA
                start += rangeA
            else: return note
  
        self.noteBuffer.discard(note)
        note = (start, key, ran)
        
        self.noteBuffer.add(note)

        return note

    def gripnote(self,p):
        x, y = p
        x -= self.rollLeft
        y -= self.rollTop

        print(y)
        for k in self.noteZones: 
            if \
                y > k[2] and \
                y < k[3] and ( \
                    abs(k[0] - x) < 5 or \
                    abs(k[1] - x) < 5 \
                ):
                
                print("found")
                return k[4]

        return None
#import some useful constants

class threadedWorker:
    def __init__(self,buffer,fps,**args):
        self.frametime = 1.0/float(fps)
        self.dblbuffer = buffer
        self.f = args["func"]
        self.fargs = args.get("args") or []
        self.do = [1,]
        thread(target=self.__Worker).start()

    def __Worker(self):
        do = self.do
        b = self.dblbuffer
        brv = b.reverse
        args = self.fargs
        f = self.f
        fr = self.frametime
        sl = time.sleep
        print ("start",fr)
        while do:
            f(b[1], *args)
            brv()
            sl(fr)
        del self

    def stop(self):
        print ("destroy")
        del self.do[:]

def clickableRect(x,y,w,h):
    return lambda xy, ax = x, ay = y, aw = w + x, ah = h + y: \
        ( ax <= xy[0] ) and ( xy[0] <= aw ) and ( xy[1] >= ay ) and ( xy[1] <= ah )
from pygame.locals import *
from database import database

#initialise the pygame module
clock = pygame.time.Clock()
db = database()

r = roll()
r.display()
r.updateRows(r.rowsurface[0])
r.updateGrid(r.gridsurface[0])
r.dbFetchNotes = db.getnotes
r.dbNoteCreate = lambda x: db.insert(*x)

#loop (repeat) forever

pTimer = lambda t=30,: thread(target = _pTimer, args = (t,)).start()

resizerI = None
resizingY = False
resizingX = False
mouseState=()
lastpos = None
p  = ()
clickTime = 0
frameTime = 0
rowDrawer = False
noteDrawer = False
gridDrawer = False
fastrender = False
#ev=Event()
#ev.set()
#timer = lambda t=1.0/30, s=ev.set,ti=Timer: ti(t, timer).start() or 1 and s()
#timer()
note=False
yStretcher = clickableRect(0,r.rollTop,r.rollLeft,r.rollHeight)
xStretcher = clickableRect(r.rollLeft,0,r.rollWidth,20)
rollclick = clickableRect(r.rollLeft,r.rollTop,r.rollWidth,r.rollHeight)
strechingNote = None

while True:
    #get all the user events
    #time.sleep(0.016)
    frameTime = clock.tick(fastrender and 60 or 5)
    #Double click detectorn
    if clickTime:
        clickTime += frameTime
        if clickTime > 300: clickTime = 0

    #
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            position = pygame.mouse.get_pos()
            ## Double click 
            f = r.gripnote(position)
            if f:
                strechingNote = f
                print("streaching")
                noteDrawer = threadedWorker(r.notesSurface,25,func=r.updateNotes)

            elif rollclick(position):
                if clickTime:
                    clickTime = 0
                    if note:
                         r.deleteNote(note)
                         r.updateNotes(r.notesSurface[0])
                    else: r.getNoteFromClick(position)
                else:
                    note = r.getNote(position)
                    clickTime = 1

            elif xStretcher(position):
                fastrender = resizingX = True
                gridDrawer = threadedWorker(r.gridsurface,60,func=r.updateGrid)
                noteDrawer = threadedWorker(r.notesSurface,60,func=r.updateNotes)
                lastpos = pygame.mouse.get_pos()
                #print "start"
                pygame.mouse.set_visible(0)

            elif yStretcher(position):
                fastrender = resizingY = True
                rowDrawer = threadedWorker(r.rowsurface,60,func=r.updateRows)
                noteDrawer = threadedWorker(r.notesSurface,60,func=r.updateNotes)
                lastpos = pygame.mouse.get_pos()
                #print "start"
                pygame.mouse.set_visible(0)
            continue

        elif event.type == MOUSEBUTTONUP:
            if resizingY:
                fastrender = resizingY = False
                rowDrawer.stop()
                noteDrawer.stop()
                pygame.mouse.set_visible(1)
            elif resizingX:
                fastrender = resizingX = False
                gridDrawer.stop()
                noteDrawer.stop()
                pygame.mouse.set_visible(1)
            elif strechingNote:
                noteDrawer.stop()
                strechingNote = None
            continue

        elif event.type == MOUSEMOTION:

            mouseState = pygame.mouse.get_pressed()

            if mouseState == (1,0,0):
                p = pygame.mouse.get_pos()
                if resizingY:
                    vector = (p[0] - lastpos[0],p[1] - lastpos[1])
                    r.parseMouseVectorY(*vector)
                    pygame.mouse.set_pos(lastpos)
                elif resizingX:
                    vector = (p[0] - lastpos[0],p[1] - lastpos[1])
                    r.parseMouseVectorX(*vector)
                    pygame.mouse.set_pos(lastpos)
                elif strechingNote:
                    print("performing streaching")
                    strechingNote = r.noteStreach( strechingNote, p )
                elif note and ( note != r.getNote(p) ):
                    r.noteBuffer.discard(note)
                    g = r.getGridCell(p[0] - r.rollLeft, p[1] - r.rollTop)
                    note =  ( g[1], int(g[0]) ) + note[2:]
                    r.noteBuffer.add(note)
                    r.updateNotes(r.notesSurface[0])
            continue

        elif event.type == QUIT:
            pygame.quit()
            pygame.mouse.set_visible(1)
            sys.exit()

        #print("tick " + str(pygame.time.get_ticks()))
        #clock.tick(40)
    r.surface.fill([180,]*3)
    tuple( map(lambda xy: r.surface.blit(xy[0][0],xy[1]), (
        (r.rowsurface, (0,r.rollTop)),
        (r.gridsurface, (r.rollLeft,10)),
        (r.notesSurface, (r.rollLeft,r.rollTop)),
    )) )
    pygame.display.flip()
        #ev.wait()
        #ev.clear()
        #print "do"
        #clock.tick(60)
