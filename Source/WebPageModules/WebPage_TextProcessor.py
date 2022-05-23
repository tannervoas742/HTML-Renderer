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
    
class WebPage_TextProcessor:
    def CleanText(self, Text):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if type(Text) != str:
            Text = str(Text)
        for Key in self.TextReplaceMap:
            Text = Text.replace(Key, self.TextReplaceMap[Key])
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return Text

    def CleanLinkText(self, OText):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Text = OText.lower().replace("'", '')
        NewText = ''
        for Char in Text:
            if Char in '-_':
                NewText += Char
            elif Char.isalnum() or Char == ' ':
                NewText += Char
        NewText = NewText.replace(' ', '-')

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if len(NewText) > 0 and NewText[0].isnumeric():
            NewText = 'A' + NewText
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return NewText


    def PreProcessText(self, Text):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        for Key in self.JSCodeMap:
            Text = Text.replace(Key, self.JSCodeMap[Key])
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return Text
            
    def PostProcessPage(self, PageText):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        for Key in self.JSCodeMap:
            PageText = PageText.replace(self.JSCodeMap[Key], Key)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        DCTSLen = len(self.DCTS)
        NewPageText = ''
        CurrentMatch = ''
        PostMatch = ''
        CurrentClose = ''
        CloseSearch = '/>'
        CloseSearchLen = len(CloseSearch)
        for Char in PageText:
            if len(CurrentMatch) == DCTSLen and self.DCTS == CurrentMatch:
                if Char == CloseSearch[len(CurrentClose)]:
                    CurrentClose += Char
                    if len(CurrentClose) == CloseSearchLen and CurrentClose == CloseSearch:
                        NewPageText += PostMatch + '>'
                        CurrentMatch = ''
                        PostMatch = ''
                        CurrentClose = ''
                else:
                    PostMatch += Char
            elif Char == self.DCTS[len(CurrentMatch)]:
                CurrentMatch += Char
            else:
                NewPageText += CurrentMatch + Char
                CurrentMatch = ''
        NewPageText += CurrentMatch + PostMatch + CurrentClose
        PageText = NewPageText

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        for Key in list(self.PostProcessRefList.keys()):
            Goal = Key.split('|+REF+')[0]
            Insert = Key.split('|+REF+')[1][:-2]
            Matched = False
            for LinkUp in self.SeenLinkUps:
                if Insert in LinkUp:
                    Snipped1 = LinkUp.replace('_' + Insert, '')
                    if Snipped1 == Goal:
                        PageText = PageText.replace(Key, LinkUp)
                        Matched = True
                        break
                    Snipped2 = LinkUp.replace(Insert + '_', '')
                    if Snipped2 == Goal:
                        PageText = PageText.replace(Key, LinkUp)
                        Matched = True
                        break
            if not Matched:
                PageText = PageText.replace(Key, Goal)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return PageText