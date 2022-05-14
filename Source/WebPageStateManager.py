import copy
import re
from WebPageEnums import WebPageEnums
from StateManager import StateManager

class WebPageStateManager(StateManager):
    def __init__(self):
        StateManager.__init__(self)
        self.GlobalState['in_list_div'] = 0
        self['visible'] = True
        self['key'] = []
        self['class'] = []
        self['style'] = []
        self['mode'] = WebPageEnums.Text
        self['lookup_table.range'] = None
        self['callback'] = []
        self['font'] = 'DEFAULT'
        self['next.font'] = []

    def MixState(self, Interface, WP):
        MixedState = copy.deepcopy(self)
        MixedState.GlobalState = self.GlobalState
        if 'HIDDEN' in Interface:
            MixedState['visible'] = False
        elif 'SHOWN' in Interface:
            MixedState['visible'] = True

        FontPattern = re.compile('FONT\((.+?)\)')
        FontMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: FontPattern.match(Code), Interface))))))
        if len(FontMatch) > 0:
            Font = FontMatch[0].replace(' ', '').split(',')
            if len(Font) >= 2:
                MixedState['font'] = Font[0]
                MixedState['next.font'] = Font[1:]
            elif len(Font) == 1:
                MixedState['font'] = Font[0]
                MixedState['next.font'] = []

        LTPattern = re.compile('LOOKUP_TABLE\((\d+)\,(\d+)\)')
        LTMatch = list(map(lambda Reg: [int(Reg.group(1)), int(Reg.group(2))], list(filter(lambda Result: Result != None, list(map(lambda Code: LTPattern.match(Code), Interface))))))                
        if len(LTMatch) > 0:
            MixedState['mode'] = WebPageEnums.LookupTable
            MixedState['lookup_table.range'] = LTMatch[0]

        TPattern = re.compile('TABLE')
        TMatch = list(map(lambda Reg: Reg.group(0), list(filter(lambda Result: Result != None, list(map(lambda Code: TPattern.match(Code), Interface))))))                
        if len(TMatch) > 0:
            MixedState['mode'] = WebPageEnums.Table

        ClassPattern = re.compile('CLASS\((.*)\)')
        ClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: ClassPattern.match(Code), Interface))))))                
        if len(ClassMatch) > 0:
            MixedState['class'] = []
            for Group in ClassMatch:
                MixedState['class'] += Group.lower().split()

        AddClassPattern = re.compile('ADD_CLASS\((.*)\)')
        AddClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: AddClassPattern.match(Code), Interface))))))                
        if len(AddClassMatch) > 0:
            for Group in AddClassMatch:
                MixedState['class'] += Group.lower().split()

        RemoveClassPattern = re.compile('REMOVE_CLASS\((.*)\)')
        RemoveClassMatch = list(map(lambda Reg: Reg.group(1), list(filter(lambda Result: Result != None, list(map(lambda Code: RemoveClassPattern.match(Code), Interface))))))                
        if len(RemoveClassMatch) > 0:
            for Group in RemoveClassMatch:
                for Tag in Group.lower().split():
                    if Tag in MixedState['class']:
                        del MixedState['class'][MixedState['class'].index(Tag)]

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
        return MixedState