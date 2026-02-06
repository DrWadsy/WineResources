ARG BASE_IMAGE=epicgames/wine-patched:10.20

FROM ubuntu:latest AS gatherer

ARG MAJOR_VERSION=17
ARG MSVC_VERSION=17.14
ARG SDK_VERSION=10.0.26100

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

# # get sdks
# RUN ./vsdownload.py --dest ./downloaded --cache ./cache --accept-license --skip-patch --major $MAJOR_VERSION --msvc-version $MSVC_VERSION --sdk-version $SDK_VERSION
# # run without specific msvc version to also grab llvm 
# RUN ./vsdownload.py --dest ./downloaded-llvm --cache ./cache --accept-license --skip-patch --major $MAJOR_VERSION

# # get netfxsdk
# RUN ./vsdownload.py --dest ./downloaded --cache ./cache --accept-license --skip-patch --major $MAJOR_VERSION --msvc-version $MSVC_VERSION --sdk-version $SDK_VERSION package Microsoft.Net.Component.4.6.2.SDK

RUN ./vsdownload.py --dest ./downloaded --cache ./cache --accept-license --skip-patch Microsoft.Net.Component.4.6.2.SDK Microsoft.VisualStudio.Component.VC.14.44.17.14.x86.x64 Microsoft.VisualStudio.Component.VC.Llvm.Clang Microsoft.VisualStudio.Component.Windows11SDK.22621

# extract netfxsdk files
RUN cd /home/ubuntu/msvc-wine/cache/Microsoft.Net.4.6.2.SDK-4.6.1590.5 && \
    msiextract ./sdk_tools462.msi && \
    mv "./Program Files/Windows Kits/NETFXSDK" /home/ubuntu/

# create AutoSDK folder structure
RUN mkdir -p /home/ubuntu/AutoSDK/HostWin64/Win64

# copy folders into the AutoSDK structure
WORKDIR /home/ubuntu/AutoSDK/HostWin64/Win64
RUN mv "/home/ubuntu/msvc-wine/downloaded/DIA SDK" "./" && \
    mv "/home/ubuntu/msvc-wine/downloaded/Windows Kits" "./Windows Kits" && \
    mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/Llvm" "./LLVM" && \
    mv "/home/ubuntu/NETFXSDK" "./Windows Kits/" && \
    if [ "$MAJOR_VERSION" = "16" ]; then \
        mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/MSVC" ./VS2019 ; \
    elif [ "$MAJOR_VERSION" = "17" ]; then \
        mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/MSVC" ./VS2022 ; \
    elif [ "$MAJOR_VERSION" = "18" ]; then \
        mv "/home/ubuntu/msvc-wine/downloaded/VC/Tools/MSVC" ./VS2026 ; \
    else \
        echo "No valid sdk version specified"; \
    fi

# Stage 2

FROM ${BASE_IMAGE}

WORKDIR $WINEPREFIX/drive_c
COPY --from=gatherer --chown=nonroot:nonroot ["/home/ubuntu/AutoSDK", "./AutoSDK"]

ENV UE_SDKS_ROOT=C:/AutoSDK