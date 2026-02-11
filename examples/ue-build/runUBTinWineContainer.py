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
parser.add_argument('--ue-source', default='', help="Set the filesystem path for the UnrealEngine source to use")
parser.add_argument('ubtargs', metavar="ubtargs", help="Arguments to pass to RunUBT, stripped of their leading hyphens", nargs="*")

# TODO decide if we will allow these as overrides for the parsed values?
parser.add_argument('--major-version', default='17', help="Set the major version of the MSVC tools to use")
parser.add_argument('--msvc-version', default='17.14', help="Set the version of the MSVC SDK to use")
parser.add_argument('--sdk-version', default='10.0.26100', help="Set the version of the Windows SDK to use")

args = parser.parse_args()

# Resolve the absolute paths to our input directories
ue_build_dir = Path(__file__).parent
examples_dir = ue_build_dir.parent
base_dir = examples_dir.parent
build_dir = base_dir / 'build'

filtered_packages = []
if args.ue_source != '':
	# parse windows_SDK.json to determine packages to pull
	windows_sdk_json = Path(args.ue_source) / 'Engine' / 'Config' / 'Windows' / 'Windows_SDK.json'
	with open(windows_sdk_json, 'r') as file:
		data = json.load(file)

	# Extract windows sdk version and remove the patch version
	sdk_version = (data.get("MainVersion")).rsplit('.', 1)[0]
	# TODO - is this right, or is 2026 support only experimental...
	# if VS2026 is supported then prefer it
	msvc_version = data.get("MinimumVisualStudio2026Version")
	if msvc_version is None:
		msvc_version = data.get("MinimumVisualStudio2022Version")
	# get the major version of msvc
	major_version = msvc_version.rsplit('.', 1)[0]

	msvc_version_suggestions = data.get("VisualStudio2026SuggestedComponents")
	if msvc_version_suggestions is None:
		msvc_version_suggestions = data.get("VisualStudio2022SuggestedComponents")

	# Get suggested packages from Windows_SDK.json
	extracted_packages = data.get("VisualStudioSuggestedComponents") + msvc_version_suggestions
	invalid_phrases = [".ATL", "VisualStudio.Workload", "Component.Unreal"]

	for package in extracted_packages:
		valid = True
		for phrase in invalid_phrases:
			if phrase in package:
				valid = False
		if valid:
			if package.startswith("Microsoft.Net.Component") and package.endswith("TargetingPack"):
				package = package.replace("TargetingPack", "SDK")
			filtered_packages.append(package)
	if len(filtered_packages) == 0:
		Utility.error("No packages could be read from {}. Check you have provided the path to the UE source code.".format(windows_sdk_json))

# build a WineResources base image
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
if args.ue_source != '' and len(filtered_packages) > 0:
		Utility.run([
		'docker', 'buildx', 'build',
		'--progress=plain',
		'--build-arg', 'MAJOR_VERSION={}'.format(major_version),
		'--build-arg', 'PACKAGES={}'.format(" ".join(filtered_packages)),
		'--build-arg', 'BASE_IMAGE={}'.format("tensorworks/wine-patched:temp"),
		'-t', 'tensorworks/autosdk-wine:{}'.format('temp'),
		ue_build_dir
		])
else:
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

# bindmount UE source into that image and run UBT with the provided args
prefixed_ubtargs = ['-{}'.format(ubtarg) for ubtarg in args.ubtargs]

if args.ue_source != '':
	Utility.run([
		'docker', 'run', '--rm', '-t',
		'-v', '{}:/home/nonroot/.local/share/wineprefixes/prefix/drive_c/UE'.format(args.ue_source),
		'tensorworks/autosdk-wine:{}'.format('temp'),
		'wine', './UE/Engine/Build/BatchFiles/RunUBT.bat',
		] + prefixed_ubtargs)