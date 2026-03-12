ARG BASE_IMAGE=epicgames/wine-patched:10.20
FROM ${BASE_IMAGE} AS structure

ARG MAJOR_VERSION=17
ARG MSVC_VERSION=17.14
ARG SDK_VERSION=10.0.26100
ARG PACKAGES=''

# Install our required system packages
USER root
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
	apt-get update && \
	apt-get install -y --no-install-recommends \
		git \
		msitools \
		python3

# Clone the msvc-wine repository
USER nonroot
RUN git clone --depth=1 'https://github.com/mstorsjo/msvc-wine.git' /tmp/msvc-wine
WORKDIR /tmp/msvc-wine

# Install the requested Visual Studio components/workloads
RUN export VSDOWNLOAD='./vsdownload.py --cache ./cache --accept-license --skip-patch' && \
	if [ "$PACKAGES" != '' ]; then \
		$VSDOWNLOAD --dest ./downloaded $PACKAGES ; \
	else \
		export VERSION_ARGS='--major $MAJOR_VERSION --msvc-version $MSVC_VERSION --sdk-version $SDK_VERSION' && \
		$VSDOWNLOAD --dest ./downloaded $VERSION_ARGS && \
		$VSDOWNLOAD --dest ./downloaded-llvm --major $MAJOR_VERSION && \
		$VSDOWNLOAD --dest ./downloaded $VERSION_ARGS Microsoft.Net.Component.4.6.2.SDK; \
	fi

# Create the AutoSDK directory structure
ENV AUTOSDK_DIR=/tmp/AutoSDK/HostWin64/Win64
RUN mkdir -p "$AUTOSDK_DIR"
RUN mkdir -p "$AUTOSDK_DIR/DIA SDK"

# Move the files for the Windows SDK into the AutoSDK structure
RUN mv '/tmp/msvc-wine/downloaded/Windows Kits' "$AUTOSDK_DIR/Windows Kits"

# Move the files for LLVM into the AutoSDK structure
RUN if [ "$PACKAGES" != '' ]; then \
		mv '/tmp/msvc-wine/downloaded/VC/Tools/Llvm' "$AUTOSDK_DIR/LLVM"; \
	else \
		mv '/tmp/msvc-wine/downloaded-llvm/VC/Tools/Llvm' "$AUTOSDK_DIR/LLVM"; \
	fi

# Move the directories for MSVC and the DIA SDK into the AutoSDK structure
RUN if [ "$MAJOR_VERSION" = '16' ]; then \
		export VS_VERSION='VS2019'; \
	elif [ "$MAJOR_VERSION" = '17' ]; then \
		export VS_VERSION='VS2022'; \
	elif [ "$MAJOR_VERSION" = '18' ]; then \
		export VS_VERSION='VS2026'; \
	else \
		echo 'Error: a valid SDK version must be specified!'; \
		exit 1; \
	fi && \
	mv '/tmp/msvc-wine/downloaded/VC/Tools/MSVC' "$AUTOSDK_DIR/$VS_VERSION" && \
	mv '/tmp/msvc-wine/downloaded/DIA SDK' "$AUTOSDK_DIR/DIA SDK/$VS_VERSION"

# Extract the files for the .NET Framework SDK and move them into the AutoSDK structure
RUN cd /tmp/msvc-wine/cache/Microsoft.Net.4.6.2.SDK-4.6.1590.5 && \
	msiextract ./sdk_tools462.msi && \
	mv './Program Files/Windows Kits/NETFXSDK' "$AUTOSDK_DIR/Windows Kits/NETFXSDK"

# Locate the Windows SDK installer executable
RUN FILE=`find ./cache/ -iname winsdksetup.exe -type f` && \
	cp "$FILE" /tmp/winsdksetup.exe

# Extract the Debugging Tools for Windows installer MSI from the Windows SDK installer executable
RUN cd /tmp && \
	wine winsdksetup.exe /layout ./winsdk_extracted /quiet /ceip off /features OptionID.WindowsDesktopDebuggers && \
	mv /tmp/winsdk_extracted/Installers /tmp/DebugTools

# Extract the files for the Debugging Tools for Windows and copy them into the AutoSDK structure
# (Note that we copy here rather than move, so we can merge the directory trees)
RUN cd /tmp/DebugTools && \
	msiextract './X64 Debuggers And Tools-x64_en-us.msi' && \
	cd './Windows Kits' && \
	cp -R * "$AUTOSDK_DIR/Windows Kits/"

# Copy the assembled AutoSDK files into a clean version of our Wine base image
FROM ${BASE_IMAGE}
COPY --from=structure --chown=nonroot:nonroot /tmp/AutoSDK ${WINEPREFIX}/drive_c/AutoSDK

ENV UE_SDKS_ROOT=C:/AutoSDK
ENV WINEDEBUG=-all
