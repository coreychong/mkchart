#!/usr/bin/python
'''

Corey Chong

Dependencies:
	*pip
	plotly
	pexpect
	tempfile


'''
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#from plotly.graph_objs import Bar, Figure, Layout as go
import plotly.graph_objs as go


#from subprocess import Popen, PIPE

import pexpect
import tempfile
import time

DEBUG = True

'''
to-do:
    -Add bron volumes to valid_vols.txt
    -Use better palette scheme for graph
    -More graceful charting library with fewer dependencies?
        * Plotly (heavy)
        * Pillow (light)
        * Matlib (kinda yucky)
    -Better way to map volume string to values (immutable)
        * Bind them from the ssh() call?
        * Currently returns a big string block
        * Could parse them from separate from multiple calls
            -From valid volumes file grep the df call 
            -Probably will take a performance hit...
'''




def getValidVol(): 
	with open("valid_vols.txt") as f: 
		return f.readline().strip("\n").split(",")





def ssh(host, cmd, user, password, timeout=30, bg_run=False):
    """SSH's to a host using the supplied credentials and executes a command.
    Throws an exception if the command doesn't return 0.
    bgrun: run command in the background"""

    fname = tempfile.mktemp()
    fout = open(fname, 'w')

    if bg_run:
        options += ' -f'
    ssh_cmd = 'ssh %s@%s "%s"' % (user, host, cmd)
    child = pexpect.spawn(ssh_cmd, timeout=timeout)
    child.expect(['password: '])
    child.sendline(password)
    child.logfile = fout
    child.expect(pexpect.EOF)
    child.close()
    fout.close()

    fin = open(fname, 'r')
    stdout = fin.read()
    fin.close()

    if 0 != child.exitstatus:
        raise Exception(stdout)

    return stdout

def readVol(validVols):
	'''
	Returns a list of mounted partitions...
	Will remove argument at some point?
	df currently only returns filesystems of type xfs (tape) or nfs (local)
	'''
	pTable = []
	#df = subprocess.Popen(["df", "-h", "-t nfs", "-t xfs"], stdout=subprocess.PIPE)
	cmd = "df -h -t xfs | awk '{print $4, $5, $6}'"  
	#Turn these into arguments at some point
	df = ssh("tape08", cmd, "root","password")


	#Delimiting and garbage removal
	df = df.split("\n")
	df.remove('\r')
	df.remove('Avail Use% Mounted\r')
	df.remove('')
	for i in range(0,len(df)): 
		df[i] = df[i].split()
	for i in df: 
		i[2] = i[2].lstrip('/')
		i[2] = i[2].rstrip('\r')
		
	#Separates into [available space, capacity, partition]
	
	for volume in df:
		for v in validVols:
			if volume[2] in v: 
				pTable.append(volume)

	return pTable

def parseVolumes(): 
#Returns an unsorted dictionary of partions (key) bound to 
#a tuple of capacity and available disk space; container should not be mutable?
	pTable = readVol(getValidVol())
	volumes = {}
	
	for x in pTable: 
		volumes[x[2]] = (int(x[1].strip("%")), x[0])
		#volumes[x[2]] = (x[1], x[0])
							        #capacity, available	
	return volumes


def drawChart(vols): 
#Stats of each partition are now mutable, for more inter
	volumes = []
	capacity = []
	available = []



	for i in sorted(vols.keys()): 
		volumes.append(i)
		capacity.append(vols[i][0])#only prints the capacity
		available.append(vols[i][1])

	#CO3NY : SAN - Current Status $DAY $DATE $TIME
	#plot([Bar(x=x,y=y)])

	print volumes

	epis = go.Bar(
		x = [capacity[0], capacity[1], capacity[2], capacity[3]], 
		y = [volumes[0], volumes[1], volumes[2], volumes[3]],
		text = available, 

		marker = dict(
			color = 'rgb(255,105,180)',
			line = dict(
				width = 1.5,
				color = 'rgb(255,105,180))',
				)
		),
		opacity=0.6,
		orientation = 'h'
	)
		
	feat = go.Bar(
		x = [capacity[4], capacity[5], capacity[6], capacity[7]], 
		y = [volumes[4], volumes[5], volumes[6], volumes[7]],
		text = available, 
		marker = dict(
			color = 'rgb(102,102,255)',
			line = dict(
				width = 1.5,
				color = 'rgb(102,102,255)',
				)
		),
		opacity=0.6,
		orientation = 'h'
	)

	trex = go.Bar(
		x = [capacity[9], capacity[10], capacity[11]], 
		y = [volumes[9], volumes[10], volumes[11]],
		text = available, 
		marker = dict(
			color = 'rgb(255,105,180)',
			line = dict(
				width = 1.5,
				color = 'rgb(255,105,180)',
				)
		),
		opacity=0.6,
		orientation = 'h'
	)

	vrap = go.Bar(
		x = [capacity[13], capacity[14], capacity[15]], 
		y = [volumes[13], volumes[14], volumes[15]],
		text = available, 
		marker = dict(
			color = 'rgb(102,255,178)',
			line = dict(
				width = 1.5,
				color = 'rgb(102,255,178)',
				)
		),
		opacity=0.6,
		orientation = 'h'
	)

	mr_util = go.Bar(
		x = [capacity[8], capacity[12]], 
		y = [volumes[8], volumes[12]],
		text = available, 
		marker = dict(
			color = 'rgb(255,255,102)',
			line = dict(
				width = 1.5,
				color = 'rgb(255,255,102)',
				)
		),
		opacity=0.6,
		orientation = 'h'
	)
	data = [epis, feat, vrap, trex, mr_util]
	layout = go.Layout(title = "SAN - Current Status " + time.strftime("%Y-%m-%d %H:%M"))

	fig = go.Figure(data=data, layout=layout)
	#fig = tools.make_subplots(rows = 5, cols = 5, shared_xaxes = True)
	plot(fig)



#parseVolumes()
drawChart(parseVolumes())

