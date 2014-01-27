#!/usr/bin/env python3

"""ControlerInterface Progresser"""

ControlerInterfaceRequiredArgs={
'ControlerInterfaceArg',
'ControlerInterfaceType'}

def check(target):
    for ReqArg in ControlerInterfaceRequiredArgs:
        if target.keys.count(ReqArg)!=1:
            raise Exception("Some of arg is missing")

