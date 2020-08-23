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

### PyAppImage tutorial 


#### Packaging `appimagelint`

The `appimagelint`'s documentation, tells 
> appimagelint is a tool to check AppImage files for common issues.
> appimagelint runs a variety of checks on AppImages and reports the results in human-readable form in the console log.

So to get started 
1. This step is optional: create the AppImage on the oldest distro for full compatability. In this tutorial, I am going to use
   the oldest LTS version of Ubuntu, i.e Ubuntu Xenial aka 16.04
   ```bash
   docker pull ubuntu:16.04
   docker run -it ubuntu:16.04
   ```
2. Download `pyappimage`'s appimage for a specific python version. For my test case, I am using `python3.8` pyappimage.
   ```bash
   sudo apt update 
   sudo apt install file  # or else appimagetool will fail in future
   sudo apt install wget  # optional : to download pyappimage's appimage
   wget https://github.com/srevinsaju/pyappimage/releases/download/continuous/pyappimage-3.8-x86_64.AppImage
   chmod +x pyappimage*.AppImage
   ```

3. Cool. Now download the `appimagelint` source code.
   ```bash
   git clone https://github.com/TheAssassin/appimagelint
   cd appimagelint
   ```

4. Now make a folder called `pyappimage`
   ```bash
   mkdir pyappimage
   cd pyappimage
   touch pyappimage.json
   ```
5. Now edit the `pyappimage/pyappimage.json` file, to add the following content.
   ```json
   {
        "name": "appimagelint",
	"entrypoint": "appimagelint.cli:run",
        "categories": ["Utility"],
   }
   ```
   if you are curious on where `appimagelint.cli:run` came from, here, on the `setup.py`, there is a section called `console_scripts`, 
   this has something like this
   ```python
   entry_points={
        "console_scripts": [
            "appimagelint = appimagelint.cli:run",
        ],
    },
    ```
    So, I took the entrypoint from there.
    
    If you are trying to package your own application, this is how `entrypoint` works
    `appimagelint.cli:run` is translated to `from appimagelint.cli import run; run()`

6. Add `updateinformation` to json. Update information is a static link to a file to get `zsync` or update information
   i.e, the appimage you are bundling, can be delta updated. For more information on how to write `updateinformation`, 
   see [AppImage Docs updateinformation](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#update-information)
   
   My final json looks like this
   ```json
   {
        "name": "appimagelint",
        "entrypoint": "appimagelint.cli:run",
        "categories": ["Utility"],
        "updateinformation": "gh-releases-zsync|TheAssassin|appimagelint|latest|appimagelint*.AppImage.zsync",
   }
   ```
   
7. Bootstrap `pyappimage`. :tada: You are ready to build.
   The command to build Python AppImage is simple; 
   just
   ```bash
   ./pyappimage=*.AppImage build
   ```
   In case you are failing with a `libfuse` error, add the `--appimage-extract-and-run` option before `build`
   And you are done.
   
   
8. Test the generated AppImage, 
   The generated appimage, is called `appimagelint-x86_64.AppImage`
   Run it by
   ```python
   ./appimagelint-x86_64.AppImage --help
   ```
   
   But this would fail now. Because of an odd error
   ```python
	Traceback (most recent call last):
		File "entrypoint.py", line 12, in <module>
		File "appimagelint/cli.py", line 91, in run
			args = parse_args()
		File "appimagelint/cli.py", line 47, in parse_args
			action="version", version=get_version(),
		File "appimagelint/cli.py", line 18, in get_version
			version = pkg_resources.require("appimagelint")[0].version
		File "pkg_resources/__init__.py", line 899, in require
		File "pkg_resources/__init__.py", line 785, in resolve
	pkg_resources.DistributionNotFound: The 'appimagelint' distribution was not found and is required by the application
	[886] Failed to execute script entrypoint
	 ```
	 
	 Looking at the traceback, it looks like on `appimagelint/cli.py` at line 18, appimagelint is trying to call `pkg_resources.require`, 
	 which calls the `pip` data to see the version which was installed. But `pyappimage` does not bundle `pip` metadata. So we might need to replace that data
	 
	 So my patch looks like this:
```diff
diff --git a/appimagelint/cli.py b/appimagelint/cli.py
index e734440..5266e53 100644
--- a/appimagelint/cli.py
+++ b/appimagelint/cli.py
@@ -15,7 +15,7 @@ from .checks import IconsCheck, GlibcABICheck, GlibcxxABICheck, DesktopFilesChec
def get_version():
		 try:
				 import pkg_resources
-        version = pkg_resources.require("appimagelint")[0].version
+        version = '0.0.1'
		 except ImportError:
				 version = "unknown"
 ```
9. Try the build again to see if it works
   ```bash
	 ./pyappimage=*.AppImage build
   ```
   > In case you are failing with a `libfuse` error, add the `--appimage-extract-and-run` option before `build`
   And you are done.
	 
10. Attempt to run again. This time it fails with a different error
```bash
./appimagelint-x86_64.AppImage --appimage-extract-and-run
Traceback (most recent call last):
	File "PyInstaller/hooks/rthooks/pyi_rth__tkinter.py", line 20, in <module>
FileNotFoundError: Tcl data directory "/tmp/appimage_extracted_9f4f32b23bc1296b3cecfc7ea8798a69/appimagelint/tcl" not found.
[4342] Failed to execute script pyi_rth__tkinter
```
	
This is because Tcl and Tkinter are bundled in a different directory. To add them separately, you could add this to `pyappimage/pyappimage.json`

```json
{
	"name": "appimagelint",
	"entrypoint": "appimagelint.cli:run",
	"categories": ["Utility"],
	"updateinformation": "gh-releases-zsync|srevinsaju|appimagelint|latest|appimagelint*.AppImage.zsync",
	"add-data": ["$APPDIR/usr/share/tcltk/tk8.4:tk", "$APPDIR/usr/share/tcltk/tcl8.4:tcl"],
}
```
I added the folders for tk and tcl from their respective folders. You could append $APPDIR to add a folder from the `pyappimage-*.AppImage` to your compiled appimage. Or use absolute path, to copy from your host OS to the appimage.
	
11. Now run it again, And :tada: it works without errors now!
	



