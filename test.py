
class Logic:
    global finalPatients
    finalPatients = []
    
    def __init__(self):
        self.mapper()
        
    def mapper(self):
        global finalPatients
        _list = ["1","2","3"]
        
        for e in _list:
            if e not in finalPatients:
                finalPatients.append(e)
                
        for p in finalPatients:
            print p

class Sub():
    global finalPatients
    l = Logic()
    
    print l.finalPatients