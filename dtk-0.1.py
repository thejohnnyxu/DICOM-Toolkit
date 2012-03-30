#!/usr/bin/python

import sys, os, dicom, sqlite3, wx

# ------------------------------
dicm	= {}
aggAtr	= []
uAgg	= []
nAgg	= []
flagged	= []
# ------------------------------
# ------------------------------
# Generic Remove Method
def rmgeneric(path, __func__):
	ERROR_STR= """Error removing : %(path)s, %(error)s """
	
	try: 
		__func__(path)
		print 'Removed ', path
	except OSError, (errno, strerror):
		print ERROR_STR % {'path' : path, 'error': strerror}

# ------------------------------		  
# Cleans up after the script	  
def cleanFolders(path):
	if not os.path.isdir(path):
		return
	
	files=os.listdir(path)
	
	for x in files:
		fullpath=os.path.join(path, x)
		if os.path.isdir(fullpath):
			cleanFolders(fullpath)
			f=os.rmdir
			rmgeneric(fullpath, f)

# ------------------------------
# ------------------------------
# Nullifies all fields not in keep list
def clean(dataset):
	global oPath, nAgg, filename, flagged, root
	
	newdir	= oPath + root
	listing	= os.walk(oPath)

	# Checks agaist keep list then nullifies anything not in the keep list
	for data_element in dataset:
		for tag in flagged:
			if data_element.name == tag:
				data_element.value = ''
	
	print listing
	
	for dirs in listing:
		for subdir in dirs:
			if not os.path.exists(newdir):
				os.makedirs(newdir)
	
	# Saves the altered file to a new directory	
	dataset.save_as(newdir + '/' + filename)
	print 'Saved: ' + filename
# ------------------------------
# Creates a header for the spreadsheet
def exportHeader():
	global atr, val, aggAtr, uKey, dicm, key, header
	
	header = []
	
	# Uniqifies the aggregate list
	for atr in aggAtr:
		if atr not in header:
			header.append(stripExport(atr))	
	# Prints out each unique header field
	for atr in header:
		FILE.write(atr + "\t")
	
	FILE.write('\n')

# ------------------------------
# Builds the spreadsheet
def exportContent():
	global atr, val, aggAtr, uKey, dicm, key, header, atrb, FILE
	
	print "Building Spreadsheet..."
	
	for key in dicm:
		for e in header:
			# creates the uKey
			atrb = key + "_" + e
			# Aligns the attributes with the header
			if atrb[len(key) + 1:] in header:
				# if key exists then proceed
				if atrb in dicm[key].keys():
					FILE.write(dicm[key][atrb] + '\t')
				else:
					FILE.write('\t')				
			else:
				FILE.write('\t')
		FILE.write('\n')
		
	print "...Done!"

# ------------------------------
# Builds the Hash
def buildHash(dataset):
	global atr, val, aggAtr, uKey, dicm, key, uAgg
		
	for data_element in dataset:
		atr = data_element.name
		val = repr(data_element.value)

		# truncates data values that are too long
		if len(val) > 100:
			val = "TOO LONG"
		
		atr = stripExport(atr).lower()
		val = stripExport(val)
		
		# Creates an aggregate list of all Attributes	
		aggAtr.append(atr)
		
		# Creates key for Attributes
		uKey = key + "_" + atr
		
		# Sets the value for each uKey
		dicm[key][uKey] = val
		
	for x in aggAtr:
		x = stripExport(x)
		if x not in uAgg:
			uAgg.append(x)
	
	print "Hashing : " + key	
	
# ------------------------------	
# Strips a string of all characters in the remove list and replaces a space with _
def stripDB(el):

	remove = ["'", "[", "]", "\"", "(", ")", "-", ".", "{", "}"]

	for char in remove:
		el = el.replace(char, "")

	el = el.replace(" ", "_")
	return el

def stripExport(el):

	remove = ["\'", "[", "]", "\""]
	for char in remove:
		el = el.replace(char, "")

	el = el.replace(" ", "_")

	return el
	
# ------------------------------
class Sanitize(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.parents = self.GetParent()
	
		self.hbox	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA1	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxB1	= wx.BoxSizer(wx.HORIZONTAL)
		
		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB1	= wx.BoxSizer(wx.VERTICAL)
		
		self.cusbtn = wx.Button(self, 101, "Customize", size=(150,50))
		self.sanbtn = wx.Button(self, 102, "Sanitize", size=(150,50))
		
		self.checklist = wx.CheckListBox(self, 111, size=(600,400), choices=[],style=0)

		# Layout
		self.hbox.Add(self.vboxA, 0, wx.ALL, 10)
		self.hbox.Add(self.vboxB, 0, wx.ALL, 10)
		self.vboxA.Add(self.hboxA1)
		self.vboxB.Add(self.hboxB1)
		self.vboxB.Add(self.vboxB1)
		self.hboxA1.Add(self.checklist)
		self.hboxB1.AddSpacer((1,340))
		self.vboxB1.Add(self.cusbtn)
		self.vboxB1.Add(self.sanbtn, 0, wx.TOP, -10)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.customize, id=101)
		self.Bind(wx.EVT_BUTTON, self.sanitize, id=102)
		wx.EVT_CHECKLISTBOX(self, self.checklist.GetId(), self.onCheck)
	
		self.SetSizer(self.hbox)
		
	# Handlers
	def customize(self, event):
		global uAgg, nAgg, listing, dicm, ds, key, dirname, dirs, files
		
		for dirname, dirs, files in listing:
			for filename in files:
				if filename.endswith('.dcm') or filename.endswith('.DCM'):
					key = filename.replace('.dcm', '')
					ds	= dicom.read_file(dirname +'/'+ filename)
					dicm[key] = {}
					buildHash(ds)
		
		self.checklist.InsertItems(items=uAgg, pos=0)
	
	def onCheck(self, event):
		global nAgg
		
		id = event.GetSelection()
		name = self.checklist.GetString(id)
		
		nAgg.append(name)
		
	def getChecked(self):
		global nAgg, flagged

		for i in range(self.checklist.GetCount()):
			if self.checklist.IsChecked(i):
				flagged.append(self.checklist.GetString(i))

	def sanitize(self, event):
		global path, filename, root
		
		self.getChecked()
		
		listing = os.walk(path)

		for dirname, dirs, files in listing:
			for filename in files:
				if filename.endswith('.dcm') or filename.endswith('.DCM'):
					ds = dicom.read_file(dirname +'/'+ filename)
					root = os.path.relpath(dirname)
					clean(ds)
					
		cleanFolders(oPath)

# ------------------------------
class Anonymize(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
	
		self.container	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA1	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA2	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA3	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA4	= wx.BoxSizer(wx.HORIZONTAL)

		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.vboxA5	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB1	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB2 = wx.BoxSizer(wx.VERTICAL)
		

# ------------------------------
class Update(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

# ------------------------------
class Database(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

# ------------------------------
class Export(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.hbox	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA1	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA2	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA3	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxA4	= wx.BoxSizer(wx.HORIZONTAL)
		self.hboxB1	= wx.BoxSizer(wx.HORIZONTAL)
		
		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB1	= wx.BoxSizer(wx.VERTICAL)
	
		self.st1 = wx.StaticText(self, 0, "Output Filename:")
		self.fileout = wx.TextCtrl(self, 0, '', size=(600,25))
		
		self.txtbtn = wx.Button(self, 601, "Generate TXT", size=(150,50))
		self.csvbtn = wx.Button(self, 602, "Generate CSV", size=(150,50))
		
		self.filename = self.fileout.GetValue()
		
		# Layout
		self.hbox.Add(self.vboxA, 0, wx.ALL, 10)
		self.hbox.Add(self.vboxB, 0, wx.ALL, 10)
		self.vboxA.Add(self.hboxA1)
		self.vboxA.Add(self.hboxA2)
		self.vboxB.Add(self.hboxB1)
		self.hboxB1.AddSpacer((1,340))
		self.vboxB.Add(self.vboxB1)
		self.hboxA1.Add(self.st1)
		self.hboxA2.Add(self.fileout)
		self.vboxB1.Add(self.txtbtn)
		self.vboxB1.Add(self.csvbtn, 0, wx.TOP, -10)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.genText, id=601)
		self.Bind(wx.EVT_BUTTON, self.genCsv, id=602)

		self.SetSizer(self.hbox)
	
	# Handlers
	def genText(self, event):
		global oPath, listing, key, ds, dicm, filename, FILE
		
		self.oFile = oPath + self.fileout.GetValue() + '.txt'
		
		FILE = open(self.oFile, 'wb')

		for dirname, dirs, files in listing:
			for filename in files:
				if filename.endswith('.dcm') or filename.endswith('.DCM'):
					key = filename.replace('.dcm', '')
					ds 	= dicom.read_file(dirname +'/'+ filename)
					dicm[key] = {}
					buildHash(ds)

		exportHeader()
		exportContent()
		
	def genCsv(self, event):
		global oPath, listing, key, ds, dicm, filename, FILE
		
		self.oFile = oPath + self.fileout.GetValue() + '.csv'
		
		FILE = open(self.oFile, 'wb')

		for dirname, dirs, files in listing:
			for filename in files:
				if filename.endswith('.dcm') or filename.endswith('.DCM'):
					key = filename.replace('.dcm', '')
					ds 	= dicom.read_file(dirname +'/'+ filename)
					dicm[key] = {}
					buildHash(ds)

		exportHeader()
		exportContent()
		
# ------------------------------
class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="DICOM Toolkit", size=(800,600))
		
		panel = wx.Panel(self)
		
		self.panel_one	= Sanitize(panel)
		self.panel_two	= Anonymize(panel)
		self.panel_three= Update(panel)
		self.panel_four	= Database(panel)
		self.panel_five	= Export(panel)

		self.vbox	= wx.BoxSizer(wx.VERTICAL)
		self.hbox1	= wx.BoxSizer(wx.HORIZONTAL)
		self.hbox2	= wx.BoxSizer(wx.HORIZONTAL)
		self.hbox3	= wx.BoxSizer(wx.HORIZONTAL)
		self.hbox4	= wx.BoxSizer(wx.HORIZONTAL)
		self.hbox5	= wx.BoxSizer(wx.HORIZONTAL)
		self.hbox6	= wx.BoxSizer(wx.HORIZONTAL)
		self.hbox7	= wx.BoxSizer(wx.HORIZONTAL)
		self.hbox8	= wx.BoxSizer(wx.HORIZONTAL)
		
		self.st1 = wx.StaticText(panel, 0, 'Source Directory:')
		self.st2 = wx.StaticText(panel, 0, 'Output Directory:')
		
		self.srcbtn		= wx.Button(panel, 101, 'Select Source', size=(150,25))
		self.destbtn	= wx.Button(panel, 102, 'Select Output', size=(150,25))
		self.sanbtn		= wx.Button(panel, 103, 'Sanitize', size=(160,30))
		self.anonbtn	= wx.Button(panel, 104, 'Anonymize', size=(160,30))
		self.upbtn		= wx.Button(panel, 105, 'Update', size=(160,30))
		self.dbbtn		= wx.Button(panel, 106, 'Database', size=(160,30))
		self.expbtn		= wx.Button(panel, 107, 'Export', size=(160,30))
		
		self.tc1 = wx.TextCtrl(panel, -1, '', size=(600,25))
		self.tc2 = wx.TextCtrl(panel, -1, '', size=(600,25))
		
		self.line1 = wx.StaticLine(panel, -1, size=(800,1))
		self.line2 = wx.StaticLine(panel, -1, size=(800,1))
		
		# Layout
		self.hbox1.Add(self.st1, 0, wx.LEFT, 10)
		self.hbox2.Add(self.tc1, 0, wx.LEFT, 10)
		self.hbox2.Add(self.srcbtn, 0, wx.LEFT, 20)
		self.hbox3.Add(self.st2, 0, wx.LEFT, 10)		
		self.hbox4.Add(self.tc2, 0, wx.LEFT, 10)
		self.hbox4.Add(self.destbtn, 0, wx.LEFT, 20)
		self.hbox5.Add(self.line1, 0, wx.LEFT, 0)
		self.hbox6.Add(self.sanbtn, 0, wx.LEFT, 0)
		self.hbox6.Add(self.anonbtn, 0, wx.LEFT, 0)
		self.hbox6.Add(self.upbtn, 0, wx.LEFT, 0)
		self.hbox6.Add(self.dbbtn, 0, wx.LEFT, 0)
		self.hbox6.Add(self.expbtn, 0, wx.LEFT, 0)
		self.hbox7.Add(self.line2, 0, wx.LEFT, 0)
		
		self.vbox.Add(self.hbox1, 0, wx.TOP, 5)
		self.vbox.Add(self.hbox2, 0, wx.TOP, 2)
		self.vbox.Add(self.hbox3, 0, wx.TOP, 5)
		self.vbox.Add(self.hbox4, 0, wx.TOP, 2)
		self.vbox.Add(self.hbox5, 0, wx.TOP, 10)
		self.vbox.Add(self.hbox6, 0, wx.TOP, 10)
		self.vbox.Add(self.hbox7, 0, wx.TOP, 0)
		self.vbox.Add(self.panel_one, 0, wx.EXPAND, 0)
		self.vbox.Add(self.panel_two, 0, wx.EXPAND, 0)
		self.vbox.Add(self.panel_three, 0, wx.EXPAND, 0)
		self.vbox.Add(self.panel_four, 0, wx.EXPAND, 0)
		self.vbox.Add(self.panel_five, 0, wx.EXPAND, 0)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.setSource,	id=101)
		self.Bind(wx.EVT_BUTTON, self.setDest,		id=102)
		self.Bind(wx.EVT_BUTTON, self.showP1,		id=103)
		self.Bind(wx.EVT_BUTTON, self.showP2,		id=104)
		self.Bind(wx.EVT_BUTTON, self.showP3,		id=105)
		self.Bind(wx.EVT_BUTTON, self.showP4,		id=106)
		self.Bind(wx.EVT_BUTTON, self.showP5,		id=107)
	
		panel.SetSizer(self.vbox)
		self.Centre()
		
	# Handlers
	def setSource(self, event):
		global oPath, listing, key, ds, dicm, path
		
		self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)

		if self.dlg.ShowModal() == wx.ID_OK:
			path = self.dlg.GetPath() + '/'
			self.tc1.SetValue(path)
			listing = os.walk(path)
		
		self.dlg.Destroy()
		
	def setDest(self, event):
		global oPath
	
		self.dlg = wx.DirDialog(self, "Choose the Output Directory:", style=wx.DD_DEFAULT_STYLE)
		
		if self.dlg.ShowModal() == wx.ID_OK:
			oPath = self.dlg.GetPath() + "/"
			self.tc2.SetValue(oPath)
		
		self.dlg.Destroy()

	def showP1(self, even):
		self.panel_one.SetPosition((0,148))
		self.panel_one.Show()
		self.panel_two.Hide()
		self.panel_three.Hide()
		self.panel_four.Hide()
		self.panel_five.Hide()
	def showP2(self, even):
		self.panel_two.SetPosition((0,148))
		self.panel_one.Hide()
		self.panel_two.Show()
		self.panel_three.Hide()
		self.panel_four.Hide()
		self.panel_five.Hide()
	def showP3(self, even):
		self.panel_three.SetPosition((0,148))
		self.panel_one.Hide()
		self.panel_two.Hide()
		self.panel_three.Show()
		self.panel_four.Hide()
		self.panel_five.Hide()
	def showP4(self, even):
		self.panel_four.SetPosition((0,148))
		self.panel_one.Hide()
		self.panel_two.Hide()
		self.panel_three.Hide()
		self.panel_four.Show()
		self.panel_five.Hide()
	def showP5(self, even):
		self.panel_five.SetPosition((0,148))
		self.panel_one.Hide()
		self.panel_two.Hide()
		self.panel_three.Hide()
		self.panel_four.Hide()
		self.panel_five.Show()

# ------------------------------
# ------------------------------
# ------------------------------
if __name__ == "__main__":
	app = wx.App(0)
	MainFrame().Show()
	app.MainLoop()
	
