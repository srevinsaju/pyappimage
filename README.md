<h1 align="center">
	<img src="pyappimage/assets/pyappimage.svg" alt="PyAppImage" height=200 width=200 align="middle">
	PyAppImage :snake:
</h1>

Ultimately simple python-to-appimage bundler

## Getting Started
> The project is still in beta. Consider reporting bugs to help development and release a stable version;

### Download `pyappimage`

* Choose the Python Version. Currently, the supported Python versions are `3.6`, `3.7` and `3.8`. 
These AppImages are built using [python-appimage](https://github.com/niess/python-appimage) which 
includes the Python Interpreter. See [why not `pyappimage`](#why-not-pyappimage) section for more
details. Corresponding to the python version, binaries will be built, using [PyInstaller]
(https://github.com/PyInstaller/PyInstaller) and are processed to make the necessary changes.

* Get the latest `pyappimage.AppImage` to begin development

### Create a `pyappimage.json` configuration file.

`pyappimage` revolves around its configuration file.
To begin with, 
* At the Python software's root directory, (the directory containing `setup.py`)
(will be updated)
