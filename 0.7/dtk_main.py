#!/usr/bin/python

import sys, os, dicom, sqlite3, wx, shutil, dtk-logic

logic = dtk_logic.Logic()

# ------------------------------
class Process(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        #global _cacheTags, _initialTags, _checkedTags, _removePrivate, tagChanges, insertTags, focusedTag, _currentTag, curSelf, proDlg, patients
    
        self.tagGroups  = ["0008", "0010 : Patient Information", "0012 : Clinical Information ", "0014", "0018", "0020", "0022", "0024", "0028",
                        "0032", "0038", "003A", "0040", "0042", "0044", "0046", "0048", "0050",
                        "0052", "0054", "0060", "0062", "0064", "0066", "0068", "0070", "0072",
                        "0074", "0076", "0078", "0088", "0100", "0400", "1000", "1010", "2000",
                        "2010", "2020", "2030", "2040", "2050", "2100", "2110", "2120", "2130",
                        "2200", "3002", "3004", "3006", "3008", "300A", "300C", "300E", "4000",
                        "4008", "4010", "4FFE", "50xx", "5200", "5400", "5600", "60xx", "7FE0",
                        "7Fxx", "FFFA", "FFFC", "FFFE", "0002", "0004"]
        
        # Sizers
        self.container  = wx.BoxSizer(wx.VERTICAL)
        
        self.hboxA  = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxA1 = wx.BoxSizer(wx.VERTICAL)
        self.vboxA2 = wx.BoxSizer(wx.VERTICAL)
        self.hboxA3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hboxB  = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxB1 = wx.BoxSizer(wx.VERTICAL)
        self.vboxB2 = wx.BoxSizer(wx.VERTICAL)
        self.hboxB3 = wx.BoxSizer(wx.HORIZONTAL)
        
        # Buttons
        self.proBtn = wx.Button(self, 101, "Process",               size=(150,25))
        self.preBtn = wx.Button(self, 102, "Previous Selection",    size=(150,25))
        self.chgBtn = wx.Button(self, 103, "Change",                size=(150,25))
        self.addBtn = wx.Button(self, 104, "Add",                   size=(75,25))
        self.rmvBtn = wx.Button(self, 105, "Remove",                size=(75,25))
        self.batBtn = wx.Button(self, 106, "Batch Process",         size=(150,25))
        
        # Text Ctrl
        self.editTc = wx.TextCtrl(self, 111, '', size=(450,25))
        self.addTc  = wx.TextCtrl(self, 112, '', size=(450,25))
        self.tagTc  = wx.TextCtrl(self, 113, 'Select a Tag', size=(450,25), style=wx.TE_READONLY)
        
        # Combo
        self.patientDrop = wx.ComboBox(self, 121, size=(600, 25), choices=self.patientGroups, style=wx.CB_READONLY)
        self.tagsDrop = wx.ComboBox(self, 121, size=(600, 25), choices=self.tagGroups, style=wx.CB_READONLY)
        
        # Checkbox
        self.privateCheck = wx.CheckBox(self, 112, "Remove Private Tags")
        
        # Dialog
        self.proDlg = wx.MessageDialog(self, 'This may take a few minutes to finish.', 'Processing DICOM Files...', wx.OK|wx.ICON_INFORMATION)
        
        # List Box
        self.tagLBox = wx.ListBox(self, 131, size=(600,140), style=wx.TE_MULTILINE)
        
        # Check List Box
        self.tagCLBox = wx.CheckListBox(self, 111, size=(600,280), choices=self.currentTags, style=0)
        
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
        self.Bind(wx.EVT_BUTTON, self.process,      id=101)
        self.Bind(wx.EVT_BUTTON, self.loadPrev,     id=102)
        self.Bind(wx.EVT_BUTTON, self.change,       id=103)
        self.Bind(wx.EVT_BUTTON, self.add,          id=104)
        self.Bind(wx.EVT_BUTTON, self.remove,       id=105)
        self.Bind(wx.EVT_CHECKLISTBOX, self.flag,   id=111)
        self.Bind(wx.EVT_LISTBOX, self.clicked,     id=111)
        self.Bind(wx.EVT_CHECKBOX, self.privTags,   id=112)
        self.Bind(wx.EVT_COMBOBOX, self.onSelect,   id=121)
        self.editTc.Bind(wx.EVT_KILL_FOCUS, self.change)
        
        # Initial Settings
        self.SetSizer(self.container)
        self.prvchk.SetValue(True)
        self.tagdrop.SetValue('0010 : Patient Information')

    # Handlers
    # self.proBtn
    def process(self, event):
        global sListing, root, filename, tPath, _checkedTags, dirname, dirs
    
        for dirname, dirs, files, in sListing:
            for filename in files:
                rFile = open(dirname + '/' + filename, 'rb')
                self.byte = repr(rFile.read())[513:517]
                if self.byte == 'DICM':
                    ds = dicom.read_file(dirname +'/'+ filename)
                    processTags(ds)
        
        SETTINGS = open('.settings.txt', 'wb')
        
        for tag in _checkedTags:
            SETTINGS.write(tag)
    
    # self.checklistbox
    def clicked(self, event):
        global focusedTag, _checkedTags, _currentTag, _fTag
        
        self.id     = event.GetSelection()
        focusedTag  = self.checklist.GetString(self.checklist.GetSelection())
        self.key    = focusedTag[:-2]
        self.tag    = self.checklist.GetString(self.id)
        
        self.checklist.Check(self.id)
        self.tagTc.SetValue(focusedTag)
        
        if self.checklist.IsChecked(self.id):
            _checkedTags.append(self.tag)
        else:
            _checkedTags.remove(self.tag)
            
        if focusedTag.endswith("*\n"):
            self.editTc.SetValue(_currentTag[self.key])
        else:
            self.editTc.Clear()
        
    # self.editTC & self.chgBtn
    def change(self, event):
        global focusedTag, tagChanges, _cacheTags, _initialTags, _checkedTags, _currentTag, curSelc, _fTag
        
        editTcValue = repr(self.editTc.GetValue())[2:-1]
        _fTag = repr(focusedTag)[2:-3]
        _currentTag[_fTag] = editTcValue
            
        # Adds a changed tick to _initialTags
        for idx, val, in enumerate(_initialTags):
            _dsTag = repr(val)[15:-3]
            pInit = repr(val)[1:15]
            if _fTag == _dsTag:
                _initialTags[idx] = pInit + _dsTag + "*\n"
                if _dsTag.endswith("*"):
                    _cdsTag = "".join(val.split("*"))[14:-1] + "*\n"
                    _initialTags[idx] = pInit + _cdsTag
                     
        # Adds a changed tick to _checkTags
        for idx, val, in enumerate(_checkedTags):
            _dsTag = repr(val)[2:-3]
            if _fTag == _dsTag:
                _checkedTags[idx] = _dsTag + "*\n"
                if _dsTag.endswith("*"):
                    _cdsTag = "".join(val.split("*"))[0:-1] + "*\n"
                    _initialTags[idx] = pInit + _cdsTag
                    
        for tag in _currentTag.items():
            tagChanges.append(tag)
            if tag[0].endswith("*"):
                tagChanges.remove(tag)
        
        self.refreshChecklist()    
        
    # Helper function for change
    def refreshChecklist(self):
        global _cacheTags, _initialTags, _checkedTags, _currentTag, _fTag
        
        curSelc     = self.tagdrop.GetValue()[:4]
        _checked    = self.checklist.GetChecked()
        _cacheTags  = []
        
        self.checklist.Clear()
        
        # Populates _cacheTags
        for pair in _initialTags:
            if pair[1:5] == curSelc:
                _cacheTags.append(pair[14:])
        
        self.checklist.InsertItems(items=_cacheTags, pos=0)
        
        # Checks all tags from _checkedTags in _cacheTags
        for tag in _checkedTags:
            for tag2 in _cacheTags:
                for i in range(len(_cacheTags)):
                    if tag == _cacheTags[i]:
                        self.checklist.Check(i)
                        
        self.editTc.SetValue(_currentTag[_fTag])
    
    # self.preBtn           
    def loadPrev(self, event):
        global _checkedTags
        
        _settings = open('.settings.txt', 'r').readlines()
        
        for line in _settings:
            if line.endswith('*\n'):
                line = line[:-2] + "\n"
                _checkedTags.append(line)
            else:
                _checkedTags.append(line)
                
        self.refreshChecklist()
    
    # self.tagdrop
    def onSelect(self, event):
        global _cacheTags, _initialTags, _checkedTags, curSelc
        
        curSelc     = self.tagdrop.GetValue()[:4]
        _checked    = self.checklist.GetChecked()
        _cacheTags  = []
        
        self.checklist.Clear()
        
        # Populates _cacheTags
        for pair in _initialTags:
            if pair[1:5] == curSelc:
                _cacheTags.append(pair[14:])
        
        self.checklist.InsertItems(items=_cacheTags, pos=0)
        
        # Checks all tags from _checkedTags in _cacheTags
        for tag in _checkedTags:
            for tag2 in _cacheTags:
                for i in range(len(_cacheTags)):
                    if tag == _cacheTags[i]:
                        self.checklist.Check(i)
    
    # self.prvchk
    def privTags(self, event):
        global _removePrivate
        
        if self.prvchk.GetValue():
            _removePrivate = True
        else:
            _removePrivate = False
    
    # self.checklist
    def flag(self, event):
        global _checkedTags
        
        self.id     = event.GetSelection()
        self.tag    = self.checklist.GetString(self.id)
        
        if self.checklist.IsChecked(self.id):
            _checkedTags.append(self.tag)
        else:
            _checkedTags.remove(self.tag)
            
    # self.addBtn
    def add(self, event):
        global insertTags
        
        tcVal = self.addTc.GetValue()
        
        insertTags.append(tcVal)
    
        self.tagLBox.Insert(tcVal, pos=0)
        
        self.addTc.Clear()

    # self.rmvBtn
    def remove(self, event):
        global insertTags
        
        curSelc     = self.tagLBox.GetSelection()
        self.val    = self.tagLBox.GetString(curSelc)
        
        self.tagLBox.Delete(curSelc)

        insertTags.remove(self.val)

# ------------------------------
#TODO fix all global stuff, try to eliminate as many global variables 
#TODO tie together the 2 drop tags and create the lists to store those value
#TODO find a way to key all the seperate lists
class Batch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        global _cacheTags, _initialTags, _checkedTags, _removePrivate, tagChanges, insertTags, focusedTag, _currentTag, curSelf, proDlg, patients, finalPats
    
        # Globals
        finalPats       = []
        curSelc         = ''
        _currentTag     = {}
        focusedTag      = ''
        _checkedTags    = []
        tagChanges      = []
        insertTags      = []
        patients        = []
        uPatients       = []
        _removePrivate  = False
        
        self.tagGroups  = ["0008", "0010 : Patient Information", "0012 : Clinical Information ", "0014", "0018", "0020", "0022", "0024", "0028",
                        "0032", "0038", "003A", "0040", "0042", "0044", "0046", "0048", "0050",
                        "0052", "0054", "0060", "0062", "0064", "0066", "0068", "0070", "0072",
                        "0074", "0076", "0078", "0088", "0100", "0400", "1000", "1010", "2000",
                        "2010", "2020", "2030", "2040", "2050", "2100", "2110", "2120", "2130",
                        "2200", "3002", "3004", "3006", "3008", "300A", "300C", "300E", "4000",
                        "4008", "4010", "4FFE", "50xx", "5200", "5400", "5600", "60xx", "7FE0",
                        "7Fxx", "FFFA", "FFFC", "FFFE", "0002", "0004"]
        
        
        # Sizers
        self.container  = wx.BoxSizer(wx.VERTICAL)

        # Buttons
        self.genBtn = wx.Button(self, 101, "Generate Map", size=(150,25))
        self.testBtn = wx.Button(self, 102, "TEST", size=(150,25))
        
        # Combo
        self.patDrop = wx.ComboBox(self, 121, size=(600, 25), choices=finalPats, style=wx.CB_READONLY)
        self.tagDrop = wx.ComboBox(self, 121, size=(600, 25), choices=self.tagGroups, style=wx.CB_READONLY)
        
        # Check List Box
        self.checklist = wx.CheckListBox(self, 111, size=(600,280), choices=_cacheTags, style=0)
        
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.map,          id=101)
        self.Bind(wx.EVT_BUTTON, self.tester,       id=102)
        self.Bind(wx.EVT_COMBOBOX, self.onSelect,   id=121)
        self.Bind(wx.EVT_CHECKLISTBOX, self.flag,   id=111)
        
        # Layout
        self.container.AddSpacer((1,20))
        self.container.Add(self.genBtn)
        self.container.Add(self.testBtn)
        self.container.Add(self.patDrop)
        self.container.Add(self.tagDrop)
        self.container.Add(self.checklist)
        
        # Initial Config
        self.patDrop.Clear()
        for pat in finalPats:
            self.patDrop.append(pat)
        
        self.SetSizer(self.container)

    def flag(self, event):
        global _checkedTags
        
        self.id     = event.GetSelection()
        self.tag    = self.checklist.GetString(self.id)
        
        if self.checklist.IsChecked(self.id):
            _checkedTags.append(self.tag)
        else:
            _checkedTags.remove(self.tag)

    # self.tagdrop
    def onSelect(self, event):
        global _cacheTags, _initialTags, _checkedTags, curSelc
        
        curSelc     = self.tagDrop.GetValue()[:4]
        _checked    = self.checklist.GetChecked()
        _cacheTags  = []
        
        self.checklist.Clear()
        
        # Populates _cacheTags
        for pair in _initialTags:
            if pair[1:5] == curSelc:
                _cacheTags.append(pair[14:])
        
        self.checklist.InsertItems(items=_cacheTags, pos=0)
        
        # Checks all tags from _checkedTags in _cacheTags
        for tag in _checkedTags:
            for tag2 in _cacheTags:
                for i in range(len(_cacheTags)):
                    if tag == _cacheTags[i]:
                        self.checklist.Check(i)

    # self.genBtn
    def map(self, event):
        global finalPats
        
        for dirname, dirs, files, in sListing:
            for filename in files:
                rFile = open(dirname + '/' + filename, 'rb')
                self.byte = repr(rFile.read())[513:517]
                if self.byte == 'DICM':
                    ds = dicom.read_file(dirname +'/'+ filename)
                    mapper(ds)
                    
        self.patDrop.Clear()
        for e in finalPats:
            self.patDrop.Append(e)
        
                    
    def tester(self, event):
        global finalPats
        pass
        
    
        

# ------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="DICOM Toolkit", size=(800,700))
        
        global tPath, sPath, tListing, sListing, srcTc, tarTc
        
        tPath = '/Users/jxu1/Documents/DICOM/dump/'
        sPath = '/Users/jxu1/Documents/DICOM/sample/'
        tListing = os.walk(tPath)
        sListing = os.walk(sPath)
        
        # Panels
        self.panel = wx.Panel(self)
        
        self.panel_one = Process(self.panel)
        self.panel_two = Batch(self.panel)

        # Sizers
        self.container = wx.BoxSizer(wx.VERTICAL)
        
        self.hboxA  = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxA1 = wx.BoxSizer(wx.VERTICAL)
        self.vboxA2 = wx.BoxSizer(wx.VERTICAL)
        
        self.hboxB = wx.BoxSizer(wx.HORIZONTAL)
        
        self.vboxC = wx.BoxSizer(wx.VERTICAL)
        
        # Static Text
        self.srcTxt = wx.StaticText(self.panel, 0, 'Source Directory:')
        self.tarTxt = wx.StaticText(self.panel, 0, 'Target Directory:')
        
        # Buttons
        self.srcBtn     = wx.Button(self.panel, 101, 'Select Source', size=(150,25))
        self.tarBtn     = wx.Button(self.panel, 102, 'Select Target', size=(150,25))
        self.p1Btn      = wx.Button(self.panel, 103, 'Process', size=(300,25))
        self.p2Btn      = wx.Button(self.panel, 104, 'Batch', size=(300,25))
        
        # Text Ctrl
        srcTc = wx.TextCtrl(self.panel, 131, '', size=(600,25))
        tarTc = wx.TextCtrl(self.panel, 132, '', size=(600,25))
        
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
        self.vboxA1.Add(srcTc)
        self.vboxA1.Add(self.tarTxt)
        self.vboxA1.Add(tarTc)
        
        self.vboxA2.AddSpacer((1,18))
        self.vboxA2.Add(self.srcBtn)
        self.vboxA2.Add(self.tarBtn, -1, wx.TOP, 15)
        
        self.hboxB.Add(self.p1Btn)
        self.hboxB.Add(self.p2Btn, -1, wx.LEFT, 5)

        self.vboxC.Add(self.panel_one)
        self.vboxC.AddSpacer((1,50))
        self.vboxC.Add(self.panel_two)
        
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.setSource,    id=101)
        self.Bind(wx.EVT_BUTTON, self.setDest,      id=102)
        self.Bind(wx.EVT_BUTTON, self.showP1,       id=103)
        self.Bind(wx.EVT_BUTTON, self.showP2,       id=104)
        self.Bind(wx.EVT_TEXT, self.refreshSource,  id=131)
        self.Bind(wx.EVT_TEXT, self.refreshTarget,  id=132)
        
        self.panel.SetSizer(self.container)
        
        self.Centre()
        srcTc.WriteText(sPath)
        tarTc.WriteText(tPath)
    
    # Handlers
    def setSource(self, event):
        global sPath, sListing
        
        self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
        
        if self.dlg.ShowModal() == wx.ID_OK:
            sPath       = self.dlg.GetPath() + '/'
            sListing    = os.walk(sPath)
            
            srcTc.SetValue(sPath)
        
        self.dlg.Destroy()
    
    def setDest(self, event):
        global tPath, tListing
        
        self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
        
        if self.dlg.ShowModal() == wx.ID_OK:
            tPath = self.dlg.GetPath() + '/'
            tListing = os.walk(tPath)
            
            tarTc.SetValue(tPath)        
        self.dlg.Destroy()
    
    def refreshSource(self, event):
        global sPath, sListing
        
        sPath = srcTc.GetValue()
        sListing = os.walk(sPath)
    
    def refreshTarget(self, event):
        global tPath, tListing
        
        tPath = tarTc.GetValue()
        tListing = os.walk(tPath)
    
    def showP1(self, even):
        self.panel_one.SetPosition((0,127))
        self.panel_one.Show()
        self.panel_two.Hide()
    def showP2(self, even):
        self.panel_two.SetPosition((0,127))
        self.panel_one.Hide()
        self.panel_two.Show()

# ------------------------------
def _genTags():
    global _initialTags, _cacheTags
    
    tags = open('tags.txt', 'r').readlines()
    
    _initialTags    = []
    _cacheTags      = []
    
    for line in tags:
        part    = line.split("\t")
        tag     = part[0]
        val     = part[1]
        
        _initialTags.append(tag + " : " + val)
        
# ------------------------------
def processTags(dataset):
    global _checkedTags, filename, tPath, root, _removePrivate, tagChanges, insertTags, _currentTag, dirname
    
    # Initiates TagLoc
    tagLoc = 0x10a0
    
    # Clears Private Tags
    if _removePrivate:
        dataset.remove_private_tags()
    
    # Blanks all checked Tags 
    for data_element in dataset:
        for tag in _checkedTags:
            _tag = repr(tag)[2:-3]
            _dsTag = repr(data_element.name)[1:-1]
            if _tag == _dsTag:
                data_element.value = ''
    
    # Sets a selected Tag to the input value
    for data_element in dataset:
        for tag in tagChanges:
            _tag = tag[0]
            _val = tag[1]
            _dsTag = repr(data_element.name)[1:-1]
            if tag[0] == _dsTag:
                data_element.value = tag[1]
    
    # Adds private Tags
    for value in insertTags:
        tagLoc += 1
        dataset.AddNew([0x0045, tagLoc], 'UT', value)
    
    root = os.path.relpath(dirname)
    root = "".join(root.split("../"))

    newdir = tPath + root
    _listing = os.walk(dirname)
    
    for dirs in _listing:
        for subdirs in dirs:
            if not os.path.exists(newdir):
                os.makedirs(newdir)
    
    # Resets tagLoc    
    tagLoc = 0x10a0
    
    dataset.save_as(newdir + "/"+ filename)    
        
# ------------------------------
def mapper(dataset):
    global patients, tPath, finalPats
    
    # PatientsName/StudyDescription + 
    
    # Creates each group node for each patient
    for data_element in dataset:
        _name   = dataset.PatientsName
        if "StudyDescription" in dataset:
            _stDesc = dataset.StudyDescription
        else:    
            _stDesc = ""
        if "StudyDate" in dataset:
            _stID   = dataset.StudyDate
        else:    
            _stID   = ""    
        if "SeriesDescription" in dataset:
            _srDesc = dataset.SeriesDescription
        else:    
            _srDesc = ""
        if "SeriesDate" in dataset:
            _srNum  = str(dataset.SeriesDate)
        else:    
            _srNum = ""
        if "SeriesTime" in dataset:
            _srTime = str(dataset.SeriesTime)
        else:
            _srTime = ""
        
        group = (_name, _stDesc, _stID, _srDesc, _srNum, _srTime)
        
        if group not in patients:
            patients.append(group)            
    
    # Creates the folder hierarchy
    _listing = os.walk(tPath)
    finalPats = [] 
    
    for dirs in _listing:
        for subdirs in dirs:
            for patient in patients:
                _lvl1 = patient[0]
                _lvl2 = patient[1] + "_" + patient[2]
                _lvl3 = patient[3] + "_" + patient[4] + "_" + patient[5]
                dir1 = tPath + _lvl1
                dir2 = dir1 + "/" + _lvl2
                dir3 = dir2 + "/" + _lvl3
                if not os.path.exists(dir1):
                    os.makedirs(dir1)
                if not os.path.exists(dir2):
                    os.makedirs(dir2)
                if not os.path.exists(dir3):
                    print dir3
                    os.makedirs(dir3)
                if _lvl1 not in finalPats:
                    finalPats.append(_lvl1)
        
            
# ------------------------------
if __name__ == "__main__":
    global _initialTags, _cacheTags
    _genTags()
    
    for pair in _initialTags:
        if pair[1:5] == "0010":
            _cacheTags.append(pair[14:])
    
    app = wx.App(0)
    MainFrame().Show()
    app.MainLoop()
