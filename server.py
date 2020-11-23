import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   #global lobby = ['', '', '']
   lobby = ['', '', '']
   matchID = 1
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
           # """
         elif 'add' in data:
            print("adding extra player")
            data = data[2:-1]
            cleanData = data.replace("\\", "")
            msg = json.loads(cleanData)
            #look for a lobby with empty space
            for i in range(3):
                  if lobby[i] == '':
                     if msg['player_id'] not in lobby: #make sure the same player isnt already in the lobby
                        print("added player " +  msg["player_id"] + " to lobby")
                        lobby[i] = {"player_id" : msg["player_id"], "timeConnected" : str(datetime.now())}
                        break
                     else:
                        print("player already in lobby")
            clients[addr]['player_id'] = msg["player_id"]
            if lobby[2] != '':
               roomFull(lobby, matchID, sock)
               matchID += 1
               lobby = ['', '', '']
            print(lobby)
            #"""
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            
            
         

             
def roomFull(room, matchId, sock):
   print("room full")
   print(room)

   Message = {"type": "gameMatch", "matchID":str(matchId), "player1": room[0], "player2": room[1], "player3": room[2]}
   s = json.dumps(Message)
   for c in clients:
      sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
   #print('blah')

               

def cleanClients(sock):
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            message = {"cmd": 2,"player":{"id":str(c)}}
            m = json.dumps(message)
            #print(m)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
            #send the remaining clients which client dropped
            for remainingClient in clients:
               sock.sendto(bytes(m,'utf8'), (remainingClient[0],remainingClient[1]))

      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      
      #print (clients)
      for c in clients:
         player = {}
         player['id'] = str(c)
         GameState['players'].append(player)
      s=json.dumps(GameState)
      #print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   random.seed(time.get_clock_info)
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
