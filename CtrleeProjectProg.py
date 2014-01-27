#!/usr/bin/env python3

"""CtrleeProject Progresser"""

CtrleeProjectRequiredArgs={
'CtrleeProjectName',
'NodeTypes'}

def check(target):
	for ReqArg in CtrleeProjectRequiredArgs:
		if target.keys.count(ReqArg)!=1:
			raise Exception("Some of arg is missing")
