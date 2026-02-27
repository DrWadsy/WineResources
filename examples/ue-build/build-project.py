#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path

class Utility:
	
	@staticmethod
	def log(message):
		"""
		Prints a log message to stderr
		"""
		print('[build-project.py] {}'.format(message), file=sys.stderr, flush=True)
	
	@staticmethod
	def error(message):
		"""
		Logs an error message and then exits immediately
		"""
		Utility.log('Error: {}'.format(message))
		sys.exit(1)
	
	@staticmethod
	def run(command, **kwargs):
		"""
		Logs and runs a command, verifying that the command succeeded
		"""
		stringified = [str(c) for c in command]
		Utility.log(stringified)
		return subprocess.run(stringified, **{'check': True, **kwargs})

# get path to UE source and build command as build args
parser = argparse.ArgumentParser()
parser.add_argument('--engine', default='', help='Set the path to the Installed Build of UE to build with', nargs='?')
parser.add_argument('--project', default='', help='Set the path to the .ueproject file to build', nargs='?')

args = parser.parse_args()

if (args.engine == ''):
	Utility.error('Invalid arguments. You must provide an Installed Build of UE')
if (args.project == ''):
	Utility.error('Invalid arguments. You must provide a project to build')

project_dir = Path(args.project).parent
project_file = Path(args.project).name

Utility.log('Project dir: {}'.format(project_dir))
Utility.log('Project file: {}'.format(project_file))

# Run our autosdk image
# bindmount in both paths
# build the project
Utility.run([
	'docker', 'run', '--rm', '-it',
	'-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/UE'.format(args.engine),
	'-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/project'.format(project_dir),
	'tensorworks/autosdk-wine:temp',
	'wine', './UE/Engine/Build/BatchFiles/RunUAT.bat', 'BuildCookRun',
	'-project=C:/project/{}'.format(project_file),
	'-nop4', '-allmaps', '-build', '-cook', '-stage', '-pak'
	'-platform=Win64', '-clientconfig=Development'
])