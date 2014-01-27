#!/usr/bin/env python3

"""CtrleeInstance Progresser"""

CtrleeInstanceRequiredArgs={
'CtrleeInstanceName',
'NodeType'}

def check(target):
	for ReqArg in CtrleeInstanceRequiredArgs:
		if target.keys.count(ReqArg)!=1:
			raise Exception("Some of arg is missing")
