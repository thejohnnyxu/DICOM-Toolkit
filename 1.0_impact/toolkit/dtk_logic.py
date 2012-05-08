#!/usr/bin/python

import sys, os, dicom, wx
# ------------------------------
class Logic():
    finalPatients   = {}
    tmpPatients     = []
    
    # ------------------------------
    def mapper(self, parent, dataset, folderName):
        # PatientsName/ StudyDescription + StudyDate/ SeriesDescription + SeriesDate + SeriesTime/

        ui = parent

        
        # Creates each group node for each patient
        for data_element in dataset:
            try:
                name        = dataset.PatientsName
                folderName  = folderName
                patient     = [folderName, name]
                
                Logic.tmpPatients.append(patient)
            except AttributeError:
                break
                
    # ------------------------------    
    def genTagSets(self, parent):

        ui = parent

        for pat in Logic.tmpPatients:
            if not Logic.finalPatients.has_key(pat[0]):
                Logic.finalPatients[pat[0]] = [pat[1]]
            if pat[1] not in Logic.finalPatients[pat[0]]:
                Logic.finalPatients[pat[0]].append(pat[1])
                
        # Populates patientDrop in Process
        ui.patientDrop.Clear()
        for pat in Logic.finalPatients.keys():
            ui.patientDrop.Append(pat)
        
        for patID in Logic.finalPatients.items():
            self.patientID      = patID
            self.tagPairs       = {}
            self.insertTags     = []
            
            rootPatient = [self.patientID, self.tagPairs, self.insertTags]
            
            if rootPatient not in ui.tagSet:
                ui.tagSet.append(rootPatient)
                
            Logic.finalPatients = []
                
    # ------------------------------
    def presetProcess(self, parent, dataset, dirname, tPath, filename, tagSet):
        
        patients    = []
        ui          = parent
        timePoint   = dirname.split("/")[-3][-2:]
        origName    = dataset.PatientsName
        
        # Clears Private Tags
        if ui.removePrivate:
            dataset.remove_private_tags()
        
        try:
            for data_element in dataset:
                for pat in tagSet:
                    _patientName = pat[0][1]
                    _newName = pat[0][0][:7]
                    _changes = pat[1]
                    _comments = pat[2]
                    if _patientName == origName:
                        for tag in _changes.items():
                            if tag[0] == data_element.name:
                                data_element.value = tag[1]
                        for comment in _comments:
                            tagLoc += 1
                            dataset.AddNew([0x0045, tagLoc], 'UT', comment)
                        
                        # Biogen Specs
                        dataset.PatientsName                = _newName
                        dataset.ClinicalTrialSponsorName    = "Biogen"
                        dataset.ClinicalTrialProtocolID     = "C97-830"
                        dataset.ClinicalTrialProtocolName   = "IMPACT"
                        dataset.ClinicalTrailSiteID         = _newName[:3]
                        dataset.ClinicalTrialSubjectID      = _newName
                        
                        if pat[0][0][-2:] == "00":
                            dataset.ClinicalTrialTimePointDescription = "BASELINE"
                        elif pat[0][0][-2:] == "12":
                            dataset.ClinicalTrialTimePointDescription = "Month 12"
                        elif pat[0][0][-2:] == "24":
                            dataset.ClinicalTrialTimePointDescription = "Month 24"
                            
                        # Folder Structure    
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
                
                        patient = (_newName, _stDesc, _stID, _srDesc, _srNum, _srTime)
                        
                        if patient not in patients:
                            patients.append(patient)                    
        except:
            pass    

        # Creates the folder hierarchy
        try:
            for dirs in os.walk(tPath):
                for subdirs in dirs:
                    for patient in patients:
                        _lvl1 = patient[0]
                        if "/" in _lvl1:
                            _lvl1 = _lvl1.replace("/", "-")
                        _lvl2 = patient[1] + "_" + patient[2]
                        _lvl3 = patient[3] + "_" + patient[4] + "_" + patient[5]
                        dir1 = tPath + _lvl1
                        dir2 = dir1 + "/" + _lvl2 + "_" + timePoint
                        dir3 = dir2 + "/" + _lvl3
                        if not os.path.exists(dir1):
                            os.makedirs(dir1)
                        if not os.path.exists(dir2):
                            os.makedirs(dir2)
                        if not os.path.exists(dir3):
                            os.makedirs(dir3)
        except UnicodeDecodeError:
            pass
        
        try:
            dataset.save_as(dir3 + "/" + filename)
        except UnboundLocalError:
            pass
        except UnicodeDecodeError:
            pass
        
                
    # ------------------------------
    def processTags(self, parent, dataset, dirname, tPath, filename):
    
        ui = parent
        
        # Initiates TagLoc
        tagLoc = 0x10a0
        
        # Clears Private Tags
        if ui.removePrivate:
            dataset.remove_private_tags()

        # Blanks all checked Tags 
        for data_element in dataset:
            for tag in ui.editPair.items():
                if tag[0] == data_element.name:
                    data_element.value = tag[1]
                    
        # Adds private Tags
        for value in ui.insertTags:
            tagLoc += 1
            dataset.AddNew([0x0045, tagLoc], 'UT', value)
    
        root = os.path.relpath(dirname)
        root = "".join(root.split("../"))

        newdir = tPath + root
    
        for dirs in os.walk(dirname):
            for subdirs in dirs:
                if not os.path.exists(newdir):
                    os.makedirs(newdir)
    
        # Resets tagLoc    
        tagLoc = 0x10a0
    
        dataset.save_as(newdir + "/" + filename)

    # ------------------------------
    def batchProcess(self, parent, dataset, dirname, tPath, filename, tagSet):
        
        patients    = []
        ui          = parent
        tagLoc      = 0x10a0
        timePoint   = dirname.split("/")[-3][-2:]
        origName    = dataset.PatientsName
        
        # Clears Private Tags
        if ui.removePrivate:
            dataset.remove_private_tags()
        
        try:
            for data_element in dataset:
                for pat in tagSet:
                    _patientName = pat[0][1]
                    _newName = pat[1]["Patient's Name"]
                    _changes = pat[1]
                    _comments = pat[2]
                    if _patientName == origName:
                        for tag in _changes.items():
                            print tag
                            if tag[0] == data_element.name:
                                data_element.value = tag[1]
                        for comment in _comments:
                            tagLoc += 1
                            dataset.AddNew([0x0045, tagLoc], 'UT', comment)
                            
                        dataset.PatientsName = _newName
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
                
                        patient = (_newName, _stDesc, _stID, _srDesc, _srNum, _srTime)
                        
                        if patient not in patients:
                            patients.append(patient)                    
        except:
            pass    

        # Creates the folder hierarchy
        try:
            for dirs in os.walk(tPath):
                for subdirs in dirs:
                    for patient in patients:
                        _lvl1 = patient[0]
                        if "/" in _lvl1:
                            _lvl1 = _lvl1.replace("/", "-")
                        _lvl2 = patient[1] + "_" + patient[2]
                        _lvl3 = patient[3] + "_" + patient[4] + "_" + patient[5]
                        dir1 = tPath + _lvl1
                        dir2 = dir1 + "/" + _lvl2 + "_" + timePoint
                        dir3 = dir2 + "/" + _lvl3
                        if not os.path.exists(dir1):
                            os.makedirs(dir1)
                        if not os.path.exists(dir2):
                            os.makedirs(dir2)
                        if not os.path.exists(dir3):
                            os.makedirs(dir3)
        except UnicodeDecodeError:
            pass
        
        try:
            dataset.save_as(dir3 + "/" + filename)
        except UnboundLocalError:
            pass
        except UnicodeDecodeError:
            pass