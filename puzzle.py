#!/usr/bin/env python3

import signal, sys, time, os, secrets, shutil, glob, random

os.environ.setdefault('ESCDELAY', '0')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

yrange=28
xrange=80

if shutil.get_terminal_size()[0]<(xrange+1) or shutil.get_terminal_size()[1]<(yrange+1):
  print("AW, terminal must be at least 81x29 to play the slidy puzzle. :(")
  exit()

import curses

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

def signal_handler(sig, frame):
  curses.nocbreak()
  screen.keypad(False)
  curses.echo()
  curses.endwin()
  sys.exit(0)

'''from pygame import mixer
mixer.init()
mixer.music.load("FF-Fanfare.mp3")'''

signal.signal(signal.SIGINT, signal_handler)

wd=os.path.dirname(os.path.realpath(__file__))

for i in range(0, curses.COLORS):
  curses.init_pair(i + 1, i, -1)

# To add colour to text in a .pim, add the colour name (such as lr) after a squirrely brace like so: {lr
colours={
  "lr": "160",
  "dr": "52",
  "or": "214",
  "br": "130",
  "ly": "226",
  "lg": "34",
  "dg": "22",
  "ol": "65",
  "lc": "159",
  "pb": "39",
  "lb": "21",
  "db": "19",
  "lm": "163",
  "pi": "162",
  "pe": "203",
  "sk": "216",
  "be": "230",
  "lw": "15",
  "si": "248"
}

if curses.COLORS==8:
  colours={
    "lr": "10",
    "dr": "2",
    "or": "4",
    "br": "4",
    "ly": "12",
    "lg": "11",
    "dg": "3",
    "ol": "3",
    "lc": "15",
    "pb": "15",
    "lb": "13",
    "db": "5",
    "lm": "14",
    "pi": "14",
    "pe": "14",
    "sk": "12",
    "be": "0",
    "lw": "8",
    "si": "0"
  }

empty=[
  "                   |",
  "                   |",
  "                   |",
  "                   |",
  "                   |",
  "                   |",
  "___________________|"
]
empty_seg=16
segments=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

seg_img=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
orig_img=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

init=1

selected_seg=16

inwindow=0

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

'''
                                           88
                                           88
                                           88
8b,dPPYba,  88       88 88,dPYba,,adPYba,  88,dPPYba,   ,adPPYba, 8b,dPPYba,
88P'   `"8a 88       88 88P'   "88"    "8a 88P'    "8a a8P_____88 88P'   "Y8
88       88 88       88 88      88      88 88       d8 8PP""""""" 88
88       88 "8a,   ,a88 88      88      88 88b,   ,a8" "8b,   ,aa 88
88       88  `"YbbdP'Y8 88      88      88 8Y"Ybbd8"'   `"Ybbd8"' 88
'''

def segment_img(image):
  global yrange
  global xrange
  global empty

  timg=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

  for idx in range(0, 7):
    '''seg_img[1].append(image[idx][0:20])
    seg_img[5].append(image[idx+7][0:20])
    seg_img[9].append(image[idx+14][0:20])
    seg_img[13].append(image[idx+21][0:20])

    seg_img[2].append(image[idx][20:40])
    seg_img[6].append(image[idx+7][20:40])
    seg_img[10].append(image[idx+14][20:40])
    seg_img[14].append(image[idx+21][20:40])

    seg_img[3].append(image[idx][40:60])
    seg_img[7].append(image[idx+7][40:60])
    seg_img[11].append(image[idx+14][40:60])
    seg_img[15].append(image[idx+21][40:60])

    seg_img[4].append(image[idx][60:80])
    seg_img[8].append(image[idx+7][60:80])
    seg_img[12].append(image[idx+14][60:80])
    seg_img[16].append(image[idx+21][60:80])'''

    timg[1].append(image[idx][0:19]+"|")
    timg[5].append(image[idx+7][0:19]+"|")
    timg[9].append(image[idx+14][0:19]+"|")
    timg[13].append(image[idx+21][0:19]+"|")

    timg[2].append(image[idx][20:39]+"|")
    timg[6].append(image[idx+7][20:39]+"|")
    timg[10].append(image[idx+14][20:39]+"|")
    timg[14].append(image[idx+21][20:39]+"|")

    timg[3].append(image[idx][40:59]+"|")
    timg[7].append(image[idx+7][40:59]+"|")
    timg[11].append(image[idx+14][40:59]+"|")
    timg[15].append(image[idx+21][40:59]+"|")

    timg[4].append(image[idx][60:79]+"|")
    timg[8].append(image[idx+7][60:79]+"|")
    timg[12].append(image[idx+14][60:79]+"|")
    timg[16].append(image[idx+21][60:79]+"|")

  for idx in range(1, 17):
    timg[idx][6]="___________________|"

  timg[16]=empty

  for line in range(7):
    image[line+21]=image[line+21][:-20]
    image[line+21]+="                    "

  return timg

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


'''screen.addstr(0,0,"1", curses.color_pair(1))
screen.addstr("2", curses.color_pair(2))
screen.addstr("10", curses.color_pair(10))
screen.addstr("6", curses.color_pair(6))
screen.addstr("14", curses.color_pair(14))
screen.addstr("13", curses.color_pair(13))
screen.addstr("15", curses.color_pair(15))
screen.addstr("7", curses.color_pair(7))
screen.addstr("3", curses.color_pair(3))
screen.addstr("11", curses.color_pair(11))
screen.addstr("12", curses.color_pair(12))
screen.addstr("4", curses.color_pair(4))

screen.addstr("2", curses.color_pair(2))
screen.addstr("10", curses.color_pair(10))
screen.addstr("6", curses.color_pair(6))
screen.addstr("8", curses.color_pair(8))
screen.addstr("9", curses.color_pair(9))
screen.addstr("16", curses.color_pair(16))
screen.refresh()
time.sleep(500)'''


def select_seg(seg):
  global selected_seg

  colour=curses.color_pair(0)
  posy=segments[selected_seg]['y']
  posx=segments[selected_seg]['x']
  '''if posy is segments[1]['y']:
    screen.addstr(posy-1, posx-1, "____________________", curses.color_pair(0))
  else:
    screen.addstr(posy-1, posx, "___________________", curses.color_pair(0))
  for posi in range(0,7):
    screen.addstr(posy+posi, posx-1, "|", curses.color_pair(0))
  #screen.addstr(posy, posx, fullline, curses.color_pair(11))
  for idx, fullline in enumerate(seg_img[selected_seg]):
    screen.addstr(posy, posx, fullline)
    posy=posy+1'''

  #draw_board()
  #screen.refresh()

  posy=segments[seg]['y']
  posx=segments[seg]['x']
  #screen.addstr(posy+6, posx-1, "_", curses.color_pair(11))
  for idx, fullline in enumerate(seg_img[seg]):
    #screen.addstr(posy, posx, fullline, curses.color_pair(11))
    posy=posy+1

  posy=segments[seg]['y']
  for posi in range(0,int(yrange/4)):
    #screen.addstr(posy+posi, posx-1, "|", curses.color_pair(11))
    screen.addstr(posy+posi, posx-1, "=", curses.color_pair(16)|curses.A_BOLD)
    screen.addstr(posy+posi, posx-1+int(xrange/4), "=", curses.color_pair(16)|curses.A_BOLD)
  if posy is segments[1]['y']:
    #screen.addstr(posy-1, posx-1, "____________________", curses.color_pair(11))
    screen.addstr(posy-1, posx-2, "======================", curses.color_pair(16)|curses.A_BOLD)
    screen.addstr(posy+int(yrange/4)-1, posx-1, "====================", curses.color_pair(16)|curses.A_BOLD)
  else:
    #screen.addstr(posy-1, posx, "___________________", curses.color_pair(11))
    screen.addstr(posy-1, posx-1, "=====================", curses.color_pair(16)|curses.A_BOLD)
    screen.addstr(posy-1+int(yrange/4), posx, "===================", curses.color_pair(16)|curses.A_BOLD)

  selected_seg=seg


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

  '''target=0
  posy=curses.getsyx()[0]
  posx=curses.getsyx()[1]
  #screen.addstr(0,0,str(curses.getsyx())+" ")
  for idx in range(1, 17):
    if posy>=segments[idx]['y'] and posy<=segments[idx]['y']+7 and posx>=segments[idx]['x'] and posx<=segments[idx]['x']+20:
      target=idx
      #screen.addstr(0,0,str(idx))
      #screen.addstr(" YES",curses.color_pair(3))
      #screen.move(pos[0], pos[1])
    #else:
      #screen.addstr(str(idx)+": "+str(segments[idx]['y'])+","+str(segments[idx]['x'])+" ")
      #screen.move(pos[0], pos[1])
  #if empty_seg==0:
  #  selected_seg=idx
  #elif selected_seg==target:
  #  selected_seg=0
  #else:
  if empty_seg==target+4 or empty_seg==target-4 or empty_seg==target+1 or empty_seg==target-1:
    #tmp_seg=seg_img[empty_seg]
    seg_img[empty_seg]=seg_img[target]
    print_segment(seg_img, empty_seg)
    screen.refresh()
    seg_img[target]=empty
    empty_seg=target
    print_segment(seg_img, target)
    screen.refresh()
    screen.move(pos[0], pos[1])
  #what segment is selected, if any
  #if target == selected, unselect, otherwise swap.'''


def shuffle_img():
  global empty_seg
  global seg_img

  #random.shuffle(seg_img)

  select_seg(secrets.randbelow(16)+1)
  seg_move()
  for idx in range(2000):
    segnum=secrets.randbelow(16)+1
    select_seg(segnum)
    seg_move()
    #time.sleep(.001)


def print_segment(seg_img, segnum):
  #screen.clear()
  global segments
  if segnum != 0:
    segnum=int(str(segnum).lstrip("0"))
  '''screen.addstr(0,0,str(segnum)+" ")
  screen.addstr(10,10,str(segnum)+"    ")
  screen.refresh()'''
  posy=segments[segnum]['y']
  posx=segments[segnum]['x']

  colour=curses.color_pair(0)
  for idx, fullline in enumerate(seg_img[segnum]):
    #line=re.split('\\x1b\[38\;5\;|m+', fullline)
    '''screen.addstr(posy, posx, "")
    for piece in line:
      if piece.isnumeric():
        if curses.COLORS==8 and int(piece)>7:
          colour=( (int(piece)-8) *256) +2097152
        elif curses.COLORS==8:
          colour=int(piece)*256
        else:
          colour=(int(piece)+1)*256
      else:
        screen.addstr(piece, colour)
        screen.refresh()'''
    screen.addstr(posy, posx, fullline)
    posy=posy+1


def show_img():
  global image

  '''for seg in range(1,17):
    print_segment(orig_img, int(seg))
    screen.refresh()
    seg=seg+1'''

  screen.clear()
  posy=segments[1]['y']
  posx=segments[1]['x']-1
  screen.addstr(posy-1, posx, "_________________________________________________________________________________")
  for line in image:
    screen.addstr(posy, posx, "|"+line)
    screen.addstr(posy, posx+len(line), "|")
    posy=posy+1
  screen.addstr(posy-1, posx, "|_______________________________________________________________________________|")
  screen.refresh()


def help():
  global segments

  posy=segments[1]['y']+int(yrange/2)-8
  posx=segments[1]['x']+int(xrange/2)-26

  screen.addstr(posy,posx,"                                                     ")
  screen.addstr(posy+1,posx," ___________________________________________________ ")
  screen.addstr(posy+2,posx," |                                                 | ")
  screen.addstr(posy+3,posx," |       Use arrow keys to move cursor around.     | ")
  screen.addstr(posy+4,posx," |      Only pieces adjacent to the empty spot     | ")
  screen.addstr(posy+5,posx," |         can be slid into the empty spot.        | ")
  screen.addstr(posy+6,posx," |                                                 | ")
  screen.addstr(posy+7,posx," |   [SPACE] = slide selected piece                | ")
  screen.addstr(posy+8,posx," |             into the empty spot                 | ")
  screen.addstr(posy+9,posx," |   s       = show original image                 | ")
  screen.addstr(posy+10,posx," |   [ESC]   = return to puzzle                    | ")
  screen.addstr(posy+11,posx," |   r       = reshuffle board                     | ")
  screen.addstr(posy+12,posx," |   l       = load new image                      | ")
  screen.addstr(posy+12,posx," |   h       = this help screen                    | ")
  screen.addstr(posy+13,posx," |   q       = quit                                | ")
  screen.addstr(posy+14,posx," |                                                 | ")
  screen.addstr(posy+15,posx," |_________________________________________________| ")
  screen.addstr(posy+16,posx,"                                                     ")
  screen.refresh()

def get_max_len(thing):
  max_len=0
  for idx, item in enumerate(thing):
    if idx == len(thing)-1:
      break;
    if len(item) > max_len:
      max_len=len(item)
  return max_len


def load_img():
  global image
  global seg_img
  global orig_img
  global empty_seg
  global inwindow
  global chars

  imgs=glob.glob('*.pim')
  inwindow=0

  posy=int(segments[1]['y']+((yrange-17)/2))
  posx=int(segments[1]['x']+((xrange-49)/2))

  window=[
    "_________________________________________________",
    "|                                               |",
    "|  You can load your own ANSI/ASCII art using   |",
    "|  this dialog as well.                         |",
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

  #for idx in range(len(window)):
  #  screen.addstr(posy+idx, posx, window[idx])

  chars=0
  while 0==0:
    screen.clear()

    for idx in range(len(window)):
      screen.addstr(posy+idx, posx, window[idx])

    chars=screen.getch()

    if (chars==108 or chars==27) and init==0:
      draw_board()
      select_seg(selected_seg)
      #chars=27
      #inwindow=0
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
          if len(image[idx])<xrange:
            image[idx]=image[idx][:-1]
            image[idx]=image[idx].ljust(xrange)
          if len(image[idx])>xrange:
            image[idx]=image[idx][:xrange]

        screen.addstr(0,0,"_".ljust(xrange+2, "_"))
        for idx in range(yrange):
          screen.addstr(idx+1,0,"|"+str(image[idx])+"|")
          screen.refresh()
        screen.addstr(yrange+1,0,"|".ljust(xrange+1, "_")+"|")

        screen.addstr(10, 30, "___________________", curses.color_pair(11))
        screen.addstr(11, 30, "|                 |", curses.color_pair(11))
        screen.addstr(12, 30, "| Image OK? (y/n) |", curses.color_pair(11))
        screen.addstr(13, 30, "|_________________|", curses.color_pair(11))

        while chars!=110 and chars!=121:
         chars=screen.getch()
         #screen.addstr(30,80,str(chars))
         #screen.refresh()

        # If n was chosen, rinse and repeat
        if chars==110:
          continue;

        else:
          empty_seg=16
          blarimg=segment_img(image)
          seg_img=segment_img(image)
          #screen.addstr(0,0,str(image))
          #screen.refresh()
          #screen.addstr(0,0,str(image[0])+"|"+str(len(image)))
          #screen.refresh()
          #time.sleep(500)
          orig_img=segment_img(image)
          '''for idx in range(1, 17):
            print_segment(seg_img, idx)
          screen.refresh()
          time.sleep(.5)'''
          shuffle_img()
          #select_seg(16)
          draw_board()
          #time.sleep(500)
          #screen.addstr(0,0,"load")
          screen.refresh()
          chars=27
          break;


def fanfare():
  colours=[10, 6, 14, 13, 15, 7, 3, 11, 12, 4, 2]

  #mixer.music.play()

  screen.addstr(segments[1]['y']-1, segments[1]['x']-1, "".ljust(xrange+1, "_"), curses.color_pair(colours[10]))

  for segnum in range(1,17):
    posy=segments[segnum]['y']
    posx=segments[segnum]['x']-1
    for idx, fullline in enumerate(seg_img[segnum]):
      colour=idx
      if segnum in range(5,9):
        colour=colour+int(yrange/4)
      if segnum in range(9,13):
        colour=colour+(int(yrange/4)*2)
      if segnum in range(12,17):
        colour=colour+(int(yrange/4)*3)
      while colour>10:
        colour=colour-11
      screen.addstr(posy, posx, "|"+fullline, curses.color_pair(colours[colour]))
      posy=posy+1

  posy=segments[1]['y']+int(yrange/2)-4
  posx=segments[1]['x']+int(xrange/2)-19

  screen.addstr(posy, posx, "______________________________________", curses.color_pair(16))
  screen.addstr(posy+1, posx, "|                                    |", curses.color_pair(16))
  screen.addstr(posy+2, posx, "|                                    |", curses.color_pair(16))
  screen.addstr(posy+3, posx, "|           You finished it!         |", curses.color_pair(16))
  screen.addstr(posy+4, posx, "|                                    |", curses.color_pair(16))
  screen.addstr(posy+5, posx, "|                 Yay!!              |", curses.color_pair(16))
  screen.addstr(posy+6, posx, "|                                    |", curses.color_pair(16))
  screen.addstr(posy+7, posx, "|                                    |", curses.color_pair(16))
  screen.addstr(posy+8, posx, "|____________________________________|", curses.color_pair(16))

  chars=0

set_segments()
load_img()
#seg_img=segment_img(image)
#orig_img=segment_img(image)
#shuffle_img()
#draw_board()

pos=curses.getsyx()
help()
inwindow=1
#80x24
chars=0
# main loop
while 0==0:
  #screen.addstr(0,0,"main"+str(inwindow)+"     ")
  #screen.refresh()
  chars=screen.getch()
  keys={
    258: {'y': 1, 'x': 0},
    259: {'y': -1, 'x': 0},
    260: {'y': 0, 'x': -1},
    261: {'y': 0, 'x': 1}
  }
  #screen.addstr(0,0,str(chars)+"     ")
  #screen.refresh()
  #screen.move(pos[0], pos[1])
  '''if chars<=261 and chars>=258:
    newy=curses.getsyx()[0]+keys[chars]['y']
    newx=curses.getsyx()[1]+keys[chars]['x']
    if newy>0 and newx>0:
      screen.move(newy, newx)
      screen.refresh()
      pos=curses.getsyx()'''

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
    #screen.refresh()
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
    '''if inwindow:
      chars=27
    else:'''
    inwindow=1
    help()

  # s for show original img
  if chars==115:
    '''if inwindow:
      chars=27
    else:'''
      #curses.curs_set(0)
    inwindow=1
    show_img()

  # l for load new img
  if chars==108:
    '''if inwindow:
      chars=27
    else:'''
    #inwindow=1
    chars=0
    load_img()

  # r for reshuffle img
  if chars==114:
    #curses.curs_set(0)
    shuffle_img()
    #draw_board()
    select_seg(16)

  screen.move(pos[0], pos[1])
  screen.refresh()
  chars=0

curses.nocbreak()
screen.keypad(False)
curses.echo()
curses.endwin()
