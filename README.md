<p align="center">
  <img src=".github/screenshot.png">
</p>
<p align="center">
  <i>A very early preview of an example application built around this toolkit.</i>
</p>

# EV3 Emulator Toolkit
### An effort to provide the necessary tools to build emulated and simulated EV3 experiences
***

## Project goal

The [LEGO Mindstorms EV3](https://en.wikipedia.org/wiki/Lego_Mindstorms_EV3) is an approachable platform for building robots and more. It is widely used in middle school, high school and universities as a way to onboard students in systems thinking, programming and robotics. Unfortunately, the toolkit is expensive and for better or worse, a mostly physical experience. Due to the events of 2020 where physical tools were no longer always available, EV3 emulation became even more important. The emulation scene is however underdeveloped with obsolete programs, highly expensive licenses and very little, if any, open source software.

The goal of this project is to develop tools to interact with EV3 binaries and to emulate them in a modular fashion in order to include emulated EV3 experiences in game engines, programs and browser experiences.

The project utilizes the actively developed MakeCode of Microsoft (also known as [pxt](https://github.com/microsoft/pxt)) and more specifically, [pxt-ev3](https://github.com/microsoft/pxt-ev3) (which is available here: https://makecode.mindstorms.com). The MakeCode project features an interactive simulator, allows for block-based programming as well as a subset of JavaScript. It is open source and assembles programs for the EV3 directly in the browser.

Most of the code is written in Python. This was done for several reasons. It's a language many know, can understand or at least read - especially more advanced students who may come in with this project via the use of EV3 in academia. That makes it so that readers can understand the main concepts of working with UF2, the EV3 etc. to easily port functionality to their projects written in other languages. Python is also a very simple language to run on a lot of machines (given that no third-party dependencies are used). The portability and understandability of Python code is well in line with what this project is all about.

A non-goal for the project is to provide an accurate or usable virtual environment for simulation or emulation. The code and documentation is mostly meant as a knowledge base with proof of concepts for working with UF2 and EV3 simulation and emulation. The code is written in a way that no third-party libraries are used which should in theory simplify the process of porting the concepts.

## What's in the box

### Toolchain

#### Compiler toolchain

A dockerized ARM toolchain is available under `tools/toolchain`. The toolchain can be used to disassemble binaries (ELF) etc using the `toolchain.sh` script. The script takes care of mounting file parameters so that the user doesn't have to.

```bash
# Build the Docker image and tag it
docker build -t ev3-emulator-toolkit/toolchain -f ./tools/toolchain/Dockerfile ./tools/toolchain/
# Run an example objdump command - disassemble an example binary
./tools/toolchain/toolchain.sh objdump -disassemble ./examples/example.elf
# Run another example command - output symbols
./tools/toolchain/toolchain.sh readelf --syms --wide ./examples/example.elf
```

#### Firmware compilation toolchain

A dockerized toolchain for building the EV3's firmware is available under `tools/firmware`. The toolchain can be used to compile the firmware available here: https://github.com/mindboards/ev3sources.

```bash
# Build the Docker image and tag it
docker build -t ev3-emulator-toolkit/firmware -f ./tools/firmware/Dockerfile ./tools/firmware/
```

#### Firmware extraction

1. Download a firmware from the official site: https://education.lego.com/en-us/support/mindstorms-ev3/firmware-update (there's a download button at the bottom of the site)
2. Use `binwalk` to extract files
  * Docker: `docker run -v "$(pwd):/samples" cincan/binwalk --extract --matryoshka --directory /samples /samples/LME-EV3_Firmware_1.10E.bin`
  * Native: `binwalk --extract --matryoshka LME-EV3_Firmware_1.10E.bin`

Described in more detail in `documentation/firmware-extraction.md`.

### Toolkit for working with the EV3, UF2 files and PXT projects

#### UF2 and PXT project toolkit

MakeCode utilizes the [UF2 format](https://github.com/microsoft/uf2) to pack its projects. The Python 3 package in `toolkit/uf2` can be used to interact with the archives to, for example, extract the project binary file.

There are some quirks to Microsoft's implementation, such as how they handle project-related meta data as well as the project's source code. These quirks are handled in the `toolkit/pxt` package.

To extract all files, meta files and source code from a project created via MakeCode, run the following command:

```
python3 -m scripts.extract examples/example.uf2
```

This will create a directory `files` with the following content:

```
files/
└── Untitled
    ├── meta.json
    ├── root
    │   └── Projects
    │       ├── Untitled.elf
    │       └── Untitled.rbf
    ├── source
    │   ├── README.md
    │   ├── main.blocks
    │   ├── main.ts
    │   └── pxt.json
    ├── source-meta.json
    └── source.json
```

The `files/Untitled/root` directory contains the files extracted from the archive in their defined tree structure. The `.elf` file is a compiled file for running the code on an EV3 device. The `.rbf` file is a small bootstrap program to execute the `.elf` file.

The `files/Untitled/source` directory contains all the source files defined in the project.

The `meta.json` and `source-meta.json` files are related to the PXT implementation and how the source code is saved. The `source.json` file contains the source in both the block (XML) format as well as the TypeScript code.

#### EV3 emulation

Still in progress.

#### EV3 simulation

In `toolkit/ev3/simulation` there's code for simulating EV3 code execution. This is currently done by extracting the Blocks source code from the UF2 archive and interpreting it. The execution is based on a simulator (main "frontend"), a runtime for evaluating code and a parser for the source code.

One may run the simulation using `python3 -m tools.simulate ./examples/example.uf2`. This should yield output like so:

```
...
INFO:root:Extracting and parsing main source
INFO:root:Registered event handler for event 'pxt-on-start'
INFO:root:Triggered event 'pxt-on-start'
INFO:root:Invoking block: variables_set
DEBUG:root:Setting variable 'XBNlNv/U_9_L2$?I%KA(' to '10'
INFO:root:Invoking block: console_log
DEBUG:root:Logging Hello, World!
Hello, World!
INFO:root:Invoking block: setLights
DEBUG:root:Setting lights to color StatusLight.Orange
INFO:root:Invoking block: motorRun
DEBUG:root:Run motor 'motors.largeA' with speed 50
INFO:root:Invoking block: moodShow
DEBUG:root:Showing mood 'moods.neutral'
```

The short-term goal of the simulation is to be able to run the most common instructions available via the PXT EV3 project (makecode.mindstorms.com). As this runtime does not know about physics, motors, sensors etc. are currently not usable. The idea is to either expose a server which one can use via APIs to communicate with the runtime, transpile the runtime to C or the like for easy embedding in other projects or simply use the code as a reference for further simulation efforts where a virtual world can be used.

#### EV3 Simulation Server

Using the `scripts.simulation_server` script, one can start a PoC Socket IO server which holds the simulation (and runtime) of a specified MakeCode project file.

It can be used to host the runtime and connect other tools such as a web-driven frontend or Unity.

It can be run like so:

```bash
python3 -m scripts.simulation_server examples/button-events.uf2
```

A simulation client is also included. It can be used to connect to the server by running the following command:

```bash
python3 -m scripts.simulation_client
```

Example usage of the client:

```
> python3 -m scripts.simulation_client

================================================================================
This is a super simple and bare-bones simulation client.

* Enter an event to trigger, along with its parameters
* Press enter without any input to step once
* Enter a number and press enter to step multiple steps
* Press CTRL+C

Examples:
buttonEnter event="ButtonEvent.Pressed" button="brick.buttonEnter"
touchEvent event="ButtonEvent.Pressed" sensor="sensors.touch1"
10
<empty>

================================================================================


connected
Choice: buttonEnter event="ButtonEvent.Pressed" button="brick.buttonEnter"
```

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
