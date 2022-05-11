import enum


class GameModes(str, enum.Enum):
    field = 'field'
    head = 'head'
    body = 'body'


class KillModes(str, enum.Enum):
    die = 'die'
    cut = 'cut'
