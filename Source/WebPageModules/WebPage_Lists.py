import yattag
import os
import io
import re
from WebPageTools.WebPageEnums import WebPageEnums
from WebPageTools.WebPageStateManager import WebPageStateManager
from WebStructures.WebTable import WebTable
from Utilities.TextProcessor import TextProcessor
from WebStructures.SimpleHTML import SimpleHTML
from Utilities.Core import *
    
class WebPage_Lists:
    def HandleLists(self, Input, State, Interface, Data):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if '<LIST_START>' in Input:
            if State.GlobalState['in_list_div'] == 0:
                self.Doc.stag('div', self.DCTS, self.Style(State), self.Class(State, 'list-div'))
            else:
                self.Doc.stag('div', self.DCTS, self.Style(State), self.Class(State))
            self.Doc.stag('ul', self.DCTS, self.Style(State), self.Class(State))
            State.GlobalState['in_list_div'] += 1
            return True

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        elif '<LIST_STOP>' in Input:
            self.Doc.stag('/ul', self.DCTS)
            State.GlobalState['in_list_div'] -= 1
            self.Doc.stag('/div', self.DCTS)
            return True

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        elif '<LIST_ITEM>' in Input:
            with self.Tag('li', self.Style(State), self.Class(State)):
                self.AddText(Input.replace('<LIST_ITEM>', ''), State, Interface + ['LIST_ITEM'], Data)
            return True

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return False