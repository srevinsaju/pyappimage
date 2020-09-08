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
import platform
import shlex
import shutil
import subprocess
import sys
import time

from pathlib import Path
from PyInstaller import __main__ as PyInstaller
from halo import Halo

from ..constants import APPRUN, DESKTOP_FILE, ENTRYPOINT, SEPARATOR
from ..utils import replace_vars
from ..version import __version__
from zap.zap import Zap
_ = shlex.split


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


def get_parameters(config, _vars):

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
                if '$APPDIR' in i:
                    i_proc = replace_vars(i, _vars)
                else:
                    i_proc = i
                kwargs.append("--{key}={arg}".format(key=key, arg=i_proc))
        else:
            if '$APPDIR' in config[key]:
                i_proc = replace_vars(config[key], _vars)
            else:
                i_proc = config[key]
            kwargs.append("--{key}={arg}".format(key=key, arg=i_proc))

    return kwargs

def install_additional_requirements(requirements, build_directory):
    if os.getenv('APPIMAGE'):
        pip = os.getenv('PYAPPIMAGE_PIP')
    else:
        pip = "{python} -m pip".format(python=get_executable_path('python3'))

    _pip_install_proc = subprocess.run(_(
        "{pip} install --prefix={build} --ignore-installed {req}".format(
            pip=pip,
            build=build_directory,
            req=' '.join(requirements)
        )
    ), capture_output=True)
    log_file = os.path.join(build_directory, 'PIP_REQ.log')
    with open(log_file, 'w') as fp:
        fp.write("PyAppImage v{}\n".format(__version__))
        fp.write(SEPARATOR)
        fp.write("PIP LOGS: \n")
        fp.write(_pip_install_proc.stdout.decode())
        fp.write("\n\n")
        fp.write(SEPARATOR)
        if _pip_install_proc.stderr is not None:
            fp.write(_pip_install_proc.stderr.decode())
        fp.write("Build exited with {}\n".format(
            _pip_install_proc.returncode))

    _pip_install_proc.check_returncode()


def install_packages(setup_py, build_directory):
    if os.getenv('APPIMAGE'):
        pip = os.getenv('PYAPPIMAGE_PIP')
    else:
        pip = "{python} -m pip".format(python=get_executable_path('python3'))
    _pip_install_proc = subprocess.run(_(
        "{pip} install --prefix={build} {proj_dir}".format(
            pip=pip,
            build=build_directory,
            proj_dir=os.path.dirname(setup_py)
        )
    ), capture_output=True)
    log_file = os.path.join(build_directory, 'PIP.log')
    with open(log_file, 'w') as fp:
        fp.write("PyAppImage v{}\n".format(__version__))
        fp.write(SEPARATOR)
        fp.write("PIP LOGS: \n")
        fp.write(_pip_install_proc.stdout.decode())
        fp.write("\n\n")
        fp.write(SEPARATOR)
        if _pip_install_proc.stderr is not None:
            fp.write(_pip_install_proc.stderr.decode())
        fp.write("Build exited with {}\n".format(
            _pip_install_proc.returncode))

    _pip_install_proc.check_returncode()
    _sp = list(Path(build_directory)
               .glob('lib/python*/site-packages'))[0].resolve()
    return _sp


def build(config, icon, appdata=None, desktop_file=None, has_fuse=True):
    entrypoint = config.pop("entrypoint")
    name = config.pop('name', 'Python')
    generic_name = config.pop('generic-name', name)
    description = config.pop('description', 'Python app generated using '
                                            'PyAppImage')
    ignored_binaries = config.pop('ignore-binaries', [])
    categories = config.pop('categories', [])
    requirements = config.pop('requirements', [])
    pyappimage_data = config.pop('data', None)
    environment_vars = config.pop('environment', None)
    updateinformation = config.pop('updateinformation')
    setup_py = os.path.realpath('setup.py')
    if not os.path.exists(setup_py):
        raise FileNotFoundError("Could not find a setup.py in the current "
                                "directory!")

    build_started_at = time.asctime()
    spinner = Halo("Building AppImage for {} ".format(name), spinner="dots")
    spinner.start()
    build_directory = os.path.realpath("{}.AppDir.BUILD".format(name))
    dist_directory = os.path.realpath("{}.AppDir".format(name))

    # internal function to generate_vars
    _vars = {
        "APPDIR": os.getenv('APPDIR', ''),
        "BUILD": build_directory,
        "CWD": os.getcwd(),
        "ROOT": os.path.realpath('/'),
        "APPIMAGE": dist_directory
    }

    _pyinstaller_workpath = os.path.join(build_directory, 'build')
    for i in (build_directory, dist_directory, _pyinstaller_workpath):
        if not os.path.exists(i):
            os.makedirs(i)

    _import, _function = entrypoint.split(':')
    entrypoint = "from {mod} import {func}; {func}()".format(
        mod=_import, func=_function)

    with open(os.path.join(build_directory, "entrypoint.py"), 'w') as w:
        w.write(ENTRYPOINT.format(
            pyappimage_version=__version__,
            python_runtime=sys.version.split('\n')[0],
            platform_version=platform.platform(),
            entrypoint=entrypoint
        ))

    site_packages = \
        install_packages(setup_py=setup_py, build_directory=build_directory)
    
    if len(requirements) >= 1:
        install_additional_requirements(requirements, build_directory)

    PyInstaller.run(_(
        "{build}/entrypoint.py --log-level=WARN --name={name} "
        "--onedir {kwargs} --distpath={dist} --specpath={workpath} "
        "--workpath={workpath} --paths={site_packages} "
        "--noconfirm --clean".format(
            name=name,
            entrypoint=entrypoint,
            kwargs=' '.join(get_parameters(config, _vars)),
            dist=dist_directory,
            build=build_directory,
            workpath=_pyinstaller_workpath,
            site_packages=site_packages
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

    if pyappimage_data is not None:
        for src in pyappimage_data:
            dest = pyappimage_data[src]
            src_fmt = replace_vars(src, _vars)
            dest_fmt = replace_vars(dest, _vars)
            src_data = os.path.realpath(src_fmt)
            dest_folder = os.path.realpath(dest_fmt)
            os.makedirs(dest_folder, exist_ok=True)
            if os.path.isdir(src_data):

                shutil.copytree(src_data, dest_folder, symlinks=True,
                                dirs_exist_ok=True)
            else:
                shutil.copy(src_data, dest_folder, follow_symlinks=True)

    env_vars = []
    if environment_vars is not None:
        for var in environment_vars:
            env_vars.append('export {}={}'.format(var, environment_vars[var]))

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
        w.write('\n'.join(env_vars))  # add the environment variables
        w.write("\n${APPDIR}/" + name + "/" + name + " $@")  # add the binary
        # entrypoint

    # chmod the apprun on 755
    os.chmod(path_to_apprun, 0o755)

    _libz = os.path.join(dist_directory, name, 'libz.so.1')
    if os.path.exists(_libz):
        os.remove(_libz)

    _libs_path = os.path.join(dist_directory, name)
    for lib in ignored_binaries:
        for i in Path(_libs_path).glob(lib):
            print("Unlinking {}".format(i))
            i.unlink(missing_ok=True)

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
