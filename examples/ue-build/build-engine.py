#!/usr/bin/env python3
import argparse, json, shutil, string, subprocess, sys
from pathlib import Path

class Utility:
	
	@staticmethod
	def log(message):
		"""
		Prints a log message to stderr
		"""
		print('[runUBTinWineContainer.py] {}'.format(message), file=sys.stderr, flush=True)
	
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
parser.add_argument('ue_source', default='', help='Set the path to the UE source code to build', nargs='?')

args = parser.parse_args()

if (args.ue_source == ''):
	Utility.error('Invalid arguments. You must provide the path to the UE source')

# Resolve the absolute paths to our input directories
ue_build_dir = Path(__file__).parent
examples_dir = ue_build_dir.parent
base_dir = examples_dir.parent
build_dir = base_dir / 'build'

windows_sdk_json = Path(args.ue_source) / 'Engine' / 'Config' / 'Windows' / 'Windows_SDK.json'

Utility.run([
	ue_build_dir / 'build-autosdk-image.py',
    windows_sdk_json
])

# Remove the ADOSuppport plugin if it is present, since it is unused and breaks builds
ADOPlugin_path = Path(args.ue_source) / 'Engine' / 'Plugins' / 'Runtime' / 'Database' / 'ADOSupport'
if ADOPlugin_path.exists():
    shutil.rmtree(ADOPlugin_path)

# bindmount UE source into that image and run UBT with the provided args
Utility.run([
    'docker', 'run', '--rm', '-t',
    '-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/UE'.format(args.ue_source),
    'tensorworks/autosdk-wine:temp',
    'wine', './UE/Engine/Build/BatchFiles/RunUAT.bat', 'BuildGraph',
    '-target=Make Installed Build Win64', '-script=Engine/Build/InstalledEngineBuild.xml',
    '-set:HostPlatformOnly=true'
])
