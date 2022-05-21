import json
import io
import os
import copy
import sys


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