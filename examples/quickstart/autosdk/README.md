# AutoSDK enabled image example

This directory contains a [Dockerfile](./context/Dockerfile) for building a container image that extends the [base image containing Epic's patched version of Wine](../../../build/) and adds the files needed for building the Unreal Engine, and packaging Unreal Engine projects.


## Contents

- [Prerequisites](#prerequisites)
- [Building the Wine base image](#building-the-wine-base-image)
- [Building the container image](#building-the-container-image)


## Prerequisites

- Unreal Engine Source Code [downloaded from here](https://github.com/EpicGames/UnrealEngine/)
- [Docker Engine](https://docs.docker.com/engine/install/) version 23.0.0 or newer
- [Python](https://www.python.org/) 3.7 or newer

> [!NOTE]
> The container image built by these example files does not contain any part of the Unreal Engine, but the source of the Engine is required for the script to determine the required AutoSDK components.


## Building the Wine base image

The scripts in this folder will automatically check that the Wine base image exists, and will build it for you if not. If you wish to build it manually then simply follow the instructions in the [README for the repository's top-level build directory](../../../build/README.md) to build a base image containing Epic's patched version of Wine. Once the build completes, the base image will be available with the tag `epicgames/wine-patched:10.20`.


## Building the container image

Run the appropriate wrapper script depending on the operating system, passing in the path to the root of the Unreal Engine source (the folder conatining the `Engine` folder):

- Under Linux and macOS, run `./assemble.sh </path/to/UE/source>`
- Under Windows, run `.\assemble.bat <path:\to\UE\source>`

The wrapper script will run the Python build script itself, using the appropriate commands for the operating system. The Python build script will automatically determine which SDK components are required for the provided version of the Engine. The script will then build the container image.

Once the build completes, the container image will be available with the tag `epicgames/autosdk-wine:<VERSION>`, where `<VERSION>` is the version of Unreal Engine that the container image was built for. The image can be used either to build the given version of the Unreal Engine, or to package Unreal Engine projects for that version.
