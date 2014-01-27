#!/usr/bin/env python3

"""Controler Progresser"""

ControlerInterfaceRequiredArgs={
'ControlerName',
'Controlerkeys'}

def check(target):
    for ReqArg in ControlerInterfaceRequiredArgs:
        if target.keys.count(ReqArg)!=1:
            raise Exception("Some of arg is missing")

