APPRUN = r"""#! /bin/bash

# Export APPRUN if running from an extracted image
self="$(readlink -f -- $0)"
here="${self%/*}"
APPDIR="${APPDIR:-${here}}"

export PYAPPIMAGE="TRUE"

"""

SEPARATOR = "\n========================\n"

CATEGORIES = [
    "AudioVideo",
    "Audio",
    "Video",
    "Development",
    "Education",
    "Game",
    "Graphics",
    "Network",
    "Office",
    "Science",
    "Settings",
    "System",
    "Utility",
]

DESKTOP_FILE = """[Desktop Entry]
Name={generic_name}
GenericName={bin}
Comment={comment}
Exec={bin}
Icon={icon}
Type=Application
Categories={categories}
StartupWMClass={bin}
"""


ENTRYPOINT = """import sys
BUILT_INFO = "{platform_version}"
PYAPPIMAGE_VERSION = "{pyappimage_version}"
PYTHON_RUNTIME = "{python_runtime}"
if '--pyappimage-runtime' in sys.argv:
    print("Built on:")
    print(" - OS:", BUILT_INFO)
    print(" - Python:", PYTHON_RUNTIME)
    print("Built using:", PYAPPIMAGE_VERSION)
    print("Python runtime:", sys.version)
else:
    {entrypoint}"""
