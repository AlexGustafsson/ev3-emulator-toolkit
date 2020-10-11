import logging
import inspect
from typing import List, Any

from qiling import Qiling
from qiling.os.posix import syscall
from qiling.os.posix.syscall.mman import ql_syscall_mmap, ql_syscall_mmap2

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s][%(module)s:%(lineno)d] %(message)s')

file_descriptors = {}

def hook_write(ql: Qiling, fd: int, buf, count: int) -> None:
    name = ql.os.file_des[fd].__class__.__name__
    log.info("Write to file: {}".format(name))
    syscall.ql_syscall_write(ql, fd, buf, count)

def hook_read(ql: Qiling, fd: int, buf, count: int) -> None:
    name = ql.os.file_des[fd].__class__.__name__
    log.info("Read file: {}".format(name))
    syscall.ql_syscall_read(ql, fd, buf, count)

def hook_open(ql: Qiling, filename_pointer: int, flags: int, mode) -> None:
    log.info("Got filename pointer: {}".format(filename_pointer))
    filename = ql.mem.string(filename_pointer)
    log.info("Open file: {}, flags: {:b}, mode: {:b}".format(filename, flags, mode))
    syscall.ql_syscall_open(ql, filename, flags, mode)

def hook_close(ql: Qiling, fd: int) -> None:
    log.info("Close file: {}".format(fd))
    syscall.ql_syscall_close(ql, filename, flags, mode)

def hook_exit(ql: Qiling, error_code: int) -> None:
    log.info("Exiting. Code: {}".format(error_code))

def hook_invalid_memory(ql: Qiling, access, address, size, value) -> None:
    log.info("Got invalid memory address. Access: {}, address: {}, size: {}, value: {}".format(access, address, size, value))
    # ql.mem.map(address & ~0xfff, 0x1000)
    # ql.mem.write(address & ~0xfff, b'Q' * 0x1000)

def syscall_hook(syscall: int) -> None:
    def handle(ql: Qiling, arg0: Any, arg1: Any, arg2: Any, arg3: Any, arg4: Any, arg5: Any) -> None:
        hook = hooks[syscall]
        signature = inspect.signature(hook)
        args = [arg0, arg1, arg2, arg3, arg4, arg5][1:len(signature.parameters)]
        hook(ql, *args)

    return handle

hooks = {
    0x01: hook_exit,
    0x03: hook_read,
    0x04: hook_write,
    0x05: hook_open,
    0x06: hook_close
}

def sandbox(path: str, args: List[str], rootfs: str) -> None:
    options = {
        "filename": [path, *args],
        "rootfs": rootfs,
        "env": None,
        "shellcoder": None,
        "ostype": "Linux",
        "archtype": "arm_thumb",
        # "archtype": "arm",
        "bigendian": False,
        "output": "debug",
        "verbose": 1,
        "profile": None,
        "console": True,
        "log_dir": None,
        "log_split": None,
        "append": None,
        "libcache": False,
        "stdin": 0,
        "stdout": 0,
        "stderr": 0
    }
    ql = Qiling(**options)
    for syscall, hook in hooks.items():
        ql.set_syscall(syscall, syscall_hook(syscall))
    ql.hook_mem_invalid(hook_invalid_memory)
    ql.debugger = ":9999"
    ql.run()

if __name__ == "__main__":
    sandbox("../examples/example.elf", [], "./rootfs")
