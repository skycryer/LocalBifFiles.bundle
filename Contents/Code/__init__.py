import re
import os
import httplib, base64
import shutil

PREFIX = '/agents/localbiffiles'
NAME = 'localBifLoader'
APPGUID = 'localBifLoader-2015'
VERSION = '0.1'
TOKEN = getToken()

def Start():
	# Switch of auto indexing of libraries
	urlRequestToPlexServer('/:/prefs?GenerateIndexFilesDuringAnalysis=0')
	
class localbiffiles(Agent.Movies):
	name = 'Local Bif Files'
	languages = [Locale.Language.NoLanguage]
	primary_provider = False
	contributes_to = ['com.plexapp.agents.imdb', 'com.plexapp.agents.themoviedb', 'com.plexapp.agents.none']
  	# Satisfy the framework here
	def search(self, results, media, lang):
		results.Append(MetadataSearchResult(id='null', score = 100))
	
	def update(self, metadata, media, lang, force):
		#Start to work
		Log.Debug(media.title)
		GetMediaInfoMovie(media.id, media.title, media.items[0].parts)

@route(PREFIX + '/GetMediaInfoTV')		
def GetMediaInfoMovie(mediaID, myTitle, parts=[]):
	Log.Debug('Checking Movie media with an ID of : %s, and a title of : %s' %(mediaID, myTitle)) 
	myURL = 'http://127.0.0.1:32400'
	#Get the hash
	myNewURL = myURL + '/library/metadata/' + mediaID + '/tree'
	sections = XML.ElementFromURL(myNewURL).xpath('//MediaPart')
	
	for section in sections:
		myMediaHash = section.get('hash')
		#Log.Debug('The hash for media %s is %s' %(mediaID, myMediaHash))
		sTargetDir = os.path.join(Core.app_support_path, 'Media', 'localhost', myMediaHash[:1] , myMediaHash[1:] + '.bundle', 'Contents', 'Indexes', '')
		#Log.Debug('Target Directory is : %s' %(sTargetDir))
		root_file = os.path.dirname(parts[0].file)
		#path to local index file
		indexPath = os.path.join(root_file, 'index-sd.bif')
		#check if index file exists in folder
		if os.path.isfile(indexPath):
			Log.Debug('index path: ' + indexPath)
			Log.Debug('target path: ' + sTargetDir)
			# Create target dir if it doesn't exists
			if not os.path.exists(sTargetDir):
				os.makedirs(sTargetDir)
			
			#copy index file to destination folder
			shutil.copyfile(indexPath, os.path.join(sTargetDir, 'index-sd.bif'))
			Log.Debug('copy "'+indexPath + '" "' + sTargetDir + '"')
			Add2Db(mediaID)
		
####################################################################################################
# This will add the newly placed index to the database
####################################################################################################
def Add2Db(myMediaID):
	opener = urllib2.build_opener(urllib2.HTTPHandler)
	#Enable Index Generation
	urlRequestToPlexServer('/:/prefs?GenerateIndexFilesDuringAnalysis=1')
	#Analyze media
	urlRequestToPlexServer('/library/metadata/' + myMediaID + '/analyze')
	#Disable Indexing
	urlRequestToPlexServer('/:/prefs?GenerateIndexFilesDuringAnalysis=0')
	
#********** Get token from plex.tv *********
''' This will return a valid token, that can be used for authenticating if needed, to be inserted into the header '''
# DO NOT APPEND THE TOKEN TO THE URL...IT MIGHT BE LOGGED....INSERT INTO THE HEADER INSTEAD
route(PREFIX + '/getToken')
def getToken():
	userName = Prefs['Plex_User']
	userPwd = Prefs['Plex_Pwd']
	myUrl = 'https://plex.tv/users/sign_in.json'
	# Create the authentication string
	base64string = String.Base64Encode('%s:%s' % (userName, userPwd))
	# Create the header
	MYAUTHHEADER= {}
	MYAUTHHEADER['X-Plex-Product'] = NAME
	MYAUTHHEADER['X-Plex-Client-Identifier'] = APPGUID
	MYAUTHHEADER['X-Plex-Version'] = VERSION
	MYAUTHHEADER['Authorization'] = 'Basic ' + base64string
	MYAUTHHEADER['X-Plex-Device-Name'] = NAME
	# Send the request
	try:
		httpResponse = HTTP.Request(myUrl, headers=MYAUTHHEADER, method='POST')
		myToken = JSON.ObjectFromString(httpResponse.content)['user']['authentication_token']
		Log.Debug('Response from plex.tv was : %s' %(httpResponse.headers["status"]))
	except:
		Log.Critical('Exception happend when trying to get a token from plex.tv')
		Log.Critical('Returned answer was %s' %httpResponse.content)
		Log.Critical('Status was: %s' %httpResponse.headers)
		return ''			
	return myToken

def urlRequestToPlexServer(urlForCall):
	txdata = ""

	headers={'X-Plex-Client-Identifier': "Test script",
			'X-Plex-Product': "Test script 356546545",
			'X-Plex-Version': "0.001",
			'X-Plex-Token': TOKEN}
	conn = httplib.HTTPConnection("127.0.0.1:32400")
	conn.request("PUT",urlForCall,txdata,headers)
	response = conn.getresponse()
	print response.status, response.reason
	data = response.read()
	print str(data)
	conn.close()