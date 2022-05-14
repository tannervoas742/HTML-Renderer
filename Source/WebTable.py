import yattag
import re
import copy

class WebTable:
    def __init__(self, Data, State, Interface, WebpageObject):
        self.Doc = WebpageObject.Doc
        self.Tag = WebpageObject.Tag
        self.Text = WebpageObject.Text
        self.Line = WebpageObject.Line
        self.Data = Data
        self.State = State
        self.Interface = Interface
        self.WebpageObject = WebpageObject

        self.RenderToPage()

    def RenderToPage(self):
        self.Widths = [None for i in self.Data[0]]
        ColumnWidthPattern = re.compile('COLUMN_WIDTH\((.*?)\)')
        ColumnWidthMatch = list(filter(lambda Result: Result != None, list(map(lambda Interface: ColumnWidthPattern.match(Interface), self.Interface))))
        if len(ColumnWidthMatch) > 0:
            NewWidths = ColumnWidthMatch[0].group(1).replace(' ', '').split(',')
            for IDX in range(len(NewWidths)):
                if IDX < len(Widths):
                    if NewWidths[IDX].lower() != 'none':
                        self.Widths[IDX] = NewWidths[IDX]
        

        
                    
        with self.Tag('table', klass='table renderer-table-bordered' + ' '.join(self.State['class'])):
            with self.Tag('thead', klass='thead-dark ' + ' '.join(self.State['class'])):
                self.add_header(self.Data[0])
            with self.Tag('tbody', klass=' '.join(self.State['class'])):
                for row in self.Data[1:]:
                    self.add_row(row)

    def add_header(self, header):
        with self.Doc.tag('tr', klass=' '.join(self.State['class'])):
            ColumnIDX = 0
            for value in header:
                NewState = copy.deepcopy(self.State)
                NewState['force-no-inline'] = True
                NewState['class'] += ['table-column-{}'.format(ColumnIDX)]
                if self.Widths[ColumnIDX] != None:
                    NewState['style'] += ['width: {}'.format(self.Widths[ColumnIDX])]
                    NewState['style'] += ['table-layout: fixed']
                self.WebpageObject.AddText(value, NewState, self.Interface, None, ForceTextTag='th')
                ColumnIDX += 1
                #self.Doc.line('th', value)

    def add_row(self, values, row_name=None):
        with self.Doc.tag('tr', klass=' '.join(self.State['class'])):
            if row_name is not None:
                NewState = copy.deepcopy(self.State)
                NewState['force-no-inline'] = True
                self.WebpageObject.AddText(row_name, NewState, self.Interface, None, ForceTextTag='th')
                #self.Doc.line('th', row_name)
            ColumnIDX = 0
            for value in values:
                NewState = copy.deepcopy(self.State)
                NewState['force-no-inline'] = True
                NewState['class'] += ['table-column-{}'.format(ColumnIDX)]
                if self.Widths[ColumnIDX] != None:
                    NewState['style'] += ['width: {}'.format(self.Widths[ColumnIDX])]
                    NewState['style'] += ['table-layout: fixed']
                self.WebpageObject.AddText(value, NewState, self.Interface, None, ForceTextTag='td')
                #self.Doc.line('td', value)
                ColumnIDX += 1