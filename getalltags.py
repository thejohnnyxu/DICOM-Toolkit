#!/usr/bin/python

import sys, os, dicom

global tagFile, tagList, iCount, pCount

tagFile = open("allTags.txt", 'wb')
tagList = []
pCount = 0

def openFiles():
    global pCount, iCount
    
    for dirname, dirs, files, in os.walk("/Users/jxu1/documents/IMPACT DVD Dump"):
        for filename in files:
            fPath = dirname + '/' + filename
            rFile = open(fPath, 'rb').read()
            byte = repr(rFile)
            if isDICM(byte, filename):
                ds = dicom.read_file(fPath)
                getTags(ds)
                pCount += 1
                print pCount, "/", iCount
                

def isDICM(bin, filename):
    bin = bin.split("\\")
        
    if "x00DICM" in bin:
        if filename == 'DICOMDIR':
            return False
        if filename.endswith(".dcm") or filename.endswith(".DCM") or "." not in filename:
            return True
    else:
        return False

def getTags(ds):
    global tagFile, tagList
    
    for data_element in ds:
        if data_element.name not in tagList:
            print data_element.name
            tagList.append(data_element.name)
            tagFile.write(data_element.name)
            tagFile.write("\n")
        
if __name__ == "__main__":
    global iCount
    
    iCount = sum([len(files) for (root, dirs, files) in os.walk('/Users/jxu1/documents/IMPACT DVD Dump')])
    print iCount
    
    openFiles()
                
