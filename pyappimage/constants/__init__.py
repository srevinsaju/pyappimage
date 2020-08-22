APPRUN = r"""#! /bin/bash

# Export APPRUN if running from an extracted image
self="$(readlink -f -- $0)"
here="${self%/*}"
APPDIR="${APPDIR:-${here}}"

export LD_LIBRARY_PATH="$APPDIR:${APPDIR}/usr/lib:${APPDIR}/usr/local/lib:${LD_LIBRARY_PATH}"
export PYAPPIMAGE="TRUE"

if [ -z "$LC_ALL" ]
then 
        export LC_ALL=C.UTF-8
fi

if [ -z "$LANG" ]
then
        export LANG=C.UTF-8
fi
"""

DESKTOP_FILE = \
    """[Desktop Entry]
Name={generic_name}
GenericName={bin}
Comment={comment}
Exec={bin}
Icon={icon}
Type=Application
Categories={categories}
StartupWMClass={bin}
"""


ENTRYPOINT = \
"""import sys
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