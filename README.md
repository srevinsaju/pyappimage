<h1 align="center">
	<img src="pyappimage/assets/pyappimage.svg" alt="PyAppImage" height=200 width=200 align="middle">
	PyAppImage :snake:
</h1>
<h3 align="center">
	Create optimized Python AppImages, faster!
</h3>
<div align="center">

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)<br/><br/>

![Python application](https://github.com/srevinsaju/pyappimage/workflows/Python%20application/badge.svg) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/srevinsaju/pyappimage) ![GitHub](https://img.shields.io/github/license/srevinsaju/pyappimage) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/srevinsaju/pyappimage?sort=semver) [![irc](https://img.shields.io/badge/IRC-%23AppImage%20on%20freenode-blue.svg)](https://webchat.freenode.net/?channels=AppImage) 

[![Mentioned in Awesome AppImage](https://awesome.re/mentioned-badge-flat.svg)](https://github.com/AppImage/awesome-appimage)

![GitHub followers](https://img.shields.io/github/followers/srevinsaju?label=Follow%20me&style=social) ![GitHub stars](https://img.shields.io/github/stars/srevinsaju/zap?style=social)
</div>

## Getting Started
> The project is still in beta. Consider reporting bugs to help development and release a stable version;

### Download `pyappimage`

* Choose the Python Version. Currently, the supported Python versions are `3.6`, `3.7` and `3.8`. 
These AppImages are built using [python-appimage](https://github.com/niess/python-appimage) which 
includes the Python Interpreter. See [why not `pyappimage`](#why-not-pyappimage) section for more
details. Corresponding to the python version, binaries will be built, using [PyInstaller]
(https://github.com/PyInstaller/PyInstaller) and are processed to make the necessary changes.

* Get the latest `pyappimage.AppImage` to begin development

### PyAppImage tutorial 

Here are some small tutorials to package some applications, and to workaround bugs when packaging software

1. Hello World AppImage
2. [Packaging Archivy](guides/archivy.md)
3. [Packaging AppImageLint](guides/appimagelint.md)



### Configuration parameters
`pyappimage` can be configured using the following parameters

#### `entrypoint`
Entrypoint is a path to the function. It is normally in the format
```python
folder.script:function
```
here, the function located in `script` file, of which the script file is
 located in the `folder` called `folder` is executed.

<br>

#### Environment Variables

Environment variables can be set before the appimage entrypoint is called. 
This can be useful in defining AppImage based variables or conditionally executing some functions when the app is being run within an appimage, 

```yml
environment: 
  HELLO: TEST
```

This will be translated to 

```bash
export HELLO=TEST
```

<br>

#### Include additional data to AppImage

These are `data` objects, including items like `png`, `json`, `txt` items which you would like to place in the AppImage. Just simple add

```
data: 
  $CWD/somefile/photo.png: $APPIMAGE/photo.png
  /usr/share/icons/myphoto.svg: $APPIMAGE/icons/icon.png
```

<br>

#### Custom Icon

Place `<appname>.png` in the `pyappimage` directory, and it will be automatically set as the AppImage dir icon. 

<br>

#### Custom Desktop File

`pyappimage` automatically generates the desktop file for you. If you want to override the desktop file generated by `pyappimage`, you can add a `<appname>.desktop` desktop file in the `pyappimage` directory, and that will be added. Make sure that your desktop file matches FreeDesktop's standards.


## When to use `pyappimage` ?

### Use `pyappimage` when
* You are creating a command line application
* Your application has reached `beta` stage
* If you have intermediate coding skills on Python
* You are writing an Hello World Application which does not need the entire Python interpreter
* If you are worried about the huge python appimage
* If you are highly experienced with PyInstaller or nuitka

### Do not use `pyappimage` when
* If your project is still in alpha
* If your project requirements are not properly written
* If you do not have a `setup.py`
* If you are building a Qt Application? (needs more references. `PyQt` pyappimage weighed 119 MB on `guiscrcpy`, so the difference is very tiney)


## Similar projects
[Awesome AppImage Python development tools](https://github.com/AppImage/awesome-appimage#deployment-tools-for-python-applications) provide a list of Awesome
tools to speed up distributing your python apps. Do check them out.
`pyappimage-*.AppImage` which you use to build your optimized Python AppImages itself use @niess 's [python-appimage](https://github.com/niess/python-appimage).
Because `pyappimage` needs a real python interpreter to bundle Python appimages for you!



## License

```
MIT License

Copyright (c) 2020 Srevin Saju

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Copyright
(c) Srevin Saju 2020

PyAppImage logo is a remix of the [Papirus Icon Theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme).

