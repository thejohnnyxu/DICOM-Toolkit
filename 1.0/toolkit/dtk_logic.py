#!/usr/bin/python

import sys, os, dicom, wx
# ------------------------------
class Logic():
    finalPatients = []

    # ------------------------------
    def mapper(self, parent, dataset, tPath, baseTags):
        # PatientsName/ StudyDescription + StudyDate/ SeriesDescription + SeriesDate + SeriesTime/
        
        ui = parent
        
        # Creates each group node for each patient
        for data_element in dataset:
            try:
                name = dataset.PatientsName
                if name not in Logic.finalPatients:
                    Logic.finalPatients.append(name)
            except AttributeError:
                break     

        # Populates patientDrop in Process
        ui.patientDrop.Clear()
        for e in Logic.finalPatients:
            ui.patientDrop.Append(e)
            
        self.genTagSets(ui)
    
    # ------------------------------    
    def genTagSets(self, ui):

        for pat in Logic.finalPatients:
            self.patientName    = pat
            self.tagPairs       = {}
            self.insertTags     = []
            
            rootPatient = [self.patientName, self.tagPairs, self.insertTags]
            
            if rootPatient not in ui.tagSet:
                ui.tagSet.append(rootPatient)
                
    # ------------------------------
    def trap(self):
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
        _listing = os.walk(dirname)
    
        for dirs in _listing:
            for subdirs in dirs:
                if not os.path.exists(newdir):
                    os.makedirs(newdir)
    
        # Resets tagLoc    
        tagLoc = 0x10a0
    
        dataset.save_as(newdir + "/" + filename)

    # ------------------------------
    def batchProcess(self, parent, dataset, dirname, tPath, filename, tagSet):
        
        patients = []
        
        ui = parent
        
        tagLoc = 0x10a0
        
        # Clears Private Tags
        if ui.removePrivate:
            dataset.remove_private_tags()
            
        for data_element in dataset:    
            try:    
                self.currentDS = dataset.PatientsName
            
                for pat in tagSet:
                    if pat[0] == self.currentDS:
                        _name = pat[0]
                        for tag in pat[1].items():
                            if tag[0] == "Patient's Name":
                                _name = tag[1]
                        for tag in pat[1].items():
                            if tag[0] == data_element.name:
                                data_element.value = tag[1]
                        for value in pat[2]:
                            tagLoc += 1
                            dataset.AddNew([0x0045, tagLoc], 'UT', value)
                    tagLoc = 0x10a0
            
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
                
                patient = (_name, _stDesc, _stID, _srDesc, _srNum, _srTime)

                if patient not in patients:
                    patients.append(patient)
            except AttributeError:
                break
                
        # Creates the folder hierarchy
        _listing = os.walk(tPath)
        try:
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
                            os.makedirs(dir3)
        except UnicodeDecodeError:
            pass
        
        try:
            dataset.save_as(dir3 + "/" + filename)
        except UnboundLocalError:
            pass
        except UnicodeDecodeError:
            pass
    