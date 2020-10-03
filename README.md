# EV3 Emulator Toolkit
### An effort to provide the necessary tools to build emulated EV3 experiences
***

## Project goal

The [LEGO Mindstorms EV3](https://en.wikipedia.org/wiki/Lego_Mindstorms_EV3) is an approachable platform for building robots and more. It is widely used in middle school, high school and universities as a way to onboard students in systems thinking, programming and robotics. Unfortunately, the toolkit is expensive and for better or worse, a mostly physical experience. Due to the events of 2020 where physical tools were no longer always available, EV3 emulation became even more important. The emulation scene is however underdeveloped with obsolete programs, highly expensive licenses and very little, if any, open source software.

The goal of this project is to develop tools to interact with EV3 binaries and to emulate them in a modular fashion in order to include emulated EV3 experiences in game engines, programs and browser experiences.

The project utilizes the actively developed MakeCode of Microsoft (also known as [pxt](https://github.com/microsoft/pxt)) and more specifically, [pxt-ev3](https://github.com/microsoft/pxt-ev3) (which is available here: https://makecode.mindstorms.com). The MakeCode project features an interactive simulator, allows for block-based programming as well as a subset of JavaScript. It is open source and assembles programs for the EV3 directly in the browser.

## What's in the box

### Compiler toolchain

A dockerized ARM toolchain is available under `tools/toolchain`. The toolchain can be used to disassemble binaries (ELF) etc using the `toolchain.sh` script. The script takes care of mounting file parameters so that the user doesn't have to.

```bash
# Build the Docker image and tag it
docker build -t ev3-emulator-toolkit/toolchain -f ./tools/toolchain/Dockerfile ./tools/toolchain/
# Run an example objdump command - disassemble an example binary
./tools/toolchain/toolchain.sh objdump -disassemble ./examples/example.elf
# Run another example command - output symbols
./tools/toolchain/toolchain.sh readelf --syms --wide ./examples/example.elf
```

### Firmware compilation toolchain

A dockerized toolchain for building the EV3's firmware is available under `tools/firmware`. The toolchain can be used to compile the firmware available here: https://github.com/mindboards/ev3sources.

```bash
# Build the Docker image and tag it
docker build -t ev3-emulator-toolkit/firmware -f ./tools/firmware/Dockerfile ./tools/firmware/
```

### Firmware extraction

1. Download a firmware from the official site: https://education.lego.com/en-us/support/mindstorms-ev3/firmware-update (there's a download button at the bottom of the site)
2. Use `binwalk` to extract files
  * Docker: `docker run -v "$(pwd):/samples" cincan/binwalk --extract --matryoshka --directory /samples /samples/LME-EV3_Firmware_1.10E.bin`
  * Native: `binwalk --extract --matryoshka LME-EV3_Firmware_1.10E.bin`

Described in more detail in `documentation/firmware-extraction.md`.

### UF2 toolchain

MakeCode utilizes the [UF2 format](https://github.com/microsoft/uf2) to pack its projects. The Python 3 package in `tools/uf2` can be used to interact with the archives to, for example, extract the project binary file.

```
python3 tools/extract.py examples/example.uf2
```

### EV3 emulation

Still in progress.

## Technical solutions

## Gathered information

Below is some information about EV3, ARM assembly etc. in no particular order.

* The EV3 CPU is 32-bit ARM9 (ARMv4T) processor, Texas Instrument AM1808 clocked at 300MHz
  * Datasheet: https://www.ti.com/lit/ds/symlink/am1808.pdf?ts=1601385746752
  * Instruction set: [32-bit ARM](https://en.wikipedia.org/wiki/ARM_architecture#32-bit_architecture) and [16-bit Thumb](https://en.wikipedia.org/wiki/ARM_architecture#Thumb)
* The EV3 has 64MB RAM and 16MB Flash
* The EV3's display is 178x128 pixels

* MakeCode downloads are packed [UF2 files](https://github.com/microsoft/uf2)
* MakeCode produces 16-bit Thumb code for the EV3, the final binary, however, seems to be regular ARM assembly
* MakeCode utilizes a small `.rbf` file to start a compiled ELF binary
  * Roughly `LEGOXm??0?>?Starting...??../prjs/BrkProg_SAVE/test.elfD??dH?H??0?>?Bye!?` where `test` is the name of the project
  * The paths are hard coded to be `../prjs/BrkProg_SAVE/name.elf` and `../prjs/BrkProg_SAVE/test.rbf` where `name` is the project's name with any instance of `lego` removed
* There are two files in the UF2 file, `Projects/name.elf` and `Projects/name.rbf` where `name` is the same as above
* MakeCode uses both a subset of JavaScript, Python and a visual block editor to compile to the same targets

* The ELF binary is assembled with GCC 2.4
* The following libraries are referenced in the built binaries:
  * /lib/ld-linux.so.3
  * libm.so.6
  * libpthread.so.0
  * libz.so.1
* The binary is built for Linux, ABI: 2.6.32, Kernel 2.6.33 RC4

Example ELF data from `./tools/toolchain/toolchain.sh readelf -h --wide ./examples/example.elf`:

```
ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF32
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           ARM
  Version:                           0x1
  Entry point address:               0x13610
  Start of program headers:          52 (bytes into file)
  Start of section headers:          34272 (bytes into file)
  Flags:                             0x5000202, Version5 EABI, soft-float ABI, <unknown>
  Size of this header:               52 (bytes)
  Size of program headers:           32 (bytes)
  Number of program headers:         8
  Size of section headers:           40 (bytes)
  Number of section headers:         28
  Section header string table index: 27
```

Example information from `file ./examples/example.elf`:

```
examples/example.elf: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.3, for GNU/Linux 2.6.32, BuildID[sha1]=999d8b506ecf0694280466708ea6a4c286c33771, stripped
```

Firmware development information is available here: https://www.lego.com/cdn/cs/set/assets/blt77bd61c3ac436ea3/LEGO_MINDSTORMS_EV3_Firmware_Developer_Kit.pdf. Below are interesting excerpts.

> MINDSTORMS EV3 is build around linux platform support packages (PSP) for AM1808 ARM9 controller. The specific packages used DaVinci-PSP-SDK-03.20.00.13 utilizes a LINUX kernel version 2.6.33 RC4. The actual used operating system is compiled using “GNU + CodeSourcery_G++ lite” compilers with various special settings.

The firmware is open source and available here: https://github.com/mindboards/ev3sources. Information on building the firmware is also available here: https://avr.icube.unistra.fr/en/index.php/Hacking_the_Lego_EV3.

## Debugging the emulator with GDB

1. Run Qiling in a Docker container: `docker run -it -v $(pwd):/var/data/ -p9999:9999 qilingframework/qiling`
2. Enter the ev3 directory and start the program: `cd /var/data/ev3 && python3 emulate.py`
3. Open GDB with the binary target specified: `gdb ./examples/example.elf`
4. Connect to the remote host: `target remote 192.168.99.110:9999`. Your container's IP will most likely be different

## Contributing

Any contribution is welcome. If you're not able to code it yourself, perhaps someone else is - so post an issue if there's anything on your mind.

### Development

Clone the repository:
```
git clone https://github.com/AlexGustafsson/ev3-emulator-toolkit && cd ev3-emulator-toolkit
```

## Trademarks

MICROSOFT, the Microsoft Logo, and MAKECODE are registered trademarks of Microsoft Corporation. They can only be used for the purposes described in and in accordance with Microsoft’s Trademark and Brand guidelines published at https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general.aspx. If the use is not covered in Microsoft’s published guidelines or you are not sure, please consult your legal counsel or the MakeCode team (makecode@microsoft.com).

LEGO, the LEGO logo, MINDSTORMS and the MINDSTORMS EV3 logo are trademarks and/ or copyrights of the LEGO Group. ©2018 The LEGO Group. All rights reserved.
