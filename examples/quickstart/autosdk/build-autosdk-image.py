#!/usr/bin/env python3
import argparse, json, platform, subprocess, sys
from pathlib import Path

class Utility:
	
	@staticmethod
	def log(message, leading_newline=False):
		"""
		Prints a log message to stderr
		"""
		print('{}[build-autosdk-image.py] {}'.format(
			'\n' if leading_newline == True else '',
			message),
			file=sys.stderr, flush=True)
	
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
parser.add_argument('engine_source', default='', help='Set the path to the UE source to use', nargs='?')

versions = parser.add_argument_group('Version arguments', 'Provide either the path to the UE source, or all three of these values')
versions.add_argument('--major-version', default='', help='Set the major version of the MSVC tools to use')
versions.add_argument('--msvc-version', default='', help='Set the version of the MSVC SDK to use')
versions.add_argument('--sdk-version', default='', help='Set the version of the Windows SDK to use')

args = parser.parse_args()

# Ensure that either the path to Windows_SDK.json is provided, or the three version args, but not both
if (args.engine_source != '' and (args.major_version != '' or args.msvc_version != '' or args.sdk_version != '')) or \
	(args.engine_source == '' and (args.major_version == '' or args.msvc_version == '' or args.sdk_version == '')):
	Utility.error('Invalid arguments. You must provide either the path to the UE source, or all three version arguments')

# Resolve the absolute paths to our input directories
autosdk_dir = Path(__file__).parent
repo_root = autosdk_dir.parent.parent.parent
build_dir = repo_root / 'build'

filtered_packages = []
ue_version = "custom"
if args.engine_source != '':
	# parse build.version to determine UE version
	build_version_file = Path(args.engine_source) / 'Engine' / 'Build' / 'Build.version'
	with open(build_version_file, 'r') as file:
		version_data = json.load(file)
	ue_version = "{}.{}.{}".format(version_data.get('MajorVersion'), version_data.get('MinorVersion'), version_data.get('PatchVersion'))

	# parse windows_SDK.json to determine packages to pull
	windows_sdk_json = Path(args.engine_source) / 'Engine' / 'Config' / 'Windows' / 'Windows_SDK.json'
	with open(windows_sdk_json, 'r') as file:
		data = json.load(file)

	# Extract windows sdk version and remove the patch version
	sdk_version = (data.get('MainVersion')).rsplit('.', 1)[0]
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

# Read the Wine version string so we know the base image tag
wine_version_file = repo_root / 'build' / 'version.json'
wine_version_contents = json.loads(wine_version_file.read_text('utf-8'))
wine_version = wine_version_contents.get('wine-version')

# build a WineResources base image
build_script = 'build.py' if platform.system() == 'Windows' else 'build.sh'
Utility.run([
	build_dir / build_script, '--layout', '--no-sudo'
	])

Utility.run([
	'docker', 'buildx', 'build',
	'--progress=plain',
	'-t', 'epicgames/wine-patched:{}'.format(wine_version),
	build_dir / 'context'
])

# build an AutoSDK enabled image
if args.engine_source != '':
	Utility.run([
		'docker', 'buildx', 'build',
		'--progress=plain',
		'--build-arg', 'MAJOR_VERSION={}'.format(major_version),
		'--build-arg', 'PACKAGES={}'.format(' '.join(filtered_packages)),
		'--build-arg', 'BASE_IMAGE=epicgames/wine-patched:{}'.format(wine_version),
		'-t', 'epicgames/autosdk-wine:{}'.format(ue_version),
		autosdk_dir
	])
else:
	Utility.run([
		'docker', 'buildx', 'build',
		'--progress=plain',
		'--build-arg', 'MAJOR_VERSION={}'.format(args.major_version),
		'--build-arg', 'MSVC_VERSION={}'.format(args.msvc_version),
		'--build-arg', 'SDK_VERSION={}'.format(args.sdk_version),
		'--build-arg', 'BASE_IMAGE=epicgames/wine-patched:{}'.format(wine_version),
		'-t', 'epicgames/autosdk-wine:{}'.format(ue_version),
		autosdk_dir
	])

Utility.log('AutoSDK docker image built: "epicgames/autosdk-wine:{}"'.format(ue_version), leading_newline=True)