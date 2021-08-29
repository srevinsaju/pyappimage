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
import shutil
import sys

import click
from .version import __version__
from . import __doc__ as lic
from .build.build import build as pyappimage_build
from .utils import (
    get_input_else_default,
    verify_bundle_id,
    verify_categories,
    verify_entrypoint,
)

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import yaml


def show_version(ctx, param, value):
    """Prints the version of the utility"""
    if not value or ctx.resilient_parsing:
        return
    click.echo("PyAppImage")
    click.echo("version: {}".format(__version__))
    ctx.exit()


def show_license(ctx, param, value):
    """Prints the license of the utility"""
    if not value or ctx.resilient_parsing:
        return
    click.echo(lic)
    ctx.exit()


def is_fuse_supported():
    if os.path.exists(os.path.join("/", ".dockerenv")):
        # detected docker
        print("Detected Docker container")
        return False
    elif shutil.which("fusermount") is not None:
        # assume fuse support
        print("fusermount detected on host system.")
        return True
    else:
        return False


@click.group()
@click.option(
    "--version", is_flag=True, callback=show_version, expose_value=False, is_eager=True
)
@click.option(
    "--license",
    "--lic",
    is_flag=True,
    callback=show_license,
    expose_value=False,
    is_eager=True,
)
def cli():
    """PyAppImage: A command line interface to create Python AppImages"""

    pass


@cli.command()
def generate():
    try:
        os.mkdir("pyappimage")
    except FileExistsError:
        print("`pyappimage` directory already exists!")

    name = get_input_else_default(
        default="hello_world", description="Enter the name of your AppImage", _type=str
    )
    bundle_id = get_input_else_default(
        default=f"com.example.{'_'.join(name.lower().split())}",
        description="Enter your AppImage's bundle id",
        _type=str,
        verify=verify_bundle_id,
    )
    categories = get_input_else_default(
        default="Utility",
        description="Enter the category to which your appimage belongs to",
        _type=str,
        verify=verify_categories,
    ).split(";")
    entrypoint = get_input_else_default(
        default=f"{bundle_id.split('.')[-1]}.__main__:main",
        description="Enter your python application's console entrypoint",
        _type=str,
        verify=verify_entrypoint,
    )
    icon = get_input_else_default(
        default=os.path.join(os.path.dirname(__file__), "assets", "pyappimage.png"),
        description="Enter the path to your logo",
        _type=str,
        verify=os.path.exists,
    )
    pyappimage_yml = os.path.join("pyappimage", "pyappimage.yml")
    _data = {
        "name": name,
        "bundle_id": bundle_id,
        "entrypoint": entrypoint,
        "categories": categories,
    }
    with open(pyappimage_yml, "w") as fp:
        yaml.dump(_data, fp)
    print(yaml.dump(_data))
    print()
    print("Copying icons")
    shutil.copy2(icon, "pyappimage", follow_symlinks=True)
    print(f"Written to {pyappimage_yml}.")


@cli.command()
@click.option(
    "-f",
    "--always-confirm/--noconfirm",
    "force",
    default=False,
    help="Do not ask for confirmation",
)
def build(force=False):
    """Build an Python AppImage"""
    for path in (".", "pyappimage"):
        if os.path.isdir(os.path.realpath(path)):
            pyappimage_yml = os.path.join(path, "pyappimage.yml")
            if os.path.exists(pyappimage_yml):
                with open(pyappimage_yml, "r") as r:
                    config = yaml.load(r, Loader=Loader)
                name = config.get("name")
                for image_type in ("png", "svg"):
                    _icon = os.path.join(
                        path, "{appname}.{type}".format(appname=name, type=image_type)
                    )
                    if os.path.exists(_icon):
                        icon_path = _icon
                        break
                else:
                    print(
                        "Warning: No icon file was provided. The default "
                        "Python icon will be used. To add an icon, place a "
                        "{appname}.svg or {appname}.png in {path}".format(
                            appname=name, path=path
                        )
                    )
                    icon_path = os.path.join(
                        os.path.dirname(__file__), "assets", "pyappimage.png"
                    )

                _appdata = os.path.join(path, "{}.appdata.xml".format(name))
                if os.path.exists(_appdata):
                    appdata = _appdata
                else:
                    print(
                        "Warning: No Appdata file provided. Please add {} "
                        "for desktop integration, and indexing.".format(_appdata)
                    )
                    appdata = None
                _desktop_file = os.path.join(path, "{}.desktop")
                if os.path.exists(_desktop_file):
                    desktop_file = _desktop_file
                else:
                    desktop_file = None
                break
    else:
        print("Could not find a valid pyappimage.yml")
        print(
            "Please create pyappimage.yml in ./pyappimage folder or at "
            "the root directory"
        )
        print("\nAlternatively, interactively generate a pyappimage file by:")
        print("\n\t $ pyappimage generate\n")
        sys.exit(1)
    if not os.path.exists("setup.py") and not os.path.exists("pyproject.toml"):
        print("Could not find setup.py or pyproject.toml in {}".format(os.getcwd()))
        print(
            "Make sure that the setup.py or pyproject.toml exists in the current directory, "
            "and run this command again."
        )
        sys.exit(1)

    build_directory = os.path.realpath("{}.AppDir.BUILD".format(name))
    dist_directory = os.path.realpath("{}.AppDir".format(name))
    if force:
        shutil.rmtree(build_directory)
        shutil.rmtree(dist_directory)
    for dir in (build_directory, dist_directory):
        if os.path.exists(dir):
            cf = click.confirm("{} exists. Do you want to overwrite it?".format(dir))
            if cf:
                shutil.rmtree(dir)
            elif dir != build_directory:
                print("Aborted!")
                sys.exit(0)
    pyappimage_build(
        config,
        appdata=appdata,
        icon=icon_path,
        desktop_file=desktop_file,
        has_fuse=is_fuse_supported(),
    )
    print("done!")


if __name__ == "__main__":
    cli()
