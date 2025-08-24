from llvmlite import ir
from llvmlite import binding as llvm
import ctypes
import os
import sys
import tempfile
if os.name == "nt":
    import ctypes.wintypes as wintypes

class IRExecutor:
    """Executes LLVM IR code and returns the result."""

    def __init__(self):
        """Initialize the LLVM execution engine."""
        # Initialize LLVM
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # Create execution engine
        self.target = llvm.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine()
        self.engine = llvm.create_mcjit_compiler(llvm.parse_assembly(""), self.target_machine)

        # Set the data layout
        self.data_layout = self.target_machine.target_data
        llvm.set_option("", "--data-layout=" + str(self.data_layout))

        # Try to load C runtime and register common externals (printf/scanf)
        self.libc = None
        try:
            # Windows: msvcrt, else fall back to current process
            if os.name == "nt":
                self.libc = ctypes.cdll.msvcrt
            else:
                # Works on most Unix-like systems where libc is loaded
                self.libc = ctypes.CDLL(None)
        except Exception:
            self.libc = None

        # Register symbols so varargs calls resolve within MCJIT
        try:
            if self.libc is not None:
                try:
                    printf_addr = ctypes.cast(self.libc.printf, ctypes.c_void_p).value
                    if printf_addr:
                        llvm.add_symbol("printf", printf_addr)
                except Exception:
                    pass
                try:
                    scanf_addr = ctypes.cast(self.libc.scanf, ctypes.c_void_p).value
                    if scanf_addr:
                        llvm.add_symbol("scanf", scanf_addr)
                except Exception:
                    pass
        except Exception:
            # Non-fatal: execution may still work if the platform resolves symbols implicitly
            pass
    
    def execute(self, ir_code: str, stdin_data: str | bytes | None = None):
        """Execute LLVM IR code, capturing stdout and providing optional stdin.

        Args:
            ir_code: LLVM IR code to execute
            stdin_data: Optional string/bytes to feed to the program via stdin

        Returns:
            Tuple of (exit_code: int, stdout: str)
        """
        mod = None
        tmp_path = None
        saved_stdout_fd = None
        stdin_tmp_path = None
        saved_stdin_fd = None
        windows_redirect_used = False
        windows_stdin_redirect_used = False

        try:
            # Parse the IR code
            mod = llvm.parse_assembly(ir_code)
            mod.verify()

            # Set the data layout
            mod.data_layout = str(self.data_layout)

            # Add the module to the engine
            self.engine.add_module(mod)
            self.engine.finalize_object()

            # Get the main function
            main_addr = self.engine.get_function_address("main")
            if not main_addr:
                raise RuntimeError("No 'main' function found in the module")
            main_func = ctypes.CFUNCTYPE(ctypes.c_int)(main_addr)

            # Prepare stdout capture
            try:
                sys.stdout.flush()
            except Exception:
                pass
            try:
                if self.libc is not None:
                    self.libc.fflush(None)
            except Exception:
                pass

            fd, tmp_path = tempfile.mkstemp(prefix="jit_stdout_", suffix=".txt")
            os.close(fd)

            # Prepare stdin capture (provide data if any; use empty file to avoid blocking)
            fd_in, stdin_tmp_path = tempfile.mkstemp(prefix="jit_stdin_", suffix=".txt")
            os.close(fd_in)
            try:
                data_bytes = b""
                if stdin_data is not None:
                    if isinstance(stdin_data, str):
                        data_bytes = stdin_data.encode("utf-8")
                    elif isinstance(stdin_data, (bytes, bytearray)):
                        data_bytes = bytes(stdin_data)
                with open(stdin_tmp_path, "wb") as fin:
                    fin.write(data_bytes)
            except Exception:
                pass

            # Redirect stdout and stdin
            if os.name == "nt" and self.libc is not None:
                # Windows: redirect MSVCRT stdout using _open_osfhandle + _dup2
                try:
                    kernel32 = ctypes.windll.kernel32
                    GENERIC_WRITE = 0x40000000
                    GENERIC_READ = 0x80000000
                    FILE_SHARE_READ = 0x00000001
                    CREATE_ALWAYS = 2
                    OPEN_EXISTING = 3
                    FILE_ATTRIBUTE_NORMAL = 0x00000080
                    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

                    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                                     wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
                    kernel32.CreateFileW.restype = wintypes.HANDLE

                    hFile = kernel32.CreateFileW(tmp_path, GENERIC_WRITE, FILE_SHARE_READ, None,
                                                  CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, None)
                    if hFile and hFile != INVALID_HANDLE_VALUE:
                        _open_osfhandle = self.libc._open_osfhandle
                        _open_osfhandle.argtypes = [ctypes.c_void_p, ctypes.c_int]
                        _open_osfhandle.restype = ctypes.c_int

                        _dup = self.libc._dup
                        _dup.argtypes = [ctypes.c_int]
                        _dup.restype = ctypes.c_int

                        _dup2 = self.libc._dup2
                        _dup2.argtypes = [ctypes.c_int, ctypes.c_int]
                        _dup2.restype = ctypes.c_int

                        _close = self.libc._close
                        _close.argtypes = [ctypes.c_int]
                        _close.restype = ctypes.c_int

                        msvcrt_fd = _open_osfhandle(hFile, 0)
                        saved_stdout_fd = _dup(1)
                        if msvcrt_fd >= 0 and saved_stdout_fd >= 0:
                            if _dup2(msvcrt_fd, 1) == 0:
                                windows_redirect_used = True
                        # Don't close hFile here; closing msvcrt_fd will close the handle
                    else:
                        windows_redirect_used = False
                except Exception:
                    windows_redirect_used = False

                # Redirect stdin for MSVCRT
                try:
                    hIn = kernel32.CreateFileW(stdin_tmp_path, GENERIC_READ, FILE_SHARE_READ, None,
                                               OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
                    if hIn and hIn != INVALID_HANDLE_VALUE:
                        _open_osfhandle = self.libc._open_osfhandle
                        _open_osfhandle.argtypes = [ctypes.c_void_p, ctypes.c_int]
                        _open_osfhandle.restype = ctypes.c_int

                        _dup = self.libc._dup
                        _dup.argtypes = [ctypes.c_int]
                        _dup.restype = ctypes.c_int

                        _dup2 = self.libc._dup2
                        _dup2.argtypes = [ctypes.c_int, ctypes.c_int]
                        _dup2.restype = ctypes.c_int

                        msvcrt_in_fd = _open_osfhandle(hIn, 0)
                        saved_stdin_fd = _dup(0)
                        if msvcrt_in_fd >= 0 and saved_stdin_fd >= 0:
                            if _dup2(msvcrt_in_fd, 0) == 0:
                                windows_stdin_redirect_used = True
                    else:
                        windows_stdin_redirect_used = False
                except Exception:
                    windows_stdin_redirect_used = False

            if not windows_redirect_used:
                # POSIX-compatible dup2 fallback for stdout
                fd_stdout = 1
                saved_stdout_fd = os.dup(fd_stdout)
                cap_fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
                os.dup2(cap_fd, fd_stdout)
                os.close(cap_fd)

            if not windows_stdin_redirect_used:
                # POSIX-compatible stdin redirect
                fd_stdin = 0
                saved_stdin_fd = os.dup(fd_stdin)
                in_fd = os.open(stdin_tmp_path, os.O_RDONLY)
                os.dup2(in_fd, fd_stdin)
                os.close(in_fd)

            # Execute the main function
            exit_code = main_func()

            # Flush C stdio after execution to ensure buffers are written
            try:
                if self.libc is not None:
                    self.libc.fflush(None)
            except Exception:
                pass

            # Restore original stdout
            if windows_redirect_used and os.name == "nt" and self.libc is not None:
                try:
                    _dup2 = self.libc._dup2
                    _dup2.argtypes = [ctypes.c_int, ctypes.c_int]
                    _dup2.restype = ctypes.c_int
                    _close = self.libc._close
                    _close.argtypes = [ctypes.c_int]
                    _close.restype = ctypes.c_int
                    if saved_stdout_fd is not None and saved_stdout_fd >= 0:
                        _dup2(saved_stdout_fd, 1)
                        _close(saved_stdout_fd)
                        saved_stdout_fd = None
                except Exception:
                    pass
            else:
                if saved_stdout_fd is not None:
                    try:
                        os.dup2(saved_stdout_fd, 1)
                    finally:
                        os.close(saved_stdout_fd)
                        saved_stdout_fd = None

            # Restore original stdin
            if windows_stdin_redirect_used and os.name == "nt" and self.libc is not None:
                try:
                    _dup2 = self.libc._dup2
                    _dup2.argtypes = [ctypes.c_int, ctypes.c_int]
                    _dup2.restype = ctypes.c_int
                    _close = self.libc._close
                    _close.argtypes = [ctypes.c_int]
                    _close.restype = ctypes.c_int
                    if saved_stdin_fd is not None and saved_stdin_fd >= 0:
                        _dup2(saved_stdin_fd, 0)
                        _close(saved_stdin_fd)
                        saved_stdin_fd = None
                except Exception:
                    pass
            else:
                if saved_stdin_fd is not None:
                    try:
                        os.dup2(saved_stdin_fd, 0)
                    finally:
                        os.close(saved_stdin_fd)
                        saved_stdin_fd = None

            # Read captured output
            stdout_data = ""
            try:
                with open(tmp_path, "rb") as f:
                    stdout_data = f.read().decode("utf-8", errors="replace")
            finally:
                try:
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
                try:
                    if stdin_tmp_path and os.path.exists(stdin_tmp_path):
                        os.remove(stdin_tmp_path)
                except Exception:
                    pass

            return exit_code, stdout_data

        except Exception as e:
            raise RuntimeError(f"Failed to execute LLVM IR: {str(e)}")
        finally:
            if mod is not None:
                try:
                    self.engine.remove_module(mod)
                except Exception:
                    pass
            # Best-effort restoration in case of early exceptions
            try:
                if os.name == "nt" and self.libc is not None:
                    _dup2 = getattr(self.libc, "_dup2", None)
                    _close = getattr(self.libc, "_close", None)
                    if _dup2 and saved_stdout_fd is not None and saved_stdout_fd >= 0:
                        _dup2(saved_stdout_fd, 1)
                        if _close:
                            _close(saved_stdout_fd)
                        saved_stdout_fd = None
                    if _dup2 and saved_stdin_fd is not None and saved_stdin_fd >= 0:
                        _dup2(saved_stdin_fd, 0)
                        if _close:
                            _close(saved_stdin_fd)
                        saved_stdin_fd = None
                else:
                    if saved_stdout_fd is not None:
                        try:
                            os.dup2(saved_stdout_fd, 1)
                        finally:
                            os.close(saved_stdout_fd)
                        saved_stdout_fd = None
                    if saved_stdin_fd is not None:
                        try:
                            os.dup2(saved_stdin_fd, 0)
                        finally:
                            os.close(saved_stdin_fd)
                        saved_stdin_fd = None
            except Exception:
                pass
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            try:
                if stdin_tmp_path and os.path.exists(stdin_tmp_path):
                    os.remove(stdin_tmp_path)
            except Exception:
                pass