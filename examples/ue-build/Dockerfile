ARG BASE_IMAGE=epicgames/wine-patched:10.20

FROM ubuntu:latest AS gatherer

ARG MAJOR_VERSION=17
ARG MSVC_VERSION=17.14
ARG SDK_VERSION=10.0.26100
ARG PACKAGES=""

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
	apt-get update && \
	apt-get install -y --no-install-recommends \
		ca-certificates \
        git \
        msitools \
        python3

# get msvc-wine
RUN git clone https://github.com/mstorsjo/msvc-wine.git /home/ubuntu/msvc-wine

WORKDIR /home/ubuntu/msvc-wine

RUN if [ "$PACKAGES" != "" ]; then \
        ./vsdownload.py --dest ./downloaded --cache ./cache --accept-license --skip-patch $PACKAGES ; \
    else \
        ./vsdownload.py --dest ./downloaded --cache ./cache --accept-license --skip-patch --major $MAJOR_VERSION --msvc-version $MSVC_VERSION --sdk-version $SDK_VERSION && \
        ./vsdownload.py --dest ./downloaded-llvm --cache ./cache --accept-license --skip-patch --major $MAJOR_VERSION && \
        ./vsdownload.py --dest ./downloaded --cache ./cache --accept-license --skip-patch --major $MAJOR_VERSION --msvc-version $MSVC_VERSION --sdk-version $SDK_VERSION package Microsoft.Net.Component.4.6.2.SDK; \
    fi

# prepare winsdksetup for next stage
RUN file=`find ./cache/ -iname winsdksetup.exe -type f` && \
    cp $file /home/ubuntu/winsdksetup.exe

# extract netfxsdk files
RUN cd /home/ubuntu/msvc-wine/cache/Microsoft.Net.4.6.2.SDK-4.6.1590.5 && \
    msiextract ./sdk_tools462.msi && \
    mv "./Program Files/Windows Kits/NETFXSDK" /home/ubuntu/

# create AutoSDK folder structure
RUN mkdir -p /home/ubuntu/AutoSDK/HostWin64/Win64

# copy folders into the AutoSDK structure
WORKDIR /home/ubuntu/AutoSDK/HostWin64/Win64
RUN mv "/home/ubuntu/msvc-wine/downloaded/Windows Kits" "./Windows Kits" && \
    if [ "$PACKAGES" != "" ]; then \
        mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/Llvm" "./LLVM"; \
    else \
        mv "/home/ubuntu/msvc-wine/downloaded-llvm/VC/Tools/Llvm" "./LLVM"; \
    fi && \
    mv "/home/ubuntu/NETFXSDK" "./Windows Kits/" && \
    mkdir "./DIA SDK" && \
    if [ "$MAJOR_VERSION" = "16" ]; then \
        mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/MSVC" ./VS2019 && \
        mv "/home/ubuntu/msvc-wine/downloaded/DIA SDK" "./DIA SDK/VS2019" ; \
    elif [ "$MAJOR_VERSION" = "17" ]; then \
        mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/MSVC" ./VS2022 && \
        mv "/home/ubuntu/msvc-wine/downloaded/DIA SDK" "./DIA SDK/VS2022" ; \
    elif [ "$MAJOR_VERSION" = "18" ]; then \
        mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/MSVC" ./VS2026 && \
        mv "/home/ubuntu/msvc-wine/downloaded/DIA SDK" "./DIA SDK/VS2026" ; \
    else \
        echo "No valid sdk version specified"; \
    fi

FROM ${BASE_IMAGE} AS installer

WORKDIR /home/ubuntu/

# create AutoSDK folder structure
RUN mkdir -p /home/ubuntu/AutoSDK/HostWin64/Win64

# Get Debugging Tools for Windows
COPY --from=gatherer --chown=nonroot:nonroot ["/home/ubuntu/winsdksetup.exe", "./winsdksetup.exe"]
RUN wine winsdksetup.exe /layout ./temp /quiet /ceip off /features OptionID.WindowsDesktopDebuggers && \
    mv "./temp/Installers" "/home/ubuntu/DebugTools"

FROM ubuntu:latest AS debug_tools_grabber

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        msitools

WORKDIR /home/ubuntu/

# create AutoSDK folder structure
RUN mkdir -p /home/ubuntu/AutoSDK/HostWin64/Win64

# Extract Debugging Tools for Windows
COPY --from=installer --chown=nonroot:nonroot ["/home/ubuntu/DebugTools", "./DebugTools"]
WORKDIR /home/ubuntu/DebugTools
RUN msiextract ./X64\ Debuggers\ And\ Tools-x64_en-us.msi && \
    mv "./Windows Kits" "/home/ubuntu/AutoSDK/HostWin64/Win64/Windows Kits"

# Stage 3
FROM ${BASE_IMAGE}

WORKDIR $WINEPREFIX/drive_c
COPY --from=gatherer --chown=nonroot:nonroot ["/home/ubuntu/AutoSDK", "./AutoSDK"]
COPY --from=debug_tools_grabber --chown=nonroot:nonroot ["/home/ubuntu/AutoSDK", "./AutoSDK"]

ENV UE_SDKS_ROOT=C:/AutoSDK
ENV WINEDEBUG=-all