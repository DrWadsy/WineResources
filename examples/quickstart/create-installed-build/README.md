# Create Installed Build example

This directory contains a script for building the Unreal Engine inside a [Wine and AutoSDK enabled container](../autosdk/) under Linux.


## Contents

- [Prerequisites](#prerequisites)
- [Building the Wine and AutoSDK enabled base images](#building-the-wine-and-autosdk-enabled-base-images)
- [Building the Unreal Engine](#building-the-unreal-engine)
  - [Wrapping the Installed Build](#wrapping-the-installed-build)


## Prerequisites

- Unreal Engine Source Code [downloaded from here](https://github.com/EpicGames/UnrealEngine/)
- [Docker Engine](https://docs.docker.com/engine/install/) version 23.0.0 or newer
- [Python](https://www.python.org/) 3.7 or newer


## Building the Wine and AutoSDK enabled base images

The scripts in this folder will automatically check that the Wine and AutoSDK enabled base images exist, and will build them for you if not. If you wish to build them manually then simply follow the instructions in the [README for the repository's top-level build directory](../../../build/README.md) to build a base image containing Epic's patched version of Wine, and the instructions in the [README for the AutoSDK example](../autosdk/README.md) to build an image also containing the AutoSDK components required by your version of the Unreal Engine. Once these builds complete, the Wine base image will be available with the tag `epicgames/wine-patched:10.20` and the AutoSDK enabled image will be available with the tag `epicgames/autosdk-wine:<VERSION>`, where `<VERSION>` is the version of Unreal Engine provided.


## Building the Unreal Engine

> [!NOTE]
> This script will only run under Linux, due to interactions between Wine and bind-mounted volumes on Windows and MacOS platforms.

Run the wrapper script, passing in the path to the root of the Unreal Engine source (the folder conatining the `Engine` folder):

- `./compile.sh </path/to/UE/source>`

The wrapper script will run the Python build script itself. The Python build script will run the appropriate AutoSDK enabled container, with the Unreal Engine source bind-mounted in. The script will then build the Engine, producing an installed Build which can be used under Windows, or in either the [wrap installed build](../wrap-installed-build/) or [package project](../package-project/) scripts.

Once the build completes, the Installed Build will be available at `</path/to/UE/source>/LocalBuilds/Engine/Windows`

### Wrapping the Installed Build
If you want to wrap the Installed Build in a container you can either run the [wrap installed build](../wrap-installed-build/) manually, or you can provide the optional `--wrap` flag at the command line:
- `./compile.sh </path/to/UE/source> --wrap`