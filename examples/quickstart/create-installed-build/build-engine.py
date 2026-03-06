#!/usr/bin/env python3
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

class Utility:
	
	@staticmethod
	def log(message):
		"""
		Prints a log message to stderr
		"""
		print('[build-engine.py] {}'.format(message), file=sys.stderr, flush=True)
	
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

def custom_copy(src, dst, *, follow_symlinks = True):
	with open(src, 'rb') as source, open(dst, 'wb') as dest:
		shutil.copy2(source, dest)
		dest.flush()
		os.fsync(dest.fileno)

# get path to UE source and build command as build args
parser = argparse.ArgumentParser()
parser.add_argument('engine_source', default='', help='Set the path to the UE source code to build')
parser.add_argument('--containerise', action='store_true', help='Containerise the Installed Build')
args = parser.parse_args()

if (args.engine_source == ''):
	Utility.error('Invalid arguments. You must provide the path to the UE source')

# Resolve the absolute paths to our input directories
create_installed_build_dir = Path(__file__).parent
quickstart_dir = create_installed_build_dir.parent

Utility.run([
	quickstart_dir / 'autosdk' / 'build-autosdk-image.py',
    args.engine_source
])

# Remove the ADOSuppport plugin if it is present, since it is unused and breaks builds
ADOPlugin_path = Path(args.engine_source) / 'Engine' / 'Plugins' / 'Runtime' / 'Database' / 'ADOSupport'
if ADOPlugin_path.exists():
    shutil.rmtree(ADOPlugin_path)

# parse build.version to determine UE version
build_version_file = Path(args.engine_source) / 'Engine' / 'Build' / 'Build.version'
with open(build_version_file, 'r') as file:
	version_data = json.load(file)
ue_version = "{}.{}.{}".format(version_data.get('MajorVersion'), version_data.get('MinorVersion'), version_data.get('PatchVersion'))

# Read the Wine version string so we know the base image tag
wine_version_file = Path(__file__).parent.parent.parent.parent / 'build' / 'version.json'
wine_version_contents = json.loads(wine_version_file.read_text('utf-8'))
wine_version = wine_version_contents.get('wine-version')

# bindmount UE source into that image and run UBT with the provided args
Utility.run([
    'docker', 'run', '--rm', '-t', '--init',
    '-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/UE'.format(args.engine_source),
    'epicgames/autosdk-ue-{}-wine:{}'.format(ue_version, wine_version),
    'wine', './UE/Engine/Build/BatchFiles/RunUAT.bat', 'BuildGraph',
    '-target=Make Installed Build Win64', '-script=Engine/Build/InstalledEngineBuild.xml',
    '-set:HostPlatformOnly=true'
])

# Optionally containerise the Installed Build
if args.containerise:
	wrap_build_dir = quickstart_dir / 'wrap-installed-build'
	destination_dir = wrap_build_dir / 'context' / 'UnrealEngine'

	files = os.listdir(destination_dir)
	for file in files:
		try:
			if os.path.isdir(destination_dir / file):
				shutil.rmtree(destination_dir / file, destination_dir / file)
			elif file != ".gitignore":
				os.remove(destination_dir / file)
		except Exception as e:
			Utility.error("Could not empty context folder before containerising: {}".format(e))

	installed_build_dir = Path(args.engine_source) / 'LocalBuilds' / 'Engine' / 'Windows'

	files = os.listdir(installed_build_dir)
	for file in files:
		try:
			if os.path.isdir(installed_build_dir / file):
				shutil.copytree(installed_build_dir / file, destination_dir / file)
			else:
				shutil.copy2(installed_build_dir / file, destination_dir / file)

		except Exception as e:
			Utility.error("Could not copy Installed Build artifacts to context folder for containerising: {}".format(e))
	
	Utility.run([
	wrap_build_dir / 'build.sh'
	])

