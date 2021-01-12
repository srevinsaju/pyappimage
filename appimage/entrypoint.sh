export PATH="${APPDIR}/usr/bin:$PATH"
export PYAPPIMAGE_PIP="${APPDIR}/usr/bin/pip"
export LD_LIBRARY_PATH="${APPDIR}/opt/python{{ python-version }}/lib:${APPDIR}/usr/lib:$LD_LIBRARY_PATH"
{{ python-executable }} -s "${APPDIR}/opt/python{{ python-version }}/bin/pyappimage" "$@"
