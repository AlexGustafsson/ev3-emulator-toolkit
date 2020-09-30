from uf2.uf2 import UF2

def main() -> None:
    uf2 = UF2.read("./example.uf2")
    # for block in uf2.blocks:
    #     with open("./blocks/{}.uf2".format(block.block_number), "wb") as file:
    #         file.write(block.pack())
    # with open("./binary.elf", "wb") as file:
    #     file.write(uf2.extract_binary())
    files = uf2.extract_files()
    for filename, content in files.items():
        with open("./files/{}".format(filename.replace("/", "_")), "wb") as file:
            file.write(content)

if __name__ == '__main__':
    main()
