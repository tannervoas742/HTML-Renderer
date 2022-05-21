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
    
class WebPage_Yattag:
    def __init__(self):
        self.HTML = SimpleHTML(self)
        self.DCTS = '_DONT_CLOSE_THIS_STAG_'

    def InitYattagDocument(self):
        self.Doc, self.Tag, self.Text, self.Line = yattag.Doc(
            defaults = {
                'title': self.MetaData['document']['title']
            },
            errors = {}
        ).ttl()