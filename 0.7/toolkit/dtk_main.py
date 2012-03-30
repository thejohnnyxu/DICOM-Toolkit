#!/usr/bin/python

import sys, os, dicom, sqlite3, wx, shutil, dtk_logic
 
logic = dtk_logic.Logic()

# ------------------------------
class Process(wx.Panel):
    tagSet      = []
    focusedTag  = ''
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        global _removePrivate, currentTags, baseTags, currentTags, currentPatient, checkedTags, currentTag, focusedTag, tagChanges
        
        checkedTags     = []
        tagChanges      = []
        currentPatient  = ""
        currentTag      = {}
        focusedTag      = ""
        
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
        self.mapBtn = wx.Button(self, 107, "Map",                   size=(150,25))
        
        # Text Ctrl
        self.editTc = wx.TextCtrl(self, 111, '', size=(450,25))
        self.addTc  = wx.TextCtrl(self, 112, '', size=(450,25))
        self.tagTc  = wx.TextCtrl(self, 113, 'Select a Tag', size=(450,25), style=wx.TE_READONLY)
        
        # Combo
        self.tagsDrop = wx.ComboBox(self, 121, size=(600, 25), choices=self.tagGroups, style=wx.CB_READONLY)
        self.patientDrop = wx.ComboBox(self, 122, size=(600, 25), choices=[], style=wx.CB_READONLY)
        
        # Checkbox
        self.privateCheck = wx.CheckBox(self, 112, "Remove Private Tags")
        
        # Dialog
        self.proDlg = wx.MessageDialog(self, 'This may take a few minutes to finish.', 'Processing DICOM Files...', wx.OK|wx.ICON_INFORMATION)
        
        # List Box
        self.tagLBox = wx.ListBox(self, 131, size=(600,140), style=wx.TE_MULTILINE)
        
        # Check List Box
        self.currentTags = []
        self.tagCLBox = wx.CheckListBox(self, 111, size=(600,255), choices=currentTags, style=0)
        
        # Layout
        self.container.Add(self.hboxA)
        self.container.AddSpacer((1,5))
        self.container.Add(self.hboxB)

        self.hboxA.Add(self.vboxA1, -1, wx.LEFT, 5)
        self.hboxA.Add(self.vboxA2, -1, wx.LEFT, 25)
        
        self.hboxB.Add(self.vboxB1, -1, wx.LEFT, 5)
        self.hboxB.Add(self.vboxB2, -1, wx.LEFT, 25)
        
        self.vboxA1.Add(self.privateCheck)
        self.vboxA1.AddSpacer((1,2))
        self.vboxA1.Add(self.patientDrop)
        self.vboxA1.Add(self.tagsDrop)
        self.vboxA1.AddSpacer((1,2))
        self.vboxA1.Add(self.tagCLBox)
        self.vboxA1.AddSpacer((1,2))
        self.vboxA1.Add(self.tagTc)
        self.vboxA1.Add(self.hboxA3)
        self.hboxA3.Add(self.editTc)
        self.hboxA3.Add(self.chgBtn)
        
        self.vboxA2.Add(self.mapBtn, -1, wx.TOP, 18)        
        self.vboxA2.Add(self.preBtn)
                
        self.vboxB1.Add(self.tagLBox)
        self.vboxB1.Add(self.hboxB3)
        self.hboxB3.Add(self.addTc)
        self.hboxB3.Add(self.addBtn)
        self.hboxB3.Add(self.rmvBtn)
        
        self.vboxB2.AddSpacer((1,110))
        self.vboxB2.Add(self.batBtn)
        self.vboxB2.Add(self.proBtn, -1, wx.TOP, 5)
        
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.process,      id=101)
        self.Bind(wx.EVT_BUTTON, self.loadPrev,     id=102)
        self.Bind(wx.EVT_BUTTON, self.change,       id=103)
        self.Bind(wx.EVT_BUTTON, self.add,          id=104)
        self.Bind(wx.EVT_BUTTON, self.remove,       id=105)
        self.Bind(wx.EVT_BUTTON, self.batch,        id=106)
        self.Bind(wx.EVT_BUTTON, self.mapper,       id=107)
        self.Bind(wx.EVT_CHECKLISTBOX, self.flag,   id=111)
        self.Bind(wx.EVT_LISTBOX, self.clicked,     id=111)
        self.Bind(wx.EVT_CHECKBOX, self.privTags,   id=112)
        self.Bind(wx.EVT_COMBOBOX, self.setPatient, id=122)
        self.Bind(wx.EVT_COMBOBOX, self.onSelect,   id=121)
        self.editTc.Bind(wx.EVT_KILL_FOCUS, self.change)
        
        # Initial Settings
        self.SetSizer(self.container)
        self.privateCheck.SetValue(True)
        self.removePrivate = True
        self.tagsDrop.SetValue('0010 : Patient Information')

    # Handlers
    # self.proBtn
    def process(self, event):
        pass
    
    # self.checklistbox
    def clicked(self, event):
        global checkedTags
        
        self.id     = event.GetSelection()
        focusedTag  = (self.tagCLBox.GetString(self.tagCLBox.GetSelection()))
        self.key    = focusedTag[:-1]
        self.tag    = self.tagCLBox.GetString(self.id)
        
        self.tagCLBox.Check(self.id)
        self.tagTc.SetValue(focusedTag)
        
        if self.tagCLBox.IsChecked(self.id):
            checkedTags.append(self.tag)
        else:
            checkedTags.remove(self.tag)
            
        if focusedTag.endswith("*\n"):
            self.editTc.SetValue(_currentTag[self.key])
        else:
            self.editTc.Clear()
        
    # self.editTC & self.chgBtn
    def change(self, event):
        global focusedTag, baseTags, checkedTags, fTag
        
        self.editTcValue = self.editTc.GetValue()
        fTag = focusedTag
        currentTag[fTag] = self.editTcValue
            
        # Adds a changed tick to _initialTags
        for idx, val, in enumerate(baseTags):
            self.dsTag = str(val)[15:-3]
            self.pInit = str(val)[1:15]
            if fTag == self.dsTag:
                baseTags[idx] = pInit + _dsTag + "*\n"
                if self.dsTag.endswith("*"):
                    self.cdsTag = "".join(val.split("*"))[14:-1] + "*\n"
                    baseTags[idx] = self.pInit + self.cdsTag
        
        for idx, val, in enumerate(checkedTags):
            self.dsTag = str(val)[2:-3]
            if fTag == self.dsTag:
                checkedTags[idx] = _dsTag + "*\n"
                if self.dsTag.endswith("*"):
                    self.cdsTag = "".join(val.split("*"))[0:-1] + "*\n"
                    baseTags[idx] = self.pInit + self.cdsTag
                    
        for tag in currentTag.items():
            tagChanges.append(tag)
            if tag[0].endswith("*"):
                tagChanges.remove(tag)
        
        self.refreshChecklist()
        
    # Helper function for change
    def refreshChecklist(self):
        global baseTags
        
        self.curSelc    = self.tagsDrop.GetValue()[:4]
        self.checked    = self.tagCLBox.GetChecked()
        cachedTags      = []
        
        self.tagCLBox.Clear()
        
        # Populates _cacheTags
        for pair in baseTags:
            self.word = str(pair[0])
            if self.word[1:5] == self.curSelc:
                cachedTags.append(pair[1])
        
        self.tagCLBox.InsertItems(items=cachedTags, pos=0)
        
        # Checks all tags from _checkedTags in _cacheTags
        for idx1, val1, in enumerate(checkedTags):
            for idx2, val2, in enumerate(cachedTags):
                if val1 == val2:
                    self.tagCLBox.Check(idx2)

        self.editTc.SetValue(currentTag[fTag])
    
    # self.preBtn           
    def loadPrev(self, event):
        pass
    
    # self.tagdrop
    def onSelect(self, event):
        self.groupSelc    = self.tagsDrop.GetValue()[:4]
        self.checked    = self.tagCLBox.GetChecked()
        
        currentTags  = []
        
        self.tagCLBox.Clear()
        
        # Populates currentTags
        for pair in baseTags:
            self.word = str(pair[0])
            if self.word[1:5] == self.groupSelc:
                currentTags.append(pair[1])
        
        
        self.tagCLBox.InsertItems(items=currentTags, pos=0)
        
        # Checks all tags from _checkedTags in currentTags
        for idx1, val1, in enumerate(checkedTags):
            for idx2, val2, in enumerate(currentTags):
                if val1 == val2:
                    self.tagCLBox.Check(idx2)
                        
                        
    def setPatient(self, event):
       global currentPatient, checkedTags
       
       self.patientSelc = self.patientDrop.GetValue()
       
       currentPatient = self.patientSelc
       
       for pat in Process.tagSet:
           avlbPatients = pat[0]
           if avlbPatients == currentPatient:
               pat = ('will', ['1'], ['2'])
               
    # self.prvchk
    def privTags(self, event):
        pass
    
    # self.checklist
    def flag(self, event):
        pass
            
    # self.addBtn
    def add(self, event):
       pass
       
    # self.rmvBtn
    def remove(self, event):
        pass
        
    def batch(self, event):
        for e in Process.tagSet:
            print e
        
    def mapper(self, event):
        global tPath, baseTags
        
        for dirname, dirs, files, in sListing:
            for filename in files:
                rFile = open(dirname + '/' + filename, 'rb')
                self.byte = repr(rFile.read())[513:517]
                if self.byte == 'DICM':
                    ds = dicom.read_file(dirname +'/'+ filename)
                    logic.mapper(self, ds, tPath, baseTags)        

# ------------------------------
class Batch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

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
    global baseTags, currentTags
    
    baseTags    = []
    currentTags = []
    
    tags = open('tags.txt', 'r').readlines()
    
    for line in tags:
        part    = line.split("\t")
        tag     = part[0]
        val     = part[1]
        pair    = (tag, val)
        
        baseTags.append(pair)
            
# ------------------------------
if __name__ == "__main__":
    global baseTags, currentTags
    
    _genTags()
    
    for pair in baseTags:
        _word = str(pair[0])[1:5]
        if _word == "0010":
            currentTags.append(pair[1])
    
    app = wx.App(0)
    MainFrame().Show()
    app.MainLoop()
