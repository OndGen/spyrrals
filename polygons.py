#!/usr/bin/python
##
##  polygARns.py  by  AR & RY:  this version 1/8/14
##
#  generate Ond spirals interactively, and save to tikz/LaTeX
#
from __future__ import print_function
from math import pi, cos, sin, sqrt, ceil
from operator import add
from Tkinter import *
import itertools
flatten = lambda lst: list(itertools.chain.from_iterable(lst))

def  make_polygon(side_length,num_sides):    
  dirs = [[cos(2*pi*(j+1)/num_sides),
           sin(2*pi*(j+1)/num_sides)]
              for j in range(num_sides-2)]
  # origin
  pos = []
  for k in range(side_length):
    x = [k,0]
    pos.append(x)
    for j in range(num_sides-2):
      for l in range(k):
        x = map(add, x, dirs[j])
        pos.append(x)
  return(pos)

# count of polygonal number: known a priori!
testfunc = {
  # n-1 for n in hexagon as we adjusted for origin !
  'H': lambda n: 3*(n-1)**2 + 3*(n-1) + 1,
  'T': lambda n: n*(n+1)/2,
  'S': lambda n: n**2,
  'P': lambda n: n[0]*(2+(n[1]-2)*(n[0]-1))/2
}

def get_max_poly(coords):
  # calculate picture size in absolute coords
  xlist = [coords[j][0] for j in range(len(coords))]
  xrange = max(xlist) - min(xlist)
  ymax = max([coords[j][1] for j in range(len(coords))])
  return([(max(xlist)+min(xlist))/2, 
          ymax/2,
          0.5 + max([xrange, ymax])/2])

# boxes and shading

boxctr = {'S': [0.5,0.5],
          'T': [0.5,sqrt(3)/6],
          'H': [0.5,sqrt(3)/2]}

def get_poly_boxes(num_sides,side_length,adjust):
  basebox = make_polygon(2,num_sides)
  basebox.append(basebox[0])
  allboxes = []
  # boxes are scaled and shifted as needed
  for j in range(side_length-1):
    allboxes.append([ [ (j+1)*basebox[k][0]-adjust[0] ,
                        (j+1)*basebox[k][1]-adjust[1] ]
                      for k in range(1+num_sides) ])
  return(allboxes)

def shade( coords, k_ond, xymax, style, FH ):
  for j in range(len(coords)):
    # scale the rgb values to get nice pictures
    rgbvals = [255-(j%k_ond)*255/k_ond*(1-int(rgb.state()[m]))
               for m in range(3)]
    # different routines for window and file
    {'pic':showcirc,
     'tex':drawcirc}[style](coords[j], 0.5, xymax, rgbvals, FH )

def save_data(FH):
  # write parameters to file so we can reproduce!
  print(''.join(['\\polydata=',
                 str(nkvars.state()),# shape.var.get(),
                 spiral.var.get(),# dual.var.get(),
                 ''.join(map(str, boxes.state())),
                 ''.join(map(str, rgb.state())),
                 str(filevars.state())]), file=FH)

# Tkinter routines for making spirals in the window
def show_pic():
  pic.delete("all") # initialize
  num_sides = int(nkvars.state()[0])
  side_length = int(nkvars.state()[1])
  # number from formula
  num = testfunc['P']([side_length,num_sides])
  k_mod = int(nkvars.state()[2])
  opt = spiral.var.get()
  coords = make_polygon(side_length,num_sides)
  adjust = get_max_poly(coords)
  coords = [[coords[j][0]-adjust[0],
             coords[j][1]-adjust[1]]
            for j in range(len(coords))]
  xymax = adjust[2]
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
    allboxes = get_poly_boxes(num_sides,side_length,adjust)
    if show_boxes[0]:
      for j in range(len(allboxes)):
        showline(allboxes[j], xymax, 2, 'yellow')
    if show_boxes[1]:
      for j in range(1,len(allboxes)):
        if not testfunc['P']([j,num_sides]) % k_mod:
          showline(allboxes[j-2], xymax, 3, 'darkorange')

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

def showcirc(ctr, rad, xymax, rgbvals, FH ):
  corners = [[ctr[0]+rad*k,ctr[1]+rad*k] for k in [-1,1]]
  xy = flatten( shiftscale( corners, xymax ))
  col = '#%02x%02x%02x' % ( rgbvals[0], rgbvals[1], rgbvals[2] )
  pic.create_oval( xy, fill=col, outline=col)


# tikz routines printed to file
def draw_pic():
  FH = open(filevars.state()[0], 'a')
  save_data(FH)
  print('\\begin{tikzpicture}', file=FH)
  num_sides = int(nkvars.state()[0])
  side_length = int(nkvars.state()[1])
  # number from formula
  num = testfunc['P']([side_length,num_sides])
  k_mod = int(nkvars.state()[2])
  opt = spiral.var.get()
  coords = make_polygon(side_length,num_sides)
  adjust = get_max_poly(coords)
  coords = [[coords[j][0]-adjust[0],
             coords[j][1]-adjust[1]]
            for j in range(len(coords))]
  xymax = adjust[2]
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
    allboxes = get_poly_boxes(num_sides,side_length,adjust)
    if show_boxes[0]:
      for j in range(len(allboxes)):
        drawline(allboxes[j], xymax, 2, 'yellow!90!black', FH )
    if show_boxes[1]:
      if opt == 'G':
        color, wid = 'yellow', 1
      else:
        color, wid = 'orange!90!black', 3
      for j in range(1,len(allboxes)):
        if not testfunc['P']([j,num_sides]) % k_mod:
          drawline(allboxes[j-2], xymax, wid, color, FH )
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

def drawcirc(ctr, rad, xymax, col, FH ):
  print("\\fill[col={%d,%d,%d}] (%f,%f) circle (%f);" % ( 
    col[0], col[1], col[2], ctr[0], ctr[1], rad ), file=FH)

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

nkvars = EntryBar(panel,
                  [['# sides', 5],
                   ['side length', 6],
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
