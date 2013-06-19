#mobile Traffic Statistics


##Introduction

This is the source of an experiment setup I'm using to do statistical analysis of mobile handheld device traffic. 
Please feel free to use this sofware in whatever way you like.

I cannot guarantee that this software will work for you out of the box. You will have to read (I'm sorry for that ;) ) and understand my code in order to be able to use it.

##Repo Content

###interception
	startup.sh:
script for interception gatway. it might be necessary to adjust IP and gateway

###masterController
	master_controller.sh:
script which controlls the DUTs. It might be required to adjust the global variables accordingly to your setup.

	top500.txt:
list of homepages 

	nma.sh:
Client for [Notify my Android](http://www.notifymyandroid.com/). This piece of software pushes a notification to your smartphone whenever an experiment is ready. Please make sure to enter service's your API Key!

###trafficAnalyzer
Software in this directory is used for traffic analysis and plot creation.

	multi_analyzer.py:

takes a pcap file as argument, processes it and stores the result in an sqlite file.

	sqlAnalyzer.py:
takes the sqlite database from the muli_analyzer script as input and creates plots. The result can be found in multipage.pdf

switches:

	-f:
the sqlite file
	-d:
turns on dns reverse lookup for every connection (in-addr.arpa)
	-c:
computes the cdn plots

	eperiment_merger.py:
super hacker code for merging and averaging several sqlite files. Don't look at it. Seriously.