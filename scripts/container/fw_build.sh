#!/usr/bin/env sh
set -ex

TMP_VAR=${MPY_PORT:?"MPY_PORT is not set"}
TMP_VAR=${MPY_BOARD:?"MPY_BOARD is not set"}
TMP_VAR=${FIRMWARE_DEST:?"FIRMWARE_DEST is not set"}
TMP_VAR=${PROJECT_ROOT:?"PROJECT_ROOT is not set"}


echo "Firmware destination: $FIRMWARE_DEST"
echo "Building firmware for ${MPY_PORT} (${MPY_BOARD})"
mkdir -p ${FIRMWARE_DEST}

cd ${PROJECT_ROOT}/ports/${MPY_PORT}

if [ -z "${FROZEN_MANIFEST}" ]; then
    EXTRA_MAKE_OPTS=""
else
    echo "Using frozen manifest: ${FROZEN_MANIFEST}"
    EXTRA_MAKE_OPTS="FROZEN_MANIFEST=${FROZEN_MANIFEST}"
fi
echo "Using extra make options: ${EXTRA_MAKE_OPTS}"

if [ -z "${APP_ROOT}" ]; then
    BUILD_META_OPTS=""
else
    echo "Using app root: ${APP_ROOT}"
    BUILD_META_OPTS="--src-dir ${APP_ROOT}"
fi
echo "Build metadata options: ${BUILD_META_OPTS}"


make-with-opts BOARD=${MPY_BOARD} ${EXTRA_MAKE_OPTS}
cp build-${MPY_BOARD}/firmware.* ${FIRMWARE_DEST}/
write_build_metadata.py --mpy-root ${PROJECT_ROOT} ${BUILD_META_OPTS} ${FIRMWARE_DEST}/build_metadata.json

echo "Firmware build complete"

# Run any additional commands passed to the script
if [ $# -gt 0 ]; then
    echo "Running additional commands: $@"
    "$@"
fi
