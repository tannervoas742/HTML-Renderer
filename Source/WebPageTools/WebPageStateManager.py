import copy
import re
from Utilities.Core import *
from WebPageTools.WebPageEnums import WebPageEnums
from Utilities.StateManager import StateManager

class WebPageStateManager(StateManager):
    def __init__(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        StateManager.__init__(self)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.GlobalState['in_list_div'] = 0
        self.GlobalState['in_slide'] = False
        self.GlobalState['in_slide_show'] = False

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self['visible'] = True
        self['key'] = []
        self['class'] = []
        self['style'] = []
        self['mode'] = WebPageEnums.Text
        self['lookup_table.range'] = None
        self['table_header'] = []
        self['callback'] = []
        self['late callback'] = []
        self['font'] = 'DEFAULT'
        self['next.font'] = []
        self['key_font'] = 'HEADER'
        self['next.key_font'] = []
        self['slide_depth'] = 0

    def SaveToKeyAndNext(self, State, Key, Matches, Count):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if Count >= 2:
            State[Key] = Matches[0]
            State[Format('next.{}', Key)] = Matches[1:]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        elif Count == 1:
            State[Key] = Matches[0]
            State[Format('next.{}', Key)] = []

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

    def HandleStorageType(self, WP, State, Interface, Function):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if Function[2] == WebPageEnums.Add:
            Function[0] = 'ADD_' + Function[0]
        elif Function[2] == WebPageEnums.Del:
            Function[0] = 'REMOVE_' + Function[0]
        elif  Function[2] == WebPageEnums.Set:
            Function[0] = Function[0]
        else:
            return

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        MatchData = WP.TP.JoinLists(WP.TP.Extract(Function[0], Interface, True))
        if WP.TP.Match:

        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            if Function[2] == WebPageEnums.Set:
                State[Function[1]] = []
            for Group in MatchData:
                if Function[2] != WebPageEnums.Del:

        #           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                    State[Function[1]] += Group.split(',')
                else:

        #           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                    for Tag in Group.split(','):
                        if Tag in State[Function[1]]:
                            del State[Function[1]][State[Function[1]].index(Tag)]

    def HandleCallbacks(self, WP, State, Interface, Function):
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        MatchData = WP.TP.Index(0, WP.TP.Split(WP.TP.Extract(Function[0], Interface, True)))
        if WP.TP.Match:
            State[Function[1]] = []
            for Group in MatchData:
                State[Function[1]] += list(map(lambda Item: '_CALLBACK_' + Item, Group.split()))
            Compiled = []
            for Func in State[Function[1]]:
                if Func.replace('_CALLBACK_', '') in WP.ParamStorage:
                    FuncText = WP.ParamStorage[Func.replace('_CALLBACK_', '')]
                    FuncText = Format('def {}(self, STATE, INTERFACE, ARG):\n    ', Func) + '\n    '.join(FuncText)
                    exec(FuncText)
                    Compiled += [eval(Func)]
            State[Function[1]] = Compiled
        else:
            State[Function[1]] = []

    def Lower(self, WP, State, Interface, Function):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if len(State[Function[1]]) != 0:
            State[Function[1]] = list(map(lambda x: x.lower(), State[Function[1]]))

    def MixState(self, Interface, WP):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        MixedState = copy.deepcopy(self)
        MixedState.GlobalState = self.GlobalState

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if MixedState['slide_depth'] > 0:
            MixedState['slide_depth'] += 1

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if 'HIDDEN' in Interface:
            MixedState['visible'] = False
        elif 'SHOWN' in Interface:
            MixedState['visible'] = True

        StateModiferFunctions = [
            ['FONT(.)'              , 'font'          ,                                                       self.HandleSingleStringKeyAndNext   ],
            ['KEYFONT(.)'           , 'key_font'      ,                                                       self.HandleSingleStringKeyAndNext   ],
            ['LOOKUP_TABLE(.,.)'    , 'mode'          , WebPageEnums.LookupTable, 'lookup_table.range', int , self.HandleEnableAndStore           ],
            ['TABLE'                , 'mode'          , WebPageEnums.Table      , None                , None, self.HandleEnableAndStore           ],
            ['SLIDES(.)'            , 'mode'          , WebPageEnums.Slides     , 'slides_group'      , str , self.HandleEnableAndStore           ],
            ['CLASS(.)'             , 'class'         , WebPageEnums.Add        ,                             [self.HandleStorageType, self.Lower]],
            ['CLASS(.)'             , 'class'         , WebPageEnums.Del        ,                             [self.HandleStorageType, self.Lower]],
            ['CLASS(.)'             , 'class'         , WebPageEnums.Set        ,                             [self.HandleStorageType, self.Lower]],
            ['STYLE(.)'             , 'style'         , WebPageEnums.Add        ,                             [self.HandleStorageType, self.Lower]],
            ['STYLE(.)'             , 'style'         , WebPageEnums.Del        ,                             [self.HandleStorageType, self.Lower]],
            ['STYLE(.)'             , 'style'         , WebPageEnums.Set        ,                             [self.HandleStorageType, self.Lower]],
            ['CALL(.)'              , 'callbacks'     ,                                                       self.HandleCallbacks                ],
            ['LATE_CALL(.)'         , 'late_callbacks',                                                       self.HandleCallbacks                ],
            ['TABLE_HEADER(.,.,.,.)', 'table_header'  , WebPageEnums.Set        ,                             self.HandleStorageType              ]
        ]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        for StateModiferFunction in StateModiferFunctions:
            if type(StateModiferFunction[-1]) != list:
                StateModiferFunction[-1] = [StateModiferFunction[-1]]
            for Callback in StateModiferFunction[-1]:
                Callback(WP, MixedState, Interface, StateModiferFunction)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        return MixedState