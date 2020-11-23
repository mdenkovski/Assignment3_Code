import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json
import requests

clients_lock = threading.Lock()
connected = 0

#local host
#serverIP = '127.0.0.1'

#amazonserver
serverIP = 'ec2-107-23-106-111.compute-1.amazonaws.com'
gamesPlayed = 0
numGamesToPlay = 0
def connectionLoop(sock):
   global gamesPlayed
   global numGamesToPlay
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)

      if gamesPlayed < numGamesToPlay:
         if 'gameMatch' in data:
            print("Game Match Data received:")
            #print(data)
            data = data[2:-1]
            matchData = json.loads(data)
            print(matchData)
            SimulateGame(matchData)
            #print(type(matchData))
            
            gamesPlayed +=1
      
     
         if 'update' in data:
            #print(data)
            #data = data[2:-1]
            #print(data)
            #cleanData = data.replace("update", "", 1).replace("\\", "")
            #print(cleanData)
         # msg = json.loads(cleanData)
            #print(msg['posX'])
            
            print("received update")
      #else:
         #print("games finished")

def SimulateGame(matchData):
   time = str(datetime.now())
   player1 = matchData['player1']
   player2 = matchData['player2']
   player3 = matchData['player3']
   matchID = matchData['matchID']
   winner = random.randint(0,2)

   player1Data = GetPlayer(player1['player_id'])
   print(player1Data)
   player2Data = GetPlayer(player2['player_id'])
   print(player2Data)
   player3Data = GetPlayer(player3['player_id'])
   print(player3Data)

   f = open("GameResults.txt", "a")
   f.write("Game ID: " + matchID + " started at " + time + "\n")
   f.write("Player 1 ID: " + player1['player_id'] + " connected to server at " + player1['timeConnected']+ "\n")
   f.write("Player 2 ID: " + player2['player_id'] + " connected to server at " + player2['timeConnected']+ "\n")
   f.write("Player 3 ID: " + player3['player_id'] + " connected to server at " + player3['timeConnected']+ "\n")
   f.write("Player 1 Rating Level Prior to game: " + player1Data['rating']+ "\n")
   f.write("Player 2 Rating Level Prior to game: " + player2Data['rating']+ "\n")
   f.write("Player 3 Rating Level Prior to game: " + player3Data['rating']+ "\n")
   
   player1Rating = int(player1Data['rating'])
   Player2Rating = int(player2Data['rating'])
   player3Rating = int(player3Data['rating'])

   player1NewRating = 0
   player2NewRating = 0
   player3NewRating = 0

   #print("Match " + matchID + " at " + time + " finished")
   if winner == 0:
      f.write("Player 1 Won the Game"+ "\n")
      player1NewRating = CalulateNewRating(player1Rating, (Player2Rating + player3Rating)/2, True )
      player2NewRating = CalulateNewRating(Player2Rating, player1Rating, False )
      player3NewRating = CalulateNewRating(player3Rating, player1Rating, False )
   #   print("player 1 wins with ID: " + player1['player_id'] + " and connected at time: " + player1['timeConnected'])
   elif winner == 1:
      f.write("Player 2 Won the Game"+ "\n")
      player1NewRating = CalulateNewRating(player1Rating, Player2Rating, False )
      player2NewRating = CalulateNewRating(Player2Rating, (player1Rating + player3Rating)/2, True)
      player3NewRating = CalulateNewRating(player3Rating, Player2Rating, False )
   #   print("player 2 wins with ID: " + player2['player_id'] + " and connected at time: " + player2['timeConnected'])
   elif winner == 2:
      f.write("Player 3 Won the Game"+ "\n")
      player1NewRating = CalulateNewRating(player1Rating, player3Rating, False )
      player2NewRating = CalulateNewRating(Player2Rating, player3Rating, False)
      player3NewRating = CalulateNewRating(player3Rating, (player1Rating + Player2Rating)/2, True )
   #   print("player 3 wins with ID: " + player3['player_id'] + " and connected at time: " + player3['timeConnected'])
   
   UpdatePlayer(player1['player_id'], str(player1NewRating))
   UpdatePlayer(player2['player_id'], str(player2NewRating))
   UpdatePlayer(player3['player_id'], str(player3NewRating))

   f.write("Player 1 Rating Level after the game: " + str(player1NewRating)+ "\n")
   f.write("Player 2 Rating Level after the game: " + str(player2NewRating)+ "\n")
   f.write("Player 3 Rating Level after the game: " + str(player3NewRating)+ "\n")
   
   f.write("\n"+ "\n"+ "\n")
   f.close()

def CalulateNewRating(playerARating, playerBRating, playerAWon) -> int:
   Qa = 10**(playerARating/400)
   Qb = 10**(playerBRating/400)
   kFactor = 32
   Ea = Qa/(Qa + Qb)
   Eb = Qb/(Qa + Qb)
   Sa = 0
   if playerAWon:
      Sa = 1
   newARating = playerARating + kFactor*(Sa- Ea)
   return round(newARating)



def GetPlayer(playerNum) -> dict:
   baseurl = "https://45rtmqywf1.execute-api.us-east-1.amazonaws.com/default/getPlayerInformation"
   queryParams = {"player_id" : playerNum}
   resp = requests.get(baseurl, json=queryParams)
   respBody = json.loads(resp.content)
   return respBody

def GetAllPlayers() -> list:
   baseurl = "https://5b1gf1tmai.execute-api.us-east-1.amazonaws.com/default/getAllPlayersInfo"
   resp = requests.get(baseurl)
   respBody = json.loads(resp.content)
   return respBody

def UpdatePlayer(playerId, rating):
   baseurl = "https://uq7yugn1i2.execute-api.us-east-1.amazonaws.com/default/updatePlayerRating"
   queryParams = {"player_id" : playerId, "rating" : rating}
   resp = requests.get(baseurl, json=queryParams)

def gameLoop(sock):
   global gamesPlayed
   global numGamesToPlay
   while True:
      if gamesPlayed < numGamesToPlay:
         clients_lock.acquire()

         playerNum = random.randrange(1001, 1011)
         message = {"type" : "add", "player_id": str(playerNum)}
         m = json.dumps(message)
         sock.sendto(bytes(m,'utf8'), (serverIP,12345))

         #game logic here
         #print("game stuff happening")
         #send the heartbeat
         sock.sendto(bytes("heartbeat",'utf8'), (serverIP,12345))
         clients_lock.release()
      time.sleep(1)



def main():
   global numGamesToPlay
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   
   f = open("GameResults.txt", "w")
   f.write("")
   f.close()

   numGames = input("Please enter how many games to play: ")
   numGamesToPlay = int(numGames)
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))


   message = {"type" : "connect"}
   m = json.dumps(message)
   s.sendto(bytes(m,'utf8'), (serverIP,12345))

   while True:
      time.sleep(1)



if __name__ == '__main__':
   main()
