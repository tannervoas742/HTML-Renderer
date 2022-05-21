import yattag
import os
import io
import re
from WebPageModules.WebPage_IO import WebPage_IO
from WebPageModules.WebPage_Yattag import WebPage_Yattag
from WebPageModules.WebPage_Tables import WebPage_Tables
from WebPageTools.WebPageEnums import WebPageEnums
from WebPageTools.WebPageStateManager import WebPageStateManager
from WebStructures.WebTable import WebTable
from Utilities.TextProcessor import TextProcessor
from Utilities.Core import *
    
class WebPage(WebPage_IO, WebPage_Yattag, WebPage_Tables):
    def InitContainers(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.TP = TextProcessor()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.SeenLinkUps = {}
        self.SeenLinkDowns = {}
        self.PostProcessRefList = {}
        self.ParamStorage = {}
        self.CollapseModelCount = 0
        self.CollapseModelRows = {}

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.JSCodeMap = {
            '<': '|~lt~|',
            '>': '|~gt~|',
            '&': '|~and~|',
            '—': '|~em~dash~|'
        }

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.TextReplaceMap = {
            '<BOLD>': self.PreProcessText('<b>'),
            '<ITALIC>': self.PreProcessText('<i>'),
            '<HIGHLIGHT>': self.PreProcessText('<mark>'),
            '<SMALL>': self.PreProcessText('<small>'),
            '<STRIKE>': self.PreProcessText('<del>'),
            '<UNDER>': self.PreProcessText('<ins>'),
            '<SUB>': self.PreProcessText('<sub>'),
            '<SUP>': self.PreProcessText('<sup>'),
            '—': self.PreProcessText('—')
        }
        for Key in list(self.TextReplaceMap.keys()):
            NewKey = Key.replace('<', '</')
            NewValue = self.TextReplaceMap[Key].replace(self.PreProcessText('<'), self.PreProcessText('</'))
            self.TextReplaceMap[NewKey] = NewValue

    def HeadAndLinkHTML(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Tag('head'):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            self.Doc.stag('meta', 'charset="UTF-8"')
            self.Doc.stag('link', 'rel="stylesheet"', 'href="../CSS/Bootstrap.css"')
            self.Doc.stag('link', 'rel="stylesheet"', 'href="../CSS/Materialize.css"')
            self.Doc.stag('link', 'rel="stylesheet"', 'href="../CSS/MyStyle.css"')
            self.Doc.stag('link', 'rel="stylesheet"', Format('href="../CSS/_AUTO_{}.css"', self.MetaData['document']['title']))
            
        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            with self.Tag('script', 'type="text/javascript"', 'src="../JS/JQuery-1.2.6.js"'):
                pass
            with self.Tag('script', 'type="text/javascript"', 'src="../JS/Bootstrap.js"'):
                pass
            with self.Tag('script', 'type="text/javascript"', 'src="../JS/Materialize.js"'):
                pass
            with self.Tag('script', 'type="text/javascript"', 'src="../JS/MyFunctionality.js"'):
                pass

        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            if 'javascript' in self.MetaData:
                for File in self.MetaData['javascript']:
                    with self.Tag('script', Format('type="text/javascript"', 'src="{}"', File)):
                        pass
    
    def StickyHeaderSection(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Tag('header'):
            with self.Tag('nav', id='sticky-header-nav'):
                with self.Tag('div'):
                    with self.Tag('ul'):
                        with self.Tag('li'):
                            self.Line('a', 'TBD')

    def CoreBodyStructure(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Tag('body', klass='content html-renderer'):
            with self.Tag('div', klass='body-div'):
                with self.Tag('div', klass='header-spacer'):
                    self.Line('p', ' ')
        
        #       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                self.LoadLevel(self.JSON)
        
        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            self.AddJS()

    def AddFooter(self, State = None):
        with self.Tag('footer'):
            if State == None:
                State = self.InitNewStateManager()
            if 'authors' in self.MetaData['document']:
                if type(self.MetaData['document']['authors']) == list:
                    for Author in self.MetaData['document']['authors']:
                        self.AddText(Format('Author: {}', Author), State, [], None)
                else:
                    self.AddText(Format('Author: {}', self.MetaData['document']['authors']), State, [], None)
            if 'date' in self.MetaData['document']:
                self.AddText(Format('Last Modified: {}', self.MetaData['document']['date']), State, [], None)

    def AddJS(self, State = None):
        if State == None:
            State = self.InitNewStateManager()

        documentReadFuncCollapsible = []
        documentReadFuncCollapsible += ['$(document).ready(function() {{']
        documentReadFuncCollapsible += ['    $(\'.collapsible-model{0}\').collapsible();']
        documentReadFuncCollapsible += ['}});']
        documentReadFuncCollapsible = '\n'.join(documentReadFuncCollapsible)

        with self.Tag('script'):
            for Model in range(self.CollapseModelCount):
                self.Text(self.PreProcessText(Format(documentReadFuncCollapsible, Model)))
                for Row in range(self.CollapseModelRows[Model]):
                    pass

    def __init__(self, SrcJSON):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        WebPage_IO.__init__(self)
        WebPage_Yattag.__init__(self)
        WebPage_Tables.__init__(self)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.Load(SrcJSON)
        self.InitContainers()
        self.InitYattagDocument()
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Tag('html', 'id="top-html"'):
            self.HeadAndLinkHTML()
            self.StickyHeaderSection()
            self.Doc.stag('br')
            self.CoreBodyStructure()
            self.Doc.stag('br')
            self.AddFooter()

    def LoadLevel(self, Input, State = None):
        if State == None:
            State = self.InitNewStateManager()
        if type(Input) not in [list, dict]:
            Rank, Input, Interface = self.GetInterfaceFromKey(str(Input))
            NewState = State.MixState(Interface, self)
            self.LoadItem(Input, NewState, Interface)
            return
        InputSorted = None
        if type(Input) == list:
            InputSorted = Input
        else:
            Items = len(list(Input.keys()))
            Digits = 2
            while Items >= 10:
                Digits += 1
                Items /= 10
            FormatString = '{:0>' + str(Digits) + '}'
            InputSorted = list(sorted(Input.keys(), key=lambda Key: Format(FormatString, self.GetInterfaceFromKey(Key)[0])))
        LastItemWasCollapse = False
        CollapseModelCount = self.CollapseModelCount
        CollapseRowCount = 0
        for OriginalKey in InputSorted:
            if type(OriginalKey) in [list, dict]:
                self.LoadLevel(OriginalKey, State)
                continue
            Rank, Key, Interface = self.GetInterfaceFromKey(OriginalKey)   
            NewState = State.MixState(Interface, self)                
            
            if type(Input) == dict:
                if 'COLLAPSE' in Interface:
                    if LastItemWasCollapse == False:
                        CollapseModelCount = self.CollapseModelCount
                        self.CollapseModelCount += 1
                        self.Doc.stag('br', style='; '.join(NewState['style']), klass=' '.join(NewState['class'] + ['pre-collapsible-br']))
                        self.Doc.stag('ul', Format('id="collapsible-model{}"', CollapseModelCount), self.DCTS, style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + [Format('collapsible collapsible-model{}', CollapseModelCount)]))
                        self.Doc.stag('li', Format('id="list-item-mode{}-row{}"', CollapseModelCount, CollapseRowCount), self.DCTS, style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + ['list-collapsible']))
                    else:
                        self.Doc.stag('/li', self.DCTS)
                        self.Doc.stag('li', Format('id="list-item-mode{}-row{}"', CollapseModelCount, CollapseRowCount), self.DCTS, style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + ['list-collapsible']))
                    self.Doc.stag('div', Format('id="collapsible-header{}-row{}"', CollapseModelCount, CollapseRowCount), self.DCTS, style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + [Format('collapsible-header normal-collapsible closed-header collapsible-header{}-row{}', CollapseModelCount, CollapseRowCount)]))
                elif LastItemWasCollapse:
                    self.CollapseModelRows[CollapseModelCount] = CollapseRowCount
                    CollapseRowCount += 0
                    LastItemWasCollapse = False
                    self.Doc.stag('/li', self.DCTS)
                    self.Doc.stag('/ul', self.DCTS)
                    
                ContinueFlag, Input[OriginalKey] = self.LoadItem(Key, NewState, Interface, Input[OriginalKey], IsKey=True)
                if 'COLLAPSE' in Interface:
                    self.Doc.stag('/div', self.DCTS)
                NewState['key'] += [Key]
                if 'COLLAPSE' in Interface:
                    self.Doc.stag('div', Format('id="collapsible-body{}-row{}"', CollapseModelCount, CollapseRowCount), self.DCTS, style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + [Format('collapsible-body collapsible-body{}-row{}', CollapseModelCount, CollapseRowCount)]))
                if ContinueFlag:
                    self.LoadLevel(Input[OriginalKey], NewState)
                if 'COLLAPSE' in Interface:
                    self.Doc.stag('/div', self.DCTS)
                    CollapseRowCount += 1
                    LastItemWasCollapse = True
                del NewState['key'][-1]
            elif type(Input) == list:
                if State['visible'] == True:
                    self.AddText(Key, NewState, Interface, None)
            elif type(Key) in [list, dict]:
                self.LoadLevel(Key, NewState)
        if LastItemWasCollapse == True:
            self.CollapseModelRows[CollapseModelCount] = CollapseRowCount
            self.Doc.stag('/li', self.DCTS)
            self.Doc.stag('/ul', self.DCTS)

    def ApplyCallbacks(self, Input, State, Interface, Data):
        if len(State['callbacks']) > 0:
            for Callback in State['callbacks']:
                Data = Callback(self, State, Interface, Data)
        return Input, State, Interface, Data

    def ApplyAPPENDCommandFamily(self, Input, State, Interface, Data):
        MatchData = self.TP.Index(0, self.TP.Split(self.TP.Extract('APPEND_BEFORE(.)', Interface, True)))
        if self.TP.Match:
            for Pattern in MatchData:
                Data = list(map(lambda Val: Pattern + str(Val), Data))
        MatchData = self.TP.Index(0, self.TP.Split(self.TP.Extract('APPEND_AFTER(.)', Interface, True)))
        if self.TP.Match:
            for Pattern in MatchData:
                Data = list(map(lambda Val: str(Val) + Pattern, Data))
        return Input, State, Interface, Data
    
    def ApplyLOOKUPCommand(self, Input, State, Interface, Data):
        MatchData = self.TP.Index(0, self.TP.Split(self.TP.Extract('LOOKUP(.)', Interface, True)))      
        if self.TP.Match:
            for Key in MatchData:
                Data = list(map(lambda Val: Val if Key not in self.ParamStorage or Val not in self.ParamStorage[Key] else self.ParamStorage[Key][Val], list(map(lambda Com: str(Com).split('#')[0], Data))))
        return Input, State, Interface, Data

    def ApplyINCCommand(self, Input, State, Interface, Data):
        Computed = []
        IntData = list(filter(lambda Item: type(Item) == int, Data))
        IntData.sort()
        for i in IntData:
            while len(Computed) < i:
                if len(Computed) == 0:
                    Computed += [0]
                else:
                    Computed += [Computed[-1]]
            Computed[i - 1] += 1
        StrData = list(sorted(list(filter(lambda Item: type(Item) == str, Data)), key=lambda Sort: int(Sort.split('=')[0])))
        for i in StrData:
            Index = int(i.split('=')[0]) - 1
            Value = i.split('=')[1]
            while len(Computed) < Index + 1:
                Computed += [Computed[-1]]
            for j in range(Index, len(Computed)):
                Computed[j] = Value
        return Input, State, Interface, Computed

    def ApplyRANGECommand(self, Input, State, Interface, Data):
        Computed = []
        while len(Data) >= 2:
            Computed += [i for i in range(Data[0], Data[1] + 1)]
            Data = Data[2:]
        Computed.sort()
        
        return Input, State, Interface, Computed

    def LoadItem(self, Input, State, Interface, Data=None, IsKey=False):
        ContinueFlag = True
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Input, State, Interface, Data = self.ApplyCallbacks(Input, State, Interface, Data)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if 'INC' in Interface:
            Input, State, Interface, Data = self.ApplyINCCommand(Input, State, Interface, Data)
        elif 'RANGE' in Interface:
            Input, State, Interface, Data = self.ApplyRANGECommand(Input, State, Interface, Data)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Input, State, Interface, Data = self.ApplyAPPENDCommandFamily(Input, State, Interface, Data)
        Input, State, Interface, Data = self.ApplyLOOKUPCommand(Input, State, Interface, Data)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.ParamStorage[Input] = Data
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if State['visible'] == False:
            return ContinueFlag, Data
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if 'HR_BEFORE' in Interface:
            self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ValidLinkup = True
        if Data == None:
            ValidLinkup = False
        if '<GOTO' in Input and '>' in Input:
            ValidLinkup = False
        if '<LIST_' in Input and '>' in Input:
            ValidLinkup = False
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #TODO: Should be "if IsKey:" but due to need to extract displayed text from <> command before doing, otherwise applied link is invalid. Also shouldn't link if displayed text is "" still.
        #      - GATE: Want to build dedicated test/command processor before applying this.
        if ValidLinkup:
            ListToLink = PermuteWithOrder(State['key'] + [Input])
            if len(ListToLink) > 1:
                for ListIn in ListToLink[1:]:
                    LinkUpID = '_'.join(list(map(lambda Item: self.CleanLinkText(Item), ListIn)))
                    self.SeenLinkUps[LinkUpID] = True
                    self.Doc.stag('a', Format('id={}', LinkUpID))
            LinkUpID = '_'.join(list(map(lambda Item: self.CleanLinkText(Item), ListToLink[0])))
            self.SeenLinkUps[LinkUpID] = True
            with self.Tag('a', Format('id={}', LinkUpID)):
                self.AddText(Input, State, Interface, Data, IsKey=IsKey)
        else:
            self.AddText(Input, State, Interface, Data, IsKey=IsKey)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if 'HR_MIDDLE' in Interface:
            self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if State['mode'] == WebPageEnums.LookupTable:
            self.AddLookupTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
            return False, None
        elif State['mode'] == WebPageEnums.Table:
            self.AddTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
            return False, None
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if type(Data) in [str, int, float, bool]:
            _, NewData, NewInterface = self.GetInterfaceFromKey(str(Data))
            NewState = State.MixState(NewInterface, self)
            self.AddText(NewData, NewState, NewInterface, None)
            return False, None
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if 'HR_AFTER' in Interface:
            self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return ContinueFlag, Data

    def CleanText(self, Text):
        if type(Text) != str:
            Text = str(Text)
        for Key in self.TextReplaceMap:
            Text = Text.replace(Key, self.TextReplaceMap[Key])
        return Text

    def AddText(self, Input, State, Interface, Data, ForceTextTag=None, IsKey=False):
        if '<LIST_START>' in Input:
            if State.GlobalState['in_list_div'] == 0:
                self.Doc.stag('div', self.DCTS, style=' ;'.join(State['style']), klass=' '.join(State['class'] + ['list-div']))
            else:
                self.Doc.stag('div', self.DCTS, style=' ;'.join(State['style']), klass=' '.join(State['class']))
            self.Doc.stag('ul', self.DCTS, style=' ;'.join(State['style']), klass=' '.join(State['class']))
            State.GlobalState['in_list_div'] += 1
            return
        elif '<LIST_STOP>' in Input:
            self.Doc.stag('/ul', self.DCTS)
            State.GlobalState['in_list_div'] -= 1
            self.Doc.stag('/div', self.DCTS)
            return
        elif '<LIST_ITEM>' in Input:
            with self.Tag('li', style=' ;'.join(State['style']), klass=' '.join(State['class'])):
                self.AddText(Input.replace('<LIST_ITEM>', ''), State, Interface + ['LIST_ITEM'], Data)
            return

        Input = self.CleanText(Input)

        TextTag = None
        if ForceTextTag == None:
            TextTag = 'p'
        else:
            TextTag = ForceTextTag
        if '<GOTO' in Input and '>' in Input:
            HasRef = None
            if '<REF:' in Input and '>' in Input:
                RefPattern = re.compile('.*?<REF:(.*?)>.*')
                RefMatch = RefPattern.match(Input)
                if RefMatch != None:
                    HasRef = '|+REF+' + '+'.join(list(map(lambda Match: self.CleanLinkText(Match), RefMatch.group(1).split(':')))) + '+|'
                    Input = Input.replace(Format('<REF:{}>', RefMatch.group(1)), '')
            FontClass = []
            if IsKey:
                FontClass = [Format('font-class-{}', State['key_font'])]
            else:
                FontClass = [Format('font-class-{}', State['font'])]
            with self.Tag(TextTag, style=' ;'.join(State['style']), klass=' '.join(State['class'] + FontClass)):
                while '<GOTO' in Input and '>' in Input:
                    if 'display:inline' not in State['style'] and 'force-no-inline' not in State:
                        if 'LIST_ITEM' not in Interface:
                            State['style'] += ['display:inline']
                    elif 'display:inline' in State['style']:
                        del State['style'][State['style'].index('display:inline')]
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
                            with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'] + ['is-anchor-link'])):
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
                            with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'])):
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
                            with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'] + ['is-anchor-link'])):
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
                            with self.Tag('a', Format('onclick="opencollapsewithlinkaddress(this, true, {})"', LinkAddress), Format('href="{}"', LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'])):
                                self.Text(Input)
                            Input = ToReplace.join(Input.split(ToReplace)[1:])
                            HitAleady = True
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
                return 
        if Input.strip() != '' or ForceTextTag != None:
            FontClass = []
            if IsKey:
                FontClass = [Format('font-class-{}', State['key_font'])]
            else:
                FontClass = [Format('font-class-{}', State['font'])]
            if 'HTML' not in Interface:
                with self.Tag(TextTag, style=' ;'.join(State['style']), klass=' '.join(State['class'] + FontClass)):
                    self.Text(Input)
            else:
                self.Text(Input)
        if IsKey:
            if len(State['next.key_font']) > 0:
                State['key_font'] = State['next.key_font'][0]
                State['next.key_font'] = State['next.key_font'][1:]
        else:
            if len(State['next.font']) > 0:
                State['font'] = State['next.font'][0]
                State['next.font'] = State['next.font'][1:]


    def InitNewStateManager(self):
        State = WebPageStateManager()
        return State

    def CleanLinkText(self, OText):
        Text = OText.lower().replace("'", '')
        NewText = ''
        for Char in Text:
            if Char in '-_':
                NewText += Char
            elif Char.isalnum() or Char == ' ':
                NewText += Char
        NewText = NewText.replace(' ', '-')
        if len(NewText) > 0 and NewText[0].isnumeric():
            NewText = 'A' + NewText
        return NewText


    def PreProcessText(self, Text):
        for Key in self.JSCodeMap:
            Text = Text.replace(Key, self.JSCodeMap[Key])
        
        return Text
            
    def PostProcessPage(self, PageText):
        for Key in self.JSCodeMap:
            PageText = PageText.replace(self.JSCodeMap[Key], Key)

        DCTSLen = len(self.DCTS)
        NewPageText = ''
        CurrentMatch = ''
        PostMatch = ''
        CurrentClose = ''
        CloseSearch = '/>'
        CloseSearchLen = len(CloseSearch)
        for Char in PageText:
            if len(CurrentMatch) == DCTSLen and self.DCTS == CurrentMatch:
                if len(CurrentClose) == CloseSearchLen and CurrentClose == CloseSearch:
                    NewPageText += PostMatch + '>'
                    CurrentMatch = ''
                    PostMatch = ''
                    CurrentClose = ''
                elif Char == CloseSearch[len(CurrentClose)]:
                    CurrentClose += Char
                else:
                    PostMatch += Char
            elif Char == self.DCTS[len(CurrentMatch)]:
                CurrentMatch += Char
            else:
                NewPageText += Char
                CurrentMatch = ''


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
        return PageText
    

    def ConsumeMetaData(self, Key):
        self.MetaData = self.JSON[Key]
        del self.JSON[Key]

    def AddCSSFontDefinitions(self, OutFile):
        if "font" in self.MetaData:
            for NewFontKey in self.MetaData["font"]:
                NewFont = Format('.font-class-{}', NewFontKey)
                FontTable = self.MetaData['font'][NewFontKey]
                OutFile.write(Format('\n{} {{ ', NewFont))
                for Key in FontTable:
                    OutFile.write(Format('{}: {} !important;', Key, FontTable[Key]))
                OutFile.write('}\n')

    def GetInterfaceFromKey(self, OKey):
        if type(OKey) != str:
            return 'INF', OKey, []
        Rank = 'INF'
        DotPattern = re.compile('(\d+?)\.(.*)')
        DotMatch = DotPattern.match(OKey)
        if DotMatch != None:
            Rank = DotMatch.group(1)
            OKey = DotMatch.group(2)
        elif '#HIDDEN' in OKey:
            Rank = '.'
        OKey = OKey.split('#')
        Interface = []
        if len(OKey) > 1:
            Interface = OKey[1:]
        return Rank, OKey[0], Interface


def main(Args):
    if os.path.exists('HTML') == False:
        os.mkdir('HTML/')
    for Arg in Args:
        WP = WebPage(Arg)
        WP.Save(Format('HTML/{}.html', WP.MetaData['document']['title']))

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])