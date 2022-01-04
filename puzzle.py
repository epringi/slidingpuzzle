#!/usr/bin/env python3

import signal, sys, time, os, secrets, shutil, glob, random, re, select, curses

# There's an ESC key delay by default, so let's put that to 0
os.environ.setdefault('ESCDELAY', '0')
# Remove the pygame promotional text when the library is loaded...
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# define the x and y range of the board
yrange=28
xrange=80

# instead of kacking out, check the terminal size, +2 for the board frame
if shutil.get_terminal_size()[0]<(xrange+2) or shutil.get_terminal_size()[1]<(yrange+2):
  print("AW, terminal must be at least "+str(xrange+2)+"x"+str(yrange+2)+" to play the slidy puzzle. :(")
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
screen.keypad(True)
curses.noecho()
curses.cbreak()
screen.keypad(True)
curses.start_color()
curses.use_default_colors()
curses.curs_set(0)
legend=curses.initscr()
legend.keypad(True)
#curses.COLORS=8

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

# in case we run if from elsewhere
wd=os.path.dirname(os.path.realpath(__file__))

# populate available colours
for i in range(0, curses.COLORS):
  curses.init_pair(i + 1, i, -1)

# define 24-bit and 8-bit.  This is clunky and could be a dict sectioned by number of colours: colours[curses.COLOURS][colour] TODO
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

# by default the empty segment and selected segment is 16
empty_seg=16
selected_seg=16

# define the size of segments and seg images
segments=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
seg_img=segments
orig_img=segments
#seg_img=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
#orig_img=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

# we are in init stage
init=1

# we start off not being in a window
inwindow=0

# show the available colours and colour help
def colour_palate():
  posy=int(curses.LINES/2)-int(len(colours)/4)+4
  posx=int(curses.COLS/2)-14

  screen.clear()
  screen.addstr(posy-9, posx, "|----------------------------|")
  screen.addstr(posy-8, posx, "| To add colour to text in a |")
  screen.addstr(posy-7, posx, "| .pim file, add the colour  |")
  screen.addstr(posy-6, posx, "| name (such as lr for light |")
  screen.addstr(posy-5, posx, "| red) between squirrely     |")
  screen.addstr(posy-4, posx, "| braces before the text to  |")
  screen.addstr(posy-3, posx, "| be coloured, like so: {lr} |")
  screen.addstr(posy-2, posx, "|                            |")
  screen.addstr(posy-2, posx, "| If using a 16-bit colour   |")
  screen.addstr(posy-2, posx, "| terminal, colours will     |")
  screen.addstr(posy-2, posx, "| look duplicated.           |")
  screen.addstr(posy-2, posx, "|                            |")
  screen.addstr(posy-1, posx, "| Available colours:         |")

  for idx, colour in enumerate(colours):
    if curses.COLORS==8 and int(colours[colour])>7:
      colour2=( (int(colours[colour])-8) *256) +2097152
    elif curses.COLORS==8:
      colour2=int(colours[colour])*256
    else:
      colour2=(int(colours[colour])+1)*256
    if (idx%2)==0:
      screen.addstr(posy+int(idx/2), posx, "| ")
    else:
      screen.addstr(posy+int(idx/2), posx+10, "          ")
    screen.addstr("### = "+colour, colour2)
    screen.addstr(" |")
    screen.refresh()
  screen.addstr(posy+int(idx/2)+1, posx, "|                            |")
  screen.addstr(posy+int(idx/2)+2, posx, "|----------------------------|")
  screen.refresh()
  chrr=screen.getch()
  load_img()

# set the position of the segments on the screen, centered, based off available space and defined range
# rest should be calculations based on range TODO
def set_segments():
  segments[1]={
    'y': int((curses.LINES-yrange)/2),
    'x': int((curses.COLS-xrange)/2)
  }
  segments[2]={
    'y': segments[1]['y'],
    'x': segments[1]['x']+20
  }
  segments[3]={
    'y': segments[1]['y'],
    'x': segments[1]['x']+40
  }
  segments[4]={
    'y': segments[1]['y'],
    'x': segments[1]['x']+60
  }
  segments[5]={
    'y': segments[1]['y']+7,
    'x': segments[1]['x']
  }
  segments[6]={
    'y': segments[1]['y']+7,
    'x': segments[1]['x']+20
  }
  segments[7]={
    'y': segments[1]['y']+7,
    'x': segments[1]['x']+40
  }
  segments[8]={
    'y': segments[1]['y']+7,
    'x': segments[1]['x']+60
  }
  segments[9]={
    'y': segments[1]['y']+14,
    'x': segments[1]['x']
  }
  segments[10]={
    'y': segments[1]['y']+14,
    'x': segments[1]['x']+20
  }
  segments[11]={
    'y': segments[1]['y']+14,
    'x': segments[1]['x']+40
  }
  segments[12]={
    'y': segments[1]['y']+14,
    'x': segments[1]['x']+60
  }
  segments[13]={
    'y': segments[1]['y']+21,
    'x': segments[1]['x']
  }
  segments[14]={
    'y': segments[1]['y']+21,
    'x': segments[1]['x']+20
  }
  segments[15]={
    'y': segments[1]['y']+21,
    'x': segments[1]['x']+40
  }
  segments[16]={
    'y': segments[1]['y']+21,
    'x': segments[1]['x']+60
  }


# break the image up into segments
def segment_img(image):
  global yrange
  global xrange
  global empty

  timg=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

  # This is complicated because of colour integration
  for idx, line in enumerate(image):
    # determine segment ranges based on the global x and y ranges
    ends=[int(xrange/4), (int(xrange/4)*2), (int(xrange/4)*3), xrange]
    begins=[0, int(xrange/4), int(xrange/4)*2, int(xrange/4)*3]
    # determine which segments this line is going into by calculation
    segs=[(int(idx/7)*4)+1, (int(idx/7)*4)+2, (int(idx/7)*4)+3, (int(idx/7)*4)+4]
    for sidx, seg in enumerate(segs):
      while (len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))!=20 and len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))!=False) or line[begins[sidx]:ends[sidx]].count("{") > line[begins[sidx]:ends[sidx]].count("}"):
        if line[begins[sidx]:ends[sidx]].count("{") > line[begins[sidx]:ends[sidx]].count("}"):
          segc=sidx
          while segc<4:
            if segc!=sidx:
              begins[segc]=begins[segc]+1
            ends[segc]=ends[segc]+1
            segc=segc+1
        elif len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))>20:
          segc=sidx
          while segc<4:
            if segc!=sidx:
              begins[segc]=begins[segc]-1
            ends[segc]=ends[segc]-1
            segc=segc-1
        elif len(re.sub('\{..}+', '', str(line[begins[sidx]:ends[sidx]])))<20:
          segc=sidx
          while segc<4:
            if segc!=sidx:
              begins[segc]=begins[segc]+1
            ends[segc]=ends[segc]+1
            segc=segc+1
      segc=sidx
      pcolour=""
      # adjust the end of the current segment and the beginning and end of the subsequent segments based on how many colour codes were found
      while segc<4:
        if segc!=sidx:
          begins[segc]=begins[segc]
        ends[segc]=ends[segc]
        segc=segc+1
      # include the last colour code found on this line, in a previous segment
      if sidx>0 and str(timg[segs[sidx-1]][idx-(int(idx/7)*7)]).rfind("{") > -1:
        pcolour=timg[segs[sidx-1]][idx-(int(idx/7)*7)][str(timg[segs[sidx-1]][idx-(int(idx/7)*7)]).rfind("{"):str(timg[segs[sidx-1]][idx-(int(idx/7)*7)]).rfind("{")+4]
      elif sidx>1 and str(timg[segs[sidx-2]][idx-(int(idx/7)*7)]).rfind("{") > -1:
        pcolour=timg[segs[sidx-2]][idx-(int(idx/7)*7)][str(timg[segs[sidx-2]][idx-(int(idx/7)*7)]).rfind("{"):str(timg[segs[sidx-2]][idx-(int(idx/7)*7)]).rfind("{")+4]
      elif sidx>2 and str(timg[segs[sidx-3]][idx-(int(idx/7)*7)]).rfind("{") > -1:
        pcolour=timg[segs[sidx-3]][idx-(int(idx/7)*7)][str(timg[segs[sidx-3]][idx-(int(idx/7)*7)]).rfind("{"):str(timg[segs[sidx-3]][idx-(int(idx/7)*7)]).rfind("{")+4]

      # prefix with the previous colour we found and add the line to the segment
      timg[seg].append(str(pcolour)+line[begins[sidx]:ends[sidx]-1])

      # blank out the last segment because it won't be used
      if seg==16:
        image[idx]=image[idx][0:begins[sidx]]+" ".ljust(20)

  for idx in range(1, 17):
    timg[idx][6]="{dw}___________________"

  timg[16]=empty

  return timg

# draw the whole board, including the segments
def draw_board():
  global init
  global seg_img
  global segments
  global yrange
  global xrange

  screen.clear()
  for posy in range(yrange+1):
    screen.addstr(posy+segments[1]['y']-1, segments[1]['x']-1, "|")
  for posx in range(xrange+1):
    screen.addstr(segments[1]['y']-1, posx+segments[1]['x']-1, "_")

  for seg in range(1,17):
    print_segment(seg_img, int(seg))
    screen.refresh()
    if init:
      time.sleep(.15)
    seg=seg+1

  screen.refresh()
  init=0

# mark a segment as active
def select_seg(seg):
  global selected_seg

  colour=curses.color_pair(0)
  posy=segments[selected_seg]['y']
  posx=segments[selected_seg]['x']

  posy=segments[seg]['y']
  posx=segments[seg]['x']
  for idx, fullline in enumerate(seg_img[seg]):
    posy=posy+1

  posy=segments[seg]['y']
  for posi in range(0,int(yrange/4)):
    screen.addstr(posy+posi, posx-1, "=", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+posi, posx-1+int(xrange/4), "=", curses.color_pair(8)|curses.A_BOLD)
  if posy is segments[1]['y']:
    screen.addstr(posy-1, posx-2, "======================", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy+int(yrange/4)-1, posx-1, "====================", curses.color_pair(8)|curses.A_BOLD)
  else:
    screen.addstr(posy-1, posx-1, "=====================", curses.color_pair(8)|curses.A_BOLD)
    screen.addstr(posy-1+int(yrange/4), posx, "===================", curses.color_pair(8)|curses.A_BOLD)

  selected_seg=seg


# move a segment into a blank spot
def seg_move():
  global empty_seg
  global selected_seg
  global seg_img
  global chars

  #check if the movement is allowed (there must be a cleaner way to do this)
  if empty_seg is selected_seg+4 or empty_seg is selected_seg-4 \
  or ((empty_seg is selected_seg+1 or empty_seg is selected_seg-1) \
  and ((empty_seg in range(1,5) and selected_seg in range(1,5)) \
  or (empty_seg in range(5,9) and selected_seg in range(5,9)) \
  or (empty_seg in range(9,13) and selected_seg in range(9,13)) \
  or (empty_seg in range(13,17) and selected_seg in range(13,17)))):
    seg_img[empty_seg]=seg_img[selected_seg]
    seg_img[selected_seg]=empty
    print_segment(seg_img, empty_seg)
    print_segment(seg_img, selected_seg)
    screen.refresh()
    empty_seg=selected_seg
    select_seg(empty_seg)
  else:
    select_seg(selected_seg)

  chars=27


# shuffle the segments
def shuffle_img():
  global empty_seg
  global seg_img

  select_seg(secrets.randbelow(16)+1)
  seg_move()
  for idx in range(2000):
    segnum=secrets.randbelow(16)+1
    select_seg(segnum)
    seg_move()


# print one segment
def print_segment(seg_img, segnum):
  global segments
  if segnum != 0:
    segnum=int(str(segnum).lstrip("0"))
  posy=segments[segnum]['y']
  posx=segments[segnum]['x']

  for idx, fullline in enumerate(seg_img[segnum]):
    colour=curses.color_pair(0)
    line=re.split('\{|}+', str(fullline))
    screen.addstr(posy, posx, "")
    for piece in line:
      if piece in colours:
        if curses.COLORS==8 and int(colours[piece])>7:
          colour=( (int(colours[piece])-8) *256) +2097152
        elif curses.COLORS==8:
          colour=int(colours[piece])*256
        else:
          colour=(int(colours[piece])+1)*256
      else:
        screen.addstr(piece, colour)
        screen.refresh()
    screen.addstr("|")
    posy=posy+1


# show the original image5
def show_img():
  global image
  global xrange

  screen.clear()
  posy=segments[1]['y']
  posx=segments[1]['x']-1
  screen.addstr(posy-1, posx, "_________________________________________________________________________________")

  for idx, fullline in enumerate(image):
    colour=curses.color_pair(0)
    line=re.split('\{|}+', str(fullline))
    screen.addstr(posy, posx, "|")
    for piece in line:
      if piece in colours:
        if curses.COLORS==8 and int(colours[piece])>7:
          colour=( (int(colours[piece])-8) *256) +2097152
        elif curses.COLORS==8:
          colour=int(colours[piece])*256
        else:
          colour=(int(colours[piece])+1)*256
      else:
        screen.addstr(piece, colour)
    screen.addstr(posy, posx+xrange, "|")
    screen.refresh()
    posy=posy+1
  screen.addstr(posy-1, posx, "|_______________________________________________________________________________|")
  screen.refresh()


# HALP.  Info
def help():
  global segments

  posy=segments[1]['y']+int(yrange/2)-8
  posx=segments[1]['x']+int(xrange/2)-26

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

  imgs=glob.glob('*.pim')
  imgs=sorted(imgs)
  inwindow=0

  window=[
    "_________________________________________________",
    "|                                               |",
    "|  You can create your own ANSI/ASCII art as    |",
    "|  well.  To see information about using        |",
    "|  colours, press 'c'.                          |",
    "|                                               |",
    "|  The art must be in a file with extension     |",
    "|  .pim (PuzzleIMage) in the same directory as  |",
    "|  this script and be "+str(xrange)+"x"+str(yrange)+" characters.         |",
    "|                                               |",
    "|  Note: the lower right "+str(int(xrange/4))+"x"+str(int(yrange/4))+" characters will   |",
    "|        be removed in the puzzle               |",
    "|                                               |",
    "|   Available Images:                           |",
    "|                                               |"
  ]

  for idx, file in enumerate(imgs):
    window.append("|   "+str(idx).rjust(2)+": "+file.ljust(39)+" |")

  window.append("|                                               |")
  window.append("|  Please choose an image for the puzzle (0-"+str(len(imgs)-1)+")  |")
  window.append("|_______________________________________________|")

  posy=int(curses.LINES/2)-int(len(window)/2)
  posx=int(curses.COLS/2)-25

  chars=0
  while 0==0:
    screen.clear()

    for idx in range(len(window)):
      screen.addstr(posy+idx, posx, window[idx])

    chars=screen.getch()

    if chars==99:
      colour_palate()

    if (chars==108 or chars==27) and init==0:
      draw_board()
      select_seg(selected_seg)
      break

    if chars==113:
      curses.nocbreak()
      screen.keypad(False)
      curses.echo()
      curses.endwin()
      exit()

    if chars>=48 and chars<=57:
      if int(chr(chars))>=0 and int(chr(chars))<len(imgs):
        f=open(imgs[int(chr(chars))], 'r')
        image=f.readlines()
        if len(image)<yrange:
          for idx in range(yrange-len(image)):
            image.append(" ".ljust(xrange))
        else:
          del image[yrange:]

        for idx in range(yrange):
          res=image[idx].count("{")*4
          if len(image[idx])-res<xrange:
            image[idx]=image[idx][:-1]
            image[idx]=image[idx].ljust(xrange+res)
          if len(image[idx])-res>xrange:
            image[idx]=image[idx][:xrange+res]
            # looks like I didn't need this?? to make sure we don't have half colour codes hanging around?
            #if image[idx].count("{")>image[idx].count("}"):
              #image[idx]=image[idx][:image[idx].rfind("{")]

        show_img()

        screen.addstr(int(curses.LINES/2)-2, int(curses.COLS/2)-10, "___________________", curses.color_pair(3)|curses.A_BOLD)
        screen.addstr(int(curses.LINES/2)-1, int(curses.COLS/2)-10, "|                 |", curses.color_pair(3)|curses.A_BOLD)
        screen.addstr(int(curses.LINES/2), int(curses.COLS/2)-10, "| Image OK? (y/n) |", curses.color_pair(3)|curses.A_BOLD)
        screen.addstr(int(curses.LINES/2)+1, int(curses.COLS/2)-10, "|_________________|", curses.color_pair(3)|curses.A_BOLD)

        while chars!=110 and chars!=121:
         chars=screen.getch()

        # If n was chosen, rinse and repeat
        if chars==110:
          continue;

        else:
          empty_seg=16
          blarimg=segment_img(image)
          seg_img=segment_img(image)
          orig_img=segment_img(image)
          shuffle_img()
          select_seg(16)
          draw_board()
          screen.refresh()
          chars=27
          break;


# yay you finished the puzzle!
def fanfare():
  #mixer.music.play()

  colours=[10, 6, 14, 13, 7, 15, 3, 11, 12, 4, 2]

  while True:
    colours.append(colours.pop(0))

    screen.addstr(segments[1]['y']-1, segments[1]['x']-1, "".ljust(xrange+1, "_"), curses.color_pair(colours[10]))

    for segnum in range(1,17):
      posy=segments[segnum]['y']
      posx=segments[segnum]['x']-1
      for idx, fullline in enumerate(seg_img[segnum]):
        fullline=re.sub('\{..}+', '', str(fullline))
        colour=idx
        if segnum in range(5,9):
          colour=colour+int(yrange/4)
        if segnum in range(9,13):
          colour=colour+(int(yrange/4)*2)
        if segnum in range(13,17):
          colour=colour+(int(yrange/4)*3)
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

    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
      break

  chars=0

set_segments()
load_img()

pos=curses.getsyx()
help()
inwindow=1
chars=0

# main loop
while 0==0:
  chars=screen.getch()
  keys={
    258: {'y': 1, 'x': 0},
    259: {'y': -1, 'x': 0},
    260: {'y': 0, 'x': -1},
    261: {'y': 0, 'x': 1}
  }

  # q for quit
  if chars==113:
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()
    exit()

  # if in a window, only thing that can be done is exit
  if chars!=115 and chars!=113 and chars!=104 and chars!=27 and inwindow:
    continue

  # s or h if in window, or esc to redraw board and exit window
  if (chars==115 or chars==104 or chars==27) and inwindow:
    draw_board()
    select_seg(selected_seg)
    inwindow=0
    continue

  # navigating around (arrow keys)
  if chars==258:
    draw_board()
    if (selected_seg+4)>16:
      select_seg(selected_seg-12)
    else:
      select_seg(selected_seg+4)

  if chars==259:
    draw_board()
    if (selected_seg-4)<1:
      select_seg(selected_seg+12)
    else:
      select_seg(selected_seg-4)

  if chars==260:
    draw_board()
    if (selected_seg-1)<1:
      select_seg(selected_seg+3)
    else:
      select_seg(selected_seg-1)

  if chars==261:
    draw_board()
    if (selected_seg+1)>16:
      select_seg(selected_seg-3)
    else:
      select_seg(selected_seg+1)

  # enter or spacebar moves the segment
  if chars==32 or chars==10:
    draw_board()
    seg_move()
    if seg_img == orig_img:
      inwindow=1
      fanfare()

  # h for help
  if chars==104:
    inwindow=1
    help()

  # s for show original img
  if chars==115:
    inwindow=1
    show_img()

  # l for load new img
  if chars==108:
    chars=0
    load_img()

  # r for reshuffle img
  if chars==114:
    shuffle_img()
    draw_board()
    select_seg(16)

  screen.move(pos[0], pos[1])
  screen.refresh()
  chars=0

curses.nocbreak()
screen.keypad(False)
curses.echo()
curses.endwin()
