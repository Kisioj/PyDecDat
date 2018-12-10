class Type:
    VOID = 0
    FLOAT = 1
    INT = 2
    STRING = 3
    CLASS = 4
    FUNC = 5
    PROTOTYPE = 6
    INSTANCE = 7


TYPE_2_STR = {
    Type.VOID: 'void',
    Type.FLOAT: 'float',
    Type.INT: 'int',
    Type.STRING: 'string',
    Type.CLASS: 'class',
    Type.FUNC: 'func',
    Type.PROTOTYPE: 'prototype',
    Type.INSTANCE: 'instance',
}

TYPES = TYPE_2_STR.keys()


class Flag:
    CONST = 1
    RETURN = 2
    CLASSVAR = 4
    EXTERNAL = 8
    MERGED = 16


FLAG_2_STR = {
    Flag.CONST: 'const',
    Flag.RETURN: 'return',
    Flag.CLASSVAR: 'classvar',
    Flag.EXTERNAL: 'external',
    Flag.MERGED: 'merged',
}

FLAGS = FLAG_2_STR.keys()


CHAR_FORMAT = '<c'  # 1 byte
BYTE_FORMAT = '<B'  # 1 byte
BYTES_FORMAT = '<{}s'
FLOAT_FORMAT = '<f'  # 4 bytes
INT_FORMAT = '<l'  # 4 bytes

EXTERNALS_TO_FIX = (
    'CREATEINVITEM.PAR1',
    'CREATEINVITEMS.PAR1',
    'HLP_GETNPC.PAR0',
    'NPC_REMOVEINVITEMS.PAR1',
    'NPC_HASITEMS.PAR1',
)
