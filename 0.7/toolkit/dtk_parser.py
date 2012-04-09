#!/usr/bin/python

import dtk_logic
class Parser():
    def parseDict(self, dict_string):
        d = {}
    
        #remove leading and trailing {}
        dict_string = self.removeFirstLast(dict_string)
        #get each element in dict
        elements = dict_string.split(",")

        #add each element to the dict
        for element in elements:
            parts = element.split(":")
            #parse the key and the corresponding value
            key = self.parseCode(parts[0])
            value = self.parseCode(parts[1])
            d[key] = value

        return d

    def parseList(self, list_string):
        l = []

        #remove leading and trailing []
        list_string = self.removeFirstLast(list_string)
    
        #get each element in list
        elements = list_string.split(",")

        #add each element to the list
        for element in elements:
            value = self.parseCode(element)
            l.append(value)
        
        return l
        

    def parseStringOrNumber(self, text):
        try:
            #first try to parse as float
            if "." in text:
                ret = float(text)
            else:
                ret = int(text)
            return ret
        except:
            return text


    def parseCode(self, text):
        '''Parse a string into a dictionary, number, or string'''
        text = self.deleteOutsideSpaces(text)

        #if the top level is a dictionary (first and last character are { and }
        if text[0] == "{" and text[len(text) - 1] == "}":
            return self.parseDict(text)
        #parse a list
        elif text[0] == "[" and text[len(text) - 1] == "]":
            return self.parseList(text)
        #if it is a special string character in python language,
        #simply return the text without the " character or the ' character
        #at the beginning and end
        elif (text[0] == '"' and text[len(text) - 1] == '"') or \
             (text[0] == "'" and text[len(text) - 1] == "'"):
            text = self.removeFirstLast(text)
            return text
        else:
            return self.parseStringOrNumber(text)

    def removeFirstLast(self, text):
        '''Removes the first and last characters in the string'''
        text = text[1:-1]
        return text

    def deleteOutsideSpaces(self, text):
        '''Deletes the leading and trailing spaces in text'''
    
        while text[0] == " ":
            text = text[1:]
        
        length = len(text)
        while length > 0 and text[length - 1] == " ":
            length -= 1
            text = text[:length]

        return text