#!/usr/bin/env python3
import argparse, json, shutil, subprocess, sys
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
engine_build = parser.add_mutually_exclusive_group(required=True)
engine_build.add_argument('--engine', default='', help='Set the path to the Installed Build of UE to build with')
engine_build.add_argument('--image', default='', help='Set the image containing an Installed Build of UE to build with')

parser.add_argument('--project', default='', required=True, help='Set the path to the .ueproject file to build')

args = parser.parse_args()

if args.project == '':
	Utility.error('Invalid arguments. You must provide a project to build')

project_dir = Path(args.project).parent
project_file = Path(args.project).name

if args.engine != '':
	# parse build.version to determine UE version
	build_version_file = Path(args.engine) / 'Engine' / 'Build' / 'Build.version'
	with open(build_version_file, 'r') as file:
		version_data = json.load(file)
	ue_version = "{}.{}.{}".format(version_data.get('MajorVersion'), version_data.get('MinorVersion'), version_data.get('PatchVersion'))

	# Read the Wine version string so we know the base image tag
	wine_version_file = Path(__file__).parent.parent.parent.parent / 'build' / 'version.json'
	wine_version_contents = json.loads(wine_version_file.read_text('utf-8'))
	wine_version = wine_version_contents.get('wine-version')

	# Run our autosdk image
	# bindmount in both paths
	# build the project
	Utility.run([
		'docker', 'run', '--rm', '-it', '--init',
		'-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/UE'.format(args.engine),
		'-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/project'.format(project_dir),
		'epicgames/autosdk-wine:{}'.format(ue_version),
		'wine', './UE/Engine/Build/BatchFiles/RunUAT.bat', 'BuildCookRun',
		'-project=C:/project/{}'.format(project_file),
		'-nop4', '-allmaps', '-build', '-cook', '-stage', '-pak'
		'-platform=Win64', '-clientconfig=Development'
	])
else:
	# Run the specified autosdk-engine image
	# bindmount in project 
	# build the project
	Utility.run([
		'docker', 'run', '--rm', '-it', '--init',
		'-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/project'.format(project_dir),
		args.image,
		'wine', './UnrealEngine/Engine/Build/BatchFiles/RunUAT.bat', 'BuildCookRun',
		'-project=C:/project/{}'.format(project_file),
		'-nop4', '-allmaps', '-build', '-cook', '-stage', '-pak'
		'-platform=Win64', '-clientconfig=Development'
	])