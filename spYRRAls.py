#!/usr/bin/python
##
##  spYRRAls.py  by  AR & RY:  this version 12/29/14
##
#  generate Ond spirals interactively, and save to tikz/LaTeX
#
from __future__ import print_function
from math import pi, cos, sin, sqrt, ceil
from operator import add
from Tkinter import *
import itertools
flatten = lambda lst: list(itertools.chain.from_iterable(lst))

def  make_spiral(shape,num=0):    
  # follows the circle, extending side lengths appropriately
  sideIncrement = {
    'H': [ 0, 0, 0, 1, -1, 1 ],
    'T': [ 1, 1, 1 ],
    'S': [ 0, 1, 0, 1 ]}
  sides = len(sideIncrement[shape])
  # directions are fractions of 2*pi
  directions = [ [cos(2*pi*j/sides), sin(2*pi*j/sides)]
                for j in range(1,1+sides) ]
  pos = []
  x = [0,0]
  dx = directions[-1]
  idir, ilen, icnt, jm = 0, 0, 0, 0
  while jm < max(num,sides):
    pos.append(x)
    x = list(map(sum, list(zip(x, dx))))
    if  icnt >= ilen:
      dx = directions[idir]
      ilen += sideIncrement[shape][idir]
      idir += 1
      icnt = -1
    icnt += 1
    if idir >= len(directions):
      idir = 0
    jm +=1
  if shape == 'H' and num > 0:
    # adjust to include origin 
    pos = [[0,0]] + [ [pos[j][0]-directions[0][0],
                       pos[j][1]-directions[0][1]]
                      for j in range(len(pos)-1) ]
  return(pos)

# count of polygonal number: known a priori!
testfunc = {
  # n-1 for n in hexagon as we adjusted for origin !
  'H': lambda n: 3*(n-1)**2 + 3*(n-1) + 1,
  'T': lambda n: n*(n+1)/2,
  'S': lambda n: n**2}

def get_max(coords):
  # calculate picture size in absolute coords
  numlist = flatten( coords )
  return(0.5 + max([ abs(numlist[j])
                     for j in range(len(numlist)) ]))

# boxes and shading

boxctr = {'S': [0.5,0.5],
          'T': [0.5,sqrt(3)/6],
          'H': [0.5,sqrt(3)/2]}

def get_boxes(sh, numBoxes):
  # candidates for complete spirals
  sides = {'S':4, 'T':3, 'H':6}[sh]
  ctrshift = {'S': lambda j: [0.5*(j%2),0.5*(j%2)],
              'T': lambda j: [0.5*((j%3)%2),sqrt(3)/6*(j%3)],
              'H': lambda j: [0,0]}[sh]
  boxscale = {'S': lambda j: j+1,
              'T': lambda j: j+1,
              'H': lambda j: j+0.5}[sh]
  # use the algorithm and adjust the center
  tmp = make_spiral( sh )
  basebox = [( tmp[j][0]-boxctr[sh][0],
               tmp[j][1]-boxctr[sh][1] )
             for j in range(sides) ]
  basebox.append(basebox[0])
  allboxes = []
  # boxes are scaled and shifted as needed
  for j in range(numBoxes):
    allboxes.append([ [ boxscale(j)*basebox[k][0] + ctrshift(j)[0],
                        boxscale(j)*basebox[k][1] + ctrshift(j)[1] ]
                      for k in range(1+sides) ])
  return(allboxes)

def shade( coords, k_ond, xymax, style, FH ):
  # this uses the dual lattice for grayscale visualizations
  sh = dual.var.get()
  sides = {'S':4, 'T':3, 'H':6}[sh]
  boxcoords = make_spiral( sh )
  if sh == 'H':
    # hexagon is rotated!
    dualbox = [( (boxcoords[j][1]-boxctr[sh][1])/sqrt(3),
                 (boxcoords[j][0]-boxctr[sh][0])/sqrt(3) )
               for j in range(sides) ]
  else:
    dualbox = [( (boxcoords[j][0]-boxctr[sh][0]),
                 (boxcoords[j][1]-boxctr[sh][1]) )
               for j in range(sides) ]
  # now translate the box around the spiral
  for j in range(len(coords)):
    box = [( dualbox[k][0] + coords[j][0],
             dualbox[k][1] + coords[j][1] )
           for k in range(sides) ]
    # scale the rgb values to get nice pictures
    rgbvals = [255-(j%k_ond)*255/k_ond*(1-int(rgb.state()[m]))
               for m in range(3)]
    # different routines for window and file
    {'pic':showcell,
     'tex':drawcell}[style](box, xymax, rgbvals, FH )

def save_data(FH):
  # write parameters to file so we can reproduce!
  print(''.join(['\\picdata=',
                 str(nkvars.state()), shape.var.get(),
                 spiral.var.get(), dual.var.get(),
                 ''.join(map(str, boxes.state())),
                 ''.join(map(str, rgb.state())),
                 str(filevars.state())]), file=FH)

# Tkinter routines for making spirals in the window
def show_pic():
  pic.delete("all") # initialize
  num = int(nkvars.state()[0])
  k_mod = int(nkvars.state()[1])
  opt = spiral.var.get()
  coords = make_spiral(shape.var.get(), num )
  xymax = get_max(coords)
  # first the spiral
  if opt == 'G' :
    shade( coords, k_mod, xymax, 'pic', 0 )
  elif opt == 'E':
    text = [ "%d" % (j+1) for j in range(num) ]
    showtext( coords, xymax, text )
  else:
    text = [ "%d" % (j%k_mod) for j in range(num) ]
    showtext( coords, xymax, text )
  # now the boxes to show the spiral candidates
  show_boxes = boxes.state()
  if show_boxes[0] or show_boxes[1]:  # all
    if shape.var.get() == 'H':
      numBoxes = int(ceil(xymax))
    else:
      numBoxes = int(ceil(sqrt(2)*xymax))
    allboxes = get_boxes(shape.var.get(), numBoxes)
    if show_boxes[0]:
      for j in range(numBoxes):
        showline(allboxes[j], xymax, 2, 'yellow')
    if show_boxes[1]:
      for j in range(numBoxes):
        if not testfunc[shape.var.get()](j+1) % k_mod:
          showline(allboxes[j], xymax, 3, 'darkorange')

def  shiftscale( coords, xymax ):
  # converts to pixel coords for image
  return( [(NN + NN/xymax*coords[j][0],
            NN - NN/xymax*coords[j][1])
           for j in range(len(coords))] )

def showtext( coords, xymax, label ):
  xy = shiftscale( coords, xymax )
  for j in range(len(coords)):
    pic.create_text( xy[j][0], xy[j][1],
                     text=label[j] )

def showline(line, xymax, w, col):
  xy = flatten( shiftscale( line, xymax ))
  pic.create_line( xy, width=w, fill=col )

def showcell(box, xymax, rgbvals, FH ):
  xy = flatten( shiftscale( box, xymax ))
  col = '#%02x%02x%02x' % ( rgbvals[0], rgbvals[1], rgbvals[2] )
  pic.create_polygon( xy, fill=col)


# tikz routines printed to file
def draw_pic():
  FH = open(filevars.state()[0], 'a')
  save_data(FH)
  print('\\begin{tikzpicture}', file=FH)
  num = int(nkvars.state()[0])
  k_mod = int(nkvars.state()[1])
  opt = spiral.var.get()
  coords = make_spiral(shape.var.get(), num )
  xymax = get_max(coords)
  # scale down large pictures
  scalesize = float(filevars.state()[1])
  if xymax > scalesize:
    print('[scale=%4f]' % (scalesize/xymax), file=FH)
  # first the spiral
  if opt == 'G' :
    print('''\\catcode`\\@=11
\\tikzset{col/.code={\\pgfutil@definecolor{.}{RGB}{#1}\\tikzset{color=.}}}
''', file=FH)  # for color definition
    shade( coords, k_mod, xymax, 'tex', FH )
  elif opt == 'E':
    text = [ '%d' % (j+1) for j in range(num) ]
    drawtext( coords, xymax, text, FH )
  else:
    text = [ '%d' % (j%k_mod) for j in range(num) ]
    drawtext( coords, xymax, text, FH )
  # now the boxes to show the spiral candidates
  show_boxes = boxes.state()
  if show_boxes[0] or show_boxes[1]:  # all
    if shape.var.get() == 'H':
      numBoxes = int(ceil(xymax))
    else:
      numBoxes = int(ceil(sqrt(2)*xymax))
    allboxes = get_boxes(shape.var.get(), numBoxes)
    if show_boxes[0]:
      for j in range(numBoxes):
        drawline(allboxes[j], xymax, 1, 'yellow!90!black', FH )
    if show_boxes[1]:
      if opt == 'G':
        color, wid = 'yellow', 1
      else:
        color, wid = 'orange!90!black', 1
      for j in range(numBoxes):
        if not testfunc[shape.var.get()](j+1) % k_mod:
          drawline(allboxes[j], xymax, wid, color, FH )
  print('\\end{tikzpicture}\n', file=FH)
  FH.close()

def drawtext( coords, xymax, label, FH ):
  for j in range(len(coords)):
    print("\\node at (%f,%f) {%s};" % (
      coords[j][0], coords[j][1], label[j] ), file=FH) 

def drawline(line, xymax, w, col, FH ):
  print("\\draw[%s,line width=%d] (%f,%f)" % ( 
    col, w, line[0][0], line[0][1] ), end='', file=FH)
  for j in range(len(line)):
    print("  -- (%f,%f)" % ( 
      line[j][0], line[j][1] ), end='', file=FH) 
  else:
    print(";", file=FH)

def drawcell(box, xymax, col, FH ):
  print("\\fill[col={%d,%d,%d}] (%f,%f)" % ( 
    col[0], col[1], col[2], box[-1][0], box[-1][1] ),
        end='', file=FH)
  for j in range(len(box)):
    print("  -- (%f,%f)" % ( 
      box[j][0], box[j][1] ), end='', file=FH) 
  else:
    print(";", file=FH)

## These classes borrowed from web tutorial for efficient Tk input
class ButtonBar(Frame):
  def __init__(self,
               parent=None,
               picks=[]):
    Frame.__init__(self, parent)
    for pick in picks:
      self.button = Button(self,
                           text=pick[0],
                           command=pick[1])
      self.button.pack(side=LEFT, anchor=W)
      
class CheckBar(Frame):
  def __init__(self,
               parent=None,
               selection=[],
               picks=[]):
    Frame.__init__(self, parent)
    Label(self, text=selection, padx=20).pack(side=LEFT)
    self.vars = []
    for pick in picks:
      var = IntVar()
      chk = Checkbutton(self, text=pick, variable=var)
      chk.pack(side=LEFT, anchor=W, expand=YES)
      self.vars.append(var)
  def state(self):
    return map((lambda var: var.get()), self.vars)

class RadioBar(Frame):
  def __init__(self,
               parent=None,
               selection=[],
               picks=[],
               initValue=''):
    Frame.__init__(self, parent)
    Label(self, text=selection, padx=20).pack(side=LEFT)
    self.var = StringVar()
    self.var.set(initValue)
    for pick in picks:
      chk = Radiobutton(self, text=pick[0],
                        variable=self.var, value=pick[1])
      chk.pack(side=LEFT, anchor=W)

class EntryBar(Frame):
  def __init__(self,
               parent=None,
               picks=[]):
    Frame.__init__(self, parent)
    self.vars = []
    for pick in picks:
      str = Label(self, text=pick[0])
      str.pack(side=LEFT, anchor=W)
      var = Entry(self, width=10)
      var.insert(5, pick[1])
      var.pack(side=LEFT, anchor=W, padx=10)
      self.vars.append(var)
  def state(self):
    return map((lambda var: var.get()), self.vars)

NN = 250         # half window size
win = Tk()

# picture
pic = Canvas(win, width=2*NN+1, height=2*NN+1)
pic.pack()
pic.config(relief=GROOVE, bd=4)

# input choices
panel = Frame(win).pack()

shape = RadioBar(panel, 'Choose shape: ',
                 [['Square', 'S'],
                  ['Triangle', 'T'],
                  ['Hexagon', 'H']], 'S')
shape.pack(side=TOP, pady=10)

nkvars = EntryBar(panel,
                  [['# cells', 100],
                   ['Ond size', 10]])
nkvars.pack(side=TOP)

spiral = RadioBar(panel, 'Spiral: ',
                     [['enumerate', 'E'],
                      ['count (mod k)', 'K'],
                      ['grayscale', 'G']], 'K')
spiral.pack(side=TOP)
spiral.config(relief=GROOVE, bd=2)

boxes = CheckBar(panel, 'Show boxes: ',
                 ['All', 'Complete'])
boxes.pack(side=TOP)

dual = RadioBar(panel, 'Dual shape: ',
                 [['Square', 'S'],
                  ['Triangle', 'T'],
                  ['Hexagon', 'H']], 'S')
dual.pack(side=TOP, pady=10)
dual.config(relief=GROOVE, bd=2)

rgb = CheckBar(panel, 'Shade color (add): ',
                 ['red', 'green', 'blue'])
rgb.pack(side=TOP)

# what we can do
actions = ButtonBar(win, [['Render', show_pic],
                          ['Print', draw_pic],
                          ['Quit', win.quit ]])
actions.pack(side=TOP, pady=10, padx=5, expand=YES)

filevars = EntryBar(panel,
                    [['Filename', 'pic-.tex'],
                     ['Scale size', 2]])
filevars.pack(side=TOP)

mainloop()
