import requests
import json
import time
import csv
from Queue import Queue
from sets import Set

#huhi 61542283



keyCounter = 0
maxSummoners = 1000
summonersProcessed = 0
matchProcessed = 0

maxMatches = 100000

summonerQ = Queue()
matchQ = Queue()

seenSID = Set()
seenMID = Set()


apikeys = [#'9543874b-46f8-4978-b005-3f18511fed2b',
		   #'c974f3f8-e0d3-4ab8-8a16-a374ef687078',
		   #'717b783d-b294-4726-8921-f0ea500e0614',
		   #'f020737e-ceb0-45c6-b91d-cdcaf56b93e9',
		   #'c974f3f8-e0d3-4ab8-8a16-a374ef687078',
		   #'03c141d7-787f-4910-a6fb-6e025d391103',
		   #'c87fb723-cf94-4643-8354-cfd153c0c5a5',
		   'eaac3b4d-8caf-49ac-9a38-55fe6f8284c5',
		   'fe37244a-9efd-4681-becb-54009710f60d',
		   '8c031716-2dab-41a0-94e4-ac1262108456',
		   '19893bfe-fdfa-4af8-b10a-cc74ae65de73',
		   '9d66e974-0384-4aac-9fba-815306cbd424',
		   '19f1278e-4d80-4096-9090-7c8896512432',
		   '7c9cb67e-ee07-4b8f-96cf-8b16d93f708e'
		  ]

def getKey():
	global keyCounter
	if keyCounter >= len(apikeys)*10 :
		keyCounter = 0
		#time.sleep(10)
	key = apikeys[keyCounter/10]
	#print keyCounter
	keyCounter = keyCounter + 1
	return key


def extractSummoners(matchID, summonersProcessed):
	key = getKey()
	req = 'https://na.api.pvp.net/api/lol/na/v2.2/match/'+str(matchID) + '?api_key='+ key
	result = requests.get(req)
	if result.status_code != 200:
		print 'bad code when extracting matchID:', matchID
		return

	res = result.json()
	for r in res['participantIdentities']:
		newSummonerID = r['player']['summonerId']
		if newSummonerID not in seenSID:
			seenSID.add(newSummonerID)
			summonerQ.put(newSummonerID)
			summonersProcessed += 1
	return summonersProcessed

def getMatches(summonerID, maxSummoners, summonersProcessed):
	global matchProcessed
	key = getKey()

	req = ('https://na.api.pvp.net/api/lol/na/v2.2/matchlist/by-summoner/'+
		   str(summonerID)+
		   '?rankedQueues=RANKED_SOLO_5x5&seasons=SEASON2015&api_key='+
		   key)

	result = requests.get(req)

	if result.status_code != 200:
		print 'bad key:', key
		return

	matchlist = result.json()
	matches = matchlist['matches']

	maxSearch = 30

	for match in matches:
		if match['matchId'] in seenMID:
			continue
		print 'Summoners Processed:', summonersProcessed
		if summonersProcessed < maxSummoners and maxSearch >= 0:
			summonersProcessed = extractSummoners(match['matchId'], summonersProcessed)
			maxSearch -= 1
		seenMID.add(match['matchId'])
		matchProcessed += 1
		print matchProcessed

	return summonersProcessed


def incrementalSearch(startID):
	
	success = 0

	for i in range(0, 1000):
		key = getKey()
		req = 'https://na.api.pvp.net/api/lol/na/v2.2/match/' + str(startID+i) + '?api_key=' + key
		result = requests.get(req)
		if result.status_code != 200:
			print 'status_code != 200'
			startID +=5
			continue
		matchJson = result.json()
		if matchJson['queueType'] != 'RANKED_SOLO_5x5':
			print matchJson['queueType']
			startID +=5
			continue
		success = success + 1
		print success

	print 'matchID:', startID + i


#incrementalSearch(1706865970)

summonerQ.put(61542283)

while len(seenMID) <= maxMatches and not summonerQ.empty():
	nextSumID = summonerQ.get()
	summonersProcessed = getMatches(nextSumID, maxSummoners, summonersProcessed)

tmp = open('matchIds.csv', 'wb')
writer = csv.writer(tmp)
writer.writerow(['MatchId'])

for mid in seenMID:
	writer.writerow([mid])

#summonersProcessed = extractSummoners(1706865970, summonersProcessed)
#print summonersProcessed
#print seenSID

#req = 'https://na.api.pvp.net/api/lol/na/v2.2/match/1706865970?api_key=9543874b-46f8-4978-b005-3f18511fed2b'

#for i in range(0, 100):
#	getMatch(1)
#req = 'https://na.api.pvp.net/api/lol/na/v2.2/matchlist/by-summoner/65389099?rankedQueues=RANKED_SOLO_5x5&seasons=SEASON2015&api_key=9543874b-46f8-4978-b005-3f18511fed2b'
#result = requests.get(req)
#print result.status_code
#res = result.json()
#for r in res['participantIdentities']:
#	print r['player']['summonerId']
#print res['matches'][0]
#print type(result.json())
