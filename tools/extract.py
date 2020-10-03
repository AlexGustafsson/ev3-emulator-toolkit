from uf2.uf2 import UF2

def main() -> None:
    # Read the archive from the first parameter
    uf2 = UF2.read(sys.argv[1])

    # Save all files
    files = uf2.extract_files()
    for filename, content in files.items():
        # path = os.path.join("./files/{}".format(meta["name"]), filename)
        path = os.path.join("./files/{}".format("a"), filename)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as file:
           file.write(content)

if __name__ == '__main__':
    main()
