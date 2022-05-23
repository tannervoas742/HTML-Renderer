import yattag
import os
import io
import re
from WebPageModules.WebPage_IO import WebPage_IO
from WebPageModules.WebPage_Yattag import WebPage_Yattag
from WebPageModules.WebPage_Tables import WebPage_Tables
from WebPageModules.WebPage_Links import WebPage_Links
from WebPageModules.WebPage_Lists import WebPage_Lists
from WebPageModules.WebPage_Commands import WebPage_Commands
from WebPageModules.WebPage_TextProcessor import WebPage_TextProcessor
from WebPageTools.WebPageEnums import WebPageEnums
from WebPageTools.WebPageStateManager import WebPageStateManager
from WebStructures.WebTable import WebTable
from Utilities.TextProcessor import TextProcessor
from Utilities.Core import *
    
class WebPage(
    WebPage_IO,
    WebPage_Yattag,
    WebPage_Tables,
    WebPage_Links,
    WebPage_Lists,
    WebPage_Commands,
    WebPage_TextProcessor
    ):

    def __init__(self, SrcJSON):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        WebPage_IO.__init__(self)
        WebPage_Yattag.__init__(self)
        WebPage_Tables.__init__(self)
        WebPage_Links.__init__(self)
        WebPage_Lists.__init__(self)
        WebPage_Commands.__init__(self)
        WebPage_TextProcessor.__init__(self)

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

    def ConsumeMetaData(self, Key):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.MetaData = self.JSON[Key]
        del self.JSON[Key]

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

    def InitNewStateManager(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        State = WebPageStateManager()
        return State

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
        with self.Tag('body', self.Class(None, 'content html-renderer')):
            with self.Tag('div', self.Class(None, 'body-div')):
                with self.Tag('div', self.Class(None, 'header-spacer')):
                    self.Line('p', ' ')
        
        #       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                self.LoadLevel(self.JSON)
        
        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            self.AddJS()

    def AddFooter(self, State = None):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Tag('footer'):
            if State == None:
                State = self.InitNewStateManager()

        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            if 'authors' in self.MetaData['document']:
                if type(self.MetaData['document']['authors']) == list:
                    for Author in self.MetaData['document']['authors']:
                        self.AddText(Format('Author: {}', Author), State, [], None)
                else:
                    self.AddText(Format('Author: {}', self.MetaData['document']['authors']), State, [], None)
        
        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            if 'date' in self.MetaData['document']:
                self.AddText(Format('Last Modified: {}', self.MetaData['document']['date']), State, [], None)

    def AddJS(self, State = None):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if State == None:
            State = self.InitNewStateManager()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        documentReadFuncCollapsible = []
        documentReadFuncCollapsible += ['$(document).ready(function() {{']
        documentReadFuncCollapsible += ['    $(\'.collapsible-model{0}\').collapsible();']
        documentReadFuncCollapsible += ['}});']
        documentReadFuncCollapsible = '\n'.join(documentReadFuncCollapsible)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Tag('script'):
            for Model in range(self.CollapseModelCount):
                self.Text(self.PreProcessText(Format(documentReadFuncCollapsible, Model)))
                for Row in range(self.CollapseModelRows[Model]):
                    pass

    def AddCSSFontDefinitions(self, OutFile):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if "font" in self.MetaData:
            for NewFontKey in self.MetaData["font"]:
                NewFont = Format('.font-class-{}', NewFontKey)
                FontTable = self.MetaData['font'][NewFontKey]

        #       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                OutFile.write(Format('\n{} {{ ', NewFont))
                for Key in FontTable:
                    OutFile.write(Format('{}: {} !important;', Key, FontTable[Key]))
                OutFile.write('}\n')

    def Class(self, State, *args):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if State == None:
            State = {}
        if 'class' not in State:
            State['class'] = []

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return Format('class="{}"', ' '.join(State['class'] + list(args)))

    def Style(self, State, *args):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if State == None:
            State = {}
        if 'style' not in State:
            State['style'] = []

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return Format('style="{}"', ' ; '.join(State['style'] + list(args)))

    def LoadLevel(self, Input, State = None):
        if State == None:
            State = self.InitNewStateManager()
        if type(Input) not in [list, dict]:
            Rank, Input, Interface = self.GetCommandInterfaceFromKey(str(Input))
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
            InputSorted = list(sorted(Input.keys(), key=lambda Key: Format(FormatString, self.GetCommandInterfaceFromKey(Key)[0])))
        LastItemWasCollapse = False
        CollapseModelCount = self.CollapseModelCount
        CollapseRowCount = 0
        for OriginalKey in InputSorted:
            if type(OriginalKey) in [list, dict]:
                self.LoadLevel(OriginalKey, State)
                continue
            Rank, Key, Interface = self.GetCommandInterfaceFromKey(OriginalKey)   
            NewState = State.MixState(Interface, self)                
            
            if type(Input) == dict:
                if 'COLLAPSE' in Interface:
                    if LastItemWasCollapse == False:
                        CollapseModelCount = self.CollapseModelCount
                        self.CollapseModelCount += 1
                        self.Doc.stag('br', self.Style(NewState), self.Class(NewState, 'pre-collapsible-br'))
                        self.Doc.stag('ul', self.DCTS, Format('id="collapsible-model{}"', CollapseModelCount), self.Style(NewState), self.Class(NewState, Format('collapsible collapsible-model{}', CollapseModelCount)))
                        self.Doc.stag('li', self.DCTS, Format('id="list-item-mode{}-row{}"', CollapseModelCount, CollapseRowCount), self.Style(NewState), self.Class(NewState, 'list-collapsible'))
                    else:
                        self.Doc.stag('/li', self.DCTS)
                        self.Doc.stag('li', self.DCTS, Format('id="list-item-mode{}-row{}"', CollapseModelCount, CollapseRowCount), self.Style(NewState), self.Class(NewState, 'list-collapsible'))
                    self.Doc.stag('div', self.DCTS, Format('id="collapsible-header{}-row{}"', CollapseModelCount, CollapseRowCount), self.Style(NewState), self.Class(NewState, Format('collapsible-header normal-collapsible closed-header collapsible-header{}-row{}', CollapseModelCount, CollapseRowCount)))
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
                    self.Doc.stag('div', self.DCTS, Format('id="collapsible-body{}-row{}"', CollapseModelCount, CollapseRowCount), self.Style(NewState), self.Class(NewState, Format('collapsible-body collapsible-body{}-row{}', CollapseModelCount, CollapseRowCount)))
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
            self.Doc.stag('hr', self.Style(State), self.Class(State))
        
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
        #      - GATE: Want to build dedicated text/command processor before applying this.
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
            self.Doc.stag('hr', self.Style(State), self.Class(State))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if State['mode'] == WebPageEnums.LookupTable:
            self.AddLookupTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', self.Style(State), self.Class(State))
            return False, None
        elif State['mode'] == WebPageEnums.Table:
            self.AddTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', self.Style(State), self.Class(State))
            return False, None
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if type(Data) in [str, int, float, bool]:
            _, NewData, NewInterface = self.GetCommandInterfaceFromKey(str(Data))
            NewState = State.MixState(NewInterface, self)
            self.AddText(NewData, NewState, NewInterface, None)
            return False, None
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if 'HR_AFTER' in Interface:
            self.Doc.stag('hr', self.Style(State), self.Class(State))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return ContinueFlag, Data

    def AddText(self, Input, State, Interface, Data, ForceTextTag=None, IsKey=False):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if self.HandleLists(Input, State, Interface, Data):
            return
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Input = self.CleanText(Input)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        TextTag = None
        if ForceTextTag == None:
            TextTag = 'p'
        else:
            TextTag = ForceTextTag

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if self.HandleLinks(Input, State, Interface, Data, TextTag=TextTag, ForceTextTag=ForceTextTag, IsKey=IsKey):
            return

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if Input.strip() != '' or ForceTextTag != None:
            FontClass = ''
            if IsKey:
                FontClass = Format('font-class-{}', State['key_font'])
            else:
                FontClass = Format('font-class-{}', State['font'])
            if 'HTML' not in Interface:
                with self.Tag(TextTag, self.Style(State), self.Class(State, FontClass)):
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

def main(Args):
    if os.path.exists('HTML') == False:
        os.mkdir('HTML/')
    for Arg in Args:
        WP = WebPage(Arg)
        WP.Save(Format('HTML/{}.html', WP.MetaData['document']['title']))

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])