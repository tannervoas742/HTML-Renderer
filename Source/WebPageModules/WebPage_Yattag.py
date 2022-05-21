import yattag
import os
import io
import re
from WebPageTools.WebPageEnums import WebPageEnums
from WebPageTools.WebPageStateManager import WebPageStateManager
from WebStructures.WebTable import WebTable
from Utilities.TextProcessor import TextProcessor
from Utilities.Core import *
    
class WebPage_Yattag:
    def InitYattagDocument(self):
        self.Doc, self.Tag, self.Text, self.Line = yattag.Doc(
            defaults = {
                'title': self.MetaData['document']['title']
            },
            errors = {}
        ).ttl()