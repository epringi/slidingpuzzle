#!/usr/bin/env python3

import signal, sys, time, os, secrets, shutil, glob, random, re, select, curses

# There's an ESC key delay by default, so let's put that to 0
os.environ.setdefault('ESCDELAY', '0')
# Remove the pygame promotional text when the library is loaded...
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# define the default (min) board size
size=4

# instead of kacking out, check the terminal size, +2 for the board frame on each axis
if shutil.get_terminal_size()[0]<((size*20)+2) or shutil.get_terminal_size()[1]<((size*7)+2):
  print("AW, terminal must be at least "+str((size*20)+2)+"x"+str((size*7)+2)+" to play the slidy puzzle. :(")
  exit()

# don't kack, be polite
'''try:
  import pygame
except:
  print("You'll need pygame module installed (https://www.pygame.org):")
  print("pip install pygame")
  print("")
  print("If you don't have Python3 pip installed, install it using this command: sudo apt install python3-pip")
  curses.nocbreak()
  stdscr.keypad(False)
  curses.echo()
  curses.endwin()
  exit()'''


# curses init stuff
screen=curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
curses.use_default_colors()
curses.curs_set(0)
curses.mousemask(1)
screen.keypad(True)

# sigint is ok
def signal_handler(sig, frame):
  curses.nocbreak()
  screen.keypad(False)
  curses.echo()
  curses.endwin()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# import the completion fanfare (TBD)
'''from pygame import mixer
mixer.init()
mixer.music.load("")'''

# in case we run if from elsewhere, make sure we know where this is in the fs
wd=os.path.dirname(os.path.realpath(__file__))

# populate available colours
for i in range(0, curses.COLORS):
  curses.init_pair(i + 1, i, -1)

# define 8-bit and 4-bit.  This is clunky and could be a dict sectioned by number of colours: colours[curses.COLOURS][colour] TODO
# To add colour to text in a .pim, add the colour name (such as lr for light red)
# between squirrely braces like so: {lr}
colours={
  "lr": "160",
  "dr": "52",
  "dy": "214",
  "or": "214",
  "br": "130",
  "ly": "226",
  "lg": "34",
  "dg": "22",
  "ol": "65",
  "lc": "159",
  "dc": "6",
  "pb": "39",
  "lb": "21",
  "db": "19",
  "lm": "163",
  "dm": "90",
  "pi": "162",
  "pe": "203",
  "sa": "216",
  "be": "230",
  "lw": "15",
  "dw": "252",
  "gr": "8",
  "si": "248"
}

if curses.COLORS==8:
  colours={
    "lr": "10",
    "dr": "2",
    "dy": "4",
    "or": "4",
    "br": "4",
    "ly": "12",
    "lg": "11",
    "dg": "3",
    "ol": "3",
    "lc": "15",
    "dc": "7",
    "pb": "15",
    "lb": "13",
    "db": "5",
    "lm": "14",
    "dm": "6",
    "pi": "14",
    "pe": "14",
    "sa": "12",
    "be": "0",
    "lw": "16",
    "dw": "8",
    "gr": "9",
    "si": "0"
  }


# a default image that works for all board sizes, just in case someone accidentally deletes all .pim files
default_image=[
"..................................................................I.......................A.........AAAAAAAAAAAAAAAAAAA.",
"..................................................................O......................A.A.........A...............A..",
"..................................................................I.....................A...A.........A.............A...",
"OIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOIOAOIOIOAOIOIOIOIOAOIOIOIOIOIOAOIOI",
"........$$$$$$$$$$$$$$$$$$$$$$$$$.................................I...................A.......A.........A.........A.....",
"........$$$$$$$$$$$$$$$$$$$$$$$$$.........@@@@@...................O..................A.........A.........A.......A......",
"........$$$.............................@@@@@@@@@.................I.................A...........A.........A.....A.......",
"........$$$...........................@@@@@@@@@@@@@...............O................A.............A.........A...A........",
"........$$$...........................@@@@@@@@@@@@@...............I...............A...............A.........A.A.........",
"........$$$...........................@@@@@@@@@@@@@...............O..............AAAAAAAAAAAAAAAAAAA.........A..........",
"........$$$.............................@@@@@@@@@.................I.....................................................",
"........$$$...............................@@@@@...................O......X..............................................",
"........$$$.......................................................I......X..............................................",
"........$$$.......................................................O......X..............................................",
"........$$$.......................................................I......X..............................................",
"........$$$..........................................V............O......X..............................................",
"........$$$.........................................VV............I......X.............DDDDDD.................D.........",
"...................................................VVV............O......X.............DDDDDD.................D.........",
"..................................................VVVV............I.....X..............DDDDDD.................D.........",
"........MMMMMMMMMMMMMMMMM........................VVVVV............O....X...............DDDDDD.................D.........",
"........M...............M.......................VVVVVV............I...X........DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD.........",
"........M...............M......................VVVVVVV............O..X.................DDDDDD.................D.........",
"........M...............M.....................VVVVVVVV............I.X..................DDDDDD.................D.........",
"........M...............M....................VVVVVVVVV............OX...................DDDDDD.................D.........",
"........M...............M...................VVVVVVVVVV............X....................DDDDDD.................D.........",
"........M...............M..................VVVVVVVVVVV...........XO....................DDDDDD.................D.........",
"........MMMMMMMMMMMMMMMMM.................VVVVVVVVVVVV..........X.I.....................................................",
".........................................VVVVVVVVVVVVV.........X..O.....................................................",
"........................................VVVVVVVVVVVVVV........X...I.....................................................",
".............WWWWWWWWWWWW..............VVVVVVVVVVVVVVV.......X....O....................KKKKKKKKKKKKKKK..................",
".............WWWWWWWWWWWW.............VVVVVVVVVVVVVVVV......X.....I....................KKKKKK........KK.................",
".............WWWWWWWWWWWW............VVVVVVVVVVVVVVVVV.....X......O....................KKKKKK.........KK................",
".................WWWW...............VVVVVVVVVVVVVVVVVV....X.......I....................KKKKKK..........KK...............",
".................WWWW..............VVVVVVVVVVVVVVVVVVV.....X......O....................KKKKKK...........KK..............",
".................WWWW.............VVVVVVVVVVVVVVVVVVVV......X.....I....................KKKKKK............KK.............",
".................WWWW............VVVVVVVVVVVVVVVVVVVVV.......X....O....................KKKKKK.............KK............",
".................WWWW...........VVVVVVVVVVVVVVVVVVVVVV........X...I....................KKKKKK..............KK...........",
".................WWWW..........VVVVVVVVVVVVVVVVVVVVVVV.........X..O....................KKKKKK...............KK..........",
".................WWWW.........VVVVVVVVVVVVVVVVVVVVVVVV..........X.I............KKKKKKKKKKKKKK................KK.........",
".............................VVVVVVVVVVVVVVVVVVVVVVVVV...........XO.....................................................",
"............................VVVVVVVVVVVVVVVVVVVVVVVVVV............X.....................................................",
"...........................VVVVVVVVVVVVVVVVVVVVVVVVVVV............OX....................................................",
]

image=[]


# this is what empty looks like! defining the empty segment
empty=[
  "                   ",
  "                   ",
  "                   ",
  "                   ",
  "                   ",
  "                   ",
  "___________________"
]

# by default the empty segment and selected segment are the last segment on the min board size
empty_seg=size*size
selected_seg=size*size

# define the max amount of segments
segments=[]
seg_img=[]
orig_img=[]
for idx in range(6*6+1):
  segments.append([])
  seg_img.append([])
  orig_img.append([])

# we are in init stage
init=1

# we start off not being in a window
inwindow=0

# show the available colours and colour help
def colour_palette():
  posy=int(curses.LINES/2)-int(len(colours)/4)+5
  posx=int(curses.COLS/2)-14

  screen.clear()
  screen.addstr(posy-13, posx, "|-----------------------------------------|")
  screen.addstr(posy-12, posx, "|                                         |")
  screen.addstr(posy-11, posx, "|  To add colour to a .pim file, add the  |")
  screen.addstr(posy-10, posx, "|  colour name (such as lr for light red) |")
  screen.addstr(posy-9, posx, "|  between squirrely braces before the    |")
  screen.addstr(posy-8, posx, "|  characters you want coloured, like so: |")
  screen.addstr(posy-7, posx, "|  {lr}$$$ {lb}@@@                        |")
  screen.addstr(posy-6, posx, "|                                         |")
  screen.addstr(posy-5, posx, "|  If using a colour terminal, colours    |")
  screen.addstr(posy-4, posx, "|  will look duplicated.                  |")
  screen.addstr(posy-3, posx, "|                                         |")
  screen.addstr(posy-2, posx, "|  Available colours:                     |")
  screen.addstr(posy-1, posx, "|                                         |")

  for idx, colour in enumerate(colours):
    if curses.COLORS==8 and int(colours[colour])>7:
      colour2=( (int(colours[colour])-8) *256) +2097152
    elif curses.COLORS==8:
      colour2=int(colours[colour])*256
    else:
      colour2=(int(colours[colour])+1)*256
    if (idx%2)==0:
      screen.addstr(posy+int(idx/2), posx, "|  ")
    else:
      screen.addstr(posy+int(idx/2), posx+16, "     ")
    screen.addstr("### = "+colour, colour2)
    screen.addstr("             |")
    screen.refresh()
  screen.addstr(posy+int(idx/2)+1, posx, "|                                         |")
  screen.addstr(posy+int(idx/2)+2, posx, "|-----------------------------------------|")
  screen.refresh()
  screen.getch()
  load_img()


def clicked_segment():
  global segments
  _, mx, my, _, _=curses.getmouse()

  for idx, seg in enumerate(segments):
    if 'y' in seg and my in range(seg['y'], seg['y']+7) and mx in range(seg['x'], seg['x']+20):
      return idx


# set the position of the segments on the screen, centered, based off available space and defined range
# rest should be calculations based on range TODO
def set_segments():
  global size
  global segments

  yspot=int((curses.LINES-(size*7))/2)
  xspot=int((curses.COLS-(size*20))/2)

  for idx in range(1, (size*size)+1):
    if (idx%size)==0:
      segments[idx]={
        'y': yspot+((int(idx/size)-1)*7),
        'x': xspot+((size-1)*20)
      }
    else:
      segments[idx]={
        'y': yspot+((int(idx/size))*7),
        'x': xspot+((idx-(int(idx/size)*size)-1)*20)
      }


# break the image up into segments
def segment_img(image):
  global size
  global empty
  yrange=size*7
  xrange=size*20

  # define the size of the temp img
  timg=[]
  for idx in range(0,(size*size)+1):
    timg.append([])

  for idx, line in enumerate(image):
    # determine segment index ranges based on the board size
    ends=[]
    for end in range(1,size+1):
      ends.append(int(xrange/size)*end)
    begins=[]
    for begin in range(0,size):
      begins.append(int(xrange/size)*begin)

    # determine which segments this line is going into based on the current index and board size
    segs=[]
    for seg in range(1,size+1):
      segs.append((int(idx/7)*size)+seg)

    for sidx, seg in enumerate(segs):
      # This is complicated because of colour integration...
      # we want to make sure the line we're inserting has only 20 REAL characters (not colours),
      # and we want to preserve the colours, and we look back into the same line of the previous
      # segment on the x axis to grab the last colour

      # while we don't have only 20 REAL characters, or we have captured an incomplete colour code in the line
      while (len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))!=20 and len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))!=False) \
      or line[begins[sidx]:ends[sidx]].count("{") > line[begins[sidx]:ends[sidx]].count("}"):
        # if we've captured an incomplete colour code in the line, increase the index range by 1 and adjust subsequent segment index ranges
        if line[begins[sidx]:ends[sidx]].count("{") > line[begins[sidx]:ends[sidx]].count("}"):
          segc=sidx
          while segc<size:
            if segc!=sidx:
              begins[segc]=begins[segc]+1
            ends[segc]=ends[segc]+1
            segc=segc+1
        # if we have too many real characters, decrease index range by 1 and adjust subsequent segment index ranges
        elif len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))>20:
          segc=sidx
          while segc<size:
            if segc!=sidx:
              begins[segc]=begins[segc]-1
            ends[segc]=ends[segc]-1
            segc=segc-1
        # if we don't have enough real characters, increase the index range by 1 and adjust subsequent segment index ranges
        elif len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))<20:
          segc=sidx
          while segc<size:
            if segc!=sidx:
              begins[segc]=begins[segc]+1
            ends[segc]=ends[segc]+1
            segc=segc+1

      # include the last colour code found on this line in the previous segment
      pcolour=""
      if sidx>0 and str(timg[segs[sidx-1]][idx-(int(idx/7)*7)]).rfind("{") > -1:
        pcolour=timg[segs[sidx-1]][idx-(int(idx/7)*7)][str(timg[segs[sidx-1]][idx-(int(idx/7)*7)]).rfind("{"):str(timg[segs[sidx-1]][idx-(int(idx/7)*7)]).rfind("{")+4]
      elif sidx>1 and str(timg[segs[sidx-2]][idx-(int(idx/7)*7)]).rfind("{") > -1:
        pcolour=timg[segs[sidx-2]][idx-(int(idx/7)*7)][str(timg[segs[sidx-2]][idx-(int(idx/7)*7)]).rfind("{"):str(timg[segs[sidx-2]][idx-(int(idx/7)*7)]).rfind("{")+4]
      elif sidx>2 and str(timg[segs[sidx-3]][idx-(int(idx/7)*7)]).rfind("{") > -1:
        pcolour=timg[segs[sidx-3]][idx-(int(idx/7)*7)][str(timg[segs[sidx-3]][idx-(int(idx/7)*7)]).rfind("{"):str(timg[segs[sidx-3]][idx-(int(idx/7)*7)]).rfind("{")+4]
      elif sidx>3 and str(timg[segs[sidx-4]][idx-(int(idx/7)*7)]).rfind("{") > -1:
        pcolour=timg[segs[sidx-4]][idx-(int(idx/7)*7)][str(timg[segs[sidx-4]][idx-(int(idx/7)*7)]).rfind("{"):str(timg[segs[sidx-4]][idx-(int(idx/7)*7)]).rfind("{")+4]

      # prefix with the previous colour we found and add the line to the segment
      timg[seg].append(str(pcolour)+line[begins[sidx]:ends[sidx]-1])

  for idx in range(1, (size*size)+1):
    timg[idx][6]="{dw}___________________"

  # empty out the last segment because it will be the empty space
  timg[size*size]=empty

  return timg


# draw the whole board, including the segments
def draw_board():
  global init
  global seg_img
  global segments
  global size
  yrange=size*7
  xrange=size*20

  screen.clear()

  # add the board border
  for posy in range(yrange+1):
    screen.addstr(posy+segments[1]['y']-1, segments[1]['x']-1, "|")
  for posx in range(xrange+1):
    screen.addstr(segments[1]['y']-1, posx+segments[1]['x']-1, "_")

  for seg in range(1,(size*size)+1):
    print_segment(seg_img, int(seg))
    # dramatic board draw...
    if init:
      screen.refresh()
      time.sleep(.15)
    seg=seg+1

  screen.refresh()
  init=0

# mark a segment as active by drawing a border around it
def select_seg(seg):
  global selected_seg
  global size
  yrange=size*7
  xrange=size*20

  colour=curses.color_pair(0)

  # get the starting coords of this segment
  posy=segments[seg]['y']
  posx=segments[seg]['x']

  for posi in range(0,int(yrange/size)):
    screen.addstr(posy+posi, posx-1, "=", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+posi, posx-1+int(xrange/size), "=", curses.color_pair(8)|curses.A_BOLD)
  if posy is segments[1]['y']:
    screen.addstr(posy-1, posx-1, "".ljust(21, "="), curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+int(yrange/size)-1, posx-1, "".ljust(21, "="), curses.color_pair(8)|curses.A_BOLD)
  else:
    screen.addstr(posy-1, posx-1, "".ljust(21, "="), curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy-1+int(yrange/size), posx, "".ljust(20, "="), curses.color_pair(8)|curses.A_BOLD)

  selected_seg=seg


# move a segment into the empty spot
def seg_move():
  global empty_seg
  global selected_seg
  global seg_img
  global chars
  global size

  # check if the movement is allowed, if the segment we're trying to move is adjacent to the empty segment
  if selected_seg == empty_seg+size or selected_seg == empty_seg-size \
  or (selected_seg == empty_seg+1 and (empty_seg%size)!=0) \
  or (selected_seg == empty_seg-1 and (selected_seg%size)!=0):
    seg_img[empty_seg]=seg_img[selected_seg]
    seg_img[selected_seg]=empty
    print_segment(seg_img, empty_seg)
    print_segment(seg_img, selected_seg)
    screen.refresh()
    empty_seg=selected_seg

  # draw the selection box
  select_seg(selected_seg)


# shuffle the segments
def shuffle_img():
  global empty_seg
  global seg_img

  for idx in range(500*size):
    segnum=secrets.randbelow(size*size)+1
    select_seg(segnum)
    # seg_move() has a sanity check so we don't need it here
    seg_move()


# Reusable code for printing a line
def print_line(fullline):
  global screen
  global colours

  colour=curses.color_pair(0)

  # split the line up into characters and colours
  splitline=re.split('\{|}+', str(fullline))

  for pidx, piece in enumerate(splitline):
    # if the pidx is not odd, then the piece isn't a colour: if the line starts with a colour,
    # the split adds an empty string before it, so colours are always odd
    if piece in colours and (pidx%2)!=0:
      if curses.COLORS==8 and int(colours[piece])>7:
        colour=( (int(colours[piece])-8) *256) +2097152
      elif curses.COLORS==8:
        colour=int(colours[piece])*256
      else:
        colour=(int(colours[piece])+1)*256
    else:
      screen.addstr(piece, colour)
      screen.refresh()


# print one segment
def print_segment(seg_img, segnum):
  global segments

  # get the starting coords of this segment
  posy=segments[segnum]['y']
  posx=segments[segnum]['x']

  for idx, fullline in enumerate(seg_img[segnum]):
    screen.addstr(posy, posx, "")
    print_line(fullline)
    screen.addstr("|")
    posy=posy+1


# show the original image
def show_img():
  global image
  global size
  xrange=size*20

  screen.clear()
  posy=segments[1]['y']
  posx=segments[1]['x']-1
  screen.addstr(posy-1, posx, "".ljust(xrange+1, "_"))

  for idx, fullline in enumerate(image):
    screen.addstr(posy, posx, "|")
    print_line(fullline)
    screen.addstr(posy, posx+xrange, "|")
    screen.refresh()
    posy=posy+1
  screen.addstr(posy-1, posx, "|".ljust(xrange, "_")+"|")
  screen.refresh()


# HALP.  Info
def help():
  global segments
  global size

  posy=segments[1]['y']+int((size*7)/2)-8
  posx=segments[1]['x']+int((size*20)/2)-26

  screen.addstr(posy,posx,"                                                     ")
  screen.addstr(posy+1,posx," ___________________________________________________ ")
  screen.addstr(posy+2,posx," |                                                 | ")
  screen.addstr(posy+3,posx," |     Use arrow keys to move around the board.    | ")
  screen.addstr(posy+4,posx," |      Only pieces adjacent to the empty spot     | ")
  screen.addstr(posy+5,posx," |          can slide into the empty spot.         | ")
  screen.addstr(posy+6,posx," |                                                 | ")
  screen.addstr(posy+7,posx," |   [SPACE] = slide selected piece                | ")
  screen.addstr(posy+8,posx," |             into the empty spot                 | ")
  screen.addstr(posy+9,posx," |   s       = show original image                 | ")
  screen.addstr(posy+10,posx," |   [ESC]   = return to puzzle                    | ")
  screen.addstr(posy+11,posx," |   r       = reshuffle board                     | ")
  screen.addstr(posy+12,posx," |   l       = load new image                      | ")
  screen.addstr(posy+13,posx," |   h       = this help screen                    | ")
  screen.addstr(posy+14,posx," |   q       = quit                                | ")
  screen.addstr(posy+15,posx," |                                                 | ")
  screen.addstr(posy+16,posx," |_________________________________________________| ")
  screen.addstr(posy+17,posx,"                                                     ")
  screen.refresh()


# get the max x len of an image (am I still using this?)
def get_max_len(thing):
  max_len=0
  for idx, item in enumerate(thing):
    if idx == len(thing)-1:
      break;
    if len(item) > max_len:
      max_len=len(item)
  return max_len


# load a new image
def load_img():
  global image
  global seg_img
  global orig_img
  global empty_seg
  global inwindow
  global chars
  global size
  global default_image

  # preserve the board size in case the user backs out
  tsize=size
  size=0

  xrange=0
  yrange=0

  inwindow=0

  # the choose a difficulty / size dialog
  difficulty=[
    "______________________________________________",
    "|                                            |",
    "|  Please choose a difficulty / board size:  |",
    "|                                            |",
    "|  4: Easy (4x4)                             |"
  ]

  if curses.COLS<((5*20)+2) or curses.LINES<((5*7)+2):
    difficulty.append("|  5: Medium (5x5) [n/a: screen too small]   |")
  else:
    difficulty.append("|  5: Medium (5x5)                           |")

  if curses.COLS<((6*20)+2) or curses.LINES<((6*7)+2):
    difficulty.append("|  6: Hard (6x6) [n/a: screen too small]     |")
  else:
    difficulty.append("|  6: Hard (6x6)                             |")

  difficulty.append("|                                            |")
  difficulty.append("|____________________________________________|")

  chars=0
  while 0==0:
    screen.clear()

    if size > 0:
      # the choose an image window
      window=[
        "_________________________________________________",
        "|                                               |",
        "|  To choose the difficulty / board size again  |",
        "|  press 'd'.                                   |",
        "|                                               |",
        "|  You can create your own ANSI/ASCII art as    |",
        "|  well.  To see information about using        |",
        "|  colours, press 'c'.                          |",
        "|                                               |",
        "|  The art must be in a file with extension     |",
        "|  .pim (PuzzleIMage) in the images directory   |",
        "|  and be "+str(xrange).rjust(3)+"x"+str(yrange)+" characters.                    |",
        "|  The file must also be postfixed with the     |",
        "|  intended size: myimg"+str(size)+"x"+str(size)+".pim                  |",
        "|  Where "+str(size)+"x"+str(size)+" indicates the image is "+str(xrange).rjust(3)+"x"+str(yrange)+".     |",
        "|                                               |",
        "|  Note: the lower right segment will           |",
        "|        be removed in the puzzle               |",
        "|                                               |",
        "|   Available Images:                           |",
        "|                                               |"
      ]

      imgs=glob.glob(wd+'/images/*'+str(size)+'x'+str(size)+'.pim')
      imgs=sorted(imgs)
      for idx, img in enumerate(imgs):
        imgs[idx]=img[:-7]
      imgs.insert(0, wd+"/images/Default")

      for idx in range(int(len(imgs)/2)):
        line="| "+str(idx).rjust(2)+": "+os.path.relpath(imgs[idx], wd+"/images/").ljust(18)+" "
        if idx+int(len(imgs)/2)<len(imgs):
          line=line+str(idx+int(len(imgs)/2)).rjust(2)+": "+os.path.relpath(imgs[idx+int(len(imgs)/2)], wd+"/images/").ljust(18)+" |"
        else:
          line=line+" ".ljust(22)+" |"
        window.append(line)
        if idx==5:
          break

      if len(imgs) > 0:
        window.append("|                                               |")
        window.append("|  Please choose an image for the puzzle (0-"+str(len(imgs)-1).rjust(2)+") |")
        window.append("|_______________________________________________|")

      else:
        window.append("|                                               |")
        window.append("|  Please choose an image for the puzzle (0-0)  |")
        window.append("|_______________________________________________|")

      posx=int(curses.COLS/2)-int(len(window[0])/2)
      posy=int(curses.LINES/2)-int(len(window)/2)

      for idx in range(len(window)):
        screen.addstr(posy+idx, posx, window[idx])

    else:
      posx=int(curses.COLS/2)-int(len(difficulty[0])/2)
      posy=int(curses.LINES/2)-int(len(difficulty)/2)

      for idx in range(len(difficulty)):
        screen.addstr(posy+idx, posx, difficulty[idx])

    chars=screen.getch()

    # c cor colours
    if chars==99 or chars==67:
      colour_palette()

    # d for difficulty (choose difficulty)
    if chars==100 or chars==68:
      size=0

    # l or esc to leave if we aren't in init mode
    if (chars==108 or chars==76 or chars==27) and init==0:
      size=tsize
      set_segments()
      draw_board()
      select_seg(selected_seg)
      break

    # q to quit
    if chars==113 or chars==81:
      curses.nocbreak()
      screen.keypad(False)
      curses.echo()
      curses.endwin()
      exit()

    # if numbers chosen and size is 0 then it's choose a size
    if chars>=52 and chars<=54 and size==0:
      # but not if the screen is too small!
      if ((curses.COLS<((5*20)+2) or curses.LINES<((5*7)+2)) and chars==53) \
      or ((curses.COLS<((6*20)+2) or curses.LINES<((6*7)+2)) and chars==54):
        continue

      size=int(chr(chars))
      chars=0
      xrange=size*20
      yrange=size*7

    # choose your image
    if chars>=48 and chars<=57 and size > 0:
      if int(chr(chars))>=0 and int(chr(chars))<len(imgs):
        image=[]
        # 0 is the hard-coded default
        if int(chr(chars))>0:
          f=open(imgs[int(chr(chars))]+str(size)+"x"+str(size)+".pim", 'r')
          image=f.readlines()
        else:
          for ln in default_image:
            image.append(ln)

        # pad missing lines if too short, otherwise del excess
        if len(image)<yrange:
          for idx in range(yrange-len(image)):
            image.append("".ljust(xrange))
        else:
          del image[yrange:]

        # pad missing chars if too short, otherwise del excess
        for idx in range(yrange):
          res=image[idx].count("{")*4
          if len(image[idx])-res<xrange:
            image[idx]=image[idx][:-1]
            image[idx]=image[idx].ljust(xrange+res)
          if len(image[idx])-res>xrange:
            image[idx]=image[idx][:xrange+res]

        set_segments()

        show_img()

        screen.addstr(int(curses.LINES/2)-2, int(curses.COLS/2)-10, "___________________", curses.color_pair(3)|curses.A_BOLD)
        screen.addstr(int(curses.LINES/2)-1, int(curses.COLS/2)-10, "|                 |", curses.color_pair(3)|curses.A_BOLD)
        screen.addstr(int(curses.LINES/2), int(curses.COLS/2)-10, "| Image OK? (y/n) |", curses.color_pair(3)|curses.A_BOLD)
        screen.addstr(int(curses.LINES/2)+1, int(curses.COLS/2)-10, "|_________________|", curses.color_pair(3)|curses.A_BOLD)

        # y or n loop
        while chars!=110 and chars!=78 and chars!=89 and chars!=121:
          chars=screen.getch()

        # If n was chosen, rinse and repeat
        if chars==110 or chars==78:
          continue;

        else:
          empty_seg=size*size
          seg_img=segment_img(image)
          orig_img=segment_img(image)
          shuffle_img()
          draw_board()
          select_seg(empty_seg)
          break;


# yay you finished the puzzle!
def fanfare():
  #mixer.music.play()
  global size
  xrange=size*20
  yrange=size*7

  # the rainbow we shall be using
  colours=[10, 6, 14, 13, 7, 15, 3, 11, 12, 4, 2]

  # accidentally created a cool pattern so random decides if we use that or rainbow
  pattern=1
  if ((secrets.randbelow(size)+1)%2)==0:
    pattern=0

  while True:
    # cycle the colours so it looks trippy
    colours.append(colours.pop(0))

    screen.addstr(segments[1]['y']-1, segments[1]['x']-1, "".ljust(xrange+1, "_"), curses.color_pair(colours[10]))

    for segnum in range(1,(size*size)+1):
      posy=segments[segnum]['y']
      posx=segments[segnum]['x']-1
      for idx, fullline in enumerate(seg_img[segnum]):
        fullline=re.sub('\{..}+', '', str(fullline))
        colour=idx

        # this one is cool
        if pattern==0:
          adjust=int(yrange/size)*int(idx/size)
        # this one is just a rainbow
        else:
          adjust=(int(yrange/size)*(int((segnum-1)/size)+1)-7)

        colour=colour+adjust

        # since we only have 11 colours
        while colour>10:
          colour=colour-11

        if curses.COLORS==8 and int(colours[colour])>7:
          colour=curses.color_pair(colours[colour]-8)|curses.A_BOLD
        elif curses.COLORS==8:
          colour=curses.color_pair(colours[colour])
        else:
          colour=curses.color_pair(colours[colour])

        screen.addstr(posy, posx, "|"+fullline+"|", colour)
        posy=posy+1

    posy=segments[1]['y']+int(yrange/2)-4
    posx=segments[1]['x']+int(xrange/2)-19

    screen.addstr(posy, posx, "______________________________________", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+1, posx, "|                                    |", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+2, posx, "|                                    |", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+3, posx, "|           You finished it!         |", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+4, posx, "|                                    |", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+5, posx, "|                 Yay!!              |", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+6, posx, "|                                    |", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+7, posx, "|                                    |", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+8, posx, "|____________________________________|", curses.color_pair(8)|curses.A_BOLD)

    screen.refresh()
    time.sleep(.2)

    # any key stops the insanity
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
      break


load_img()
help()
inwindow=1
chars=0

# main loop
while 0==0:
  chars=screen.getch()

  # q for quit
  if chars==113 or chars==81:
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()
    exit()

  # if in a window, only thing that can be done is exit
  if chars!=115 and chars!=835 and chars!=113 and chars!=81 and chars!=104 and chars!=72 and chars!=27 and chars!=curses.KEY_MOUSE and inwindow:
    continue

  # s or h if in window, or esc to redraw board and exit window
  if (chars==115 or chars==835 or chars==104 or chars==72 or chars==27 or chars==curses.KEY_MOUSE) and inwindow:
    draw_board()
    select_seg(selected_seg)
    inwindow=0
    continue

  # navigating around (arrow keys)
  if chars==258: #down
    draw_board()
    if (selected_seg+size) > (size*size):
      select_seg(selected_seg-(size*(size-1)))
    else:
      select_seg(selected_seg+size)

  if chars==259: #up
    draw_board()
    if (selected_seg-size)<1:
      select_seg(selected_seg+(size*(size-1)))
    else:
      select_seg(selected_seg-size)

  if chars==260: #left
    draw_board()
    if (selected_seg-1)<1:
      select_seg(selected_seg+size)
    elif ((selected_seg-1)%size)==0:
      select_seg(selected_seg+size-1)
    else:
      select_seg(selected_seg-1)

  if chars==261: #right
    draw_board()
    if (selected_seg+1) > (size*size):
      select_seg((size*size)-size+1)
    elif (selected_seg%size)==0:
      select_seg(selected_seg-size+1)
    else:
      select_seg(selected_seg+1)

  if chars==curses.KEY_MOUSE:
    draw_board()
    selected_seg=clicked_segment()
    seg_move()
    if seg_img == orig_img:
      inwindow=1
      fanfare()

  # enter or spacebar moves the segment
  if chars==32 or chars==10:
    draw_board()
    seg_move()
    if seg_img == orig_img:
      inwindow=1
      fanfare()

  # h for help
  if chars==104 or chars==72:
    inwindow=1
    help()

  # s for show original img
  if chars==115 or chars==835:
    inwindow=1
    show_img()

  # l for load new img
  if chars==108 or chars==76:
    chars=0
    load_img()

  # r for reshuffle img
  if chars==114 or chars==82:
    shuffle_img()
    draw_board()
    select_seg(25)

  screen.refresh()
  chars=0

curses.nocbreak()
screen.keypad(False)
curses.echo()
curses.endwin()
