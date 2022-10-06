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

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        for IndexY in range(len(Table)):
            for IndexX in range(len(Table[IndexY])):
                Table[IndexY][IndexX] = str(Table[IndexY][IndexX])
        return Table

    def ConvertToHeaderRow(self, Info, Length):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        EffectiveCounter = 0
        Row = []
        InfoKeysSorted = list(sorted(Info.keys(), key=lambda x: x))
        for Key in InfoKeysSorted:
            while EffectiveCounter < Key - 1:
                Row += ['']
                EffectiveCounter += 1
            Row += [[1 + Info[Key][0] - Key, Info[Key][1]]]
            EffectiveCounter += 1 + Info[Key][0] - Key
        while EffectiveCounter < Length:
            Row += ['']
            EffectiveCounter += 1

        return Row


    def AddLookupTable(self, Input, State, Interface, Data):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Table = [Data]
        for i in range(State['lookup_table.range'][0] - 1, State['lookup_table.range'][1]):
            Row = []
            for Key in Data:
                if i >= len(self.ParamStorage[Key]):
                    Row += [self.ParamStorage[Key][-1]]
                else:    
                    Row += [self.ParamStorage[Key][i]]
            Table += [Row]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Table = self.CleanTable(Table)
        HeaderCount = 1

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if len(State['table_header']) % 4 != 0:
            FlushPrintUTF8('#TABLE_HEADER Error: command used without 4 arguments (HEADER_ROW, COL_START, COL_END, VALUE)')
            exit(1)
        
        if len(State['table_header']) >= 4:
            Headers = {}
            while len(State['table_header']) >= 4:
                if int(State['table_header'][0]) not in Headers:
                    Headers[int(State['table_header'][0])] = {}
                if int(State['table_header'][1]) in Headers[int(State['table_header'][0])]:
                    FlushPrintUTF8(Format('#TABLE_HEADER Error: Repeated start value {} for row {}', int(State['table_header'][1]), int(State['table_header'][0])))
                    exit(-1)
                Headers[int(State['table_header'][0])][int(State['table_header'][1])] = [int(State['table_header'][2]), State['table_header'][3]]
                State['table_header'] = State['table_header'][4:]
        
            for Key in Headers:
                Headers[Key] = self.ConvertToHeaderRow(Headers[Key], len(Table[0]))

            HeaderKeysSorted = list(sorted(Headers.keys(), key=lambda x: x, reverse=True))
            for Key in HeaderKeysSorted:
                Table = [Headers[Key]] + Table
                HeaderCount += 1

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        WebTable(Table, State, Interface, self, HeaderCount)

    def AddTable(self, Input, State, Interface, Data):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if type(Data) == dict:
            NewData = []
            Ranks = list(map(lambda Ret: self.GetCommandInterfaceFromKey(Ret)[0:2], Data.keys()))
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

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        Table = Data
        Table = self.CleanTable(Table)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        WebTable(Table, State, Interface, self)