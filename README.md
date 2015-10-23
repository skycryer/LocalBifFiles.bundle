Local Media Index File Scanner for Plex
==================
This scanner is for Plex Media Server

This scanner copies your local media index file (index-sd.bif) from your Movie Folder to your Plex Server.

I liked the idea of the index files, but they need long time to generate and backing up is not that easy. Restore is also a big problem. 
For backup i have only a php script running at the moment, you can find it here on gitHub too. 

To restore your index files this scanner will help you. 

It is a first version so please be aware of bugs. But on testing it, i could not find them, maybe i am code blind. All developers will know that ;-).

Please use this on your own risk.

If you find a bug or have suggestions please post them [on the Plex Forum](https://forums.plex.tv/discussion/189092/plex-media-index-file-local-scanner?new=1)  


Installation
------------
- Just copy the bundle into the Plugin Folder and then add username and password to the config
- Config your Agents to use the new scanner with your library
- For existing Media you need to make a Refresh all, for new Media you do not need to Refresh

Username and Password are need to generate the token to communicate with Plex Server.

Information about where to find the plugin folder can be found [here](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-)  
