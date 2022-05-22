import yattag
import re
import copy
from Utilities.Core import *

class WebTable:
    def __init__(self, Data, State, Interface, WebpageObject):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.Doc = WebpageObject.Doc
        self.Tag = WebpageObject.Tag
        self.Text = WebpageObject.Text
        self.Line = WebpageObject.Line
        self.Data = Data
        self.State = State
        self.Interface = Interface
        self.WebpageObject = WebpageObject

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.RenderToPage()

    def RenderToPage(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.Widths = [None for i in self.Data[0]]
        ColumnWidthPattern = re.compile('COLUMN_WIDTH\((.*?)\)')
        ColumnWidthMatch = list(filter(lambda Result: Result != None, list(map(lambda Interface: ColumnWidthPattern.match(Interface), self.Interface))))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if len(ColumnWidthMatch) > 0:
            NewWidths = ColumnWidthMatch[0].group(1).replace(' ', '').split(',')
            for IDX in range(len(NewWidths)):
                if IDX < len(self.Widths):
                    if NewWidths[IDX].lower() != 'none':
                        self.Widths[IDX] = NewWidths[IDX]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Tag('table', self.WebpageObject.Class(self.State, 'table renderer-table-bordered')):
            with self.Tag('thead', self.WebpageObject.Class(self.State, 'thead-dark ')):
                self.add_header(self.Data[0])
            with self.Tag('tbody', self.WebpageObject.Class(self.State)):
                for row in self.Data[1:]:
                    self.add_row(row)

    def add_header(self, header):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Doc.tag('tr', self.WebpageObject.Class(self.State)):
            ColumnIDX = 0
            for value in header:
                NewState = copy.deepcopy(self.State)
                NewState['force-no-inline'] = True
                NewState['class'] += [Format('table-column-{}', ColumnIDX)]
                if self.Widths[ColumnIDX] != None:
                    NewState['style'] += [Format('width: {}', self.Widths[ColumnIDX])]
                    NewState['style'] += ['table-layout: fixed']
                self.WebpageObject.AddText(value, NewState, self.Interface, None, ForceTextTag='th')
                ColumnIDX += 1
                #self.Doc.line('th', value)

    def add_row(self, values, row_name=None):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        with self.Doc.tag('tr', self.WebpageObject.Class(self.State)):
            if row_name is not None:
                NewState = copy.deepcopy(self.State)
                NewState['force-no-inline'] = True
                self.WebpageObject.AddText(row_name, NewState, self.Interface, None, ForceTextTag='th')
                #self.Doc.line('th', row_name)
            ColumnIDX = 0
            for value in values:
                NewState = copy.deepcopy(self.State)
                NewState['force-no-inline'] = True
                NewState['class'] += [Format('table-column-{}', ColumnIDX)]
                if self.Widths[ColumnIDX] != None:
                    NewState['style'] += [Format('width: {}', self.Widths[ColumnIDX])]
                    NewState['style'] += ['table-layout: fixed']
                self.WebpageObject.AddText(value, NewState, self.Interface, None, ForceTextTag='td')
                #self.Doc.line('td', value)
                ColumnIDX += 1