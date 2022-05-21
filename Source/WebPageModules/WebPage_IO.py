import yattag
import os
import io
import re
from WebPageTools.WebPageEnums import WebPageEnums
from WebPageTools.WebPageStateManager import WebPageStateManager
from WebStructures.WebTable import WebTable
from Utilities.TextProcessor import TextProcessor
from Utilities.Core import *
    
class WebPage_IO:
    def Load(self, SrcJSON):
        CleanTarget = SrcJSON.replace('\\', '/').replace('//', '/').replace('/', os.sep)
        self.JSON = ReadJSON(CleanTarget)

        #NOTE: Required external definition
        self.ConsumeMetaData("_metadata")

    def Save(self, OutHTML):
        CleanTarget = OutHTML.replace('\\', '/').replace('//', '/').replace('/', os.sep)
        with io.open(CleanTarget, mode='w', encoding='utf-8') as OutFile:
            PageText = self.Doc.getvalue()
            #NOTE: Required external definition
            PageText = self.PostProcessPage(PageText)
            OutFile.write(PageText)
        
        CSSPath = '/'.join(OutHTML.split('/')[:-1]).replace('HTML', 'CSS')
        OutCSS = Format('{}/_AUTO_{}.css', CSSPath, self.MetaData['document']['title'])
        CleanTarget = OutCSS.replace('\\', '/').replace('//', '/').replace('/', os.sep)
        with io.open(CleanTarget, mode='w', encoding='utf-8') as OutFile:
            #NOTE: Required external definition
            self.AddCSSFontDefinitions(OutFile)