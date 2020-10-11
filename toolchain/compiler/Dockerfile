# A Dockerfile wrapping the arm cross-platform toolchain
# Build with: docker build -t ev3-emulator-toolkit/toolchain .

FROM debian:buster-slim as builder

RUN apt-get update && apt-get install -y git bzip2 wget rename && rm -rf /var/lib/apt/lists/*

# Releases and info are available here:
# https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm
# https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads
RUN wget -qO- https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2020q2/gcc-arm-none-eabi-9-2020-q2-update-x86_64-linux.tar.bz2 | tar -xj
RUN rename -v -e 's/\/arm-none-eabi-/\//' /gcc-arm-none-eabi-9-2020-q2-update/bin/*

FROM debian:buster-slim

COPY --from=builder /gcc-arm-none-eabi-9-2020-q2-update/bin /bin
COPY --from=builder /gcc-arm-none-eabi-9-2020-q2-update/lib /lib/gcc

ENTRYPOINT ["sh", "-c"]
