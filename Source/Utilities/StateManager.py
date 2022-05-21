import copy

class StateManager(dict):
    def __init__(self, GlobalState={}):
        dict.__init__(self)
        self.GlobalState = GlobalState
        