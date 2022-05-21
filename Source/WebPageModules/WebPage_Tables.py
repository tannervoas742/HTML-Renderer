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
    
class WebPage_Tables:
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

        WebTable(Table, State, Interface, self)

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
            Ranks = list(map(lambda Ret: '.'.join(Ret) if Ret[0].isnumeric() == False else '.'.join([Format(FormatString, Ret[0]), Ret[1]]), Ranks))
            for Key in list(sorted(list(Data.keys()), key=lambda x: str(x))):
                NewData += [['.'.join(Key.split('.')[1:]), Data[Key]]]
            Data = NewData
        Table = Data
        Table = self.CleanTable(Table)
        WebTable(Table, State, Interface, self)