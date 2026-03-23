# Wrapped Installed Build example

This directory contains a [Dockerfile](./context/Dockerfile) for building a container image that extends the [base image containing Epic's patched version of Wine and AutoSDK](../autosdk/) and adds the files for an Installed Build of Unreal Engine.


## Contents

- [Prerequisites](#prerequisites)
- [Building the Wine and AutoSDK enabled base images](#building-the-wine-and-autosdk-enabled-base-images)
- [Building the container image](#building-the-container-image)
    - [Copying the Installed Build files](#copying-the-installed-build-files)
    - [Running the build script](#running-the-build-script)


## Prerequisites

- Installed Build of the Unreal Engine, either:
  - Copied from a Windows machine
  - Built using the [create installed build script](../create-installed-build/)
- [Docker Engine](https://docs.docker.com/engine/install/) version 23.0.0 or newer
- [Python](https://www.python.org/) 3.7 or newer


## Building the Wine and AutoSDK enabled base images

The scripts in this folder will automatically check that the Wine and AutoSDK enabled base image exists, and will build it for you if not. If you wish to build it manually then simply follow the instructions in the [README for the AutoSDK example](../autosdk/README.md) to build a base image containing Epic's patched version of Wine and the AutoSDK components required by your version of the Unreal Engine. Once the build completes, the Wine base image will be available with the tag `epicgames/wine-patched:10.20` and the AutoSDK enabled image will be available with the tag `epicgames/autosdk-wine:<VERSION>`, where `<VERSION>` is the version of Unreal Engine provided.

## Building the container image

### Copying the Installed Build files

This example does not build Unreal Engine from source, but rather wraps an existing Installed Build that needs to be supplied by the user. You will either need a Windows machine to download or build an Installed Build, or you can use the [create installed build script](../create-installed-build/) on a Linux machine. Either way, once the files have been obtained then the container image itself can be built under Linux, macOS or Windows.

The recommended way to obtain an Installed Build under Windows is to install Unreal Engine via the Epic Games Launcher, by following these instructions: <https://dev.epicgames.com/documentation/en-us/unreal-engine/installing-unreal-engine>

Alternatively, you can create an Installed Build by building Unreal Engine from source, by following these instructions: <https://dev.epicgames.com/documentation/en-us/unreal-engine/create-an-installed-build-of-unreal-engine>

Once you have obtained the Installed Build files, copy them to the [context/UnrealEngine](./context/UnrealEngine/) subdirectory. If the files have been copied correctly then the Unreal Editor executable should exist at the path:

```
context/UnrealEngine/Engine/Binaries/Win64/UnrealEditor.exe
```

> [!WARNING]
> When copying the Installed Build files under Windows, you may encounter an error if any of the destination file paths exceed the [maximum path length limit](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation). To avoid this, either ensure the destination directory has a short path (e.g. by storing the local copy of this repository in the root of a drive, such as `C:\WineResources`), or follow Microsoft's [instructions to enable long path support](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?#enable-long-paths-in-windows-10-version-1607-and-later).

### Running the build script

Run the appropriate wrapper script depending on the operating system:

- Under Linux and macOS, run `./build.sh`
- Under Windows, run `.\build.bat`

The wrapper script will run the Python build script itself, using the appropriate commands for the operating system. The Python build script will verify that the Installed Build files have been copied to the correct location, and will then automatically detect the version of Unreal Engine that the files represent. The script will then build the container image.

Once the build completes, the container image will be available with the tag `epicgames/unreal-engine-<VERSION>:autosdk-wine`, where `<VERSION>` is the version of Unreal Engine that the container image was built for. The image can be used to package Unreal Engine projects, either manually of by using the [package project script](../package-project/).

> [!IMPORTANT]
> The Dockerfile step that copies the Installed Build files into the container image may take a long time to complete (i.e. over an hour on many systems, and potentially multiple hours under Windows when using Docker Desktop with WSL2). There is no output to indicate the progress of the copy operation, so it may appear to have frozen, but this is almost certainly not the case and you will simply need to wait for it to complete.
