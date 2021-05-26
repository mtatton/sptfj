import os
import sys
import spotipy
import spotipy.util as util
import json
import sqlite3 
import traceback

# CONFIGURATION SECTION
username = ''
os.environ["SPOTIPY_CLIENT_ID"]=''
os.environ["SPOTIPY_CLIENT_SECRET"]='' 
os.environ["SPOTIPY_REDIRECT_URI"]='http://127.0.0.1:9999'
device=""
scope = 'user-read-playback-state,user-library-read,user-modify-playback-state'

db_location="sptf.db"

def get_max_rowid():
  try:
    con=sqlite3.connect(db_location)
    qry="select max(rowid) from sptf_search_history"
    c = con.cursor()                                                        
    c.execute(qry)
    rows = c.fetchall()                                                                                                               
    con.close()
    return (rows)
  except Exception:
    traceback.print_exc(file=sys.stdout)
    print ("ERR [ FAILED TO GET MAX ROWID ] 001000x0010 (1) : get_max_rowid")

def sptf_currently_playing():

  token = util.prompt_for_user_token(username, scope)

  artist="..."
  album="..."
  song="..."

  if token:
      sp = spotipy.Spotify(auth=token)
      res=sp.currently_playing();
      try:
        if (type(res) != "None"):
          artist=res["item"]["album"]["artists"][0]["name"]
          album=res["item"]["album"]["name"]
          song=res["item"]["name"]
      except:
        pass
      return([artist,album,song])
  else:
      print("Error during action for ", username)

def get_search(id):

  try:
    con=sqlite3.connect(db_location)
    qry="select needle,res from sptf_search_history where rowid = ?"
    c = con.cursor()                                                        
    c.execute(qry,(id,))                                                          
    rows = c.fetchall()                                                                                                               
    #print (rows)                                                           
    con.close()
    return (rows)
  except Exception:
    traceback.print_exc(file=sys.stdout)
    print ("ERR [ FAILED TO GET SEARCH ] 001000x0020 (1) : get_search")

def sptf_display_devices():

  token = util.prompt_for_user_token(username, scope)
  
  if token:
      print("Put desired ID from here into sptf.py to device variable")
      sp = spotipy.Spotify(auth=token)
      dev=sp.devices();
      #print(dev["devices"])
      print("ID"+"|"+"Active"+"|"+"Name"+"|"+"Type")
      for d in dev["devices"]:
        print(d["id"]+"|"+str(d["is_active"])+"|"+d["name"]+"|"+d["type"])
  else:
      print("Error during action for ", username)

def sptf_play_ctx(ctx_uri):

  token = util.prompt_for_user_token(username, scope)
  
  if token:
      sp = spotipy.Spotify(auth=token)
      sp.start_playback(device,context_uri=ctx_uri);
      return("Action: Pause, Result: OK")
  else:
      print("Error during action for ", username)

def init_db():
  try:
    conn=sqlite3.connect(db_location)
    cur = conn.cursor()
    cur.execute("create  table if not exists  sptf_search_history (needle text, res text)")
  except Exception:
    traceback.print_exc(file=sys.stdout)
    print ("ERR [ FAILED TO INIT DB ] 001000x0030 (1) : init_db")

def delete_record(rowid):

  try:
    conn=sqlite3.connect(db_location)
    cur = conn.cursor()
    cur.execute("""create table sptf_search_history_tmp as 
      select * 
      from sptf_search_history 
      where rowid != ?""", (rowid,))
    cur.execute("""drop table sptf_search_history""")
    cur.execute("""create table sptf_search_history as 
      select * 
      from sptf_search_history_tmp""")
    cur.execute("""drop table sptf_search_history_tmp""")
    conn.commit()
    conn.close()
  except Exception:
    traceback.print_exc(file=sys.stdout)
    print ("ERR [ DELETE RECORD FAILED ] 001000x0040 (1) : delete_record")

def save_search(needle,res):

  try:
    conn=sqlite3.connect(db_location)
    cur = conn.cursor()
    cur.execute("""insert into sptf_search_history 
      select ?, ? 
      where not exists (
        select 1 from sptf_search_history
        where res = ?)
    """,(needle,res,res,))
    conn.commit()
    conn.close()
  except Exception:
    traceback.print_exc(file=sys.stdout)
    print ("ERR [ SAVE SEARCH FAILED ] 001000x0050 (1) : save_search")


def sptf_search(needle):

  token = util.prompt_for_user_token(username, scope)
  
  if token:
      sp = spotipy.Spotify(auth=token)
      dev=sp.search(needle);
      return(dev)
  else:
      print("Error during action for ", username)

def sptf_previous_track():

  token = util.prompt_for_user_token(username, scope)
  
  if token:
      sp = spotipy.Spotify(auth=token)
      sp.previous_track();
  else:
      print("Error during action for ", username)

def sptf_next_track():

  token = util.prompt_for_user_token(username, scope)
  
  if token:
      sp = spotipy.Spotify(auth=token)
      sp.next_track();
  else:
      print("Error during action for ", username)


def sptf_search_album(needle,save_to_history=1):

  albums=[]
  albums_display=[]
  album=""
  song=""
  artist=""
  album_display=""
  res=sptf_search(needle)
  if (len(res["tracks"]["items"])>0):
    i=res["tracks"]["items"][0]
    artist=i["album"]["artists"][0]["name"]
    song=str(i["album"]["artists"][0]["name"])
    album=i["album"]["name"]
    albums.append(str(i["album"]["uri"]))
    album_display=artist+"|"+album
    albums_display.append(album_display)
  try:
    sptf_play_ctx(albums[0])
  except Exception as e:
    return(["ERR",str(e)])
  
  if (save_to_history==1):
    save_search(needle,album_display)
    return(["PLA",album_display])
  else:
    return(["PLA",album_display])
