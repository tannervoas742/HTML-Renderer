import copy
import re
from Utilities import *
from WebPageEnums import WebPageEnums
from StateManager import StateManager

class WebPageStateManager(StateManager):
    def __init__(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        StateManager.__init__(self)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.GlobalState['in_list_div'] = 0

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self['visible'] = True
        self['key'] = []
        self['class'] = []
        self['style'] = []
        self['mode'] = WebPageEnums.Text
        self['lookup_table.range'] = None
        self['callback'] = []
        self['font'] = 'DEFAULT'
        self['next.font'] = []
        self['key_font'] = 'HEADER'
        self['next.key_font'] = []

    def SaveToKeyAndNext(self, State, Key, Matches, Count):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if Count >= 2:
            State[Key] = Matches[0]
            State['next.{}'.format(Key)] = Matches[1:]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        elif Count == 1:
            State[Key] = Matches[0]
            State['next.{}'.format(Key)] = []

    def HandleSingleStringKeyAndNext(self, WP, State, Interface, Function):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        MatchData = WP.TP.Index(0, WP.TP.Split(WP.TP.Extract(Function[0], Interface, True)))
        if WP.TP.Match:
            Match, Count = WP.TP.CSV(MatchData[0])
            self.SaveToKeyAndNext(State, Function[1], Match, Count)

    def HandleEnableAndStore(self, WP, State, Interface, Function):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        MatchData = WP.TP.Extract(Function[0], Interface, True, Processor=Function[4])
        if WP.TP.Match:
            State[Function[1]] = Function[2]
            if Function[3] != None:
                State[Function[3]] = MatchData[0]

    def MixState(self, Interface, WP):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        MixedState = copy.deepcopy(self)
        MixedState.GlobalState = self.GlobalState

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if 'HIDDEN' in Interface:
            MixedState['visible'] = False
        elif 'SHOWN' in Interface:
            MixedState['visible'] = True

        Functions = [
            ['FONT(.)'          , 'font'                                                      , self.HandleSingleStringKeyAndNext],
            ['KEYFONT(.)'       , 'key_font'                                                  , self.HandleSingleStringKeyAndNext],
            ['LOOKUP_TABLE(.,.)', 'mode', WebPageEnums.LookupTable, 'lookup_table.range', int , self.HandleEnableAndStore        ],
            ['TABLE'            , 'mode', WebPageEnums.Table      , None                , None, self.HandleEnableAndStore        ]
        ]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        for Function in Functions:
            Function[-1](WP, MixedState, Interface, Function)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ClassPattern = re.compile('CLASS\((.*)\)')
        ClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: ClassPattern.match(Code), Interface))))))                
        if len(ClassMatch) > 0:
            MixedState['class'] = []
            for Group in ClassMatch:
                MixedState['class'] += Group.lower().split()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        AddClassPattern = re.compile('ADD_CLASS\((.*)\)')
        AddClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: AddClassPattern.match(Code), Interface))))))                
        if len(AddClassMatch) > 0:
            for Group in AddClassMatch:
                MixedState['class'] += Group.lower().split()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        RemoveClassPattern = re.compile('REMOVE_CLASS\((.*)\)')
        RemoveClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: RemoveClassPattern.match(Code), Interface))))))                
        if len(RemoveClassMatch) > 0:
            for Group in RemoveClassMatch:
                for Tag in Group.lower().split():
                    if Tag in MixedState['class']:
                        del MixedState['class'][MixedState['class'].index(Tag)]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        CallPattern = re.compile('CALL\((.*)\)')
        CallMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: CallPattern.match(Code), Interface))))))                
        if len(CallMatch) > 0:
            MixedState['callback'] = []
            for Group in CallMatch:
                MixedState['callback'] += list(map(lambda Item: '_CALLBACK_' + Item, Group.split()))
            
            Compiled = []
            for Func in MixedState['callback']:
                if Func.replace('_CALLBACK_', '') in WP.ParamStorage:
                    FuncText = WP.ParamStorage[Func.replace('_CALLBACK_', '')]
                    FuncText = 'def {}(self, STATE, INTERFACE, ARG):\n    '.format(Func) + '\n    '.join(FuncText)
                    exec(FuncText)
                    Compiled += [eval(Func)]
            MixedState['callback'] = Compiled
        else:
            MixedState['callback'] = []

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return MixedState