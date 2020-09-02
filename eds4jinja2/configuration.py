import json
from enum import Enum


class ActionType(Enum):
    NoAction = 0,
    CopyToOutput = 1


class Generic:

    def __init__(self, output, res):
        self.outputType = output
        self.resources = res


    outputType: str
    resources: []


class Resource:

    def __init__(self, file, actType):
        self.fileName = file
        self.action = actType

    fileName:str
    action: ActionType


class Configuration:

    def __init__(self):
        pass

    generic: Generic
    jinja2Params: dict








