#!/usr/bin/python

import sys, os, dicom, wx, dtk_logic, dtk_parser, webbrowser, datetime

logic = dtk_logic.Logic()
parser = dtk_parser.Parser()

# ------------------------------
class Process(wx.Panel):
    
    cachedTags      = []
    currentPatient  = ""
    focusedTag      = ""
    insertTags      = []
    tagSet          = []
    editPair        = {}
    removePrivate   = True
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.tagGroups  = ["0008", "0010 : Patient Information", "0012 : Clinical Information ", "0014", "0018", "0020", "0022", "0024", "0028",
                        "0032 : Study Information", "0038", "003A", "0040", "0042", "0044", "0046", "0048", "0050",
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
        self.hboxA4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxA5 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hboxB  = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxB1 = wx.BoxSizer(wx.VERTICAL)
        self.vboxB2 = wx.BoxSizer(wx.VERTICAL)
        self.hboxB3 = wx.BoxSizer(wx.HORIZONTAL)
        
        # Buttons
        self.proBtn = wx.Button(self, 101, "Process", size=(150,25))
        self.lodBtn = wx.Button(self, 102, "Load Map", size=(150,25))
        self.chgBtn = wx.Button(self, 103, "Edit Tag", size=(150,25))
        self.addBtn = wx.Button(self, 104, "Add", size=(75,25))
        self.rmvBtn = wx.Button(self, 105, "Remove", size=(75,25))
        self.batBtn = wx.Button(self, 106, "Batch Process", size=(150,25))
        self.mapBtn = wx.Button(self, 107, "Map", size=(150,25))
        self.genBtn = wx.Button(self, 108, "Save Map", size=(150,25))
        self.anoBtn = wx.Button(self, 109, "Anonymize", size=(150,25))
        self.cnlBtn = wx.Button(self, 110, "Remove Edit", size=(380,25))
        
        # Text Ctrl
        self.editTc = wx.TextCtrl(self, 111, 'Input field for new Tag value', size=(600,25))
        self.addTc  = wx.TextCtrl(self, 112, 'Input field for adding Comments', size=(450,25))
        self.tagTc  = wx.TextCtrl(self, 113, 'Select a Tag to edit it', size=(780,25), style=wx.TE_READONLY)
        
        # Combo
        self.tagsDrop = wx.ComboBox(self, 121, size=(780, 25), choices=self.tagGroups, style=wx.CB_READONLY)
        self.patientDrop = wx.ComboBox(self, 122, size=(780, 25), choices=['Patients List'], style=wx.CB_READONLY)
        
        # Checkbox
        self.privateCheck = wx.CheckBox(self, 131, "Remove Private Tags")
        
        # Lines
        self.line1 = wx.StaticLine(self, -1, size=(800,1))
        
        # List Box
        self.tagLBox = wx.ListBox(self, 141, size=(600,135), style=wx.TE_MULTILINE)
        self.changedLBox = wx.ListBox(self, 142, size=(380,230), style=wx.TE_MULTILINE)
        
        # Check List Box
        self.tagCLBox = wx.CheckListBox(self, 151, size=(400,255), choices=Process.cachedTags, style=0)
 
        # Layout
        self.container.Add(self.hboxA)
        self.container.AddSpacer((1,5))
        self.container.Add(self.line1)
        self.container.AddSpacer((1,5))
        self.container.Add(self.hboxB)

        self.hboxA.Add(self.vboxA1, -1, wx.LEFT, 5)
        self.hboxB.Add(self.vboxB1, -1, wx.LEFT, 5)
        self.hboxB.Add(self.vboxB2, -1, wx.LEFT, 25)
        
        self.vboxA1.Add(self.privateCheck)
        self.vboxA1.AddSpacer((1,2))
        self.vboxA1.Add(self.hboxA4)
        self.vboxA1.Add(self.tagsDrop)
        self.vboxA1.AddSpacer((1,2))
        self.vboxA1.Add(self.hboxA5)
        self.vboxA1.AddSpacer((1,2))
        self.vboxA1.Add(self.tagTc)
        self.vboxA1.AddSpacer((1,5))
        self.vboxA1.Add(self.hboxA3)
        self.hboxA3.Add(self.editTc)
        self.hboxA3.AddSpacer((25,1))
        self.hboxA3.Add(self.chgBtn)
        
        self.hboxA5.Add(self.tagCLBox)
        self.hboxA5.Add(self.vboxA2)
        self.vboxA2.Add(self.changedLBox)
        self.vboxA2.Add(self.cnlBtn)
        
        self.hboxA4.Add(self.patientDrop)
                
        self.vboxB1.Add(self.tagLBox)
        self.vboxB1.Add(self.hboxB3)
        self.hboxB3.Add(self.addTc)
        self.hboxB3.Add(self.addBtn)
        self.hboxB3.Add(self.rmvBtn)
        
        self.vboxB2.AddSpacer((1,10))
        self.vboxB2.Add(self.mapBtn)
        self.vboxB2.Add(self.anoBtn)
        self.vboxB2.Add(self.lodBtn)
        self.vboxB2.Add(self.genBtn)
        self.vboxB2.Add(self.batBtn)
        self.vboxB2.Add(self.proBtn)
        
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.process,      id=101)
        self.Bind(wx.EVT_BUTTON, self.loadMap,      id=102)
        self.Bind(wx.EVT_BUTTON, self.change,       id=103)
        self.Bind(wx.EVT_BUTTON, self.add,          id=104)
        self.Bind(wx.EVT_BUTTON, self.remove,       id=105)
        self.Bind(wx.EVT_BUTTON, self.batch,        id=106)
        self.Bind(wx.EVT_BUTTON, self.mapper,       id=107)
        self.Bind(wx.EVT_BUTTON, self.genMap,       id=108)
        self.Bind(wx.EVT_BUTTON, self.anonymize,    id=109)
        self.Bind(wx.EVT_BUTTON, self.removeEdit,   id=110)
        self.Bind(wx.EVT_CHECKLISTBOX, self.flag,   id=151)
        self.Bind(wx.EVT_LISTBOX, self.clicked,     id=151)
        self.Bind(wx.EVT_LISTBOX, self.displayValue,id=142)
        self.Bind(wx.EVT_CHECKBOX, self.privTags,   id=131)
        self.Bind(wx.EVT_COMBOBOX, self.setPatient, id=122)
        self.Bind(wx.EVT_COMBOBOX, self.onSelect,   id=121)
        self.addTc.Bind(wx.EVT_SET_FOCUS, self.clearField)

        # Initial Settings
        self.SetSizer(self.container)
        self.privateCheck.SetValue(True)
        self.removePrivate = True
        self.tagsDrop.SetValue('0010 : Patient Information')
        self.patientDrop.SetValue('Patients List')
    
    # ------------------------------
    # Handlers
        
    # Map Button
    def mapper(self, event):
        global baseTags
        
        print "I : ", Process.tagSet, logic.finalPatients
        Process.editPair    = {}
        Process.tagSet      = []
        isMissing           = False
        print "A : ", Process.tagSet, logic.finalPatients
        
        timeStamp           = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        logName             = "logs/runlog_" + timeStamp + ".txt"  
        errorFile           = open(logName, 'wb')
        
        self.patientDrop.Clear()
        
        dlg1 = wx.MessageDialog(self, 'Mapping the Source Directory may take a long time. Do you want to continue?', 'Mapping', wx.ICON_QUESTION | wx.YES_NO | wx.YES_DEFAULT)
        dlg2 = wx.MessageDialog(self, 'The program has finished mapping the source directory.', 'Done Mapping!', wx.OK | wx.ICON_INFORMATION)
        dlg3 = wx.MessageDialog(self, 'There were files without a Patient\'s Name, please check the runlog.txt for more information', 'Notice!', wx.OK | wx.ICON_INFORMATION)
        
        errorFile.write("The following files are flagged for not having a Patient\'s Name:\n")
        
        if dlg1.ShowModal() == wx.ID_YES:
            dlg1.Destroy()
        
            for idx, val, in enumerate(Process.cachedTags):
                self.tagCLBox.Check(idx, 0)
            
            for dirname, dirs, files, in MainFrame.sListing:
                for filename in files:
                    fPath = dirname + '/' + filename
                    rFile = open(fPath, 'rb').read()
                    self.byte = repr(rFile)
                    if self.isDICM(self.byte, filename):
                        ds = dicom.read_file(fPath)
                        if ds.PatientsName == "":
                            errorFile.write(fPath + "\n")
                            isMissing = True
                        else:
                            logic.mapper(self, ds)
            
            if isMissing:
                dlg3.ShowModal()
                dlg3.Destroy()
                
            logic.genTagSets(self)
            
            dlg2.ShowModal()
            dlg2.Destroy()
            print "F : ", Process.tagSet, logic.finalPatients

    # ------------------------------
    # Process Button
    def process(self, event):

        dlg = wx.MessageDialog(self, 'Done Processing.', 'Notice!', wx.OK | wx.ICON_INFORMATION)
    
        for dirname, dirs, files, in MainFrame.sListing:
            for filename in files:
                fPath = dirname + '/' + filename
                rFile = open(fPath, 'rb').read()
                self.byte = repr(rFile)
                if self.isDICM(self.byte, filename):
                    ds = dicom.read_file(fPath)
                    logic.processTags(self, ds, dirname, tPath, filename)
        
        dlg.ShowModal()
        dlg.Destroy()
        
    # ------------------------------
    # Batch Process Button
    def batch(self, event):

        dlg = wx.MessageDialog(self, 'Batch Processing Done.', 'Notice!', wx.OK | wx.ICON_INFORMATION)
        
        for dirname, dirs, files, in MainFrame.sListing:
            for filename in files:
                fPath = dirname + '/' + filename
                rFile = open(fPath, 'rb').read()
                self.byte = repr(rFile)
                if self.isDICM(self.byte, filename):
                    ds = dicom.read_file(fPath)
                    logic.batchProcess(self, ds, dirname, tPath, filename, Process.tagSet)
        
        dlg.ShowModal()
        dlg.Destroy()
        
    # ------------------------------    
    # self.checklistbox
    def clicked(self, event):

        self.id = event.GetSelection()
        Process.focusedTag = self.tagCLBox.GetString(self.tagCLBox.GetSelection())      
        self.tag = self.tagCLBox.GetString(self.id)
        
        self.tagCLBox.Check(self.id)
        self.tagTc.SetValue(Process.focusedTag)
        
        if self.tagCLBox.IsChecked(self.id):
            if self.tag not in Process.editPair.keys():
                Process.editPair[self.tag] = ''
        else:
            Process.editPair.remove(self.tag)
            
        if Process.editPair.has_key(Process.focusedTag):
            self.editTc.SetValue(Process.editPair[Process.focusedTag])
        else:
            self.editTc.Clear()
            
        self.refreshChecklist()
    
    # ------------------------------
    # Displays is the values of selected Tag in self.changedLBox
    def displayValue(self, event):
        
        self.id = event.GetSelection()
        self.tag = self.changedLBox.GetString(self.id).split(" => ")
        
        Process.focusedTag = self.tag[0]
        
        self.tagTc.SetValue(Process.focusedTag)
            
        if Process.editPair.has_key(Process.focusedTag):
            self.editTc.SetValue(Process.editPair[Process.focusedTag])
        else:
            self.editTc.Clear()
            
    # ------------------------------        
    # self.anoBtn
    def anonymize(self, event):
        print Process.tagSet
        
    # ------------------------------    
    # Refreshes self.tagCLBox
    def refreshChecklist(self):
        
        self.displayList = []
        
        self.curSelc        = self.tagsDrop.GetValue()[:4]
        self.checked        = self.tagCLBox.GetChecked()
        Process.cachedTags  = []        
        
        self.changedLBox.Clear()
        self.tagCLBox.Clear()
        
        # Populates cachedTags
        for pair in baseTags:
            self.word = str(pair[0])
            if self.word[1:5] == self.curSelc:
                Process.cachedTags.append(pair[1])
        
        self.tagCLBox.InsertItems(items=Process.cachedTags, pos=0)
        
        for pair in Process.editPair.items():

            self.displayList.append(pair[0] + " => " + pair[1])
            
        self.changedLBox.InsertItems(items=self.displayList, pos=0)
        
        for idx1, val1, in enumerate(Process.editPair.keys()):
            for idx2, val2, in enumerate(Process.cachedTags):
                if val1 == val2:
                    self.tagCLBox.Check(idx2)

        for pair in Process.editPair.items():
            if Process.focusedTag == pair[0]:
                self.editTc.SetValue(pair[1])
    
    # ------------------------------                
    # self.editTC & self.chgBtn
    def change(self, event):
        global baseTags
        
        Process.editPair[Process.focusedTag] = self.editTc.GetValue()
        
        for pat in Process.tagSet:
            if pat[0] == Process.currentPatient:
                pat[1] = Process.editPair
            
        self.editTc.Clear()
        self.refreshChecklist()
    
    # ------------------------------    
    # Remove edited value for selected Tag
    def removeEdit(self, event):
        curSelc     = self.changedLBox.GetSelection()
        self.val    = self.changedLBox.GetString(curSelc)
        
        self.changedLBox.Delete(curSelc)
        
        for pat in Process.tagSet:
            for key in Process.editPair.keys():
                if key == self.val:
                    del Process.editPair[key]
                    for tag in pat[1]:
                        if key == tag:
                            pat[1].remove(tag)
        
        self.refreshChecklist()
    
    # ------------------------------
    # self.preBtn           
    def loadMap(self, event):
        
        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
        
        if dlg.ShowModal() == wx.ID_OK:
            _path = dlg.GetPath()
            _mypath = os.path.basename(_path)
        dlg.Destroy()
        
        mapFile = open(_path, 'r')
        
        self.patientDrop.Clear()
        
        Process.tagSet      = []
        self.tmpFile        = []
        self.patientName    = ""
        self.tagPairs       = {}
        self.rootPatient    = []
        
        self.mapFile = mapFile.readlines()

        self.mapFile = self.chunks(self.mapFile, 3)
        
        for pat in self.mapFile:
            self.patientName    = parser.parseCode(pat[0])
            self.tagPairs       = parser.parseCode(pat[1])
            self.insertTags     = parser.parseCode(pat[2])
            
            self.rootPatient = [self.patientName, self.tagPairs, self.insertTags]
            
            Process.tagSet.append(self.rootPatient)

        for pat in Process.tagSet:
            self.patientDrop.Append(pat[0])
   
        self.refreshChecklist()
        mapFile.close()
    
    # ------------------------------
    # Creates chunks from the Map File
    def chunks(self, givenList, groupSize):
        return [givenList[i:i+groupSize] for i in range(0, len(givenList), groupSize)]

    # ------------------------------
    # self.tagdrop
    def onSelect(self, event):
        
        self.groupSelc  = self.tagsDrop.GetValue()[:4]
        self.checked    = self.tagCLBox.GetChecked()
        
        Process.cachedTags  = []
        
        self.tagCLBox.Clear()
        
        # Populates Process.cachedTags
        for pair in baseTags:
            self.word = str(pair[0])
            if self.word[1:5] == self.groupSelc:
                Process.cachedTags.append(pair[1])
        
        self.tagCLBox.InsertItems(items=Process.cachedTags, pos=0)
        
        for idx1, val1, in enumerate(Process.editPair.keys()):
            for idx2, val2, in enumerate(Process.cachedTags):
                if val1 == val2:
                    self.tagCLBox.Check(idx2)
                    
        self.refreshChecklist()

    # ------------------------------
    # Sets the Patient in Patient Dropdown
    def setPatient(self, event):

        Process.currentPatient = self.patientDrop.GetValue()
        
        # Uncheck everything
        for idx1, val1, in enumerate(Process.cachedTags):
            self.tagCLBox.Check(idx1, 0)
                    
        # Clears Process.cachedTags
        Process.cachedTags = []
        
        self.tagLBox.Clear()
        
        for pat in Process.tagSet:
            if pat[0] == Process.currentPatient:
                Process.editPair    = pat[1]
                Process.insertTags  = pat[2]
                
        for idx1, val1, in enumerate(Process.editPair.keys()):
            for idx2, val2, in enumerate(Process.cachedTags):
                if val1 == val2:
                    self.tagCLBox.Check(idx2)
                    
        for pat in Process.tagSet:
            if pat[0] == Process.currentPatient:
                for entry in pat[2]:
                    self.tagLBox.Append(entry)
        
        for pat in Process.tagSet:
            if pat[0] == Process.currentPatient:
                pat[1] = Process.editPair
                pat[2] = Process.insertTags
                
        self.refreshChecklist()
        
    # ------------------------------                   
    # self.prvchk
    def privTags(self, event):
        if self.privateCheck.GetValue():
            Process.removePrivate = True
        else:
            Process.removePrivate = False
    
    # ------------------------------
    # self.checklist
    def flag(self, event):
        self.id     = event.GetSelection()
        self.tag    = self.tagCLBox.GetString(self.id)
        
        if self.tagCLBox.IsChecked(self.id):
            Process.editPair[self.tag] = ''
        else:
            Process.editPair.remove(self.tag)
            
    # ------------------------------
    # self.addBtn
    def add(self, event):
       tcVal = self.addTc.GetValue()
        
       Process.insertTags.append(tcVal)
    
       self.tagLBox.Insert(tcVal, pos=0)
        
       self.addTc.Clear()
    
    # ------------------------------   
    # self.rmvBtn
    def remove(self, event):
        curSelc     = self.tagLBox.GetSelection()
        self.val    = self.tagLBox.GetString(curSelc)
        
        self.tagLBox.Delete(curSelc)

        Process.insertTags.remove(self.val)
        
    # ------------------------------
    # Checks if a file is a DICOM image    
    def isDICM(self, bin, filename):
        bin = bin.split("\\")
        
        if "x00DICM" in bin:
            if filename == 'DICOMDIR':
                return False
            if filename.endswith(".dcm") or filename.endswith(".DCM") or "." not in filename:
                return True
        else:
            return False
    
    # ------------------------------                
    def genMap(self, event):
        
        dlg = wx.TextEntryDialog(self, "Name the Map File", "")

        if dlg.ShowModal() == wx.ID_OK:
            mapFileName = dlg.GetValue()
            mapFileName += '.txt'
        dlg.Destroy()
        
        mapFile = open("mapfiles/" + mapFileName, 'wb')
        
        for pat in Process.tagSet:
            for line in pat:
                line = str(line)
                line = line.replace("u'", "'")
                line = line.replace('u"', '"')
                mapFile.write(line + "\n")
                
        mapFile.close()
        
    # ------------------------------    
    def clearField(self, event):
        self.addTc.Clear()

# ------------------------------
class Batch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
# ------------------------------
class MainFrame(wx.Frame):
    tPath = ''
    sPath = ''
    sListing = ''
    tListing = ''
    
    def __init__(self):
        wx.Frame.__init__(self, None, title="DICOM Toolkit", size=(800,705))
    
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
        self.p2Btn      = wx.Button(self.panel, 104, 'Export', size=(300,25))
        self.hlpBtn     = wx.Button(self.panel, 105, "User's Guide", size=(150,25))
        
        # Text Ctrl
        self.srcTc = wx.TextCtrl(self.panel, 131, '', size=(600,25), style=wx.TE_READONLY)
        self.tarTc = wx.TextCtrl(self.panel, 132, '', size=(600,25), style=wx.TE_READONLY)
        
        # Line
        self.line1 = wx.StaticLine(self.panel, -1, size=(800,1))
        self.line2 = wx.StaticLine(self.panel, -1, size=(800,1))
        self.line3 = wx.StaticLine(self.panel, -1, size=(1,600))
        
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
        self.hboxB.Add(self.hlpBtn)

        self.vboxC.Add(self.panel_one)
        self.vboxC.AddSpacer((1,50))
        self.vboxC.Add(self.panel_two)
        
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.setSource,    id=101)
        self.Bind(wx.EVT_BUTTON, self.setDest,      id=102)
        self.Bind(wx.EVT_BUTTON, self.showP1,       id=103)
        self.Bind(wx.EVT_BUTTON, self.showP2,       id=104)
        self.Bind(wx.EVT_BUTTON, self.help,         id=105)
        
        self.panel.SetSizer(self.container)
        
        self.Centre()
        
    # ------------------------------
    # Handlers
    def setSource(self, event):
        
        self.dlg = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
        
        if self.dlg.ShowModal() == wx.ID_OK:
            MainFrame.sPath     = self.dlg.GetPath() + '/'
            MainFrame.sListing  = os.walk(MainFrame.sPath)
            self.srcTc.SetValue(MainFrame.sPath)
            
        self.dlg.Destroy()
    
    # ------------------------------
    def setDest(self, event):
        
        self.dlg = wx.DirDialog(self, "Choose the Target Directory:", style=wx.DD_DEFAULT_STYLE)
        
        if self.dlg.ShowModal() == wx.ID_OK:
            MainFrame.tPath     = self.dlg.GetPath() + '/'
            MainFrame.tListing  = os.walk(MainFrame.tPath)
            self.tarTc.SetValue(MainFrame.tPath)
        
        self.dlg.Destroy()
    
    # ------------------------------
    def showP1(self, event):
        self.panel_one.SetPosition((0,127))
        self.panel_one.Show()
        self.panel_two.Hide()
    def showP2(self, event):
        self.panel_two.SetPosition((0,127))
        self.panel_one.Hide()
        self.panel_two.Show()
    
    # ------------------------------    
    # self.hlpBtn
    def help(self, event):
       webbrowser.open('file:/Users/jxu1/Documents/DICOM/dtk/0.7/toolkit/docs/readme.html')

# ------------------------------
def _genTags():
    global baseTags
    
    baseTags            = []
    Process.cachedTags  = []
    
    tags = open('tags.txt', 'r').readlines()
    
    for line in tags:
        part    = line.split("\t")
        tag     = part[0]
        val     = part[1][:-1]
        pair    = [tag, val]
        
        baseTags.append(pair)
            
# ------------------------------
if __name__ == "__main__":
    global baseTags
    
    _genTags()
    
    for pair in baseTags:
        _word = str(pair[0])[1:5]
        if _word == "0010":
            Process.cachedTags.append(pair[1])
    
    app = wx.App(0)
    MainFrame().Show()
    app.MainLoop()
