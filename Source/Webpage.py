import yattag
import json
import os
import io
import copy
import re

class WebpageEnums:
    # Text Specifiers
    class Text:
        pass
    class LookupTable:
        pass
    class Table:
        pass

class WebTable:
    def __init__(self, Doc, Tag, Text, Line, Data, State, Interface, WebpageObject):
        self.Doc = Doc
        self.Tag = Tag
        self.Text = Text
        self.Line = Line
        self.Data = Data
        self.State = State
        self.Interface = Interface
        self.WebpageObject = WebpageObject

        self.RenderToPage()

    def RenderToPage(self):
        Widths = [None for i in self.Data[0]]
        ColumnWidthPattern = re.compile('COLUMN_WIDTH\((.*?)\)')
        ColumnWidthMatch = list(filter(lambda Result: Result != None, list(map(lambda Interface: ColumnWidthPattern.match(Interface), self.Interface))))
        if len(ColumnWidthMatch) > 0:
            NewWidths = ColumnWidthMatch[0].group(1).replace(' ', '').split(',')
            for IDX in range(len(NewWidths)):
                if IDX < len(Widths):
                    if NewWidths[IDX].lower() != 'none':
                        Widths[IDX] = NewWidths[IDX]
        def add_header(doc, header):
            with doc.tag('tr', klass=' '.join(self.State['class'])):
                ColumnIDX = 0
                for value in header:
                    NewState = copy.deepcopy(self.State)
                    NewState['force-no-inline'] = True
                    NewState['class'] += ['table-column-{}'.format(ColumnIDX)]
                    if Widths[ColumnIDX] != None:
                        NewState['style'] += ['width: {}'.format(Widths[ColumnIDX])]
                        NewState['style'] += ['table-layout: fixed']
                    self.WebpageObject.AddText(value, NewState, self.Interface, None, ForceTextTag='th')
                    ColumnIDX += 1
                    #doc.line('th', value)

        def add_row(doc, values, row_name=None):
            with doc.tag('tr', klass=' '.join(self.State['class'])):
                if row_name is not None:
                    NewState = copy.deepcopy(self.State)
                    NewState['force-no-inline'] = True
                    self.WebpageObject.AddText(row_name, NewState, self.Interface, None, ForceTextTag='th')
                    #doc.line('th', row_name)
                ColumnIDX = 0
                for value in values:
                    NewState = copy.deepcopy(self.State)
                    NewState['force-no-inline'] = True
                    NewState['class'] += ['table-column-{}'.format(ColumnIDX)]
                    if Widths[ColumnIDX] != None:
                        NewState['style'] += ['width: {}'.format(Widths[ColumnIDX])]
                        NewState['style'] += ['table-layout: fixed']
                    self.WebpageObject.AddText(value, NewState, self.Interface, None, ForceTextTag='td')
                    #doc.line('td', value)
                    ColumnIDX += 1
                    
        with self.Tag('table', klass='table renderer-table-bordered' + ' '.join(self.State['class'])):
            with self.Tag('thead', klass='thead-dark ' + ' '.join(self.State['class'])):
                add_header(self.Doc, self.Data[0])
            with self.Tag('tbody', klass=' '.join(self.State['class'])):
                for row in self.Data[1:]:
                    add_row(self.Doc, row)

def PermuteWithOrder(List):
    if len(List) == 1:
        return [[List[0]]]
    ChildList = PermuteWithOrder(List[1:])
    return list(map(lambda Item: [List[0]] + Item, copy.deepcopy(ChildList))) + ChildList

def FlushPrintUTF8(*args, **kw):
    if 'end' not in kw:
        kw['end'] = '\n'
    if 'sep' not in kw:
        kw['sep'] = ' '
    text = kw['sep'].join(list(map(lambda x: str(x), args))) + kw['end']
    sys.stdout.buffer.write((str(text)).encode(sys.stdout.encoding, 'backslashreplace'))
    sys.stdout.flush()

def ReadJSON(path):
    MakePath = path.split('/')
    MakeIndex = 0
    while MakeIndex + 1 < len(MakePath):
        if not os.path.exists('/'.join(MakePath[:MakeIndex+1])):
            os.mkdir('/'.join(MakePath[:MakeIndex+1]))
        MakeIndex += 1
    try:
        with io.open(path, mode='r', encoding='utf-8') as json_file:
            structure = json.load(json_file)
        return structure
    except BaseException:
        FlushPrintUTF8("Failed to read: {}".format(path))
        return {}

def WriteJSON(path, structure, beautify=True):
    MakePath = path.split('/')
    MakeIndex = 0
    while MakeIndex + 1 < len(MakePath):
        if not os.path.exists('/'.join(MakePath[:MakeIndex+1])):
            os.mkdir('/'.join(MakePath[:MakeIndex+1]))
        MakeIndex += 1
    with io.open(path, mode='w', encoding='utf-8') as json_file:
        json.dump(structure, json_file, indent=2 if beautify else None, sort_keys=beautify, ensure_ascii=False)

def DeepSize(Item):
    Size = 0
    if type(Item) == list:
        for Sub in Item:
            Size += DeepSize(Sub)
    elif type(Item) == dict:
        for Key in Item:
            Size += DeepSize(Item[Key])
    else:
        return 1
    return Size
    
class Webpage:
    def __init__(self, SrcJSON):
        CleanTarget = SrcJSON.replace('\\', '/').replace('//', '/').replace('/', os.sep)
        self.JSON = ReadJSON(CleanTarget)
        self.ConsumeMetaData("_metadata")

        self.SeenLinkUps = {}
        self.SeenLinkDowns = {}
        self.PostProcessRefList = {}

        self.JSCodeMap = {
            '<': '|~lt~|',
            '>': '|~gt~|',
            '&': '|~and~|',
            '—': '|~em~dash~|'
        }

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

        self.Doc, self.Tag, self.Text, self.Line = yattag.Doc(
            defaults = {
                'title': self.MetaData['document']['title']
            },
            errors = {}
        ).ttl()

        self.ParamStorage = {}
        self.CollapseModelCount = 0
        self.CollapseModelRows = {}

        with self.Tag('html', 'id="top-html"'):

            with self.Tag('head'):
                self.Doc.stag('meta', 'charset="UTF-8"')
                self.Doc.stag('link', 'href="../CSS/bootstrap.min.css"', 'rel="stylesheet"')
                self.Doc.stag('link', 'rel="stylesheet"', 'href="../CSS/materialize.css"')
                self.Doc.stag('link', 'rel="stylesheet"', 'href="../CSS/mystyle.css"')
                #self.Doc.stag('link', 'rel="stylesheet"', 'href="../CSS/random.css"')
                

                with self.Tag('script', 'type="text/javascript"', 'src="../JS/jquery-1.2.6.js"'):
                    pass
                with self.Tag('script', 'type="text/javascript"', 'src="../JS/bootstrap.min.js"'):
                    pass
                with self.Tag('script', 'type="text/javascript"', 'src="../JS/materialize.js"'):
                    pass
                with self.Tag('script', 'type="text/javascript"', 'src="../JS/myfunctionality.js"'):
                    pass

            self.ItemsToProcess = DeepSize(self.JSON)
            
            with self.Tag('header'):
                with self.Tag('nav', id='sticky-header-nav'):
                    with self.Tag('div'):
                        with self.Tag('ul'):
                            with self.Tag('li'):
                                self.Line('a', 'TBD')
            with self.Tag('body', klass='content html-renderer'):
                with self.Tag('div', klass='body-div'):
                    with self.Tag('div', klass='header-spacer'):
                        self.Line('p', ' ')
                    self.LoadLevel(self.JSON)
                self.AddJS()
            with self.Tag('footer'):
                self.AddFooter()

    def AddFooter(self, State = None):
        if State == None:
            State = self.GetInitState()
        if 'authors' in self.MetaData['document']:
            if type(self.MetaData['document']['authors']) == list:
                for Author in self.MetaData['document']['authors']:
                    self.Line('p', 'Author: {}'.format(Author))
            else:
                self.Line('p', 'Author: {}'.format(self.MetaData['document']['authors']))
        if 'date' in self.MetaData['document']:
            self.Line('p', 'Last Modified: {}'.format(self.MetaData['document']['date']))

    def AddJS(self, State = None):
        if State == None:
            State = self.GetInitState()

        documentReadFuncCollapsible = []
        documentReadFuncCollapsible += ['$(document).ready(function() {{']
        documentReadFuncCollapsible += ['    $(\'.collapsible-model{0}\').collapsible();']
        documentReadFuncCollapsible += ['}});']
        documentReadFuncCollapsible = '\n'.join(documentReadFuncCollapsible)

        with self.Tag('script'):
            for Model in range(self.CollapseModelCount):
                self.Text(self.PreProcessText(documentReadFuncCollapsible.format(Model)))
                for Row in range(self.CollapseModelRows[Model]):
                    pass

    def LoadLevel(self, Input, State = None):
        if State == None:
            State = self.GetInitState()
        if type(Input) not in [list, dict]:
            Rank, Input, Interface = self.GetInterfaceFromKey(str(Input))
            NewState = self.MixState(State, Interface)
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
            InputSorted = list(sorted(Input.keys(), key=lambda Key: FormatString.format(self.GetInterfaceFromKey(Key)[0])))
        LastItemWasCollapse = False
        CollapseModelCount = self.CollapseModelCount
        CollapseRowCount = 0
        for OriginalKey in InputSorted:
            if type(OriginalKey) in [list, dict]:
                self.LoadLevel(OriginalKey, State)
                continue
            Rank, Key, Interface = self.GetInterfaceFromKey(OriginalKey)   
            NewState = self.MixState(State, Interface)                
            
            if type(Input) == dict:
                if 'COLLAPSE' in Interface:
                    if LastItemWasCollapse == False:
                        CollapseModelCount = self.CollapseModelCount
                        self.CollapseModelCount += 1
                        self.Doc.stag('br', style='; '.join(NewState['style']), klass=' '.join(NewState['class'] + ['pre-collapsible-br']))
                        self.Doc.stag('ul', 'id="collapsible-model{}"'.format(CollapseModelCount), '_DONT_CLOSE_THIS_STAG_', style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + ['collapsible collapsible-model{}'.format(CollapseModelCount)]))
                        self.Doc.stag('li', 'id="list-item-mode{}-row{}"'.format(CollapseModelCount, CollapseRowCount), '_DONT_CLOSE_THIS_STAG_', style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + ['list-collapsible']))
                    else:
                        self.Doc.stag('/li', '_DONT_CLOSE_THIS_STAG_')
                        self.Doc.stag('li', 'id="list-item-mode{}-row{}"'.format(CollapseModelCount, CollapseRowCount), '_DONT_CLOSE_THIS_STAG_', style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + ['list-collapsible']))
                    self.Doc.stag('div', 'id="collapsible-header{}-row{}"'.format(CollapseModelCount, CollapseRowCount), '_DONT_CLOSE_THIS_STAG_', style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + ['collapsible-header normal-collapsible closed-header collapsible-header{}-row{}'.format(CollapseModelCount, CollapseRowCount)]))
                elif LastItemWasCollapse:
                    self.CollapseModelRows[CollapseModelCount] = CollapseRowCount
                    CollapseRowCount += 0
                    LastItemWasCollapse = False
                    self.Doc.stag('/li', '_DONT_CLOSE_THIS_STAG_')
                    self.Doc.stag('/ul', '_DONT_CLOSE_THIS_STAG_')
                    
                ContinueFlag, Input[OriginalKey] = self.LoadItem(Key, NewState, Interface, Input[OriginalKey])
                if 'COLLAPSE' in Interface:
                    self.Doc.stag('/div', '_DONT_CLOSE_THIS_STAG_')
                NewState['key'] += [Key]
                if 'COLLAPSE' in Interface:
                    self.Doc.stag('div', 'id="collapsible-body{}-row{}"'.format(CollapseModelCount, CollapseRowCount), '_DONT_CLOSE_THIS_STAG_', style=' ;'.join(NewState['style']), klass=' '.join(NewState['class'] + ['collapsible-body collapsible-body{}-row{}'.format(CollapseModelCount, CollapseRowCount)]))
                if ContinueFlag:
                    self.LoadLevel(Input[OriginalKey], NewState)
                if 'COLLAPSE' in Interface:
                    self.Doc.stag('/div', '_DONT_CLOSE_THIS_STAG_')
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
            self.Doc.stag('/li', '_DONT_CLOSE_THIS_STAG_')
            self.Doc.stag('/ul', '_DONT_CLOSE_THIS_STAG_')

    def LoadItem(self, Input, State, Interface, Data=None):
        ContinueFlag = True
        if len(State['callback']) > 0:
            for Callback in State['callback']:
                Data = Callback(self, State, Interface, Data)
        if 'INC' in Interface:
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
            BeforeReg = re.compile("APPEND_BEFORE\((.*?)\)")
            BeforeMatch = list(filter(lambda Res: Res != None, list(map(lambda Com: BeforeReg.match(Com), Interface))))
            for Match in BeforeMatch:
                Pattern = Match.group(1)
                Computed = list(map(lambda Val: Pattern + str(Val), Computed))
            AfterReg = re.compile("APPEND_AFTER\((.*?)\)")
            AfterMatch = list(filter(lambda Res: Res != None, list(map(lambda Com: AfterReg.match(Com), Interface))))
            for Match in AfterMatch:
                Pattern = Match.group(1)
                Computed = list(map(lambda Val: str(Val) + Pattern, Computed))
            LookupReg = re.compile("LOOKUP\((.*?)\)")
            LookupMatch = list(filter(lambda Res: Res != None, list(map(lambda Com: LookupReg.match(Com), Interface))))
            for Match in LookupMatch:
                Key = Match.group(1)
                Computed = list(map(lambda Val: "<ERROR : LOOKUP_NOT_FOUND : {} : {}>".format(Key, Val) if Key not in self.ParamStorage or Val not in self.ParamStorage[Key] else self.ParamStorage[Key][Val], list(map(lambda Com: str(Com), Computed))))
            self.ParamStorage[Input] = Computed
            ContinueFlag = False
        elif 'RANGE' in Interface:
            Computed = []
            while len(Data) >= 2:
                Computed += [i for i in range(Data[0], Data[1] + 1)]
                Data = Data[2:]
            Computed.sort()
            BeforeReg = re.compile("APPEND_BEFORE\((.*?)\)")
            BeforeMatch = list(filter(lambda Res: Res != None, list(map(lambda Com: BeforeReg.match(Com), Interface))))
            for Match in BeforeMatch:
                Pattern = Match.group(1)
                Computed = list(map(lambda Val: Pattern + str(Val), Computed))
            AfterReg = re.compile("APPEND_AFTER\((.*?)\)")
            AfterMatch = list(filter(lambda Res: Res != None, list(map(lambda Com: AfterReg.match(Com), Interface))))
            for Match in AfterMatch:
                Pattern = Match.group(1)
                Computed = list(map(lambda Val: str(Val) + Pattern, Computed))
            LookupReg = re.compile("LOOKUP\((.*?)\)")
            LookupMatch = list(filter(lambda Res: Res != None, list(map(lambda Com: LookupReg.match(Com), Interface))))
            for Match in LookupMatch:
                Key = Match.group(1)
                Computed = list(map(lambda Val: "<ERROR:LOOKUP_NOT_FOUND:{}:{}".format(Key, Val) if Key not in self.ParamStorage or Val not in self.ParamStorage[Key] else self.ParamStorage[Key][Val], list(map(lambda Com: str(Com), Computed))))
            self.ParamStorage[Input] = Computed
            ContinueFlag = False
        else:
            self.ParamStorage[Input] = Data
        if State['visible'] == False:
            return ContinueFlag, Data
        if 'HR_BEFORE' in Interface:
            self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
        ValidLinkup = True
        if Data == None:
            ValidLinkup = False
        if '<GOTO' in Input and '>' in Input:
            ValidLinkup = False
        if '<LIST_' in Input and '>' in Input:
            ValidLinkup = False
        if ValidLinkup:
            ListToLink = PermuteWithOrder(State['key'] + [Input])
            if len(ListToLink) > 1:
                for ListIn in ListToLink[1:]:
                    LinkUpID = '_'.join(list(map(lambda Item: self.CleanLinkText(Item), ListIn)))
                    self.SeenLinkUps[LinkUpID] = True
                    self.Doc.stag('a', 'id={}'.format(LinkUpID))
            LinkUpID = '_'.join(list(map(lambda Item: self.CleanLinkText(Item), ListToLink[0])))
            self.SeenLinkUps[LinkUpID] = True
            with self.Tag('a', 'id={}'.format(LinkUpID)):
                self.AddText(Input, State, Interface, Data)
        else:
            self.AddText(Input, State, Interface, Data)
        if 'HR_MIDDLE' in Interface:
            self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
        if State['mode'] == WebpageEnums.LookupTable:
            self.AddLookupTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
            return False, None
        elif State['mode'] == WebpageEnums.Table:
            self.AddTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
            return False, None
        if type(Data) in [str, int, float, bool]:
            _, Data, Interface = self.GetInterfaceFromKey(str(Data))
            self.AddText(Data, State, Interface, None)
            return False, None
        if 'HR_AFTER' in Interface:
            self.Doc.stag('hr', style=' ;'.join(State['style']), klass=' '.join(State['class']))
        return ContinueFlag, Data

    def CleanText(self, Text):
        if type(Text) != str:
            Text = str(Text)
        for Key in self.TextReplaceMap:
            Text = Text.replace(Key, self.TextReplaceMap[Key])
        return Text

    def AddText(self, Input, State, Interface, Data, ForceTextTag=None):
        if '<LIST_START>' in Input:
            if self.in_list_div == 0:
                self.Doc.stag('div', '_DONT_CLOSE_THIS_STAG_', style=' ;'.join(State['style']), klass=' '.join(State['class'] + ['list-div']))
            self.Doc.stag('ul', '_DONT_CLOSE_THIS_STAG_', style=' ;'.join(State['style']), klass=' '.join(State['class']))
            self.in_list_div += 1
            return
        elif '<LIST_STOP>' in Input:
            self.Doc.stag('/ul', '_DONT_CLOSE_THIS_STAG_')
            self.in_list_div -= 1
            if self.in_list_div == 0:
                self.Doc.stag('/div', '_DONT_CLOSE_THIS_STAG_')
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
                    Input = Input.replace('<REF:{}>'.format(RefMatch.group(1)), '')
            with self.Tag(TextTag, style=' ;'.join(State['style']), klass=' '.join(State['class'])):
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
                            ToReplace = "<GOTO:{}:{}+{}>".format(Text, File, Location)
                            self.Text(Input.split(ToReplace)[0])
                            LinkAddress = '\'{0}.html#{1}\''.format(File, self.CleanLinkText(Location))
                            if HasRef != None:
                                LinkAddress = LinkAddress[1:-1] + HasRef
                                self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                                LinkAddress = "'{}'".format(LinkAddress)
                            if LinkAddress not in self.SeenLinkDowns:
                                self.SeenLinkDowns[LinkAddress] = 0
                            self.SeenLinkDowns[LinkAddress] += 1    
                            with self.Tag('a', 'onclick="opencollapsewithlinkaddress(this, true, {})"'.format(LinkAddress), 'onload="opencollapsewithlinkaddress(this, false, {})"'.format(LinkAddress), 'href="{}"'.format(LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'] + ['is-anchor-link'])):
                                self.Text(Text)
                            Input = ToReplace.join(Input.split(ToReplace)[1:])
                            HitAleady = True
                    if not HitAleady:
                        GotoPattern2 = re.compile('.*?<GOTO:(.*?):(.*?)>.*')
                        GotoMatch2 = GotoPattern2.match(Input)
                        if GotoMatch2 != None:
                            Text = GotoMatch2.group(1)
                            File = GotoMatch2.group(2)
                            ToReplace = "<GOTO:{}:{}>".format(Text, File)
                            self.Text(Input.split(ToReplace)[0])
                            LinkAddress = '\"{0}.html\"'.format(File)
                            if HasRef != None:
                                LinkAddress = LinkAddress[1:-1] + HasRef
                                self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                                LinkAddress = "'{}'".format(LinkAddress)
                            if LinkAddress not in self.SeenLinkDowns:
                                self.SeenLinkDowns[LinkAddress] = 0
                            self.SeenLinkDowns[LinkAddress] += 1  
                            with self.Tag('a', 'onclick="opencollapsewithlinkaddress(this, true, {})"'.format(LinkAddress), 'onload="opencollapsewithlinkaddress(this, false, {})"'.format(LinkAddress), 'href="{}"'.format(LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'])):
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
                            ToReplace = "<GOTO:{}+{}>".format(Text, Location)
                            self.Text(Input.split(ToReplace)[0])
                            LinkAddress = '\"{0}.html#{1}\"'.format(File, self.CleanLinkText(Location))
                            if HasRef != None:
                                LinkAddress = LinkAddress[1:-1] + HasRef
                                self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                                LinkAddress = "'{}'".format(LinkAddress)
                            if LinkAddress not in self.SeenLinkDowns:
                                self.SeenLinkDowns[LinkAddress] = 0
                            self.SeenLinkDowns[LinkAddress] += 1  
                            with self.Tag('a', 'onclick="opencollapsewithlinkaddress(this, true, {})"'.format(LinkAddress), 'onload="opencollapsewithlinkaddress(this, false, {})"'.format(LinkAddress), 'href="{}"'.format(LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'] + ['is-anchor-link'])):
                                self.Text(Text)
                            Input = ToReplace.join(Input.split(ToReplace)[1:])
                            HitAleady = True
                    if not HitAleady:
                        GotoPattern4 = re.compile('.*?<GOTO:(.*?)>.*')
                        GotoMatch4 = GotoPattern4.match(Input)
                        if GotoMatch4 != None:
                            File = GotoMatch4.group(1)
                            Text = File
                            ToReplace = "<GOTO:{}>".format(Text)
                            self.Text(Input.split(ToReplace)[0])
                            LinkAddress = '\"{0}.html\"'.format(File)
                            if HasRef != None:
                                LinkAddress = LinkAddress[1:-1] + HasRef
                                self.PostProcessRefList[LinkAddress.split('#')[-1]] = Text 
                                LinkAddress = "'{}'".format(LinkAddress)
                            if LinkAddress not in self.SeenLinkDowns:
                                self.SeenLinkDowns[LinkAddress] = 0
                            self.SeenLinkDowns[LinkAddress] += 1  
                            with self.Tag('a', 'onclick="opencollapsewithlinkaddress(this, true, {})"'.format(LinkAddress), 'onload="opencollapsewithlinkaddress(this, false, {})"'.format(LinkAddress), 'href="{}"'.format(LinkAddress.replace('\'', '')), style=' ;'.join(State['style']), klass=' '.join(State['class'])):
                                self.Text(Text)
                            Input = ToReplace.join(Input.split(ToReplace)[1:])
                            HitAleady = True
                if Input.strip() != '':
                    self.Text(Input)
                return 
        if Input.strip() != '':   
            with self.Tag(TextTag, style=' ;'.join(State['style']), klass=' '.join(State['class'])):
                self.Text(Input)

    def CleanTable(self, Table):
        for IndexY in range(len(Table)):
            for IndexX in range(len(Table[IndexY])):
                Table[IndexY][IndexX] = str(Table[IndexY][IndexX])
        return Table


    def AddLookupTable(self, Input, State, Interface, Data):
        Table = [Data]
        for i in range(State['lookup_table.range'][0] - 1, State['lookup_table.range'][1]):
            Row = []
            for Key in Data:
                if i >= len(self.ParamStorage[Key]):
                    Row += [self.ParamStorage[Key][-1]]
                else:    
                    Row += [self.ParamStorage[Key][i]]
            Table += [Row]

        Table = self.CleanTable(Table)

        WebTable(self.Doc, self.Tag, self.Text, self.Line, Table, State, Interface, self)

    def AddTable(self, Input, State, Interface, Data):
        if type(Data) == dict:
            NewData = []
            Ranks = list(map(lambda Ret: self.GetInterfaceFromKey(Ret)[0:2], Data.keys()))
            FormatString = 2
            Count = len(Ranks)
            while Count >= 10:
                FormatString += 1
                Count /= 10
            FormatString = '{:0>' + str(FormatString) + '}'
            Ranks = list(map(lambda Ret: '.'.join(Ret) if Ret[0].isnumeric() == False else '.'.join([FormatString.format(Ret[0]), Ret[1]]), Ranks))
            for Key in list(sorted(list(Data.keys()), key=lambda x: str(x))):
                NewData += [['.'.join(Key.split('.')[1:]), Data[Key]]]
            Data = NewData
        Table = Data
        Table = self.CleanTable(Table)
        WebTable(self.Doc, self.Tag, self.Text, self.Line, Table, State, Interface, self)


    def GetInitState(self):
        self.in_list_div = 0
        State = {}
        State['visible'] = True
        State['key'] = []
        State['class'] = []
        State['style'] = []
        State['mode'] = WebpageEnums.Text
        State['lookup_table.range'] = None
        State['callback'] = []
        return State
    
    def MixState(self, State, Interface):
        State = copy.deepcopy(State)
        if 'HIDDEN' in Interface:
            State['visible'] = False
        elif 'SHOWN' in Interface:
            State['visible'] = True

        LTPattern = re.compile('LOOKUP_TABLE\((\d+)\,(\d+)\)')
        LTMatch = list(map(lambda Reg: [int(Reg.group(1)), int(Reg.group(2))], list(filter(lambda Result: Result != None, list(map(lambda Code: LTPattern.match(Code), Interface))))))                
        if len(LTMatch) > 0:
            State['mode'] = WebpageEnums.LookupTable
            State['lookup_table.range'] = LTMatch[0]

        TPattern = re.compile('TABLE')
        TMatch = list(map(lambda Reg: Reg.group(0), list(filter(lambda Result: Result != None, list(map(lambda Code: TPattern.match(Code), Interface))))))                
        if len(TMatch) > 0:
            State['mode'] = WebpageEnums.Table

        ClassPattern = re.compile('CLASS\((.*)\)')
        ClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: ClassPattern.match(Code), Interface))))))                
        if len(ClassMatch) > 0:
            State['class'] = []
            for Group in ClassMatch:
                State['class'] += Group.lower().split()

        AddClassPattern = re.compile('ADD_CLASS\((.*)\)')
        AddClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: AddClassPattern.match(Code), Interface))))))                
        if len(AddClassMatch) > 0:
            for Group in AddClassMatch:
                State['class'] += Group.lower().split()

        RemoveClassPattern = re.compile('REMOVE_CLASS\((.*)\)')
        RemoveClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: RemoveClassPattern.match(Code), Interface))))))                
        if len(RemoveClassMatch) > 0:
            for Group in RemoveClassMatch:
                for Tag in Group.lower().split():
                    if Tag in State['class']:
                        del State['class'][State['class'].index(Tag)]

        CallPattern = re.compile('CALL\((.*)\)')
        CallMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: CallPattern.match(Code), Interface))))))                
        if len(CallMatch) > 0:
            State['callback'] = []
            for Group in CallMatch:
                State['callback'] += list(map(lambda Item: '_CALLBACK_' + Item, Group.split()))
            
            Compiled = []
            for Func in State['callback']:
                if Func.replace('_CALLBACK_', '') in self.ParamStorage:
                    FuncText = self.ParamStorage[Func.replace('_CALLBACK_', '')]
                    FuncText = 'def {}(self, STATE, INTERFACE, ARG):\n    '.format(Func) + '\n    '.join(FuncText)
                    exec(FuncText)
                    Compiled += [eval(Func)]
            State['callback'] = Compiled
        else:
            State['callback'] = []
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

        _DONT_CLOSE_THIS_STAG_re = re.compile('.*?_DONT_CLOSE_THIS_STAG_(.*?)/>.*')
        _DONT_CLOSE_THIS_STAG_ma = _DONT_CLOSE_THIS_STAG_re.match(PageText)
        while _DONT_CLOSE_THIS_STAG_ma != None:
            PageText = PageText.replace('_DONT_CLOSE_THIS_STAG_{}/>'.format(_DONT_CLOSE_THIS_STAG_ma.group(1)), '{}>'.format(_DONT_CLOSE_THIS_STAG_ma.group(1)))
            _DONT_CLOSE_THIS_STAG_ma = _DONT_CLOSE_THIS_STAG_re.match(PageText)


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

    def Save(self, OutHTML):
        CleanTarget = OutHTML.replace('\\', '/').replace('//', '/').replace('/', os.sep)
        with io.open(CleanTarget, mode='w', encoding='utf-8') as OutFile:
            PageText = self.Doc.getvalue()
            PageText = self.PostProcessPage(PageText)
            OutFile.write(PageText) 
    

    def ConsumeMetaData(self, Key):
        self.MetaData = self.JSON[Key]
        del self.JSON[Key]

    def GetInterfaceFromKey(self, OKey):
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
        WP = Webpage(Arg)
        WP.Save('HTML/{}.html'.format(WP.MetaData['document']['title']))
        #SortedByCount = list(sorted(WP.SeenLinkUps.keys(), key=lambda Key: WP.SeenLinkUps[Key], reverse=True))
        #for Key in SortedByCount:
        #    FlushPrintUTF8(Key, WP.SeenLinkUps[Key])

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])