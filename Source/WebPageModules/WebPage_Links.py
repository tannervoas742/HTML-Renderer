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
    
class WebPage_Links:
    def HandleLinks(self, Input, State, Interface, Data, TextTag='p', ForceTextTag=None, IsKey=False):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Matched = False

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        FontClass = ''
        if IsKey:
            FontClass = Format('font-class-{}', State['key_font'])
        else:
            FontClass = Format('font-class-{}', State['font'])
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        HasRef = None
        MatchData = self.TP.Index(0, self.TP.Split(self.TP.Extract('<REF:.>', Input, False)))
        if self.TP.Match:
            HasRef = '|+REF+' + '+'.join(list(map(lambda Match: self.CleanLinkText(Match), MatchData[0].split(':')))) + '+|'
            Input = Input.replace(Format('<REF:{}>', MatchData[0]), '')

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        MatchData = self.TP.Index(0, self.TP.Split(self.TP.Extract('<GOTO:.>', Input, False)))
        if self.TP.Match:
            self.Doc.stag(TextTag, self.DCTS, self.Style(State), self.Class(State, FontClass))
            Matched = True

        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            if 'display:inline' not in State['style'] and 'force-no-inline' not in State:
                if 'LIST_ITEM' not in Interface:
                    State['style'] += ['display:inline']
            elif 'display:inline' in State['style']:
                del State['style'][State['style'].index('display:inline')]
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        while self.TP.Match:           

        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            HitAleady = False
            if not HitAleady:
                GotoPattern1 = re.compile('.*?<GOTO:(.*?):(.*?)\+(.*?)>.*')
                GotoMatch1 = GotoPattern1.match(Input)
                if GotoMatch1 != None:
                    Text = GotoMatch1.group(1)
                    File = GotoMatch1.group(2)
                    Location = GotoMatch1.group(3)
                    ToReplace = Format("<GOTO:{}:{}+{}>", Text, File, Location)
                    self.Text(Input.split(ToReplace)[0])
                    LinkAddress = Format('\'{0}.html#{1}\'', File, self.CleanLinkText(Location))
                    if HasRef != None:
                        LinkAddress = LinkAddress[1:-1] + HasRef
                        self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                        LinkAddress = Format("'{}'", LinkAddress)
                    if LinkAddress not in self.SeenLinkDowns:
                        self.SeenLinkDowns[LinkAddress] = 0
                    self.SeenLinkDowns[LinkAddress] += 1    
                    with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), self.Style(State), self.Class(State, 'is-anchor-link')):
                        self.Text(Text)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    HitAleady = True
            if not HitAleady:
                GotoPattern2 = re.compile('.*?<GOTO:(.*?):(.*?)>.*')
                GotoMatch2 = GotoPattern2.match(Input)
                if GotoMatch2 != None:
                    Text = GotoMatch2.group(1)
                    File = GotoMatch2.group(2)
                    ToReplace = Format("<GOTO:{}:{}>", Text, File)
                    self.Text(Input.split(ToReplace)[0])
                    LinkAddress = Format('\"{0}.html\"', File)
                    if HasRef != None:
                        LinkAddress = LinkAddress[1:-1] + HasRef
                        self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                        LinkAddress = Format("'{}'", LinkAddress)
                    if LinkAddress not in self.SeenLinkDowns:
                        self.SeenLinkDowns[LinkAddress] = 0
                    self.SeenLinkDowns[LinkAddress] += 1  
                    with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), self.Style(State), self.Class(State)):
                        self.Text(Text)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    HitAleady = True
            if not HitAleady:
                GotoPattern3 = re.compile('.*?<GOTO:(.*?)\+(.*?)>.*')
                GotoMatch3 = GotoPattern3.match(Input)
                if GotoMatch3 != None:
                    File = GotoMatch3.group(1)
                    Text = File
                    Location = GotoMatch3.group(2)
                    ToReplace = Format("<GOTO:{}+{}>", Text, Location)
                    self.Text(Input.split(ToReplace)[0])
                    LinkAddress = Format('\"{0}.html#{1}\"', File, self.CleanLinkText(Location))
                    if HasRef != None:
                        LinkAddress = LinkAddress[1:-1] + HasRef
                        self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                        LinkAddress = Format("'{}'", LinkAddress)
                    if LinkAddress not in self.SeenLinkDowns:
                        self.SeenLinkDowns[LinkAddress] = 0
                    self.SeenLinkDowns[LinkAddress] += 1  
                    with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), self.Style(State), self.Class(State, 'is-anchor-link')):
                        self.Text(Text)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    HitAleady = True
            if not HitAleady:
                GotoPattern4 = re.compile('.*?<GOTO:(.*?)>.*')
                GotoMatch4 = GotoPattern4.match(Input)
                if GotoMatch4 != None:
                    File = GotoMatch4.group(1)
                    Text = File
                    ToReplace = Format("<GOTO:{}>", Text)
                    self.Text(Input.split(ToReplace)[0])
                    LinkAddress = Format('\"{0}.html\"', File)
                    if HasRef != None:
                        LinkAddress = LinkAddress[1:-1] + HasRef
                        self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                        LinkAddress = Format("'{}'", LinkAddress)
                    if LinkAddress not in self.SeenLinkDowns:
                        self.SeenLinkDowns[LinkAddress] = 0
                    self.SeenLinkDowns[LinkAddress] += 1  
                    with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), self.Style(State), self.Class(State)):
                        self.Text(Input)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    HitAleady = True
    
        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            MatchData = self.TP.Index(0, self.TP.Split(self.TP.Extract('<GOTO:.>', Input, False)))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if Matched:
            if Input.strip() != '' or ForceTextTag != None:
                self.Text(Input)
            if IsKey:
                if len(State['next.key_font']) > 0:
                    State['key_font'] = State['next.key_font'][0]
                    State['next.key_font'] = State['next.key_font'][1:]
            else:
                if len(State['next.font']) > 0:
                    State['font'] = State['next.font'][0]
                    State['next.font'] = State['next.font'][1:]
            return True

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if Matched:
            self.Doc.stag('/' + TextTag, self.DCTS, self.Style(State), self.Class(State, FontClass))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        else:
            return False