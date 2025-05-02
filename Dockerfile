FROM alpine:latest AS base

# Install core dependencies
RUN apk add --no-cache \
    alpine-sdk \
    bash \
    curl \
    git \
    libusb-dev \
    libffi-dev \
    python3 \
    shadow


# Add a helper script for parallel make
COPY --chmod=755 <<EOT /usr/local/bin/make-with-opts
#!/usr/bin/env sh
set -ex
if which nproc > /dev/null; then
    NCPU="\$(nproc)"
else
    NCPU="\$(sysctl -n hw.ncpu)"
fi
make -j \$NCPU "\$@"
EOT


COPY --chmod=755 ./scripts/container/write_build_metadata.py /usr/local/bin/
COPY --chmod=755 ./scripts/container/fw_build.sh /usr/local/bin/

ENV HOME=/home/app

RUN useradd -ms /bin/sh -u 1001 app
RUN mkdir -p ${HOME}
RUN chown -R app:app ${HOME}

USER app
WORKDIR ${HOME}

ARG MICROPYTHON_VERSION="master"
ARG MICROPYTHON_REPO="https://github.com/micropython/micropython.git"
ENV MICROPYTHON_VERSION=${MICROPYTHON_VERSION}
ENV MICROPYTHON_REPO=${MICROPYTHON_REPO}
LABEL micropython_version=${MICROPYTHON_VERSION}
LABEL micropython_repo=${MICROPYTHON_REPO}

ENV PROJECT_ROOT=${HOME}/micropython

# Clone the repository
RUN git clone --depth 1 --branch ${MICROPYTHON_VERSION} --single-branch ${MICROPYTHON_REPO} ${PROJECT_ROOT}
WORKDIR ${PROJECT_ROOT}


ENV PATH="${PATH}:${PROJECT_ROOT}/mpy-cross/build:${PROJECT_ROOT}/tools"

# Build the unix port
SHELL ["/bin/bash", "-c"]
RUN source tools/ci.sh && ci_unix_standard_build

FROM base AS unix



FROM base AS unix_tests

# Test
CMD ["/bin/bash", "-c", "source tools/ci.sh && ci_unix_standard_run_tests"]


FROM base AS rp2_base

ENV MPY_PORT='rp2'

# Install rp2 dependencies
USER root
RUN apk add --no-cache \
    cmake \
    g++-arm-none-eabi \
    gcc-arm-none-eabi \
    gcompat \
    libc6-compat \
    libstdc++ \
    newlib-arm-none-eabi

USER app


# Build picotool
ENV PICOTOOL_SETUP_ROOT=${HOME}/picotool-setup
ENV PICO_SDK_PATH=${PROJECT_ROOT}/lib/pico-sdk
WORKDIR ${PROJECT_ROOT}
RUN git submodule update --init --depth 1 lib/mbedtls
RUN git submodule update --init --depth 1 lib/pico-sdk
RUN git submodule update --init --depth 1 lib/tinyusb
RUN git clone --depth 1 --single-branch https://github.com/raspberrypi/picotool.git ${PICOTOOL_SETUP_ROOT}/picotool
RUN mkdir -p ${PICOTOOL_SETUP_ROOT}/picotool/build
WORKDIR ${PICOTOOL_SETUP_ROOT}/picotool/build
RUN cmake -DCMAKE_INSTALL_PREFIX=~/.local -DPICO_SDK_PATH=${PICO_SDK_PATH} ..
RUN make-with-opts
RUN make install
ENV PATH="${PATH}:${HOME}/.local/bin"
RUN echo "PATH \$PATH"
RUN picotool version

WORKDIR ${PROJECT_ROOT}


FROM rp2_base AS rp2

# Setup rp2 submodules
RUN make-with-opts -C mpy-cross
RUN make-with-opts -C ports/${MPY_PORT} submodules

RUN <<EOT bash
set -ex
cd ${PROJECT_ROOT}/ports/${MPY_PORT}/boards
for dir in *; do
    if [ -d "\$dir" ]; then
        make-with-opts -C ../ BOARD=\$dir submodules
    fi
done
EOT


ENV FIRMWARE_DEST="${HOME}/firmware"

ENTRYPOINT ["fw_build.sh"]
