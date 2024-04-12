# ruff: noqa
r"""Wrapper for rfbclient.h

Generated with:
/home/lhebendanz/Projects/ctypesgen/run.py -l libvncclient.so /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h -o /home/lhebendanz/Projects/clan-core/pkgs/clan-vm-manager/tests/helpers/libvncclient.py

Do not modify this file.
"""

__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import sys
from ctypes import *  # noqa: F403

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types


class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):
    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function:
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value


# End preamble

_libs = {}
_libdirs = []

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import ctypes
import ctypes.util
import glob
import os.path
import platform
import re
import sys


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.CDLL(path, self.mode))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    f"Unknown calling convention '{calling_convention}' for function '{name}'"
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(
                        os.path.join(os.path.dirname(__file__), fmt % libname)
                    )

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except OSError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
            "LD_LIBRARY_PATH",
            "SHLIB_PATH",  # HP-UX
            "LIBPATH",  # OS/2, AIX
            "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

add_library_search_dirs([])

# Begin libraries
_libs["libvncclient.so"] = load_library("libvncclient.so")

# 1 libraries
# End libraries

# No modules

__uint8_t = c_ubyte  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types.h: 38

__uint16_t = c_ushort  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types.h: 40

__uint32_t = c_uint  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types.h: 42

__off_t = c_long  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types.h: 152

__off64_t = c_long  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types.h: 153

__time_t = c_long  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types.h: 160

__suseconds_t = c_long  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types.h: 162


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types/struct_FILE.h: 49
class struct__IO_FILE(Structure):
    pass


FILE = struct__IO_FILE  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types/FILE.h: 7


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types/struct_FILE.h: 36
class struct__IO_marker(Structure):
    pass


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types/struct_FILE.h: 37
class struct__IO_codecvt(Structure):
    pass


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types/struct_FILE.h: 38
class struct__IO_wide_data(Structure):
    pass


_IO_lock_t = None  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types/struct_FILE.h: 43

struct__IO_FILE.__slots__ = [
    "_flags",
    "_IO_read_ptr",
    "_IO_read_end",
    "_IO_read_base",
    "_IO_write_base",
    "_IO_write_ptr",
    "_IO_write_end",
    "_IO_buf_base",
    "_IO_buf_end",
    "_IO_save_base",
    "_IO_backup_base",
    "_IO_save_end",
    "_markers",
    "_chain",
    "_fileno",
    "_flags2",
    "_old_offset",
    "_cur_column",
    "_vtable_offset",
    "_shortbuf",
    "_lock",
    "_offset",
    "_codecvt",
    "_wide_data",
    "_freeres_list",
    "_freeres_buf",
    "__pad5",
    "_mode",
    "_unused2",
]
struct__IO_FILE._fields_ = [
    ("_flags", c_int),
    ("_IO_read_ptr", String),
    ("_IO_read_end", String),
    ("_IO_read_base", String),
    ("_IO_write_base", String),
    ("_IO_write_ptr", String),
    ("_IO_write_end", String),
    ("_IO_buf_base", String),
    ("_IO_buf_end", String),
    ("_IO_save_base", String),
    ("_IO_backup_base", String),
    ("_IO_save_end", String),
    ("_markers", POINTER(struct__IO_marker)),
    ("_chain", POINTER(struct__IO_FILE)),
    ("_fileno", c_int),
    ("_flags2", c_int),
    ("_old_offset", __off_t),
    ("_cur_column", c_ushort),
    ("_vtable_offset", c_char),
    ("_shortbuf", c_char * 1),
    ("_lock", POINTER(_IO_lock_t)),
    ("_offset", __off64_t),
    ("_codecvt", POINTER(struct__IO_codecvt)),
    ("_wide_data", POINTER(struct__IO_wide_data)),
    ("_freeres_list", POINTER(struct__IO_FILE)),
    ("_freeres_buf", POINTER(None)),
    ("__pad5", c_size_t),
    ("_mode", c_int),
    (
        "_unused2",
        c_char
        * int(((15 * sizeof(c_int)) - (4 * sizeof(POINTER(None)))) - sizeof(c_size_t)),
    ),
]


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/types/struct_timeval.h: 8
class struct_timeval(Structure):
    pass


struct_timeval.__slots__ = [
    "tv_sec",
    "tv_usec",
]
struct_timeval._fields_ = [
    ("tv_sec", __time_t),
    ("tv_usec", __suseconds_t),
]


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/thread-shared-types.h: 51
class struct___pthread_internal_list(Structure):
    pass


struct___pthread_internal_list.__slots__ = [
    "__prev",
    "__next",
]
struct___pthread_internal_list._fields_ = [
    ("__prev", POINTER(struct___pthread_internal_list)),
    ("__next", POINTER(struct___pthread_internal_list)),
]

__pthread_list_t = struct___pthread_internal_list  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/thread-shared-types.h: 55


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/struct_mutex.h: 22
class struct___pthread_mutex_s(Structure):
    pass


struct___pthread_mutex_s.__slots__ = [
    "__lock",
    "__count",
    "__owner",
    "__nusers",
    "__kind",
    "__spins",
    "__elision",
    "__list",
]
struct___pthread_mutex_s._fields_ = [
    ("__lock", c_int),
    ("__count", c_uint),
    ("__owner", c_int),
    ("__nusers", c_uint),
    ("__kind", c_int),
    ("__spins", c_short),
    ("__elision", c_short),
    ("__list", __pthread_list_t),
]


# /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/pthreadtypes.h: 72
class union_anon_14(Union):
    pass


union_anon_14.__slots__ = [
    "__data",
    "__size",
    "__align",
]
union_anon_14._fields_ = [
    ("__data", struct___pthread_mutex_s),
    ("__size", c_char * 40),
    ("__align", c_long),
]

pthread_mutex_t = union_anon_14  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/pthreadtypes.h: 72

uint8_t = __uint8_t  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/stdint-uintn.h: 24

uint16_t = __uint16_t  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/stdint-uintn.h: 25

uint32_t = __uint32_t  # /nix/store/6jk1d1m5j9d8gjyq79zqlgqqs9j3gcwn-glibc-2.38-44-dev/include/bits/stdint-uintn.h: 26

Byte = c_ubyte  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zconf.h: 393

uInt = c_uint  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zconf.h: 395

uLong = c_ulong  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zconf.h: 396

Bytef = Byte  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zconf.h: 402

voidpf = POINTER(
    None
)  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zconf.h: 411

alloc_func = CFUNCTYPE(
    UNCHECKED(voidpf), voidpf, uInt, uInt
)  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zlib.h: 81

free_func = CFUNCTYPE(
    UNCHECKED(None), voidpf, voidpf
)  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zlib.h: 82


# /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zlib.h: 84
class struct_internal_state(Structure):
    pass


# /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zlib.h: 106
class struct_z_stream_s(Structure):
    pass


struct_z_stream_s.__slots__ = [
    "next_in",
    "avail_in",
    "total_in",
    "next_out",
    "avail_out",
    "total_out",
    "msg",
    "state",
    "zalloc",
    "zfree",
    "opaque",
    "data_type",
    "adler",
    "reserved",
]
struct_z_stream_s._fields_ = [
    ("next_in", POINTER(Bytef)),
    ("avail_in", uInt),
    ("total_in", uLong),
    ("next_out", POINTER(Bytef)),
    ("avail_out", uInt),
    ("total_out", uLong),
    ("msg", String),
    ("state", POINTER(struct_internal_state)),
    ("zalloc", alloc_func),
    ("zfree", free_func),
    ("opaque", voidpf),
    ("data_type", c_int),
    ("adler", uLong),
    ("reserved", uLong),
]

z_stream = struct_z_stream_s  # /nix/store/6gbq1krsayq346c7lccn2lbpv74ljqwz-zlib-1.3.1-dev/include/zlib.h: 106

rfbBool = c_int8  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 108


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 152
class struct_anon_33(Structure):
    pass


struct_anon_33.__slots__ = [
    "x",
    "y",
    "w",
    "h",
]
struct_anon_33._fields_ = [
    ("x", uint16_t),
    ("y", uint16_t),
    ("w", uint16_t),
    ("h", uint16_t),
]

rfbRectangle = struct_anon_33  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 152


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 207
class struct_anon_34(Structure):
    pass


struct_anon_34.__slots__ = [
    "bitsPerPixel",
    "depth",
    "bigEndian",
    "trueColour",
    "redMax",
    "greenMax",
    "blueMax",
    "redShift",
    "greenShift",
    "blueShift",
    "pad1",
    "pad2",
]
struct_anon_34._fields_ = [
    ("bitsPerPixel", uint8_t),
    ("depth", uint8_t),
    ("bigEndian", uint8_t),
    ("trueColour", uint8_t),
    ("redMax", uint16_t),
    ("greenMax", uint16_t),
    ("blueMax", uint16_t),
    ("redShift", uint8_t),
    ("greenShift", uint8_t),
    ("blueShift", uint8_t),
    ("pad1", uint8_t),
    ("pad2", uint16_t),
]

rfbPixelFormat = struct_anon_34  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 207


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 376
class struct_anon_36(Structure):
    pass


struct_anon_36.__slots__ = [
    "framebufferWidth",
    "framebufferHeight",
    "format",
    "nameLength",
]
struct_anon_36._fields_ = [
    ("framebufferWidth", uint16_t),
    ("framebufferHeight", uint16_t),
    ("format", rfbPixelFormat),
    ("nameLength", uint32_t),
]

rfbServerInitMsg = struct_anon_36  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 376


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 562
class struct_anon_37(Structure):
    pass


struct_anon_37.__slots__ = [
    "type",
    "pad",
    "nRects",
]
struct_anon_37._fields_ = [
    ("type", uint8_t),
    ("pad", uint8_t),
    ("nRects", uint16_t),
]

rfbFramebufferUpdateMsg = struct_anon_37  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 562


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 577
class struct_anon_38(Structure):
    pass


struct_anon_38.__slots__ = [
    "r",
    "encoding",
]
struct_anon_38._fields_ = [
    ("r", rfbRectangle),
    ("encoding", uint32_t),
]

rfbFramebufferUpdateRectHeader = struct_anon_38  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 577


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 591
class struct_anon_39(Structure):
    pass


struct_anon_39.__slots__ = [
    "client2server",
    "server2client",
]
struct_anon_39._fields_ = [
    ("client2server", uint8_t * 32),
    ("server2client", uint8_t * 32),
]

rfbSupportedMessages = struct_anon_39  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 591


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 987
class struct_anon_46(Structure):
    pass


struct_anon_46.__slots__ = [
    "type",
    "pad",
    "firstColour",
    "nColours",
]
struct_anon_46._fields_ = [
    ("type", uint8_t),
    ("pad", uint8_t),
    ("firstColour", uint16_t),
    ("nColours", uint16_t),
]

rfbSetColourMapEntriesMsg = struct_anon_46  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 987


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 999
class struct_anon_47(Structure):
    pass


struct_anon_47.__slots__ = [
    "type",
]
struct_anon_47._fields_ = [
    ("type", uint8_t),
]

rfbBellMsg = struct_anon_47  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 999


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1015
class struct_anon_48(Structure):
    pass


struct_anon_48.__slots__ = [
    "type",
    "pad1",
    "pad2",
    "length",
]
struct_anon_48._fields_ = [
    ("type", uint8_t),
    ("pad1", uint8_t),
    ("pad2", uint16_t),
    ("length", uint32_t),
]

rfbServerCutTextMsg = struct_anon_48  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1015


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1035
class struct__rfbFileTransferMsg(Structure):
    pass


struct__rfbFileTransferMsg.__slots__ = [
    "type",
    "contentType",
    "contentParam",
    "pad",
    "size",
    "length",
]
struct__rfbFileTransferMsg._fields_ = [
    ("type", uint8_t),
    ("contentType", uint8_t),
    ("contentParam", uint8_t),
    ("pad", uint8_t),
    ("size", uint32_t),
    ("length", uint32_t),
]

rfbFileTransferMsg = struct__rfbFileTransferMsg  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1035


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1108
class struct__rfbTextChatMsg(Structure):
    pass


struct__rfbTextChatMsg.__slots__ = [
    "type",
    "pad1",
    "pad2",
    "length",
]
struct__rfbTextChatMsg._fields_ = [
    ("type", uint8_t),
    ("pad1", uint8_t),
    ("pad2", uint16_t),
    ("length", uint32_t),
]

rfbTextChatMsg = struct__rfbTextChatMsg  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1108


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1144
class struct_anon_49(Structure):
    pass


struct_anon_49.__slots__ = [
    "type",
    "pad",
    "version",
    "code",
]
struct_anon_49._fields_ = [
    ("type", uint8_t),
    ("pad", uint8_t),
    ("version", uint8_t),
    ("code", uint8_t),
]

rfbXvpMsg = struct_anon_49  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1144


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1169
class struct_rfbExtDesktopSizeMsg(Structure):
    pass


struct_rfbExtDesktopSizeMsg.__slots__ = [
    "numberOfScreens",
    "pad",
]
struct_rfbExtDesktopSizeMsg._fields_ = [
    ("numberOfScreens", uint8_t),
    ("pad", uint8_t * 3),
]

rfbExtDesktopSizeMsg = struct_rfbExtDesktopSizeMsg  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1169


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1178
class struct_rfbExtDesktopScreen(Structure):
    pass


struct_rfbExtDesktopScreen.__slots__ = [
    "id",
    "x",
    "y",
    "width",
    "height",
    "flags",
]
struct_rfbExtDesktopScreen._fields_ = [
    ("id", uint32_t),
    ("x", uint16_t),
    ("y", uint16_t),
    ("width", uint16_t),
    ("height", uint16_t),
    ("flags", uint32_t),
]

rfbExtDesktopScreen = struct_rfbExtDesktopScreen  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1178


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1225
class struct__rfbResizeFrameBufferMsg(Structure):
    pass


struct__rfbResizeFrameBufferMsg.__slots__ = [
    "type",
    "pad1",
    "framebufferWidth",
    "framebufferHeigth",
]
struct__rfbResizeFrameBufferMsg._fields_ = [
    ("type", uint8_t),
    ("pad1", uint8_t),
    ("framebufferWidth", uint16_t),
    ("framebufferHeigth", uint16_t),
]

rfbResizeFrameBufferMsg = struct__rfbResizeFrameBufferMsg  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1225


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1247
class struct_anon_50(Structure):
    pass


struct_anon_50.__slots__ = [
    "type",
    "pad1",
    "desktop_w",
    "desktop_h",
    "buffer_w",
    "buffer_h",
    "pad2",
]
struct_anon_50._fields_ = [
    ("type", uint8_t),
    ("pad1", uint8_t),
    ("desktop_w", uint16_t),
    ("desktop_h", uint16_t),
    ("buffer_w", uint16_t),
    ("buffer_h", uint16_t),
    ("pad2", uint16_t),
]

rfbPalmVNCReSizeFrameBufferMsg = struct_anon_50  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1247


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1270
class union_anon_51(Union):
    pass


union_anon_51.__slots__ = [
    "type",
    "fu",
    "scme",
    "b",
    "sct",
    "rsfb",
    "prsfb",
    "ft",
    "tc",
    "xvp",
    "eds",
]
union_anon_51._fields_ = [
    ("type", uint8_t),
    ("fu", rfbFramebufferUpdateMsg),
    ("scme", rfbSetColourMapEntriesMsg),
    ("b", rfbBellMsg),
    ("sct", rfbServerCutTextMsg),
    ("rsfb", rfbResizeFrameBufferMsg),
    ("prsfb", rfbPalmVNCReSizeFrameBufferMsg),
    ("ft", rfbFileTransferMsg),
    ("tc", rfbTextChatMsg),
    ("xvp", rfbXvpMsg),
    ("eds", rfbExtDesktopSizeMsg),
]

rfbServerToClientMsg = union_anon_51  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbproto.h: 1270


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 109
class struct_anon_75(Structure):
    pass


struct_anon_75.__slots__ = [
    "file",
    "tv",
    "readTimestamp",
    "doNotSleep",
]
struct_anon_75._fields_ = [
    ("file", POINTER(FILE)),
    ("tv", struct_timeval),
    ("readTimestamp", rfbBool),
    ("doNotSleep", rfbBool),
]

rfbVNCRec = struct_anon_75  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 109


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 113
class struct_rfbClientData(Structure):
    pass


struct_rfbClientData.__slots__ = [
    "tag",
    "data",
    "next",
]
struct_rfbClientData._fields_ = [
    ("tag", POINTER(None)),
    ("data", POINTER(None)),
    ("next", POINTER(struct_rfbClientData)),
]

rfbClientData = struct_rfbClientData  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 117


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 139
class struct_anon_76(Structure):
    pass


struct_anon_76.__slots__ = [
    "shareDesktop",
    "viewOnly",
    "encodingsString",
    "useBGR233",
    "nColours",
    "forceOwnCmap",
    "forceTrueColour",
    "requestedDepth",
    "compressLevel",
    "qualityLevel",
    "enableJPEG",
    "useRemoteCursor",
    "palmVNC",
    "scaleSetting",
]
struct_anon_76._fields_ = [
    ("shareDesktop", rfbBool),
    ("viewOnly", rfbBool),
    ("encodingsString", String),
    ("useBGR233", rfbBool),
    ("nColours", c_int),
    ("forceOwnCmap", rfbBool),
    ("forceTrueColour", rfbBool),
    ("requestedDepth", c_int),
    ("compressLevel", c_int),
    ("qualityLevel", c_int),
    ("enableJPEG", rfbBool),
    ("useRemoteCursor", rfbBool),
    ("palmVNC", rfbBool),
    ("scaleSetting", c_int),
]

AppData = struct_anon_76  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 139


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 145
class struct_anon_77(Structure):
    pass


struct_anon_77.__slots__ = [
    "x509CACertFile",
    "x509CACrlFile",
    "x509ClientCertFile",
    "x509ClientKeyFile",
    "x509CrlVerifyMode",
]
struct_anon_77._fields_ = [
    ("x509CACertFile", c_char_p),
    ("x509CACrlFile", c_char_p),
    ("x509ClientCertFile", c_char_p),
    ("x509ClientKeyFile", c_char_p),
    ("x509CrlVerifyMode", uint8_t),
]

x509Credential = struct_anon_77


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 154
class struct_anon_78(Structure):
    pass


struct_anon_78.__slots__ = [
    "username",
    "password",
]
struct_anon_78._fields_ = [
    ("username", c_char_p),
    ("password", c_char_p),
]


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 159
class union__rfbCredential(Union):
    pass


union__rfbCredential.__slots__ = [
    "x509Credential",
    "userCredential",
]
union__rfbCredential._fields_ = [
    ("x509Credential", struct_anon_77),
    ("userCredential", struct_anon_78),
]

rfbCredential = union__rfbCredential  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 159


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 241
class struct__rfbClient(Structure):
    pass


HandleTextChatProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), c_int, String
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 183

HandleXvpMsgProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), uint8_t, uint8_t
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 193

HandleKeyboardLedStateProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), c_int, c_int
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 194

HandleCursorPosProc = CFUNCTYPE(
    UNCHECKED(rfbBool), POINTER(struct__rfbClient), c_int, c_int
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 195

SoftCursorLockAreaProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), c_int, c_int, c_int, c_int
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 196

SoftCursorUnlockScreenProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient)
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 197

GotFrameBufferUpdateProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), c_int, c_int, c_int, c_int
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 208

FinishedFrameBufferUpdateProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient)
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 215

GetPasswordProc = CFUNCTYPE(
    UNCHECKED(String), POINTER(struct__rfbClient)
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 216

GetCredentialProc = CFUNCTYPE(
    UNCHECKED(POINTER(rfbCredential)), POINTER(struct__rfbClient), c_int
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 217

MallocFrameBufferProc = CFUNCTYPE(
    UNCHECKED(rfbBool), POINTER(struct__rfbClient)
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 218

GotXCutTextProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), String, c_int
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 219

BellProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient)
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 220

GotCursorShapeProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), c_int, c_int, c_int, c_int, c_int
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 228

GotCopyRectProc = CFUNCTYPE(
    UNCHECKED(None),
    POINTER(struct__rfbClient),
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 229

GotFillRectProc = CFUNCTYPE(
    UNCHECKED(None), POINTER(struct__rfbClient), c_int, c_int, c_int, c_int, uint32_t
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 230

GotBitmapProc = CFUNCTYPE(
    UNCHECKED(None),
    POINTER(struct__rfbClient),
    POINTER(uint8_t),
    c_int,
    c_int,
    c_int,
    c_int,
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 231

GotJpegProc = CFUNCTYPE(
    UNCHECKED(rfbBool),
    POINTER(struct__rfbClient),
    POINTER(uint8_t),
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 232

LockWriteToTLSProc = CFUNCTYPE(
    UNCHECKED(rfbBool), POINTER(struct__rfbClient)
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 233

UnlockWriteToTLSProc = CFUNCTYPE(
    UNCHECKED(rfbBool), POINTER(struct__rfbClient)
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 234


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 255
class struct_anon_79(Structure):
    pass


struct_anon_79.__slots__ = [
    "x",
    "y",
    "w",
    "h",
]
struct_anon_79._fields_ = [
    ("x", c_int),
    ("y", c_int),
    ("w", c_int),
    ("h", c_int),
]


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 325
class struct_jpeg_source_mgr(Structure):
    pass


struct__rfbClient.__slots__ = [
    "frameBuffer",
    "width",
    "height",
    "endianTest",
    "appData",
    "programName",
    "serverHost",
    "serverPort",
    "listenSpecified",
    "listenPort",
    "flashPort",
    "updateRect",
    "buffer",
    "sock",
    "canUseCoRRE",
    "canUseHextile",
    "desktopName",
    "format",
    "si",
    "buf",
    "bufoutptr",
    "buffered",
    "ultra_buffer_size",
    "ultra_buffer",
    "raw_buffer_size",
    "raw_buffer",
    "decompStream",
    "decompStreamInited",
    "zlib_buffer",
    "zlibStream",
    "zlibStreamActive",
    "cutZeros",
    "rectWidth",
    "rectColors",
    "tightPalette",
    "tightPrevRow",
    "jpegError",
    "jpegSrcManager",
    "jpegBufferPtr",
    "jpegBufferLen",
    "rcSource",
    "rcMask",
    "clientData",
    "vncRec",
    "KeyboardLedStateEnabled",
    "CurrentKeyboardLedState",
    "canHandleNewFBSize",
    "HandleTextChat",
    "HandleKeyboardLedState",
    "HandleCursorPos",
    "SoftCursorLockArea",
    "SoftCursorUnlockScreen",
    "GotFrameBufferUpdate",
    "GetPassword",
    "MallocFrameBuffer",
    "GotXCutText",
    "Bell",
    "GotCursorShape",
    "GotCopyRect",
    "supportedMessages",
    "major",
    "minor",
    "authScheme",
    "subAuthScheme",
    "tlsSession",
    "GetCredential",
    "clientAuthSchemes",
    "destHost",
    "destPort",
    "QoS_DSCP",
    "HandleXvpMsg",
    "listenSock",
    "FinishedFrameBufferUpdate",
    "listenAddress",
    "listen6Sock",
    "listen6Address",
    "listen6Port",
    "outputWindow",
    "LockWriteToTLS",
    "UnlockWriteToTLS",
    "GotFillRect",
    "GotBitmap",
    "GotJpeg",
    "tjhnd",
    "connectTimeout",
    "readTimeout",
    "tlsRwMutex",
    "requestedResize",
    "screen",
]
struct__rfbClient._fields_ = [
    ("frameBuffer", POINTER(uint8_t)),
    ("width", c_int),
    ("height", c_int),
    ("endianTest", c_int),
    ("appData", AppData),
    ("programName", String),
    ("serverHost", String),
    ("serverPort", c_int),
    ("listenSpecified", rfbBool),
    ("listenPort", c_int),
    ("flashPort", c_int),
    ("updateRect", struct_anon_79),
    ("buffer", c_char * int(640 * 480)),
    ("sock", c_int),
    ("canUseCoRRE", rfbBool),
    ("canUseHextile", rfbBool),
    ("desktopName", String),
    ("format", rfbPixelFormat),
    ("si", rfbServerInitMsg),
    ("buf", c_char * 8192),
    ("bufoutptr", String),
    ("buffered", c_uint),
    ("ultra_buffer_size", c_int),
    ("ultra_buffer", String),
    ("raw_buffer_size", c_int),
    ("raw_buffer", String),
    ("decompStream", z_stream),
    ("decompStreamInited", rfbBool),
    ("zlib_buffer", c_char * 30000),
    ("zlibStream", z_stream * 4),
    ("zlibStreamActive", rfbBool * 4),
    ("cutZeros", rfbBool),
    ("rectWidth", c_int),
    ("rectColors", c_int),
    ("tightPalette", c_char * int(256 * 4)),
    ("tightPrevRow", uint8_t * int((2048 * 3) * sizeof(uint16_t))),
    ("jpegError", rfbBool),
    ("jpegSrcManager", POINTER(struct_jpeg_source_mgr)),
    ("jpegBufferPtr", POINTER(None)),
    ("jpegBufferLen", c_size_t),
    ("rcSource", POINTER(uint8_t)),
    ("rcMask", POINTER(uint8_t)),
    ("clientData", POINTER(rfbClientData)),
    ("vncRec", POINTER(rfbVNCRec)),
    ("KeyboardLedStateEnabled", c_int),
    ("CurrentKeyboardLedState", c_int),
    ("canHandleNewFBSize", c_int),
    ("HandleTextChat", HandleTextChatProc),
    ("HandleKeyboardLedState", HandleKeyboardLedStateProc),
    ("HandleCursorPos", HandleCursorPosProc),
    ("SoftCursorLockArea", SoftCursorLockAreaProc),
    ("SoftCursorUnlockScreen", SoftCursorUnlockScreenProc),
    ("GotFrameBufferUpdate", GotFrameBufferUpdateProc),
    ("GetPassword", GetPasswordProc),
    ("MallocFrameBuffer", MallocFrameBufferProc),
    ("GotXCutText", GotXCutTextProc),
    ("Bell", BellProc),
    ("GotCursorShape", GotCursorShapeProc),
    ("GotCopyRect", GotCopyRectProc),
    ("supportedMessages", rfbSupportedMessages),
    ("major", c_int),
    ("minor", c_int),
    ("authScheme", uint32_t),
    ("subAuthScheme", uint32_t),
    ("tlsSession", POINTER(None)),
    ("GetCredential", GetCredentialProc),
    ("clientAuthSchemes", POINTER(uint32_t)),
    ("destHost", String),
    ("destPort", c_int),
    ("QoS_DSCP", c_int),
    ("HandleXvpMsg", HandleXvpMsgProc),
    ("listenSock", c_int),
    ("FinishedFrameBufferUpdate", FinishedFrameBufferUpdateProc),
    ("listenAddress", String),
    ("listen6Sock", c_int),
    ("listen6Address", String),
    ("listen6Port", c_int),
    ("outputWindow", c_ulong),
    ("LockWriteToTLS", LockWriteToTLSProc),
    ("UnlockWriteToTLS", UnlockWriteToTLSProc),
    ("GotFillRect", GotFillRectProc),
    ("GotBitmap", GotBitmapProc),
    ("GotJpeg", GotJpegProc),
    ("tjhnd", POINTER(None)),
    ("connectTimeout", c_uint),
    ("readTimeout", c_uint),
    ("tlsRwMutex", pthread_mutex_t),
    ("requestedResize", rfbBool),
    ("screen", rfbExtDesktopScreen),
]

rfbClient = struct__rfbClient  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 480

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 489
if _libs["libvncclient.so"].has("HandleCursorShape", "cdecl"):
    HandleCursorShape = _libs["libvncclient.so"].get("HandleCursorShape", "cdecl")
    HandleCursorShape.argtypes = [
        POINTER(rfbClient),
        c_int,
        c_int,
        c_int,
        c_int,
        uint32_t,
    ]
    HandleCursorShape.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 493
if _libs["libvncclient.so"].has("listenForIncomingConnections", "cdecl"):
    listenForIncomingConnections = _libs["libvncclient.so"].get(
        "listenForIncomingConnections", "cdecl"
    )
    listenForIncomingConnections.argtypes = [POINTER(rfbClient)]
    listenForIncomingConnections.restype = None

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 494
if _libs["libvncclient.so"].has("listenForIncomingConnectionsNoFork", "cdecl"):
    listenForIncomingConnectionsNoFork = _libs["libvncclient.so"].get(
        "listenForIncomingConnectionsNoFork", "cdecl"
    )
    listenForIncomingConnectionsNoFork.argtypes = [POINTER(rfbClient), c_int]
    listenForIncomingConnectionsNoFork.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 498
try:
    rfbEnableClientLogging = (rfbBool).in_dll(
        _libs["libvncclient.so"], "rfbEnableClientLogging"
    )
except:
    pass

rfbClientLogProc = CFUNCTYPE(
    UNCHECKED(None), String
)  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 499

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 500
try:
    rfbClientLog = (rfbClientLogProc).in_dll(_libs["libvncclient.so"], "rfbClientLog")
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 500
try:
    rfbClientErr = (rfbClientLogProc).in_dll(_libs["libvncclient.so"], "rfbClientErr")
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 501
if _libs["libvncclient.so"].has("ConnectToRFBServer", "cdecl"):
    ConnectToRFBServer = _libs["libvncclient.so"].get("ConnectToRFBServer", "cdecl")
    ConnectToRFBServer.argtypes = [POINTER(rfbClient), String, c_int]
    ConnectToRFBServer.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 502
if _libs["libvncclient.so"].has("ConnectToRFBRepeater", "cdecl"):
    ConnectToRFBRepeater = _libs["libvncclient.so"].get("ConnectToRFBRepeater", "cdecl")
    ConnectToRFBRepeater.argtypes = [POINTER(rfbClient), String, c_int, String, c_int]
    ConnectToRFBRepeater.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 503
if _libs["libvncclient.so"].has("SetClientAuthSchemes", "cdecl"):
    SetClientAuthSchemes = _libs["libvncclient.so"].get("SetClientAuthSchemes", "cdecl")
    SetClientAuthSchemes.argtypes = [POINTER(rfbClient), POINTER(uint32_t), c_int]
    SetClientAuthSchemes.restype = None

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 504
if _libs["libvncclient.so"].has("InitialiseRFBConnection", "cdecl"):
    InitialiseRFBConnection = _libs["libvncclient.so"].get(
        "InitialiseRFBConnection", "cdecl"
    )
    InitialiseRFBConnection.argtypes = [POINTER(rfbClient)]
    InitialiseRFBConnection.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 522
if _libs["libvncclient.so"].has("SetFormatAndEncodings", "cdecl"):
    SetFormatAndEncodings = _libs["libvncclient.so"].get(
        "SetFormatAndEncodings", "cdecl"
    )
    SetFormatAndEncodings.argtypes = [POINTER(rfbClient)]
    SetFormatAndEncodings.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 523
if _libs["libvncclient.so"].has("SendIncrementalFramebufferUpdateRequest", "cdecl"):
    SendIncrementalFramebufferUpdateRequest = _libs["libvncclient.so"].get(
        "SendIncrementalFramebufferUpdateRequest", "cdecl"
    )
    SendIncrementalFramebufferUpdateRequest.argtypes = [POINTER(rfbClient)]
    SendIncrementalFramebufferUpdateRequest.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 544
if _libs["libvncclient.so"].has("SendFramebufferUpdateRequest", "cdecl"):
    SendFramebufferUpdateRequest = _libs["libvncclient.so"].get(
        "SendFramebufferUpdateRequest", "cdecl"
    )
    SendFramebufferUpdateRequest.argtypes = [
        POINTER(rfbClient),
        c_int,
        c_int,
        c_int,
        c_int,
        rfbBool,
    ]
    SendFramebufferUpdateRequest.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 547
if _libs["libvncclient.so"].has("SendScaleSetting", "cdecl"):
    SendScaleSetting = _libs["libvncclient.so"].get("SendScaleSetting", "cdecl")
    SendScaleSetting.argtypes = [POINTER(rfbClient), c_int]
    SendScaleSetting.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 568
if _libs["libvncclient.so"].has("SendPointerEvent", "cdecl"):
    SendPointerEvent = _libs["libvncclient.so"].get("SendPointerEvent", "cdecl")
    SendPointerEvent.argtypes = [POINTER(rfbClient), c_int, c_int, c_int]
    SendPointerEvent.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 576
if _libs["libvncclient.so"].has("SendExtDesktopSize", "cdecl"):
    SendExtDesktopSize = _libs["libvncclient.so"].get("SendExtDesktopSize", "cdecl")
    SendExtDesktopSize.argtypes = [POINTER(rfbClient), uint16_t, uint16_t]
    SendExtDesktopSize.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 586
if _libs["libvncclient.so"].has("SendKeyEvent", "cdecl"):
    SendKeyEvent = _libs["libvncclient.so"].get("SendKeyEvent", "cdecl")
    SendKeyEvent.argtypes = [POINTER(rfbClient), uint32_t, rfbBool]
    SendKeyEvent.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 597
if _libs["libvncclient.so"].has("SendExtendedKeyEvent", "cdecl"):
    SendExtendedKeyEvent = _libs["libvncclient.so"].get("SendExtendedKeyEvent", "cdecl")
    SendExtendedKeyEvent.argtypes = [POINTER(rfbClient), uint32_t, uint32_t, rfbBool]
    SendExtendedKeyEvent.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 610
if _libs["libvncclient.so"].has("SendClientCutText", "cdecl"):
    SendClientCutText = _libs["libvncclient.so"].get("SendClientCutText", "cdecl")
    SendClientCutText.argtypes = [POINTER(rfbClient), String, c_int]
    SendClientCutText.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 621
if _libs["libvncclient.so"].has("HandleRFBServerMessage", "cdecl"):
    HandleRFBServerMessage = _libs["libvncclient.so"].get(
        "HandleRFBServerMessage", "cdecl"
    )
    HandleRFBServerMessage.argtypes = [POINTER(rfbClient)]
    HandleRFBServerMessage.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 629
if _libs["libvncclient.so"].has("TextChatSend", "cdecl"):
    TextChatSend = _libs["libvncclient.so"].get("TextChatSend", "cdecl")
    TextChatSend.argtypes = [POINTER(rfbClient), String]
    TextChatSend.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 635
if _libs["libvncclient.so"].has("TextChatOpen", "cdecl"):
    TextChatOpen = _libs["libvncclient.so"].get("TextChatOpen", "cdecl")
    TextChatOpen.argtypes = [POINTER(rfbClient)]
    TextChatOpen.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 641
if _libs["libvncclient.so"].has("TextChatClose", "cdecl"):
    TextChatClose = _libs["libvncclient.so"].get("TextChatClose", "cdecl")
    TextChatClose.argtypes = [POINTER(rfbClient)]
    TextChatClose.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 642
if _libs["libvncclient.so"].has("TextChatFinish", "cdecl"):
    TextChatFinish = _libs["libvncclient.so"].get("TextChatFinish", "cdecl")
    TextChatFinish.argtypes = [POINTER(rfbClient)]
    TextChatFinish.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 643
if _libs["libvncclient.so"].has("PermitServerInput", "cdecl"):
    PermitServerInput = _libs["libvncclient.so"].get("PermitServerInput", "cdecl")
    PermitServerInput.argtypes = [POINTER(rfbClient), c_int]
    PermitServerInput.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 644
if _libs["libvncclient.so"].has("SendXvpMsg", "cdecl"):
    SendXvpMsg = _libs["libvncclient.so"].get("SendXvpMsg", "cdecl")
    SendXvpMsg.argtypes = [POINTER(rfbClient), uint8_t, uint8_t]
    SendXvpMsg.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 646
if _libs["libvncclient.so"].has("PrintPixelFormat", "cdecl"):
    PrintPixelFormat = _libs["libvncclient.so"].get("PrintPixelFormat", "cdecl")
    PrintPixelFormat.argtypes = [POINTER(rfbPixelFormat)]
    PrintPixelFormat.restype = None

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 648
if _libs["libvncclient.so"].has("SupportsClient2Server", "cdecl"):
    SupportsClient2Server = _libs["libvncclient.so"].get(
        "SupportsClient2Server", "cdecl"
    )
    SupportsClient2Server.argtypes = [POINTER(rfbClient), c_int]
    SupportsClient2Server.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 649
if _libs["libvncclient.so"].has("SupportsServer2Client", "cdecl"):
    SupportsServer2Client = _libs["libvncclient.so"].get(
        "SupportsServer2Client", "cdecl"
    )
    SupportsServer2Client.argtypes = [POINTER(rfbClient), c_int]
    SupportsServer2Client.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 666
if _libs["libvncclient.so"].has("rfbClientSetClientData", "cdecl"):
    rfbClientSetClientData = _libs["libvncclient.so"].get(
        "rfbClientSetClientData", "cdecl"
    )
    rfbClientSetClientData.argtypes = [POINTER(rfbClient), POINTER(None), POINTER(None)]
    rfbClientSetClientData.restype = None

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 675
if _libs["libvncclient.so"].has("rfbClientGetClientData", "cdecl"):
    rfbClientGetClientData = _libs["libvncclient.so"].get(
        "rfbClientGetClientData", "cdecl"
    )
    rfbClientGetClientData.argtypes = [POINTER(rfbClient), POINTER(None)]
    rfbClientGetClientData.restype = POINTER(c_ubyte)
    rfbClientGetClientData.errcheck = lambda v, *a: cast(v, c_void_p)


# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 679
class struct__rfbClientProtocolExtension(Structure):
    pass


struct__rfbClientProtocolExtension.__slots__ = [
    "encodings",
    "handleEncoding",
    "handleMessage",
    "next",
    "securityTypes",
    "handleAuthentication",
]
struct__rfbClientProtocolExtension._fields_ = [
    ("encodings", POINTER(c_int)),
    (
        "handleEncoding",
        CFUNCTYPE(
            UNCHECKED(rfbBool),
            POINTER(rfbClient),
            POINTER(rfbFramebufferUpdateRectHeader),
        ),
    ),
    (
        "handleMessage",
        CFUNCTYPE(
            UNCHECKED(rfbBool), POINTER(rfbClient), POINTER(rfbServerToClientMsg)
        ),
    ),
    ("next", POINTER(struct__rfbClientProtocolExtension)),
    ("securityTypes", POINTER(uint32_t)),
    (
        "handleAuthentication",
        CFUNCTYPE(UNCHECKED(rfbBool), POINTER(rfbClient), uint32_t),
    ),
]

rfbClientProtocolExtension = struct__rfbClientProtocolExtension  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 691

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 693
if _libs["libvncclient.so"].has("rfbClientRegisterExtension", "cdecl"):
    rfbClientRegisterExtension = _libs["libvncclient.so"].get(
        "rfbClientRegisterExtension", "cdecl"
    )
    rfbClientRegisterExtension.argtypes = [POINTER(rfbClientProtocolExtension)]
    rfbClientRegisterExtension.restype = None

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 697
try:
    errorMessageOnReadFailure = (rfbBool).in_dll(
        _libs["libvncclient.so"], "errorMessageOnReadFailure"
    )
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 699
if _libs["libvncclient.so"].has("ReadFromRFBServer", "cdecl"):
    ReadFromRFBServer = _libs["libvncclient.so"].get("ReadFromRFBServer", "cdecl")
    ReadFromRFBServer.argtypes = [POINTER(rfbClient), String, c_uint]
    ReadFromRFBServer.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 700
if _libs["libvncclient.so"].has("WriteToRFBServer", "cdecl"):
    WriteToRFBServer = _libs["libvncclient.so"].get("WriteToRFBServer", "cdecl")
    WriteToRFBServer.argtypes = [POINTER(rfbClient), String, c_uint]
    WriteToRFBServer.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 701
if _libs["libvncclient.so"].has("FindFreeTcpPort", "cdecl"):
    FindFreeTcpPort = _libs["libvncclient.so"].get("FindFreeTcpPort", "cdecl")
    FindFreeTcpPort.argtypes = []
    FindFreeTcpPort.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 702
if _libs["libvncclient.so"].has("ListenAtTcpPort", "cdecl"):
    ListenAtTcpPort = _libs["libvncclient.so"].get("ListenAtTcpPort", "cdecl")
    ListenAtTcpPort.argtypes = [c_int]
    ListenAtTcpPort.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 703
if _libs["libvncclient.so"].has("ListenAtTcpPortAndAddress", "cdecl"):
    ListenAtTcpPortAndAddress = _libs["libvncclient.so"].get(
        "ListenAtTcpPortAndAddress", "cdecl"
    )
    ListenAtTcpPortAndAddress.argtypes = [c_int, String]
    ListenAtTcpPortAndAddress.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 710
if _libs["libvncclient.so"].has("ConnectClientToTcpAddr", "cdecl"):
    ConnectClientToTcpAddr = _libs["libvncclient.so"].get(
        "ConnectClientToTcpAddr", "cdecl"
    )
    ConnectClientToTcpAddr.argtypes = [c_uint, c_int]
    ConnectClientToTcpAddr.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 717
if _libs["libvncclient.so"].has("ConnectClientToTcpAddr6", "cdecl"):
    ConnectClientToTcpAddr6 = _libs["libvncclient.so"].get(
        "ConnectClientToTcpAddr6", "cdecl"
    )
    ConnectClientToTcpAddr6.argtypes = [String, c_int]
    ConnectClientToTcpAddr6.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 723
if _libs["libvncclient.so"].has("ConnectClientToUnixSock", "cdecl"):
    ConnectClientToUnixSock = _libs["libvncclient.so"].get(
        "ConnectClientToUnixSock", "cdecl"
    )
    ConnectClientToUnixSock.argtypes = [String]
    ConnectClientToUnixSock.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 731
if _libs["libvncclient.so"].has("ConnectClientToTcpAddrWithTimeout", "cdecl"):
    ConnectClientToTcpAddrWithTimeout = _libs["libvncclient.so"].get(
        "ConnectClientToTcpAddrWithTimeout", "cdecl"
    )
    ConnectClientToTcpAddrWithTimeout.argtypes = [c_uint, c_int, c_uint]
    ConnectClientToTcpAddrWithTimeout.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 739
if _libs["libvncclient.so"].has("ConnectClientToTcpAddr6WithTimeout", "cdecl"):
    ConnectClientToTcpAddr6WithTimeout = _libs["libvncclient.so"].get(
        "ConnectClientToTcpAddr6WithTimeout", "cdecl"
    )
    ConnectClientToTcpAddr6WithTimeout.argtypes = [String, c_int, c_uint]
    ConnectClientToTcpAddr6WithTimeout.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 746
if _libs["libvncclient.so"].has("ConnectClientToUnixSockWithTimeout", "cdecl"):
    ConnectClientToUnixSockWithTimeout = _libs["libvncclient.so"].get(
        "ConnectClientToUnixSockWithTimeout", "cdecl"
    )
    ConnectClientToUnixSockWithTimeout.argtypes = [String, c_uint]
    ConnectClientToUnixSockWithTimeout.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 747
if _libs["libvncclient.so"].has("AcceptTcpConnection", "cdecl"):
    AcceptTcpConnection = _libs["libvncclient.so"].get("AcceptTcpConnection", "cdecl")
    AcceptTcpConnection.argtypes = [c_int]
    AcceptTcpConnection.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 748
if _libs["libvncclient.so"].has("SetNonBlocking", "cdecl"):
    SetNonBlocking = _libs["libvncclient.so"].get("SetNonBlocking", "cdecl")
    SetNonBlocking.argtypes = [c_int]
    SetNonBlocking.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 749
if _libs["libvncclient.so"].has("SetBlocking", "cdecl"):
    SetBlocking = _libs["libvncclient.so"].get("SetBlocking", "cdecl")
    SetBlocking.argtypes = [c_int]
    SetBlocking.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 750
if _libs["libvncclient.so"].has("SetDSCP", "cdecl"):
    SetDSCP = _libs["libvncclient.so"].get("SetDSCP", "cdecl")
    SetDSCP.argtypes = [c_int, c_int]
    SetDSCP.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 752
if _libs["libvncclient.so"].has("StringToIPAddr", "cdecl"):
    StringToIPAddr = _libs["libvncclient.so"].get("StringToIPAddr", "cdecl")
    StringToIPAddr.argtypes = [String, POINTER(c_uint)]
    StringToIPAddr.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 753
if _libs["libvncclient.so"].has("SameMachine", "cdecl"):
    SameMachine = _libs["libvncclient.so"].get("SameMachine", "cdecl")
    SameMachine.argtypes = [c_int]
    SameMachine.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 764
if _libs["libvncclient.so"].has("WaitForMessage", "cdecl"):
    WaitForMessage = _libs["libvncclient.so"].get("WaitForMessage", "cdecl")
    WaitForMessage.argtypes = [POINTER(rfbClient), c_uint]
    WaitForMessage.restype = c_int

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 791
if _libs["libvncclient.so"].has("rfbGetClient", "cdecl"):
    rfbGetClient = _libs["libvncclient.so"].get("rfbGetClient", "cdecl")
    rfbGetClient.argtypes = [c_int, c_int, c_int]
    rfbGetClient.restype = POINTER(rfbClient)

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 823
if _libs["libvncclient.so"].has("rfbInitClient", "cdecl"):
    rfbInitClient = _libs["libvncclient.so"].get("rfbInitClient", "cdecl")
    rfbInitClient.argtypes = [
        POINTER(rfbClient),
        POINTER(c_int),
        POINTER(POINTER(c_char)),
    ]
    rfbInitClient.restype = rfbBool

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 831
if _libs["libvncclient.so"].has("rfbClientCleanup", "cdecl"):
    rfbClientCleanup = _libs["libvncclient.so"].get("rfbClientCleanup", "cdecl")
    rfbClientCleanup.argtypes = [POINTER(rfbClient)]
    rfbClientCleanup.restype = None

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 83
try:
    FLASH_PORT_OFFSET = 5400
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 84
try:
    LISTEN_PORT_OFFSET = 5500
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 85
try:
    TUNNEL_PORT_OFFSET = 5500
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 86
try:
    SERVER_PORT_OFFSET = 5900
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 88
try:
    DEFAULT_CONNECT_TIMEOUT = 60
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 89
try:
    DEFAULT_READ_TIMEOUT = 0
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 91
try:
    DEFAULT_SSH_CMD = "/usr/bin/ssh"
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 161
try:
    rfbCredentialTypeX509 = 1
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 162
try:
    rfbCredentialTypeUser = 2
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 167
try:
    rfbX509CrlVerifyNone = 0
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 168
try:
    rfbX509CrlVerifyClient = 1
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 169
try:
    rfbX509CrlVerifyAll = 2
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 264
try:
    RFB_BUFFER_SIZE = 640 * 480
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 277
try:
    RFB_BUF_SIZE = 8192
except:
    pass

# /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 308
try:
    ZLIB_BUFFER_SIZE = 30000
except:
    pass

rfbClientData = struct_rfbClientData  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 113

_rfbCredential = union__rfbCredential  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 159

_rfbClient = struct__rfbClient  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 241

jpeg_source_mgr = struct_jpeg_source_mgr  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 325

_rfbClientProtocolExtension = struct__rfbClientProtocolExtension  # /nix/store/25f5jlhp815846zxprn3v3h47qrbqgdb-libvncserver-0.9.14-dev/include/rfb/rfbclient.h: 679

# No inserted files

# No prefix-stripping
