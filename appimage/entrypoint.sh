export PYAPPIMAGE_PIP=${APPDIR}/opt/python{{ python-version }}/bin/pip
{{ python-executable }} -s ${APPDIR}/opt/python{{ python-version }}/bin/pyappimage "$@"
