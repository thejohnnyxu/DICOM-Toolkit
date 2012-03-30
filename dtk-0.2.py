#!/usr/bin/python

import sys, os, dicom, sqlite3, wx
		
# ------------------------------
class Sanitize(wx.Panel):
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
		self.container	= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
		
		# Buttons
		self.sanbtn	= wx.Button(self, 101, "Sanitize", size=(150,50))
		self.defbtn	= wx.Button(self, 102, "Previous Selection", size=(150,50))
		
		# Combo
		self.tagdrop = wx.ComboBox(self, 121, size=(600, 25), choices=self.tagGroups, style=wx.CB_READONLY)
		
		# Checkbox
		self.prvchk	= wx.CheckBox(self, 112, "Remove Private Tags")
		
		# Check List Box
		self.checklist = wx.CheckListBox(self, 111, size=(600,390), choices=_cacheTags,style=0)

		# Layout
		self.container.Add(self.vboxA, -1, wx.LEFT, 5)
		self.container.Add(self.vboxB, -1, wx.LEFT, 25)
		
		self.vboxA.Add(self.prvchk)
		self.vboxA.Add(self.tagdrop, -1, wx.TOP, 5)
		self.vboxA.Add(self.checklist)
		
		self.vboxB.AddSpacer((1,23))
		self.vboxB.Add(self.defbtn)
		self.vboxB.AddSpacer((1,345))
		self.vboxB.Add(self.sanbtn)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.sanitize,		id=101)
		self.Bind(wx.EVT_BUTTON, self.loadPrev,		id=102)
		self.Bind(wx.EVT_CHECKLISTBOX, self.flag,	id=111)
		self.Bind(wx.EVT_CHECKBOX, self.privTags,	id=112)
		self.Bind(wx.EVT_COMBOBOX, self.onSelect,	id=121)
	
		self.SetSizer(self.container)
		self.prvchk.SetValue(True)
		
	# Handlers
	def sanitize(self, event):
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
class Anonymize(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
	
		# Sizers
		self.container	= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
		
		# Checkboxes
		self.chk1	= wx.CheckBox(self, 211, "Patient\'s Name")
		self.chk2	= wx.CheckBox(self, 212, "Patient ID")
		self.chk3	= wx.CheckBox(self, 213, "Patient\'s Birth Date")
		self.chk4	= wx.CheckBox(self, 214, "Patient\'s Age")
		self.chk5	= wx.CheckBox(self, 215, "Patient\'s Weight")
		self.chk6	= wx.CheckBox(self, 216, "Patient\'s Sex")
		self.chk7	= wx.CheckBox(self, 217, "Institutional Department Name")
		self.chk8	= wx.CheckBox(self, 218, "Physician(s) of Record")
		self.chk9	= wx.CheckBox(self, 219, "Referring Physician's Name")
		
		# Text Ctrl
		self.tc1 = wx.TextCtrl(self, -1, '', size=(600,25))
		self.tc2 = wx.TextCtrl(self, -1, '', size=(600,25))
		
		# Buttons
		self.anobtn	= wx.Button(self, 201, "Anonymize", size=(150,50))
		self.allbtn	= wx.Button(self, 202, "Clear All", size=(150,50))
		
		# Layout
		self.container.Add(self.vboxA, -1, wx.LEFT, 5)
		self.container.Add(self.vboxB, -1, wx.LEFT, 25)
		
		self.vboxA.Add(self.chk1, -1, wx.TOP, 5)
		self.vboxA.Add(self.tc1)
		self.vboxA.Add(self.chk2, -1, wx.TOP, 5)
		self.vboxA.Add(self.tc2)
		self.vboxA.Add(self.chk3, -1, wx.TOP, 5)
		self.vboxA.Add(self.chk4, -1, wx.TOP, 5)
		self.vboxA.Add(self.chk5, -1, wx.TOP, 5)
		self.vboxA.Add(self.chk6, -1, wx.TOP, 5)
		self.vboxA.Add(self.chk7, -1, wx.TOP, 5)
		self.vboxA.Add(self.chk8, -1, wx.TOP, 5)
		self.vboxA.Add(self.chk9, -1, wx.TOP, 5)
		
		self.vboxB.AddSpacer((1,368))
		self.vboxB.Add(self.allbtn)
		self.vboxB.Add(self.anobtn)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.anon,	id=201)
		self.Bind(wx.EVT_BUTTON, self.all, id=202)
		
		self.Bind(wx.EVT_CHECKBOX, self.pName,	id=211)
		self.Bind(wx.EVT_CHECKBOX, self.pID,	id=212)
		self.Bind(wx.EVT_CHECKBOX, self.pDOB,	id=213)
		self.Bind(wx.EVT_CHECKBOX, self.pAge,	id=214)
		self.Bind(wx.EVT_CHECKBOX, self.pWei,	id=215)
		self.Bind(wx.EVT_CHECKBOX, self.pSex,	id=216)
		self.Bind(wx.EVT_CHECKBOX, self.pInst,	id=217)
		self.Bind(wx.EVT_CHECKBOX, self.pPhys,	id=218)
		self.Bind(wx.EVT_CHECKBOX, self.pRef,	id=219)
		
		self.SetSizer(self.container)
		self.chk1.SetValue(True)
		
	# Handlers
	def anon(self, event):
		print 'anonymize button'
		
	def all(self, event):
		print 'all button'	
		
	def pName(self, event):
		if self.chk1.GetValue():
			print "checked"
		else:
			print "un-checked"

	def pID(self, event):
		if self.chk2.GetValue():
			print "checked"
		else:
			print "un-checked"
			
	def pDOB(self, event):
		if self.chk3.GetValue():
			print "checked"
		else:
			print "un-checked"
			
	def pAge(self, event):
		if self.chk4.GetValue():
			print "checked"
		else:
			print "un-checked"
			
	def pWei(self, event):
		if self.chk5.GetValue():
			print "checked"
		else:
			print "un-checked"
			
	def pSex(self, event):
		if self.chk6.GetValue():
			print "checked"
		else:
			print "un-checked"	
			
	def pInst(self, event):
		if self.chk7.GetValue():
			print "checked"
		else:
			print "un-checked"
			
	def pPhys(self, event):
		if self.chk8.GetValue():
			print "checked"
		else:
			print "un-checked"
	
	def pRef(self, event):
		if self.chk9.GetValue():
			print "checked"
		else:
			print "un-checked"
	
# ------------------------------
class Update(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.tags = ['abc', 'sadas', 'asdsad']
		
		# Sizers
		self.container	= wx.BoxSizer(wx.HORIZONTAL)
		
		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.hboxA2	= wx.BoxSizer(wx.HORIZONTAL)
		
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
		
		# Buttons
		self.upbtn	= wx.Button(self, 301, "Update", size=(150,50))
		self.addbtn	= wx.Button(self, 302, "Add", size=(150,50))
		self.delbtn	= wx.Button(self, 303, "Remove", size=(150,50))
		self.chgbtn	= wx.Button(self, 304, "Change", size=(150,50))

		# Text Ctrl
		self.tc1 = wx.TextCtrl(self, -1, '', size=(600,25))
		self.tc2 = wx.TextCtrl(self, -1, '', size=(600,25))
		
		# Combo
		self.taglist	= wx.ComboBox(self, 321, size=(600, 25), choices=self.tags, style=wx.CB_READONLY)
		
		# List Box
		self.list	= wx.ListBox(self, 311, size=(600,332), choices=[],style=0)

		# Layout
		self.container.Add(self.vboxA, -1, wx.LEFT, 5)
		self.container.Add(self.vboxB, -1, wx.LEFT, 25)
		
		self.vboxA.Add(self.taglist)
		self.vboxA.Add(self.tc1)
		self.vboxA.Add(self.list, -1, wx.TOP, 5)
		self.vboxA.Add(self.tc2)
		self.vboxA.Add(self.hboxA2, -1, wx.TOP, 5)
		self.hboxA2.Add(self.addbtn)
		self.hboxA2.Add(self.delbtn)
		
		self.vboxB.AddSpacer((1,28))
		self.vboxB.Add(self.chgbtn)
		self.vboxB.AddSpacer((1,340))
		self.vboxB.Add(self.upbtn)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.change,		id=304)
		self.Bind(wx.EVT_BUTTON, self.up,			id=301)
		self.Bind(wx.EVT_BUTTON, self.add,			id=302)
		self.Bind(wx.EVT_BUTTON, self.remove,		id=303)
		self.Bind(wx.EVT_COMBOBOX, self.onSelect,	id=321)
		
		self.SetSizer(self.container)
		
	# Handlers
	def onSelect(self, event):
		selc = self.tagdrop.GetValue()
		print selc
		
	def change(self, event):
		print 'change button'

	def up(self, event):
		print 'update button'
		
	def add(self, event):
		print 'add button'
		
	def remove(self, event):
		print 'remove button'
# ------------------------------
class Database(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		# Sizers
		self.container	= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
		
		# Text Ctrl
		self.tc1 = wx.TextCtrl(self, -1, '', size=(600,25))
		self.tc2 = wx.TextCtrl(self, -1, '', size=(600,25))
		
		# Static Text
		self.st1 = wx.StaticText(self, 0, 'Database File:')
		self.st2 = wx.StaticText(self, 0, 'File Name:')
		
		# Buttons
		self.selbtn	= wx.Button(self, 401, "Select Database", size=(150,50))
		self.genbtn	= wx.Button(self, 402, "Generate", size=(150,50))
		
		# Layout
		self.container.Add(self.vboxA, -1, wx.LEFT, 5)
		self.container.Add(self.vboxB, -1, wx.LEFT, 25)
		
		self.vboxA.Add(self.st1, -1, wx.TOP, 5)
		self.vboxA.Add(self.tc1)
		self.vboxA.Add(self.st2, -1, wx.TOP, 5)
		self.vboxA.Add(self.tc2)
		
		self.vboxB.AddSpacer((1,21))
		self.vboxB.Add(self.selbtn)
		self.vboxB.AddSpacer((1,347))
		self.vboxB.Add(self.genbtn)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.selDB,	id=401)
		self.Bind(wx.EVT_BUTTON, self.genDB,	id=402)
		
		self.SetSizer(self.container)
		
	# Handlers
	def selDB(self, event):
		print 'seldb button'
		
	def genDB(self, event):
		print 'gendb button'
# ------------------------------
class Export(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		# Sizers
		self.container	= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxA	= wx.BoxSizer(wx.VERTICAL)
		self.vboxB	= wx.BoxSizer(wx.VERTICAL)
	
		# Static Text
		self.st1 = wx.StaticText(self, 0, "Output Filename:")
		
		# Text Ctrl
		self.fileout = wx.TextCtrl(self, 0, '', size=(600,25))
		
		# Buttons
		self.txtbtn = wx.Button(self, 601, "Generate TXT", size=(150,50))
		self.csvbtn = wx.Button(self, 602, "Generate CSV", size=(150,50))
		
		self.filename = self.fileout.GetValue()
		
		# Layout
		self.container.Add(self.vboxA, -1, wx.LEFT, 5)
		self.container.Add(self.vboxB, -1, wx.LEFT, 25)
		
		self.vboxA.Add(self.st1, -1, wx.TOP, 5)
		self.vboxA.Add(self.fileout)
		
		self.vboxB.AddSpacer((1,368))
		self.vboxB.Add(self.txtbtn)
		self.vboxB.Add(self.csvbtn)

		# Bindings
		self.Bind(wx.EVT_BUTTON, self.genText, id=601)
		self.Bind(wx.EVT_BUTTON, self.genCsv, id=602)

		self.SetSizer(self.container)
	
	# Handlers
	def genText(self, event):
		print 'generate txt button'
		
	def genCsv(self, event):
		print 'generate csv button'
		
# ------------------------------
class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="DICOM Toolkit", size=(800,600))
		
		global tPath, sPath, tListing, sListing
		
		tPath = '/Users/jxu1/Documents/DICOM/dump/'
		sPath = '/Users/jxu1/Documents/DICOM/sample/'
		tListing = os.walk(tPath)
		sListing = os.walk(sPath)
		
		# Panels
		self.panel = wx.Panel(self)
		
		self.panel_one	= Sanitize(self.panel)
		self.panel_two	= Anonymize(self.panel)
		self.panel_three= Update(self.panel)
		self.panel_four	= Database(self.panel)
		self.panel_five	= Export(self.panel)

		# Sizers
		self.container	= wx.BoxSizer(wx.VERTICAL)
		
		self.hboxA		= wx.BoxSizer(wx.HORIZONTAL)
		self.vboxA1		= wx.BoxSizer(wx.VERTICAL)
		self.vboxA2		= wx.BoxSizer(wx.VERTICAL)
		
		self.vboxB		= wx.BoxSizer(wx.VERTICAL)
		self.hboxB1		= wx.BoxSizer(wx.HORIZONTAL)
		
		self.vboxC		= wx.BoxSizer(wx.VERTICAL)
		
		# Static Text
		self.st1 = wx.StaticText(self.panel, 0, 'Source Directory:')
		self.st2 = wx.StaticText(self.panel, 0, 'Target Directory:')
		
		# Buttons
		self.srcbtn		= wx.Button(self.panel, 101, 'Select Source', size=(150,25))
		self.destbtn	= wx.Button(self.panel, 102, 'Select Target', size=(150,25))
		self.sanbtn		= wx.Button(self.panel, 103, 'Sanitize', size=(160,30))
		self.anonbtn	= wx.Button(self.panel, 104, 'Anonymize', size=(160,30))
		self.upbtn		= wx.Button(self.panel, 105, 'Update', size=(160,30))
		self.dbbtn		= wx.Button(self.panel, 106, 'Database', size=(160,30))
		self.expbtn		= wx.Button(self.panel, 107, 'Export', size=(160,30))
		
		# Text Ctrl
		self.tc1 = wx.TextCtrl(self.panel, 131, '', size=(600,25))
		self.tc2 = wx.TextCtrl(self.panel, 132, '', size=(600,25))
		
		# Line
		self.line1 = wx.StaticLine(self.panel, -1, size=(800,1))
		self.line2 = wx.StaticLine(self.panel, -1, size=(800,1))
		
		# Layout
		self.container.Add(self.hboxA)
		self.container.Add(self.vboxB)
		self.container.Add(self.vboxC)
		
		self.hboxA.Add(self.vboxA1, -1, wx.LEFT, 5)
		self.hboxA.Add(self.vboxA2, -1, wx.LEFT, 25)
		self.vboxA1.Add(self.st1)
		self.vboxA1.Add(self.tc1)
		self.vboxA1.Add(self.st2)
		self.vboxA1.Add(self.tc2)
		self.vboxA2.AddSpacer((1,15))
		self.vboxA2.Add(self.srcbtn)
		self.vboxA2.Add(self.destbtn, -1, wx.TOP, 15)
		
		self.vboxB.AddSpacer((800,5))
		self.vboxB.Add(self.line1, -1, wx.BOTTOM, 5)
		self.vboxB.Add(self.hboxB1)
		self.vboxB.Add(self.line2)
		self.hboxB1.Add(self.sanbtn)
		self.hboxB1.Add(self.anonbtn)
		self.hboxB1.Add(self.upbtn)
		self.hboxB1.Add(self.dbbtn)
		self.hboxB1.Add(self.expbtn)
		
		self.vboxC.AddSpacer((1,5))
		self.vboxC.Add(self.panel_one)
		self.vboxC.Add(self.panel_two)
		self.vboxC.Add(self.panel_three)
		self.vboxC.Add(self.panel_four)
		self.vboxC.Add(self.panel_five)
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.setSource,	id=101)
		self.Bind(wx.EVT_BUTTON, self.setDest,		id=102)
		self.Bind(wx.EVT_BUTTON, self.showP1,		id=103)
		self.Bind(wx.EVT_BUTTON, self.showP2,		id=104)
		self.Bind(wx.EVT_BUTTON, self.showP3,		id=105)
		self.Bind(wx.EVT_BUTTON, self.showP4,		id=106)
		self.Bind(wx.EVT_BUTTON, self.showP5,		id=107)
		self.Bind(wx.EVT_TEXT, self.refreshSource, id=131)
		self.Bind(wx.EVT_TEXT, self.refreshTarget, id=132)	
		self.panel.SetSizer(self.container)
		
		self.Centre()
		self.tc1.WriteText(sPath)
		self.tc2.WriteText(tPath)
		
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
		self.panel_three.Hide()
		self.panel_four.Hide()
		self.panel_five.Hide()
	def showP2(self, even):
		self.panel_two.SetPosition((0,131))
		self.panel_one.Hide()
		self.panel_two.Show()
		self.panel_three.Hide()
		self.panel_four.Hide()
		self.panel_five.Hide()
	def showP3(self, even):
		self.panel_three.SetPosition((0,131))
		self.panel_one.Hide()
		self.panel_two.Hide()
		self.panel_three.Show()
		self.panel_four.Hide()
		self.panel_five.Hide()
	def showP4(self, even):
		self.panel_four.SetPosition((0,131))
		self.panel_one.Hide()
		self.panel_two.Hide()
		self.panel_three.Hide()
		self.panel_four.Show()
		self.panel_five.Hide()
	def showP5(self, even):
		self.panel_five.SetPosition((0,131))
		self.panel_one.Hide()
		self.panel_two.Hide()
		self.panel_three.Hide()
		self.panel_four.Hide()
		self.panel_five.Show()

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
	