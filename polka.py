import requests
import csv
import time

apikeys = ['9543874b-46f8-4978-b005-3f18511fed2b',
		   'c974f3f8-e0d3-4ab8-8a16-a374ef687078',
		   '717b783d-b294-4726-8921-f0ea500e0614',
		   'f020737e-ceb0-45c6-b91d-cdcaf56b93e9',
		   'c974f3f8-e0d3-4ab8-8a16-a374ef687078',
		   '03c141d7-787f-4910-a6fb-6e025d391103',
		   'c87fb723-cf94-4643-8354-cfd153c0c5a5',
		   'eaac3b4d-8caf-49ac-9a38-55fe6f8284c5',
		   'fe37244a-9efd-4681-becb-54009710f60d',
		   '8c031716-2dab-41a0-94e4-ac1262108456',
		   '19893bfe-fdfa-4af8-b10a-cc74ae65de73',
		   '9d66e974-0384-4aac-9fba-815306cbd424',
		   '19f1278e-4d80-4096-9090-7c8896512432',
		   '7c9cb67e-ee07-4b8f-96cf-8b16d93f708e'
		  ]

keyCounter = 0

def getKey():
	global keyCounter
	#if keyCounter >= len(apikeys)*10 :
	#	keyCounter = 0
		#time.sleep(10)
	key = apikeys[keyCounter%len(apikeys)]
	#print keyCounter
	keyCounter = keyCounter + 1
	return key


def getMatchInfo(matchId, outcsv, outfile):
	outputRow = []
	key = getKey()
	print key
	req = 'https://na.api.pvp.net/api/lol/na/v2.2/match/'+str(matchId) + '?api_key='+ key

	result = requests.get(req)
	while result.status_code == 429:
		print result.headers
		print result
		time.sleep(2)
		result = requests.get(req)
		
	if result.status_code != 200:
		print result.status_code
		print 'mid:', matchId
		print 'bad status code'
		return

	res = result.json()
	outputRow.append(matchId)
	outputRow.append(res['matchDuration'])
	outputRow.append(res['matchVersion'])

	blueChamps = []
	redChamps = []
	for participant in res['participants']:
		if participant['teamId'] == 100:
			blueChamps.append(participant['championId'])
		else:
			redChamps.append(participant['championId'])
	for blueId in blueChamps:
		outputRow.append(blueId)
	for redId in redChamps:
		outputRow.append(redId)

	blueBans = []
	redBans = []
	redWinner = 0

	for team in res['teams']:
		if team['teamId'] == 100:
			if 'bans' in team:
				for banChamp in team['bans']:
					blueBans.append(banChamp['championId'])
			while len(blueBans) < 3:
				blueBans.append('')
		else:
			if team['winner'] == True:
				redWinner = 1
			if 'bans' in team:
				for banChamp in team['bans']:
					redBans.append(banChamp['championId'])
			while len(redBans) < 3:
				redBans.append('')

	for blueBanId in blueBans:
		outputRow.append(blueBanId)
	for redBanId in redBans:
		outputRow.append(redBanId)

	outputRow.append(redWinner)

	outcsv.writerow(outputRow)

	outfile.flush()



def runFromCsv(csvfilename, outcsv, outfile, begRow, endRow):
	with open(csvfilename, 'rb') as csvfile:
		idReader = csv.reader(csvfile)
		#remove header
		next(idReader)
		for i in range(1, begRow):
			next(idReader)

		it = 0
		for row in idReader:
			if begRow + it > endRow:
				break
			matchId = row[0]
			getMatchInfo(matchId, outcsv, outfile)
			it += 1

matchesOutFile = open('matches3000-3999.csv', 'wb')
matchCsvWriter = csv.writer(matchesOutFile)
matchCsvWriter.writerow(['MatchId', 'MatchDuration', 'MatchVersion', 'BluePick1', 
	'BluePick2','BluePick3','BluePick4','BluePick5', 'RedPick1', 'RedPick2', 'RedPick3',
	'RedPick4', 'RedPick5', 'BlueBan1', 'BlueBan2', 'BlueBan3', 'RedBan1', 'RedBan2', 'RedBan3',
	'RedWinner'])
runFromCsv('matchIds.csv', matchCsvWriter, matchesOutFile, 3000,3999)

#getMatchInfo(1948599197, matchCsvWriter, matchesOutFile)



