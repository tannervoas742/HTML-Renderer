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
    def __init__(self, Doc, Tag, Text, Line, Data, State):
        self.Doc = Doc
        self.Tag = Tag
        self.Text = Text
        self.Line = Line
        self.Data = Data
        self.State = State

        self.RenderToPage()

    def RenderToPage(self):

        def add_header(doc, header):
            with doc.tag('tr', klass=' '.join(self.State['class'])):
                for value in header:
                    doc.line('th', value)

        def add_row(doc, values, row_name=None):
            with doc.tag('tr', klass=' '.join(self.State['class'])):
                if row_name is not None:
                    doc.line('th', row_name)
                for value in values:
                    doc.line('td', value)
                    
        with self.Tag('table', klass='table table-bordered table-responsive table-striped ' + ' '.join(self.State['class'])):
            with self.Tag('thead', klass='thead-light ' + ' '.join(self.State['class'])):
                add_header(self.Doc, self.Data[0])
            with self.Tag('tbody', klass=' '.join(self.State['class'])):
                for row in self.Data[1:]:
                    add_row(self.Doc, row)




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

class Webpage:
    def __init__(self, SrcJSON):
        CleanTarget = SrcJSON.replace('\\', '/').replace('//', '/').replace('/', os.sep)
        self.JSON = ReadJSON(CleanTarget)
        self.ConsumeMetaData("_metadata")

        self.Doc, self.Tag, self.Text, self.Line = yattag.Doc(
            defaults = {
                'title': self.MetaData['document']['title']
            },
            errors = {}
        ).ttl()

        self.ParamStorage = {}

        self.LoadLevel(self.JSON)

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
        for OriginalKey in InputSorted:
            if type(OriginalKey) in [list, dict]:
                self.LoadLevel(OriginalKey, State)
                continue
            Rank, Key, Interface = self.GetInterfaceFromKey(OriginalKey)
            NewState = self.MixState(State, Interface)
            
            if type(Input) == dict:
                ContinueFlag, Input[OriginalKey] = self.LoadItem(Key, NewState, Interface, Input[OriginalKey])
                NewState['key'] = Key
                if ContinueFlag:
                    self.LoadLevel(Input[OriginalKey], NewState)
            elif type(Key) in [list, dict]:
                self.LoadLevel(Key, NewState)

    def LoadItem(self, Input, State, Interface, Data=None):
        ContinueFlag = True
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
            
            self.ParamStorage[Input] = Computed
            ContinueFlag = False
        elif 'RANGE' in Interface:
            Computed = []
            while len(Data) >= 2:
                Computed += [i for i in range(Data[0], Data[1] + 1)]
                Data = Data[2:]
            Computed.sort()
            self.ParamStorage[Input] = Computed
            ContinueFlag = False
        else:
            self.ParamStorage[Input] = Data
        if State['visible'] == False:
            return ContinueFlag, Data
        if 'HR_BEFORE' in Interface:
            self.Doc.stag('hr', klass=' '.join(State['class']))
        self.AddText(Input, State, Interface, Data)
        if 'HR_MIDDLE' in Interface:
            self.Doc.stag('hr', klass=' '.join(State['class']))
        if State['mode'] == WebpageEnums.LookupTable:
            self.AddLookupTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', klass=' '.join(State['class']))
            return False, None
        elif State['mode'] == WebpageEnums.Table:
            self.AddTable(Input, State, Interface, Data)
            if 'HR_AFTER' in Interface:
                self.Doc.stag('hr', klass=' '.join(State['class']))
            return False, None

        if 'CONCAT_LINES' in Interface:
            #Data = '\n'.join(Data)
            for Row in Data:
                self.AddText(Row, State, Interface, None)
            return False, None
        if 'HR_AFTER' in Interface:
            self.Doc.stag('hr', klass=' '.join(State['class']))
        return ContinueFlag, Data

    def AddText(self, Input, State, Interface, Data):
        if '<LIST_START>' in Input:
            self.Doc.stag('ul', klass=' '.join(State['class']))
            return
        elif '<LIST_STOP>' in Input:
            self.Doc.stag('/ul', klass=' '.join(State['class']))
            return
        elif '<LIST_ITEM>' in Input:
            with self.Tag('li', klass=' '.join(State['class'])):
                self.AddText(Input.replace('<LIST_ITEM>', ''), State, Interface, Data)
            return

        TextTag = None
        if State['text.size'] == 0:
            TextTag = 'p'
        else:
            TextTag = 'h{}'.format(State['text.size'])
        if '<GOTO' in Input:
            while '<GOTO' in Input:
                GotoPattern1 = re.compile('.*?<GOTO:(.*?):(.*?)\+(.*?)>.*')
                GotoMatch1 = GotoPattern1.match(Input)
                if GotoMatch1 != None:
                    Text = GotoMatch1.group(1)
                    File = GotoMatch1.group(2)
                    Location = GotoMatch1.group(3)
                    ToReplace = "<GOTO:{}:{}+{}>".format(Text, File, Location)
                    with self.Tag(TextTag, klass=' '.join(State['class'])):
                        self.Text(Input.split(ToReplace)[0])
                    with self.Tag('a', 'href=\"{0}.html#{1}\"'.format(File, Location.lower().replace(' ', '-')), klass=' '.join(State['class'])):
                        self.Text(Text)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    return self.AddText(Input, State, Interface, Data)
                GotoPattern2 = re.compile('.*?<GOTO:(.*?):(.*?)>.*')
                GotoMatch2 = GotoPattern2.match(Input)
                if GotoMatch2 != None:
                    Text = GotoMatch2.group(1)
                    File = GotoMatch2.group(2)
                    ToReplace = "<GOTO:{}:{}>".format(Text, File)
                    with self.Tag(TextTag, klass=' '.join(State['class'])):
                        self.Text(Input.split(ToReplace)[0])
                    with self.Tag('a', 'href=\"{0}.html\"'.format(File), klass=' '.join(State['class'])):
                        self.Text(Text)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    return self.AddText(Input, State, Interface, Data)
                GotoPattern3 = re.compile('.*?<GOTO:(.*?)\+(.*?)>.*')
                GotoMatch3 = GotoPattern3.match(Input)
                if GotoMatch3 != None:
                    File = GotoMatch3.group(1)
                    Text = File
                    Location = GotoMatch3.group(2)
                    ToReplace = "<GOTO:{}+{}>".format(Text, Location)
                    with self.Tag(TextTag, klass=' '.join(State['class'])):
                        self.Text(Input.split(ToReplace)[0])
                    with self.Tag('a', 'href=\"{0}.html#{1}\"'.format(File, Location.lower().replace(' ', '-')), klass=' '.join(State['class'])):
                        self.Text(Text)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    return self.AddText(Input, State, Interface, Data)
                GotoPattern4 = re.compile('.*?<GOTO:(.*?)>.*')
                GotoMatch4 = GotoPattern4.match(Input)
                if GotoMatch4 != None:
                    File = GotoMatch4.group(1)
                    Text = File
                    ToReplace = "<GOTO:{}>".format(Text)
                    with self.Tag(TextTag, klass=' '.join(State['class'])):
                        self.Text(Input.split(ToReplace)[0])
                    with self.Tag('a', 'href=\"{0}.html\"'.format(File), klass=' '.join(State['class'])):
                        self.Text(Text)
                    Input = ToReplace.join(Input.split(ToReplace)[1:])
                    return self.AddText(Input, State, Interface, Data)
            
        with self.Tag(TextTag, klass=' '.join(State['class'])):
            self.Text(Input)


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

        WebTable(self.Doc, self.Tag, self.Text, self.Line, Table, State)

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
        Table = [[''] * len(Data[0])] + Data
        WebTable(self.Doc, self.Tag, self.Text, self.Line, Table, State)


    def GetInitState(self):
        State = {}
        State['visible'] = True
        State['key'] = ''
        State['class'] = []
        State['mode'] = WebpageEnums.Text
        State['text.size'] = 0
        State['lookup_table.range'] = None
        return State
    
    def MixState(self, State, Interface):
        State = copy.deepcopy(State)
        if 'HIDDEN' in Interface:
            State['visible'] = False
        elif 'SHOWN' in Interface:
            State['visible'] = True
        HPattern = re.compile('H(\d+)')
        HMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: HPattern.match(Code), Interface))))))
        if len(HMatch) > 0:
            State['text.size'] = int(max(HMatch))
            if State['text.size'] > 0:
                State['text.size'] = 4 - State['text.size']

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
        return State
            

    def Save(self, OutHTML):
        CleanTarget = OutHTML.replace('\\', '/').replace('//', '/').replace('/', os.sep)
        OutFile = open(CleanTarget, 'w')
        OutFile.write(self.Doc.getvalue()) 
        OutFile.close()
    

    def ConsumeMetaData(self, Key):
        self.MetaData = self.JSON[Key]
        del self.JSON[Key]

    def GetInterfaceFromKey(self, OKey):
        Rank = 'INF'
        if '.' in OKey:
            Rank = OKey.split('.')[0]
            OKey = '.'.join(OKey.split('.')[1:])
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
        WP.Save(Arg.replace('Json', 'HTML').replace('json', 'html'))

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])