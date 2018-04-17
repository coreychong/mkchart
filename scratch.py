#!/usr/bin/python
'''
Deprecated imports???
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
import plotly.offline as offline
from plotly.graph_objs import Scatter, Layout
init_notebook_mode()
'''

'''

Stuff to-do: 

*Truncate or adjust scaling of y axis
	-Also some pretty printing

*Eye pleasing color palate
	-Make it easier to difference adjacent bars/data points

*Display available capacity 
	-Perhaps in-fill bar with proportional amount
	 then print the bytes in/on top of bar

*Add support for tracking past data
	-Write to text file and render on demand?
	-Decaying histogram?
		Maybe shoulder-to-shoulder with diminishing opacity






'''






from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from plotly.graph_objs import Scatter, Figure, Layout, Bar

import subprocess




def getValidVol():
#Returns a list of valid partitions from file... 
#Expect this to be replaced by more graceful subprocess call
#Or perhaps add arguments to add/remove valid volumes? Change mode to r+ in that case


	with open("valid_vols.txt") as f:
	
		return f.readline().strip("\n").split(",")


def readVol(validVolumes): 

	#Currently grabs a list of mounted partitions
	
	pTable = []
	df = subprocess.Popen(["df", "-h"], stdout=subprocess.PIPE)
	for line in df.stdout: 
		line = line.split()
		
		for v in validVolumes: 
			if v in line[0]:
				pTable.append(line)
	
	return pTable
	 


def main(): 
	
	pTable = readVol(getValidVol())

	dict = {}

	for x in pTable:  
		print x
		dict[x[-1].replace('/Volumes/', '').strip('/')] = int(x[4].strip("%"))
 	
 	x = []
 	y = []
	for i in sorted(dict.keys()): 
		x.append(i)
		y.append(dict[i])


	#x = sorted([i[-1].replace('/Volumes/', '').strip('/') for i in pTable], key=str.lower)
	#y = [int(i[4].strip("%")) for i in pTable]
	layout = Layout(
    	showlegend=True,
    	height=600,
    	width=600,
	)
	plot([Bar(x=x,y=y)])
	#plot([Bar(x=x, y=y )])
'''
	for i in pTable:
		print i


	test = Scatter(
		x = pTable[:][4],
		y = pTable[-1], 
		mode = 'markers',
		markers = dict(size=[40, 60, 80, 100])
	)
	
	data = [test]
	layout = Layout(
    	showlegend=False,
    	height=600,
    	width=600,
	)

	fig = dict(data=data,layout=layout)
	iplot(fig)


	#plotly.offline.plot({
    #	"data": [Scatter(x=[1, 2, 3, 4], y=[4, 3, 2, 1])],
    #	"layout": Layout(title="hello world")
	#})
'''




main()