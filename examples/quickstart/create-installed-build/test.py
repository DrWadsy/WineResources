#!/usr/bin/env python3
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

wrap_build_dir = Path('/mnt/2TBStorage/TW-WineResources-Fork/WineResources/examples/quickstart') / 'wrap-installed-build'

installed_build_dir = Path('/mnt/2TBStorage/UnrealEngine') / 'LocalBuilds' / 'Engine' / 'Windows'

files = os.listdir(installed_build_dir)

for file in files:
	try:
		shutil.move( installed_build_dir / file, wrap_build_dir / 'context' / 'UnrealEngine' / file)

	except Exception as e:
		print("Could not copy Installed Build artifacts to context folder for containerising: {}".format(e))
    
# for root, dirs, files in os.walk(installed_build_dir):
# 	relative_path = os.path.relpath(root, installed_build_dir)
# 	destination_path = wrap_build_dir / 'context' / 'UnrealEngine' / relative_path

# 	if not os.path.exists(destination_path):
# 		os.makedirs(destination_path)

# 	for file in files:
# 		try:
# 			shutil.move(Path(root) / file, destination_path / file)

# 		except Exception as e:
# 			print("Could not copy Installed Build artifacts to context folder for containerising: {}".format(e))