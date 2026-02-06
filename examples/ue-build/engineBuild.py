#!/usr/bin/env python3
import argparse, json, shutil, string, subprocess, sys
from pathlib import Path

class Utility:
	
	@staticmethod
	def log(message):
		"""
		Prints a log message to stderr
		"""
		print('[engineBuild.py] {}'.format(message), file=sys.stderr, flush=True)
	
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

# TODO find a mechanism to derive this from the build script
# The wine version in use (which we use to determine the auto-generated image tag)
# WINE_PACKAGE_VERSION = '10.20'

# get path to UE source and build command as build args
# TODO decide if we want to allow users to define build args for the WineResources build or not
parser = argparse.ArgumentParser()
parser.add_argument('--ue-source', default='./UnrealEngine', help="Set the filesystem path for the UnrealEngine source to use")
parser.add_argument('command', metavar="command", help="Build command to run under Wine.", nargs="*")

# TODO decide if we will allow these as overrides for the parsed values?
# parser.add_argument('--major-version', default='17', help="Set the major version of the MSVC tools to use")
# parser.add_argument('--msvc-version', default='17.14', help="Set the version of the MSVC SDK to use")
# parser.add_argument('--sdk-version', default='10.0.26100', help="Set the version of the Windows SDK to use")

args = parser.parse_args()

# Resolve the absolute paths to our input directories
ue_build_dir = Path(__file__).parent
examples_dir = ue_build_dir.parent
base_dir = examples_dir.parent
build_dir = base_dir / 'build'

# TODO If we do allow command-line flags to override the parsed values then add logic here to skip parsing what we can
# parse windows_SDK.json to determine version numbers
windows_sdk_json = Path(args.ue_source) / 'Engine' / 'Config' / 'Windows' / 'Windows_SDK.json'
with open(windows_sdk_json, 'r') as file:
    data = json.load(file)

# Extract windows sdk version and remove the patch version
sdk_version = (data.get("MainVersion")).rsplit('.', 1)[0]
# If VS2026 is support then prefer it
msvc_version = data.get("MinimumVisualStudio2026Version")
if msvc_version is None:
	msvc_version = data.get("MinimumVisualStudio2022Version")
# get the major version of msvc
major_version = msvc_version.rsplit('.', 1)[0]

# build a WineResources base image
# I could use the layout flag, then manually run the docker build to define my own image tag...
Utility.run([
	build_dir / 'build.sh', '--layout', '--no-32bit', '--no-sudo'
	])

Utility.run([
	'docker', 'buildx', 'build',
	'--progress=plain',
	'-t', 'tensorworks/wine-patched:{}'.format("temp"),
	build_dir / 'context'
	])

# build an AutoSDK enabled image
Utility.run([
	'docker', 'buildx', 'build',
	'--progress=plain',
	'--build-arg', 'MAJOR_VERSION={}'.format(major_version),
	'--build-arg', 'MSVC_VERSION={}'.format(msvc_version),
	'--build-arg', 'SDK_VERSION={}'.format(sdk_version),
	'--build-arg', 'BASE_IMAGE={}'.format("tensorworks/wine-patched:temp"),
	'-t', 'tensorworks/autosdk-wine:{}'.format('temp'),
	ue_build_dir
	])

# bindmount UE source into that image and run a build

print(' '.join(args.command))
print("Main version:", sdk_version)