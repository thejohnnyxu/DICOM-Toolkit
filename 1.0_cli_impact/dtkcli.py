#!/usr/bin/python

import sys, os, dicom

class Main():
    
    sPath = "/Users/jxu1/Documents/DICOM/IMPACT DVD DUMP/8/"
    tPath = "/Users/jxu1/Documents/DICOM/dump/8/"
    
    def process(self):
        
        for dirname, dirs, files, in os.walk(Main.sPath):
            for filename in files:
                fPath = dirname + '/' + filename
                rFile = open(fPath, 'rb').read()
                self.byte = repr(rFile)
                if self.isDICM(self.byte, filename):
                    ds = dicom.read_file(fPath)
                    self.impact(self, ds, dirname, Main.tPath, filename)
                    
        print 'Done!'
        
    def isDICM(self, bin, filename):
        bin = bin.split("\\")
        
        if "x00DICM" in bin:
            if filename == 'DICOMDIR':
                return False
            if filename.endswith(".dcm") or filename.endswith(".DCM") or "." not in filename:
                return True
        else:
            return False

    def impact(self, parent, dataset, dirname, tPath, filename):
        
        toBlank = ["Institution Address", "Referring Physician's Name", "Referring Physician's Address",
                   "Referring Physician's Telephone Numbers", "Referring Physician Identification Sequence", "Institutional Department Name",
                   "Physician(s) of Record", "Performing Physician's Name", "Name of Physician(s) Reading Study", "Operators' Name",
                   "Issuer of Patient ID", "Patient's Insurance Plan Code Sequence", "Other Patient IDs",
                   "Other Patient Names", "Other Patient IDs Sequence", "Patient's Birth Name", "Patient's Address",
                   "Insurance Plan Identification", "Patient's Mother's Birth Name", "Military Rank", "Branch of Service",
                   "Medical Record Locator", "Patient's Telephone Number"]
        
        patients    = []
        ui          = parent
        timePoint   = dirname.split("/")[-3][-2:]
        path        = dirname.split("/")
        folderName  = path[-3]
        newName     = folderName[:7]
        pId         = "C97-830_" + newName
        
        dataset.remove_private_tags()
        
        dataset.PatientsName                = newName
        dataset.PatientID                   = pId
        dataset.ClinicalTrialSponsorName    = "Biogen"
        dataset.ClinicalTrialProtocolID     = "C97-830"
        dataset.ClinicalTrialProtocolName   = "IMPACT"
        dataset.ClinicalTrailSiteID         = newName[:3]
        dataset.ClinicalTrialSubjectID      = newName
        
        if timePoint == "00":
            dataset.ClinicalTrialTimePointDescription = "BASELINE"
        elif timePoint == "12":
            dataset.ClinicalTrialTimePointDescription = "Month 12"
        elif timePoint == "24":
            dataset.ClinicalTrialTimePointDescription = "Month 24"
        
        for data_element in dataset:
            for tag in toBlank:
                if tag == data_element.name:
                    data_element.value = ''
            
        if "StudyDescription" in dataset:
            _stDesc = str(dataset.StudyDescription)
        else:    
            _stDesc = ""
        if "StudyDate" in dataset:
            _stID   = str(dataset.StudyDate)
        else:    
            _stID   = ""    
        if "SeriesDescription" in dataset:
            _srDesc = str(dataset.SeriesDescription)
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
                
        patient = (newName, _stDesc, _stID, _srDesc, _srNum, _srTime)
                        
        if patient not in patients:
            patients.append(patient)

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
        
if __name__ == "__main__":
    
    main = Main()
    
    main.process()