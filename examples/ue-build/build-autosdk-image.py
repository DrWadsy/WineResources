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

parser = argparse.ArgumentParser()
parser.add_argument('windows_sdk_json', default='', help='Set the path to the Windows_SDK.json file to use', nargs='?')

versions = parser.add_argument_group('Version arguments', 'Provide either the path to the UE source, or all three of these values')
versions.add_argument('--major-version', default='', help='Set the major version of the MSVC tools to use')
versions.add_argument('--msvc-version', default='', help='Set the version of the MSVC SDK to use')
versions.add_argument('--sdk-version', default='', help='Set the version of the Windows SDK to use')

args = parser.parse_args()

# Ensure that either the path to Windows_SDK.json is provided, or the three version args, but not both
if (args.windows_sdk_json != '' and (args.major_version != '' or args.msvc_version != '' or args.sdk_version != '')) or \
	(args.windows_sdk_json == '' and (args.major_version == '' or args.msvc_version == '' or args.sdk_version == '')):
	Utility.error('Invalid arguments. You must provide either the path to "Windows_SDK.json", or all three version arguments')

# Resolve the absolute paths to our input directories
ue_build_dir = Path(__file__).parent
examples_dir = ue_build_dir.parent
base_dir = examples_dir.parent
build_dir = base_dir / 'build'

filtered_packages = []
if args.windows_sdk_json != '':
	# parse windows_SDK.json to determine packages to pull
	# windows_sdk_json = Path(args.windows_sdk_json) / 'Engine' / 'Config' / 'Windows' / 'Windows_SDK.json'
	with open(args.windows_sdk_json, 'r') as file:
		data = json.load(file)

	# Extract windows sdk version and remove the patch version
	sdk_version = (data.get('MainVersion')).rsplit('.', 1)[0]
	# TODO - is this right, or is 2026 support only experimental...
	# if VS2026 is supported then prefer it
	msvc_version = data.get('MinimumVisualStudio2026Version')
	if msvc_version is None:
		msvc_version = data.get('MinimumVisualStudio2022Version')
	# get the major version of msvc
	major_version = msvc_version.rsplit('.', 1)[0]

	msvc_version_suggestions = data.get('VisualStudio2026SuggestedComponents')
	if msvc_version_suggestions is None:
		msvc_version_suggestions = data.get('VisualStudio2022SuggestedComponents')

	# Get suggested packages from Windows_SDK.json
	extracted_packages = data.get('VisualStudioSuggestedComponents') + msvc_version_suggestions
	invalid_phrases = ['.ATL', 'VisualStudio.Workload', 'Component.Unreal']

	for package in extracted_packages:
		valid = True
		for phrase in invalid_phrases:
			if phrase in package:
				valid = False
		if valid:
			if package.startswith('Microsoft.Net.Component') and package.endswith('TargetingPack'):
				package = package.replace('TargetingPack', 'SDK')
			filtered_packages.append(package) 
	if len(filtered_packages) == 0:
		Utility.error('No packages could be read from {}. Check you have provided the path to the UE source code.'.format(args.windows_sdk_json))

# build a WineResources base image
Utility.run([
	build_dir / 'build.sh', '--layout', '--no-sudo'
	])

Utility.run([
	'docker', 'buildx', 'build',
	'--progress=plain',
	'-t', 'tensorworks/wine-patched:temp',
	build_dir / 'context'
])

# build an AutoSDK enabled image
if args.windows_sdk_json != '':
	Utility.run([
		'docker', 'buildx', 'build',
		'--progress=plain',
		'--build-arg', 'MAJOR_VERSION={}'.format(major_version),
		'--build-arg', 'PACKAGES={}'.format(' '.join(filtered_packages)),
		'--build-arg', 'BASE_IMAGE=tensorworks/wine-patched:temp',
		'-t', 'tensorworks/autosdk-wine:temp',
		ue_build_dir
	])
else:
	Utility.run([
		'docker', 'buildx', 'build',
		'--progress=plain',
		'--build-arg', 'MAJOR_VERSION={}'.format(args.major_version),
		'--build-arg', 'MSVC_VERSION={}'.format(args.msvc_version),
		'--build-arg', 'SDK_VERSION={}'.format(args.sdk_version),
		'--build-arg', 'BASE_IMAGE=tensorworks/wine-patched:temp',
		'-t', 'tensorworks/autosdk-wine:temp',
		ue_build_dir
	])

Utility.log('AutoSDK docker image built: "tensorworks/autosdk-wine:temp"')