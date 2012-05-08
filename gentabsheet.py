iFile = open('tags.txt', 'rb')
oFile = open('forpatty.txt', 'wb')
tmpFile = iFile.readlines()

for line in tmpFile:
    groupNumber = line[1:5]
    oFile.write(groupNumber + "\t" +line)