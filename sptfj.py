import curses                                                                   
import json
import locale  
import os
import sys
import traceback                                                       
from sptf import delete_record
from sptf import get_search
from sptf import get_max_rowid
from sptf import init_db
from sptf import sptf_currently_playing
from sptf import sptf_display_devices
from sptf import sptf_next_track
from sptf import sptf_previous_track
from sptf import sptf_search_album

LANG="EN"

msg_str={}


msg_str["APP_NAME_EN"]="<-...-| ... SPoTiFy Jukebox ... |-...->"
msg_str["ENTRY_DIAL_EN"]="We shall play: "
msg_str["NOW_PLAYING_EN"]="Now playing: "

inpstr=""

if len(sys.argv)>=2:
  if (sys.argv[1]=="--devices"):
    sptf_display_devices()
    exit(0)

init_db()
scr = curses.initscr()
curses.noecho()                                                               
curses.cbreak()                                                               
curses.start_color()                                                          
scr.keypad(1)                                                              
curses.init_pair(1,curses.COLOR_CYAN,curses.COLOR_BLACK) 
hiTe=curses.color_pair(1)|curses.A_BOLD
miTe=curses.color_pair(1)
loTe=curses.color_pair(1)|curses.A_DIM
scr.clear()
scr.refresh()
height,width=scr.getmaxyx()
x=0
cnt=0
last_search=""
err=""
action=""
hist_search=""
cur_hist_id=1
save_flag=1
xrowid=1
track_filter=""
while x != 27: # Until ESC keypress 
  # DRAW THE TEXT USER INTERFACE
  scr.addstr(0,0,msg_str["APP_NAME_"+LANG],loTe)
  scr.addstr(2,0,msg_str["ENTRY_DIAL_"+LANG],loTe)
  scr.addstr(4,0,inpstr)
  scr.addstr(6,0,msg_str["NOW_PLAYING_"+LANG],loTe)
  curplay=sptf_currently_playing()
  artist=curplay[0] 
  album=curplay[1] 
  song=curplay[2] 
  scr.addstr(8,0," "*(width-1))
  scr.addstr(8,0,artist+"|",hiTe)
  scr.addstr(8,len(artist)+1,album+"|",miTe)
  scr.addstr(8,len(artist)+len(album)+2,song,loTe)
  scr.addstr(height-1,0,action,loTe)
  xrowid=get_max_rowid()[0][0]
  # DRAW THE SEARCH HISTORY
  scr.addstr(10,0,"| History: |-[ ",loTe)
  scr.addstr(10,15,"{:05d}".format(cur_hist_id),hiTe)
  scr.addstr(10,20," / ",miTe)
  scr.addstr(10,23,"{:05d}".format(xrowid)+" ]-",loTe)
  x=int(height/2)-1
  if (str(xrowid) != "None" and str(xrowid) != "NoneType"):
    rownum=0
    hist_cur=""
    first_displayed_track=-1
    for y in range(cur_hist_id,xrowid+1):
      if y>0:
        hist_cur=get_search(y)
      if (len(hist_cur)>0):
        hist_str=hist_cur[0][0].replace('\n','')
        res_str=str(hist_cur[0][1])
        display_track=1
        if (track_filter!=""):
          tmp_str=res_str.lower()
          if (tmp_str.find(track_filter)==-1):
            display_track=0
        if (display_track==1):
          if (track_filter!="" and first_displayed_track==-1):
            first_displayed_track=y
          if (cur_hist_id==y):
            scr.addstr(12+rownum,0,"> "+str(y)+"|"+res_str,hiTe)
          else:
            scr.addstr(12+rownum,0,"  "+str(y)+"|"+res_str,loTe)
          rownum+=1
        if (rownum>x):
          break
    if (track_filter!=""):
      cur_hist_id=first_displayed_track
  if err:
    scr.addstr(9,0,"Message: "+err,loTe)
    action="ERROR"
  else:
    scr.addstr(9,0," "*(height-1))
  # CURSOR CLEANUP
  scr.move(0, width-1)
  x = scr.getch()
  # PROCESS KEY PRESS
  if (x==curses.KEY_BACKSPACE): # BACKSPACE
    scr.addstr(4,0,str(" "*(len(inpstr))))
    inpstr=inpstr[:-1]
  elif (x==10): # ENTER
    action="SEARCH"
    if (cnt>0):
      save_flag=1
    elif (track_filter!=""):
      save_flag=0
    cnt=0
    scr.clear()
  elif (x >= 32 and x <= 126): # ANY OTHER KEY
    inpstr+=chr(x)
    cnt+=1
  else: # ANY OTHER KEY
    action="ANY KEY ...      "
  # PROCESS ACTIONS
  if (inpstr==".k"): # MOVE TO PREVIOUS ITEM
    action="PREVIOUS ITEM       "
    if (cur_hist_id-1>=1):
      scr.addstr(3,0,str(" "*(len(inpstr)+1)))
      cur_hist_id-=1
    inpstr=""
    save_flag=0
    scr.clear()
  elif (inpstr==".j"): # MOVE TO NEXT ITEM
    action="NEXT ITEM         "
    if (cur_hist_id+1<=xrowid):
      scr.addstr(3,0,str(" "*(len(inpstr)+1)))
      cur_hist_id+=1
    inpstr=""
    save_flag=0
    scr.clear()
  elif (inpstr[0:2]==".s"): # SEARCH IN ITEMS
    track_filter=inpstr[3:]
    scr.clear()
    save_flag=0
  elif (inpstr==".c"): # PLAY CURRENT TRACK
    action="CURRENT SEARCH"
    scr.addstr(3,0,str(" "*(len(inpstr)+1)))
    hist_search=str(get_search(cur_hist_id)[0][0])
    action="SEARCH"
    inpstr=hist_search
    save_flag=0
  elif (inpstr==".tn"): # NEXT TRACK
    sptf_next_track()
    inpstr=""
  elif (inpstr==".tp"): # PREVIOUS TRACK
    sptf_previous_track()
    inpstr=""
  elif (inpstr==".p"): # PREVIOUS ITEM
    action="PREVIOUS ITEM"
    scr.addstr(3,0,str(" "*(len(inpstr)+1)))
    if (cur_hist_id-1>=1):
      cur_hist_id-=1
      hist_search=str(get_search(cur_hist_id)[0][0])
      action="SEARCH"
      inpstr=hist_search
      save_flag=0
    else:
      inpstr=""
    save_flag=0
  elif (inpstr==".n"): # NEXT ITEM
    action="NEXT ITEM"
    if (cur_hist_id+1<=xrowid):
      scr.addstr(3,0,str(" "*(len(inpstr)+1)))
      cur_hist_id+=1
      hist_search=str(get_search(cur_hist_id)[0][0])
      action="SEARCH"
      inpstr=hist_search
    else:
      inpstr=""
    save_flag=0
  elif (inpstr==".l"): # LAST ITEM IN HISTORY
    cur_hist_id=xrowid
    inpstr=""
    scr.clear()
  elif (inpstr==".f"): # FIRST ITEM IN HISTORY
    cur_hist_id=1
    inpstr=""
    scr.clear()
  elif (inpstr[0:2]==".d" and action=="SEARCH"): # Jump to history
    action="DELETE FROM PLAYLIST"
    rid=inpstr[3:]
    if (len(inpstr[3:])>0):
      rid=int(inpstr[3:])
      delete_record(rid)   
      action="DELETE FROM PLAYLIST"+str(rid)
    save_flag=0  
    cur_hist_id=xrowid
    inpstr=""
  elif (inpstr[0:2]==".g" and action=="SEARCH"): # Jump to history
    action="MOVE TO HISTORY "
    cur_hist_id=inpstr[3:]
    if (len(inpstr[3:])>0):
      cur_hist_id=int(inpstr[3:])
    inpstr=""
    save_flag=0  
  elif (inpstr[0:2]==".h" and action=="SEARCH"): # Jump to history
    action="GO TO HISTORY "
    #if (cur_hist_id+1<=xrowid):
    cur_hist_id=inpstr[3:]
    #scr.addstr(20,0,str(cur_hist_id))
    if (len(inpstr[3:])>0):
      try:
        cur_hist_id=int(inpstr[3:])
      except:
        cur_hist_id=1
      #print(str(cur_hist_id))
    else:
      cur_hist_id=xrowid
    if cur_hist_id > xrowid:
      cur_hist_id = xrowid
    elif cur_hist_id < 1:
      cur_hist_id = 1
    hist_search=str(get_search(cur_hist_id)[0][0])
    action="SEARCH"
    inpstr=hist_search
    save_flag=0  
  elif (inpstr==".q"): # QUIT
    break
  # Process commands arguments
  # RESET THE SEARCH FILTER
  if (inpstr[0:2]==".s" and action=="SEARCH" and len(inpstr)==2):
    track_filter=""
    inpstr=""
    save_flag=0  
    action="CLEAR TRACK FILTER"
    cur_hist_id=1
  # PRESSED ENTER AND THERE IS SEARCH ARGUMENT
  if (action=="SEARCH" and track_filter !="" and inpstr!=""):
    if (cur_hist_id>xrowid):
      cur_hist_id=xrowid
    hist_search=str(get_search(cur_hist_id)[0][0])
    inpstr=hist_search
  # PRESSED ENTER AND THERE IS NO TRACK FILTER NOR INPUT STRING
  if (action=="SEARCH" and track_filter =="" and inpstr==""):
    if (cur_hist_id>xrowid):
      cur_hist_id=xrowid
    hist_search=str(get_search(cur_hist_id)[0][0])
    inpstr=hist_search
  # SEARCH FOR THE ALBUM ON SPTF
  if (action=="SEARCH"):
    ret=sptf_search_album(inpstr,save_flag)
    if (ret[0]=="ERR"):
      err=ret[1]
    else:
      last_search=ret[1] 
      err=""
    scr.addstr(3,0,str(" "*(len(inpstr)+1)))
    inpstr=""
    action=""
    scr.refresh()
    scr.clear()
# RESET THE TERMINAL TO ORIGINAL STATE
curses.nocbreak()
scr.keypad(0)
curses.echo()
curses.endwin()
