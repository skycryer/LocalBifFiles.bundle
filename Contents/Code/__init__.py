import re
import os
from lxml import etree
import urllib2
import urllib
import subprocess

PREFIX = '/agents/localbiffiles'
NAME = 'localBifLoader'
APPGUID = 'localBifLoader-2015'
VERSION = '0.1'

def Start():

	token = getToken(userName, userPwd)
	Log.Debug('Token: ' + token)
	# Switch of auto indexing of libraries, sadly, framework only supports GET, so need to use urllib2
	opener = urllib2.build_opener(urllib2.HTTPHandler)
	request = urllib2.Request('http://127.0.0.1:32400/:/prefs?GenerateIndexFilesDuringAnalysis=0')
	request.get_method = lambda: 'PUT'
	#url = opener.open(request)
		
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
		sTargetDir = os.path.join(Core.app_support_path, 'Media', 'localhost', myMediaHash[:1] , myMediaHash[1:] + '.bundle', 'Contents', 'Indexes')
		#Log.Debug('Target Directory is : %s' %(sTargetDir))
		root_file = os.path.dirname(parts[0].file)
		#Log.Debug('root file: ' + root_file)
		indexPath = os.path.join(root_file, 'index-sd.bif')
		#Log.Debug('index path: ' + indexPath)
		#check if index file exists in folder
		if os.path.isfile(indexPath):
			Log.Debug('index bif exists')
			Log.Debug('index path: ' + indexPath)
			Log.Debug('target path: ' + sTargetDir)
			# Create target dir if it doesn't exists
			if not os.path.exists(sTargetDir):
				os.makedirs(sTargetDir)
			
			#copy index file to destination folder
			subprocess.Popen('copy "'+indexPath + '" "' + sTargetDir + '"')
			Log.Debug('copy "'+indexPath + '" "' + sTargetDir + '"')
			#shutil.copyfile(indexPath, sTargetDir)
			#Add2Db(myMediaID)
		
####################################################################################################
# This will add the newly placed index to the database
####################################################################################################
def Add2Db(myMediaID):
	opener = urllib2.build_opener(urllib2.HTTPHandler)
	#Enable Index Generation
	request = urllib2.Request('http://127.0.0.1:32400/:/prefs?GenerateIndexFilesDuringAnalysis=1')
	request.get_method = lambda: 'PUT'
	url = opener.open(request)
	#Analyze media
	request = urllib2.Request('http://127.0.0.1:32400/library/metadata/' + myMediaID + '/analyze')
	request.get_method = lambda: 'PUT'
	url = opener.open(request)
	#Disable Indexing
	request = urllib2.Request('http://127.0.0.1:32400/:/prefs?GenerateIndexFilesDuringAnalysis=0')
	request.get_method = lambda: 'PUT'
	url = opener.open(request)
	
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
