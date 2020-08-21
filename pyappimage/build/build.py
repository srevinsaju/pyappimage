#!/usr/bin/env python3
"""
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

--------------
This file is a part of the PyAppImage Python AppImage builder
"""

import os
import shlex
import shutil
import subprocess
import time

from PyInstaller import __main__ as PyInstaller
from halo import Halo

from ..constants import APPRUN, DESKTOP_FILE
from ..version import __version__
from zap.zap import Zap
_ = shlex.split

SEPARATOR = "\n========================\n"


def get_executable_path(executable, raise_error=True):
    """
    Returns the absolute path of the executable
    if it is found on the PATH,
    if it is not found raises a FileNotFoundError
    :param executable:
    :return:
    """
    # gets the PATH environment variable
    path = os.getenv('PATH').split(os.pathsep)
    for i in path:
        if os.path.exists(os.path.join(i, executable)):
            return os.path.join(i, executable)
    if raise_error:
        raise FileNotFoundError(
            "Could not find {p} on PATH. "
            "Make sure {p} is added to path and try again".format(
                p=executable))
    else:
        return False


def get_parameters(config):

    kwargs = []
    _ = config.pop("distpath", None)  # to prevent overriding the dist path
    for key in config:
        if isinstance(config[key], bool):
            if config[key] is True:
                kwargs.append("--{key}".format(key=key))
            elif config[key] is None:
                raise ValueError("Config contains invalid data: null")
        elif isinstance(config[key], list):
            for i in config[key]:
                kwargs.append("--{key}={arg}".format(key=key, arg=i))
        else:
            kwargs.append("--{key}={arg}".format(key=key, arg=config[key]))

    return kwargs


def build(config, icon, appdata=None, desktop_file=None ,has_fuse=True):
    entrypoint = config.pop("entrypoint")
    name = config.pop('name', 'Python')
    generic_name = config.pop('generic-name', name)
    description = config.pop('description', 'Python app generated using '
                                            'PyAppImage')
    categories = config.pop('categories', [])
    updateinformation = config.pop('updateinformation')

    build_started_at = time.asctime()
    spinner = Halo("Building AppImage for {} ".format(name), spinner="dots")
    spinner.start()
    build_directory = os.path.realpath("{}.AppDir.BUILD".format(name))
    dist_directory = os.path.realpath("{}.AppDir".format(name))
    _pyinstaller_workpath = os.path.join(build_directory, 'build')
    for i in (build_directory, dist_directory, _pyinstaller_workpath):
        if not os.path.exists(i):
            os.makedirs(i)

    _import, _function = entrypoint.split(':')
    entrypoint = "from {mod} import {func}; {func}()".format(
        mod=_import, func=_function)

    with open(os.path.join(build_directory, "entrypoint.py"), 'w') as w:
        w.write(entrypoint)

    PyInstaller.run(_(
        "{build}/entrypoint.py --log-level=WARN --strip --name={name} "
        "--onedir {kwargs} --distpath={dist} --specpath={workpath} "
        "--workpath={workpath} "
        "--noconfirm --clean".format(
            pyinstaller=get_executable_path("pyinstaller"),
            name=name,
            entrypoint=entrypoint,
            kwargs=' '.join(get_parameters(config)),
            dist=dist_directory,
            build=build_directory,
            workpath=_pyinstaller_workpath
        )))

    if not os.path.exists(os.path.join(dist_directory, name, name)):
        spinner.fail("Build failed")
        spinner.stop()

    # build has succeeded
    spinner.succeed("Build succeeded! ")
    spinner.info("Copying icons ")
    icon_name = icon.split(os.path.sep)[-1]
    shutil.copyfile(
        icon, os.path.join(dist_directory, icon_name), follow_symlinks=True)
    if appdata is not None:
        spinner.info("Copying {}.appdata.xml".format(name))
        appdata_dir = os.path.join(dist_directory, 'usr', 'share')
        os.makedirs(appdata_dir, exist_ok=True)
        shutil.copyfile(
            appdata, os.path.join(appdata_dir, '{}.appdata.xml'.format(name)),
            follow_symlinks=True)
    if desktop_file is None:
        with open(os.path.join(dist_directory, '{}.desktop'.format(name)),
                  'w') as w:
            w.write(DESKTOP_FILE.format(
                bin=name,
                generic_name=generic_name,
                comment=description,
                categories=";".join(categories) + ";",
                icon=icon_name.split('.')[0]
            ))
    else:
        shutil.copyfile(
            desktop_file,
            os.path.join(dist_directory, '{}.desktop'.format(name)),
            follow_symlinks=True
        )

    spinner.start("Downloading appimagetool")
    appimagetool = Zap("appimagetool")
    appimagetool.install(select_default=True, tag_name="continuous",
                         always_proceed=True)
    path_to_appimagetool = appimagetool.appdata().get('path')
    fuse_arguments = "--appimage-extract-and-run" if not has_fuse else ""
    spinner.succeed("AppImageTool download succeeded!")

    # writing Entrypoint
    spinner.info("Writing AppRun appimagetool")
    path_to_apprun = os.path.join(dist_directory, 'AppRun')
    with open(path_to_apprun, 'w') as w:
        w.write(APPRUN)
        w.write("${APPDIR}/" + name + "/" + name + " $@")
    os.chmod(path_to_apprun, 0o755)

    _libz = os.path.join(dist_directory, name, 'libz.so.1')
    if os.path.exists(_libz):
        os.remove(_libz)

    spinner.start("Building AppImage")

    dest_appimage_output_name = "{name}-{machine}.AppImage".format(
        name=name,
        machine=os.uname().machine
    )

    _build_appimage_process = subprocess.Popen(_(
        "{appimagetool} {fuse_arguments} {update} {SRC} {DEST}".format(
            appimagetool=path_to_appimagetool,
            fuse_arguments=fuse_arguments,
            update="-u {}".format(updateinformation)
            if updateinformation else "",
            SRC=dist_directory,
            DEST=dest_appimage_output_name,
        )),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    _build_appimage_process_exit_code = _build_appimage_process.wait()
    _build_appimage_process_out, _build_appimage_process_err = \
        _build_appimage_process.communicate()

    log_file = os.path.join(build_directory, 'DIST.log')

    with open(log_file, 'w') as fp:
        fp.write("PyAppImage v{}\n".format(__version__))
        fp.write("Build started at {}\n".format(build_started_at))
        fp.write(SEPARATOR)
        fp.write("BUILD LOGS\n")
        fp.write(_build_appimage_process_out.decode())
        fp.write("\n\n")
        fp.write(SEPARATOR)
        fp.write(_build_appimage_process_err.decode())
        fp.write("Build exited with {}\n".format(
            _build_appimage_process_exit_code))

    if _build_appimage_process_exit_code != 0:
        spinner.fail("Packing failed")
        spinner.info("Check {} for build logs.".format(log_file))
        spinner.stop()
        return

    spinner.succeed("PyAppImage Succeeded.")
    spinner.succeed("Successfully built {} as {}".format(
        name, dest_appimage_output_name))
    spinner.stop()
    return
