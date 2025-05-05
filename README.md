# micropython-builder

Docker images for [MicroPython] development and compilation


## Links

|   |   |
|---|---|
| Source Code | https://github.com/MansfieldTX-MattR/micropython-builder |
| Docker Hub | https://hub.docker.com/r/mattrmansfieldtx/micropython-builder |




## Image Variants

Images are built and tagged according to the [port] they are intended for.
At this time, the following ports are available:


| Port      | Description                                 | Tags                                        |
|-----------|---------------------------------------------|---------------------------------------------|
| `unix`    | The base image for all other ports.         | [latest-unix], [1.25-unix], [1.25.0-unix]   |
| `rp2`     | Image for RP2xxx-based boards.              | [latest-rp2], [1.25-rp2], [1.25.0-rp2]      |


All version tags are derived from the releases/tags of the [MicroPython repository] itself.


## Building Firmware


Configuration for the build is done through the following environment variables:

- `MPY_BOARD`
  - The [board] to build for. This is required.
- `FIRMWARE_DEST`
  - The directory on the container to place the firmware files in.
    The default is `${HOME}/firmware` (or specifically, `/home/app/firmware`).
- `EXTRA_BUILD_META`
  - Any extra metadata to be added to the [build metadata](#build-metadata) file.
    If given, this should be formatted as `key1=value1,key2=value2,...`.
- `FROZEN_MANIFEST`
  - (Optional) The path to a [manifest file] to add as frozen bytecode (embedded in the firmware).
    The `manifest.py` file and any files it references must exist on the container.


### Examples

A helper script is provided in this repository to build firmware and as a usage example
(see [scripts/build_firmware.py](scripts/build_firmware.py)).
If not using the helper script, you can build firmware by running the following:

```bash
# Assuming the local destination is `./firmware`
mkdir -p firmware
docker run --rm \
    --mount type=bind,source=$(pwd)/firmware,target=/home/app/firmware \
    -e FIRMWARE_DEST=/home/app/firmware \
    -e MPY_BOARD=YOUR_BOARD \
    -e EXTRA_BUILD_META=key1=value1,key2=value2 \
    mattrmansfieldtx/micropython-builder:latest-rp2
```


If building with a [manifest file]:

```bash
# Assuming the local destination is `./firmware` and the source files are in `./src`
mkdir -p firmware
docker run --rm \
    --mount type=bind,source=$(pwd)/firmware,target=/home/app/firmware \
    --mount type=bind,source=$(pwd)/src,target=/home/app/src \
    -e FIRMWARE_DEST=/home/app/firmware \
    -e MPY_BOARD=YOUR_BOARD \
    -e FROZEN_MANIFEST=/home/app/src/manifest.py \
    mattrmansfieldtx/micropython-builder:latest-rp2
```


### Build Metadata

After a successful build, a `build_metadata.json` file will be created in the `FIRMWARE_DEST` directory along with the firmware binaries.
It contains the following information:

```json
{
    "mpy_commit": "abcdefg",
    "file_checksum": "1234567890abcdef",
    "file_checksums": {
        "src/file1.py": "1234567890abcdef",
        "src/file2.py": "1234567890abcdef"
    }
}
```

- `mpy_commit`
  - The commit hash of the [MicroPython Repository] used to build the firmware.
- `file_checksum`
  - The SHA-1 hash of all Python files in the source directory.
    The algorithm used to calculate the combined checksum can be found in the
    [write_build_metadata.py](scripts/container/write_build_metadata.py) script in this repository.
    **NOTE**: This is only available for [frozen builds] and will be `null` otherwise.
- `file_checksums`
  - A dictionary of the SHA-1 hashes of each individual Python file in the source directory.
    **NOTE**: This is only available for [frozen builds] and will be an empty dictionary otherwise.

Any extra metadata specified in the `EXTRA_BUILD_META` environment variable will be added to this as top-level keys.



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project is not affiliated with or endorsed by the MicroPython project or its contributors.
The MicroPython project is licensed separately.
See the [MicroPython repository] for details.



[MicroPython]: https://micropython.org/
[MicroPython repository]: https://github.com/micropython/micropython
[port]: https://docs.micropython.org/en/latest/reference/glossary.html#term-port
[board]: https://docs.micropython.org/en/latest/reference/glossary.html#term-board
[frozen builds]: https://docs.micropython.org/en/latest/develop/optimizations.html#frozen-bytecode
[manifest file]: https://docs.micropython.org/en/latest/reference/manifest.html#manifest
[latest-unix]: https://hub.docker.com/r/mattrmansfieldtx/micropython-builder/tags?page=1&name=latest-unix
[1.25-unix]: https://hub.docker.com/r/mattrmansfieldtx/micropython-builder/tags?page=1&name=1.25-unix
[1.25.0-unix]: https://hub.docker.com/r/mattrmansfieldtx/micropython-builder/tags?page=1&name=1.25.0-unix
[latest-rp2]: https://hub.docker.com/r/mattrmansfieldtx/micropython-builder/tags?page=1&name=latest-rp2
[1.25-rp2]: https://hub.docker.com/r/mattrmansfieldtx/micropython-builder/tags?page=1&name=1.25-rp2
[1.25.0-rp2]: https://hub.docker.com/r/mattrmansfieldtx/micropython-builder/tags?page=1&name=1.25.0-rp2
