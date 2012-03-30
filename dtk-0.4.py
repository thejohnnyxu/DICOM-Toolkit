#!/usr/bin/python

import sys, os, dicom, sqlite3, wx, shutil

# ------------------------------
class Process(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        global _cacheTags, _initialTags, _checkedTags, _removePrivate, tagChanges, insertTags, focusedTag, _currentTag, curSelf
        
        # Globals
        curSelc         = ''
        _currentTag     = {}
        focusedTag      = ''
        _checkedTags    = []
        tagChanges      = []
        insertTags      = []
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
        
        self.hboxA  = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxA1 = wx.BoxSizer(wx.VERTICAL)
        self.vboxA2 = wx.BoxSizer(wx.VERTICAL)
        self.hboxA3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hboxB  = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxB1 = wx.BoxSizer(wx.VERTICAL)
        self.vboxB2 = wx.BoxSizer(wx.VERTICAL)
        self.hboxB3 = wx.BoxSizer(wx.HORIZONTAL)
        
        # Buttons
        self.proBtn = wx.Button(self, 101, "Process", size=(150,25))
        self.preBtn = wx.Button(self, 102, "Previous Selection", size=(150,25))
        self.chgBtn = wx.Button(self, 103, "Change", size=(150,25))
        self.addBtn = wx.Button(self, 104, "Add", size=(75,25))
        self.rmvBtn = wx.Button(self, 105, "Remove", size=(75,25))
        
        # Text Ctrl
        self.editTc = wx.TextCtrl(self, 141, '', size=(450,25))
        self.addTc  = wx.TextCtrl(self, 142, '', size=(450,25))
        self.tagTc  = wx.TextCtrl(self, 143, 'Select a Tag', size=(450,25), style=wx.TE_READONLY)
        
        # Combo
        self.tagdrop = wx.ComboBox(self, 121, size=(600, 25), choices=self.tagGroups, style=wx.CB_READONLY)
        
        # Checkbox
        self.prvchk = wx.CheckBox(self, 112, "Remove Private Tags")
        
        # Dialog
        self.proDlg = wx.MessageDialog(self, 'This may take a few minutes.', 'Processing DICOM Files...', wx.OK|wx.ICON_INFORMATION)
        
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
        global sListing, root, filename, tPath, _checkedTags
    
        for dirname, dirs, files, in sListing:
            for filename in files:
                rFile = open(dirname + '/' + filename, 'rb')
                self.byte = repr(rFile.read())[513:517]
                if self.byte == 'DICM':
                    ds = dicom.read_file(dirname +'/'+ filename)
                    root = os.path.relpath(dirname)
                    processTags(ds)
        
        SETTINGS = open('.settings.txt', 'wb')
        
        for tag in _checkedTags:
            SETTINGS.write(tag)
    
    # self.checklistbox
    def clicked(self, event):
        global focusedTag, _checkedTags, _currentTag
        
        self.id     = event.GetSelection()
        focusedTag  = self.checklist.GetString(self.checklist.GetSelection())
        
        self.checklist.Check(self.id)
        self.tagTc.SetValue(focusedTag)
        
        self.id     = event.GetSelection()
        self.tag    = self.checklist.GetString(self.id)
        
        if self.checklist.IsChecked(self.id):
            _checkedTags.append(self.tag)
        else:
            _checkedTags.remove(self.tag)
            
        if focusedTag.endswith("*\n"):
            self.key = focusedTag[:-2]
            self.editTc.SetValue(_currentTag[self.key])
    
    # self.editTC & self.chgBtn
    def change(self, event):
        global focusedTag, tagChanges, _cacheTags, _initialTags, _checkedTags, _currentTag, curSelc
        
        editTcValue = repr(self.editTc.GetValue())[2:-1]
        _fTag = repr(focusedTag)[2:-3]
        _currentTag[_fTag] = editTcValue
        
        for tag in _currentTag.items():
            tagChanges.append(tag)

        
        
        self.editTc.Clear()
        
        # Adds a changed tick to _initialTags
        for idx, val, in enumerate(_initialTags):
            _dsTag = repr(val)[15:-3]
            if _fTag == _dsTag:
                pInit = repr(val)[1:15]
                newpair = pInit + repr(val)[15:-3] + "*" + "\n"
                _initialTags[idx] = newpair
        
        # Adds a changed tick to _checkTags
        for idx, val, in enumerate(_checkedTags):
            _dsTag = repr(val)[2:-3]
            if _fTag == _dsTag:
                newpair = _dsTag + "*" + "\n"
                _checkedTags[idx] = newpair
                
        self.refreshChecklist()
        
    # Helper function for change
    def refreshChecklist(self):
        global _cacheTags, _initialTags, _checkedTags
        
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
        
        curSelc   = self.tagLBox.GetSelection()
        self.val    = self.tagLBox.GetString(curSelc)
        
        self.tagLBox.Delete(curSelc)

        insertTags.remove(self.val)
    
# ------------------------------
def processTags(dataset):
    global _checkedTags, filename, tPath, root, _removePrivate, tagChanges, insertTags, _currentTag
    
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
    
    newdir = tPath + root[3:]
    _listing = os.walk(root)
    
    for dirs in _listing:
        for subdirs in dirs:
            if not os.path.exists(newdir):
                os.makedirs(newdir)
    
    # Resets tagLoc    
    tagLoc = 0x10a0
    
    dataset.save_as(newdir + "/"+ filename)

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
        
        self.panel_one    = Process(self.panel)
        self.panel_two    = Export(self.panel)
        
        self.panel_two.Hide()
        
        # Sizers
        self.container    = wx.BoxSizer(wx.VERTICAL)
        
        self.hboxA    = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxA1    = wx.BoxSizer(wx.VERTICAL)
        self.vboxA2    = wx.BoxSizer(wx.VERTICAL)
        
        self.hboxB    = wx.BoxSizer(wx.HORIZONTAL)
        
        self.vboxC    = wx.BoxSizer(wx.VERTICAL)
        
        # Static Text
        self.srcTxt = wx.StaticText(self.panel, 0, 'Source Directory:')
        self.tarTxt = wx.StaticText(self.panel, 0, 'Target Directory:')
        
        # Buttons
        self.srcBtn     = wx.Button(self.panel, 101, 'Select Source', size=(150,25))
        self.tarBtn     = wx.Button(self.panel, 102, 'Select Target', size=(150,25))
        self.p1Btn      = wx.Button(self.panel, 103, 'Process', size=(300,25))
        self.p2Btn      = wx.Button(self.panel, 104, 'Export', size=(300,25))
        self.cpyBtn     = wx.Button(self.panel, 105, "Copy Source", size=(150,25))
        
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
        self.hboxB.Add(self.p2Btn, -1, wx.LEFT, 5)
        self.hboxB.AddSpacer((25,1))
        self.hboxB.Add(self.cpyBtn)
        
        self.vboxC.Add(self.panel_one)
        self.vboxC.Add(self.panel_two)
        
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.setSource,    id=101)
        self.Bind(wx.EVT_BUTTON, self.setDest,      id=102)
        self.Bind(wx.EVT_BUTTON, self.showP1,       id=103)
        self.Bind(wx.EVT_BUTTON, self.showP2,       id=104)
        self.Bind(wx.EVT_BUTTON, self.copy,         id=105)
        self.Bind(wx.EVT_TEXT, self.refreshSource,  id=131)
        self.Bind(wx.EVT_TEXT, self.refreshTarget,  id=132)
        
        self.panel.SetSizer(self.container)
        
        self.Centre()
        self.srcTc.WriteText(sPath)
        self.tarTc.WriteText(tPath)
    
    # Handlers
    def setSource(self, event):
        global sPath, sListing
        
        self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
        
        if self.dlg.ShowModal() == wx.ID_OK:
            sPath       = self.dlg.GetPath() + '/'
            sListing    = os.walk(sPath)
            
            self.srcTc.SetValue(sPath)
        
        self.dlg.Destroy()
    
    def setDest(self, event):
        global tPath, tListing
        
        self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
        
        if self.dlg.ShowModal() == wx.ID_OK:
            tPath = self.dlg.GetPath() + '/'
            tListing = os.walk(tPath)
            
            self.tarTc.SetValue(tPath)        
        self.dlg.Destroy()
    
    def refreshSource(self, event):
        global sPath, sListing
        
        sPath = self.srcTc.GetValue()
        sListing = os.walk(sPath)
    
    def refreshTarget(self, event):
        global tPath, tListing
        
        tPath = self.tarTc.GetValue()
        tListing = os.walk(tPath)
    
    def showP1(self, even):
        self.panel_one.SetPosition((0,127))
        self.panel_one.Show()
        self.panel_two.Hide()
    def showP2(self, even):
        self.panel_two.SetPosition((0,127))
        self.panel_one.Hide()
        self.panel_two.Show()
        
    # self.cpyBtn
    def copy(self, event):
        global sListing, root, filename, tPath, dirname
    
        for dirname, dirs, files, in sListing:
            for filename in files:
                rFile = open(dirname + '/' + filename, 'rb')
                self.byte = repr(rFile.read())[513:517]
                if self.byte == 'DICM':
                    self.transfer()
    
    #Helper for copy
    def transfer(self):
        global dirname, filename
        
        newdir  = tPath + dirname
        _source = dirname + "/" + filename
        _target = newdir + "/" + filename

        for dirs in tListing:
            for subdirs in dirs:
                if not os.path.exists(newdir):
                    os.makedirs(newdir)
                    
        shutil.copyfile(_source, _target)
        

       


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
if __name__ == "__main__":
    global _initialTags, _cacheTags
    _genTags()
    
    for pair in _initialTags:
        if pair[1:5] == "0010":
            _cacheTags.append(pair[14:])
    
    app = wx.App(0)
    MainFrame().Show()
    app.MainLoop()
