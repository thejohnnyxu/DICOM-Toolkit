#!/usr/bin/python

import sys, os, dicom, wx
# ------------------------------
class Logic():
    finalPatients = []
    def __init__(self):
        pass
    
    # Support Functions for dtk_main
    def processTags(self, dataset, _removePrivate):
        pass
        
    # ------------------------------
    def mapper(self, parent, dataset, tPath, baseTags):
        # PatientsName/StudyDescription + StudyDate/SeriesDescription + SeriesDate + SeriesTime/
        patients = []
        
        ui = parent
        
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
                    if _lvl1 not in Logic.finalPatients:
                        Logic.finalPatients.append(_lvl1)
        
        # Populates patientDrop in Process
        ui.patientDrop.Clear()
        for e in Logic.finalPatients:
            ui.patientDrop.Append(e)
            
        self.genTagSets(ui, dataset, patients, baseTags)
        
    def genTagSets(self, ui, dataset, patients, baseTags):

        for pat in Logic.finalPatients:
            self.patientName = pat
            self.checkedList = []
            self.newValues   = []
            
            rootPatient = [self.patientName, self.checkedList, self.newValues]
            
            if rootPatient not in ui.tagSet:
                ui.tagSet.append(rootPatient)
                print ui.tagSet
                

if __name__ == "__main__":
    pass
        
    