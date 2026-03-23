# Package Project example

This directory contains a script for packaging an Unreal Engine project using an Installed Build inside a [Wine and AutoSDK enabled container](../autosdk/) under Linux. The installed Build can either be stored on your machine, or [wrapped in a container](../wrap-installed-build/).


## Contents

- [Prerequisites](#prerequisites)
- [Building the Wine and AutoSDK enabled base images](#building-the-wine-and-autosdk-enabled-base-images)
- [Packaging the project](#packaging-the-project)


## Prerequisites

- Installed Build of the Unreal Engine, either
  - stored on your machine
  - [wrapped in a container](../wrap-installed-build/)
- Compatible UE project
- [Docker Engine](https://docs.docker.com/engine/install/) version 23.0.0 or newer
- [Python](https://www.python.org/) 3.7 or newer


## Building the Wine and AutoSDK enabled base images

The scripts in this folder will automatically check that the Wine and AutoSDK enabled base images exist, and will build them for you if not. If you wish to build them manually then simply follow the instructions in the [README for the repository's top-level build directory](../../../build/README.md) to build a base image containing Epic's patched version of Wine, and the instructions in the [README for the AutoSDK example](../autosdk/README.md) to build an image also containing the AutoSDK components required by your version of the Unreal Engine. Once these builds complete, the Wine base image will be available with the tag `epicgames/wine-patched:10.20` and the AutoSDK enabled image will be available with the tag `epicgames/autosdk-wine:<VERSION>`, where `<VERSION>` is the version of Unreal Engine provided.


## Packaging the project

> [!NOTE]
> This script will only run under Linux, due to interactions between Wine and bind-mounted volumes on Windows and MacOS platforms.

Run the wrapper script, passing in:
- the `project` flag, with the path to the uproject file you wish to build with
- EITHER:
  - the `--engine` flag, with the path to the root of the Unreal Engine source (the folder conatining the `Engine` folder)
  - the `--image` flag, with the image tag for your containerised Unreal Image source

- `./package.sh --engine </path/to/UE/source> --project </path/to/.uproject/file>`
- `./package.sh -- engine </path/to/UE/source> --image <inatslled-build:image-tag>`

The wrapper script will run the Python build script itself. If the Installed Build files are provided then the Python build script will run the appropriate AutoSDK enabled container, with both the Unreal Engine source and the project folder bind-mounted in. If an image containing an Installed Build is provided then the Python build script will run that image in a container with the project folder bind-mounted in. Either way the script will package the project in place, using the provided Installed Build.

Once the build completes, the packaged project will be available at `</project/path>/dist/Windows`.
