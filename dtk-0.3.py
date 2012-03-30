#!/usr/bin/python

import sys, os, dicom, sqlite3, wx
		
# ------------------------------
class Process(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		global _cacheTags, _initialTags, _checkedTags, _removePrivate, _tempChecked
		
		_cacheTags		= []
		_checkedTags	= []
		_removePrivate	= False
		
		self.tagGroups	= ["0008", "0010 : Patient Information", "0012 : Clinical Information ", "0014", "0018", "0020", "0022", "0024", "0028",
						"0032", "0038", "003A", "0040", "0042", "0044", "0046", "0048", "0050",
						"0052", "0054", "0060", "0062", "0064", "0066", "0068", "0070", "0072",
						"0074", "0076", "0078", "0088", "0100", "0400", "1000", "1010", "2000",
						"2010", "2020", "2030", "2040", "2050", "2100", "2110", "2120", "2130",
						"2200", "3002", "3004", "3006", "3008", "300A", "300C", "300E", "4000",
						"4008", "4010", "4FFE", "50xx", "5200", "5400", "5600", "60xx", "7FE0",
						"7Fxx", "FFFA", "FFFC", "FFFE", "0002", "0004"]
		
		# Sizers
		self.container	= wx.BoxSizer(wx.VERTICAL)
		
		self.hboxA	= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxA1	= wx.BoxSizer(wx.VERTICAL)
		self.vboxA2	= wx.BoxSizer(wx.VERTICAL)
		self.hboxA3 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.hboxB	= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxB1	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB2	= wx.BoxSizer(wx.VERTICAL)
		self.hboxB3 = wx.BoxSizer(wx.HORIZONTAL)		
		
		# Buttons
		self.proBtn	= wx.Button(self, 101, "Process", size=(150,25))
		self.preBtn	= wx.Button(self, 102, "Previous Selection", size=(150,25))
		self.chgBtn	= wx.Button(self, 103, "Change", size=(150,25))
		self.addBtn	= wx.Button(self, 104, "Add", size=(75,25))
		self.rmvBtn	= wx.Button(self, 105, "Remove", size=(75,25))
				
		# Text Ctrl
		self.editTc	= wx.TextCtrl(self, -1, '', size=(450,25))
		self.addTc	= wx.TextCtrl(self, -1, '', size=(450,25))
		self.tagTc	= wx.TextCtrl(self, -1, 'Select a Tag', size=(450,25), style=wx.TE_READONLY)
		
		# Combo
		self.tagdrop = wx.ComboBox(self, 121, size=(600, 25), choices=self.tagGroups, style=wx.CB_READONLY)
		
		# Checkbox
		self.prvchk	= wx.CheckBox(self, 112, "Remove Private Tags")
		
		# List Box
		self.tagLBox = wx.ListBox(self, 131, size=(600,140), style=wx.TE_MULTILINE)
		
		# Check List Box
		self.checklist = wx.CheckListBox(self, 111, size=(600,280), choices=_cacheTags,style=0)

		# Layout
		self.container.Add(self.hboxA)
		self.container.AddSpacer((1,5))
		self.container.Add(self.hboxB)
		
		self.hboxA.Add(self.vboxA1, -1, wx.LEFT, 5)
		self.hboxA.Add(self.vboxA2, -1, wx.LEFT, 25)
		
		self.hboxB.Add(self.vboxB1, -1, wx.LEFT, 5)
		self.hboxB.Add(self.vboxB2, -1, wx.LEFT, 25)
		
		self.vboxA1.Add(self.prvchk)
		self.vboxA1.AddSpacer((1,2))
		self.vboxA1.Add(self.tagdrop)
		self.vboxA1.AddSpacer((1,2))
		self.vboxA1.Add(self.checklist)
		self.vboxA1.AddSpacer((1,2))
		self.vboxA1.Add(self.tagTc)
		self.vboxA1.Add(self.hboxA3)
		self.hboxA3.Add(self.editTc)
		self.hboxA3.Add(self.chgBtn)
		
		self.vboxA2.Add(self.preBtn, -1, wx.TOP, 20)
		
		self.vboxB1.Add(self.tagLBox)
		self.vboxB1.Add(self.hboxB3)
		self.hboxB3.Add(self.addTc)
		self.hboxB3.Add(self.addBtn)
		self.hboxB3.Add(self.rmvBtn)

		self.vboxB2.AddSpacer((1,140))
		self.vboxB2.Add(self.proBtn)
	
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.process,		id=101)
		self.Bind(wx.EVT_BUTTON, self.loadPrev,		id=102)
		self.Bind(wx.EVT_BUTTON, self.change,		id=103)
		self.Bind(wx.EVT_BUTTON, self.add,			id=104)
		self.Bind(wx.EVT_BUTTON, self.remove,		id=105)
		self.Bind(wx.EVT_CHECKLISTBOX, self.flag,	id=111)
		self.Bind(wx.EVT_CHECKBOX, self.privTags,	id=112)
		self.Bind(wx.EVT_COMBOBOX, self.onSelect,	id=121)
		self.Bind(wx.EVT_LISTBOX, self.clicked,		id=111)
	
		self.SetSizer(self.container)
		self.prvchk.SetValue(True)
		
	# Handlers
	def process(self, event):
		global sListing, root, filename, tPath, _checkedTags
		
		for dirname, dirs, files, in sListing:
			for filename in files:
				if filename.endswith('.dcm') or filename.endswith('.DCM'):
					ds = dicom.read_file(dirname +'/'+ filename)
					root = os.path.relpath(dirname)
					clearTags(ds)			
		
		SETTINGS = open('.settings.txt', 'wb')
		
		for tag in _checkedTags:
			SETTINGS.write(tag)
			
	def clicked(self, event):
		global focusedTag
		
		focusedTag = self.checklist.GetString(self.checklist.GetSelection())
					
		self.tagTc.SetValue(focusedTag)
		
	def change(self, event):
		global editTcValue
		
		editTcValue = self.editTc.GetValue()
		
		for dirname, dirs, files, in sListing:
			for filename in files:
				if filename.endswith('.dcm') or filename.endswith('.DCM'):
					ds = dicom.read_file(dirname +'/'+ filename)
					root = os.path.relpath(dirname)
					editTags(ds)
		
	def loadPrev(self, event):
		global _checkedTags

		_settings = open('.settings.txt', 'r').readlines()

		for line in _settings:
			_checkedTags.append(line)
		
	def onSelect(self, event):
		global _cacheTags, _initialTags, _checkedTags, _tempChecked
	
		self.selc	= self.tagdrop.GetValue()[:4]
		_checked	= self.checklist.GetChecked()
		_cacheTags	= []
		
		self.checklist.Clear()
			
		for pair in _initialTags:
			if pair[1:5] == self.selc:
				_cacheTags.append(pair[14:])
				
		self.checklist.InsertItems(items=_cacheTags, pos=0)
		
		for tag in _checkedTags:
			for tag2 in _cacheTags:
				for i in range(len(_cacheTags)):
					if tag == _cacheTags[i]:
						self.checklist.Check(i)
		
	def privTags(self, event):
		global _removePrivate
		
		if self.prvchk.GetValue():
			_removePrivate = True
		else:
			_removePrivate = False
		
	def flag(self, event):
		global _checkedTags
		
		self.id		= event.GetSelection()
		self.tag	= self.checklist.GetString(self.id)
		
		if self.checklist.IsChecked(self.id):
			_checkedTags.append(self.tag)
		else:
			_checkedTags.remove(self.tag)
			
	def add(self, event):
		print 'add'
		
	def remove(self, event):
		print 'remove'

# ------------------------------
def clearTags(dataset):
	global _checkedTags, filename, tPath, root, _removePrivate
	
	for data_element in dataset:
		for tag in _checkedTags:
			_tag = repr(tag)[2:-3]
			_dsTag = repr(data_element.name)[1:-1]
			if _tag == _dsTag:
				data_element.value = ''
	
	newdir = tPath + root[3:]
	_listing = os.walk(root)
	
	for dirs in _listing:
		for subdirs in dirs:
			if not os.path.exists(newdir):
				os.makedirs(newdir)
				
	if _removePrivate:
		dataset.remove_private_tags()
	
	dataset.save_as(newdir + "/"+ filename)

# ------------------------------
def editTags(dataset):
	global focusedTag, editTcValue
	
	for data_element in dataset:
		_fTag = repr(focusedTag)[2:-3]
		_dsTag = repr(data_element.name)[1:-1]
		if _fTag == _dsTag:
			data_element.value = editTcValue
			
# ------------------------------
def insertTag(dataset):
	global addTcValue
	
	self.tagLoc = 0x10a0

	

# ------------------------------
class Export(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
	
# ------------------------------
class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="DICOM Toolkit", size=(800,700))
		
		global tPath, sPath, tListing, sListing
		
		tPath = '/Users/jxu1/Documents/DICOM/dump/'
		sPath = '/Users/jxu1/Documents/DICOM/sample/'
		tListing = os.walk(tPath)
		sListing = os.walk(sPath)
		
		# Panels
		self.panel = wx.Panel(self)
		
		self.panel_one	= Process(self.panel)
		self.panel_two	= Export(self.panel)
		
		self.panel_two.Hide()

		# Sizers
		self.container	= wx.BoxSizer(wx.VERTICAL)
		
		self.hboxA	= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxA1	= wx.BoxSizer(wx.VERTICAL)
		self.vboxA2	= wx.BoxSizer(wx.VERTICAL)
		
		self.hboxB	= wx.BoxSizer(wx.HORIZONTAL)
		
		self.vboxC	= wx.BoxSizer(wx.VERTICAL)
		
		# Static Text
		self.srcTxt = wx.StaticText(self.panel, 0, 'Source Directory:')
		self.tarTxt = wx.StaticText(self.panel, 0, 'Target Directory:')
		
		# Buttons
		self.srcBtn	= wx.Button(self.panel, 101, 'Select Source', size=(150,25))
		self.tarBtn	= wx.Button(self.panel, 102, 'Select Target', size=(150,25))
		self.p1Btn	= wx.Button(self.panel, 103, 'Process', size=(395,25))
		self.p2Btn	= wx.Button(self.panel, 104, 'Export', size=(395,25))
		
		# Text Ctrl
		self.srcTc = wx.TextCtrl(self.panel, 131, '', size=(600,25))
		self.tarTc = wx.TextCtrl(self.panel, 132, '', size=(600,25))
		
		# Line
		self.line1 = wx.StaticLine(self.panel, -1, size=(800,1))
		self.line2 = wx.StaticLine(self.panel, -1, size=(800,1))
		
		# Layout
		self.container.Add(self.hboxA)
		self.container.AddSpacer((1,5))
		self.container.Add(self.line1)
		self.container.AddSpacer((1,5))
		self.container.Add(self.hboxB)
		self.container.Add(self.line2)
		self.container.AddSpacer((1,5))
		self.container.Add(self.vboxC)
		
		self.hboxA.Add(self.vboxA1, -1, wx.LEFT, 5)
		self.hboxA.Add(self.vboxA2, -1, wx.LEFT, 25)
		
		self.vboxA1.Add(self.srcTxt)
		self.vboxA1.Add(self.srcTc)
		self.vboxA1.Add(self.tarTxt)
		self.vboxA1.Add(self.tarTc)
		
		self.vboxA2.AddSpacer((1,18))
		self.vboxA2.Add(self.srcBtn)
		self.vboxA2.Add(self.tarBtn, -1, wx.TOP, 15)
		
		self.hboxB.Add(self.p1Btn)
		self.hboxB.Add(self.p2Btn)
		
		self.vboxC.Add(self.panel_one)
		self.vboxC.Add(self.panel_two)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.setSource,	id=101)
		self.Bind(wx.EVT_BUTTON, self.setDest,		id=102)
		self.Bind(wx.EVT_BUTTON, self.showP1,		id=103)
		self.Bind(wx.EVT_BUTTON, self.showP2,		id=104)
		self.Bind(wx.EVT_TEXT, self.refreshSource, id=131)
		self.Bind(wx.EVT_TEXT, self.refreshTarget, id=132)	
		self.panel.SetSizer(self.container)
		
		self.Centre()
		self.srcTc.WriteText(sPath)
		self.tarTc.WriteText(tPath)
		
	# Handlers
	def setSource(self, event):
		global sPath, sListing
		
		self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
		
		if self.dlg.ShowModal() == wx.ID_OK:
			sPath		= self.dlg.GetPath() + '/'
			sListing	= os.walk(sPath)

			self.tc1.SetValue(sPath)
		
		self.dlg.Destroy()
		
		
	def setDest(self, event):
		global tPath, tListing
		
		self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
		
		if self.dlg.ShowModal() == wx.ID_OK:
			tPath = self.dlg.GetPath() + '/'
		 	tListing = os.walk(tPath)

			self.tc2.SetValue(tPath)
		
		self.dlg.Destroy()
		
	def refreshSource(self, event):
		global sPath, sListing
		
		sPath = self.tc1.GetValue()
		sListing = os.walk(sPath)
		
	def refreshTarget(self, event):
		global tPath, tListing
		
		tPath = self.tc2.GetValue()
		tListing = os.walk(tPath)
		
	def showP1(self, even):
		self.panel_one.SetPosition((0,131))
		self.panel_one.Show()
		self.panel_two.Hide()
	def showP2(self, even):
		self.panel_two.SetPosition((0,131))
		self.panel_one.Hide()
		self.panel_two.Show()

# ------------------------------
def _genTags():
	global _initialTags, _cacheTags
	
	tags = open('tags.txt', 'r').readlines()
	
	_initialTags	= []
	_cacheTags		= []
	
	for line in tags:
		part	= line.split("\t")
		tag	= part[0]
		val	= part[1]
		
		_initialTags.append(tag + " : " + val)
		
# ------------------------------

if __name__ == "__main__":
	_genTags()
	app = wx.App(0)
	MainFrame().Show()
	app.MainLoop()
	