# Tutorial II : Packaging Archivy
[Archivy](https://github.com/Uzay-G/archivy) is a cool Flask app that can be used to make notes using Markdown and web interface, supporrted by an ElasticSearch engine

## Getting Started
1. Get started on a very old Linux distros, or an ubuntu 16.04 docker image

2. Now clone the source code of `archivy`
```bash
git clone https://github.com/Uzay-G/archivy
cd archivy
```

3. Add a `pyappimage/pyappimage.json`. this file is a configuration file for PyAppImage to know what to build, etc.
```json
{
  "name": "archivy",
  "categories": ["Utility"],
  "entrypoint": "archivy.run:main",
  "updateinformation": "gh-releases-zsync|Uzay-G|archivy|latest|archivy*.AppImage.zsync",
}
```
3. Build the AppImage by downloading and running `pyappimage-*.AppImage`
```bash
wget https://github.com/srevinsaju/pyappimage/releases/continuous/pyappimage-3.8-x86_64.AppImage
chmod +x *.AppImage
# build the AppImage
./pyappimage-*.AppImage build
# or if the AppImage is complaining of libfuse, then
export APPIMAGE_EXPORT_AND_RUN=1 
./pyappimage-*.AppImage build
# or alternatively pass the --appimage-extract-and-run flag
```

4. :tada:, you created an AppImage successfully! Let's test it
```bash
./archivy-*.AppImage
```

Wow! It loads the flask server! 

Let's open the link 0.0.0.0. But, now it raises a Jinja2 Template Error. This is because the `static`, `template` and `assets` directory is not copied to the AppImage directly. Pyappimage only converts static Python source code to binaries. So you have to selectively add them to the `pyappimage/pyappimage.json`

```json
{
        "name": "archivy",
        "entrypoint": "archivy.run:main",
        "categories": ["Utility"],
        "updateinformation": "gh-releases-zsync|srevinsaju|archivy|latest|appimagelint*.AppImage.zsync",
        "pyappimage_data": ["$CWD/archivy/static:$APPIMAGE/static", "$CWD/archivy/templates:$APPIMAGE/templates", "/root/git/archivy/assets:$APPIMAGE/assets"]
}
```

`pyappimage_data` is a json configuration data, which copies the data from `$CWD` , which is the abbreviation for Current Working Directory to the `$APPIMAGE` which is the AppImage directory, before it is compiled to a standalone AppImage. But, Flask still doesn't know where to search for the `templates` and `static` folder. So you have to manually instruct `Flask` to load `templates` and `static` from their APPIMAGE folder directory.

```diff
diff --git a/archivy/__init__.py b/archivy/__init__.py
index 3a8575e..bc3c819 100644
--- a/archivy/__init__.py
+++ b/archivy/__init__.py
@@ -1,5 +1,6 @@
 import elasticsearch
 import subprocess
+import os
 from pathlib import Path
 from threading import Thread
 
@@ -11,7 +12,8 @@ from archivy import data
 from archivy.config import Config
 from archivy.check_changes import run_watcher
 
-app = Flask(__name__)
+app = Flask(__name__, template_folder=os.path.join(os.getenv('APPDIR'), 'templates'),
+        static_folder=os.path.join(os.getenv('APPDIR'), 'static'))
 app.config.from_object(Config)
 
 # create dir that will hold data if it doesn"t already exist

```

See, the `app = Flask(__name__)` was replaced to provide the `template_folder` and `static_folder` paths. `$APPDIR` is an environment variable which is defined when an appimage is run. It points to the root of the Squash Fuse File System. Alternatively, its also possible to provide environment variables in the json file. 

```json
{
        "name": "archivy",
        "entrypoint": "archivy.run:main",
        "categories": ["Utility"],
        "updateinformation": "gh-releases-zsync|srevinsaju|archivy|latest|appimagelint*.AppImage.zsync",
        "environment_vars": {
            "LD_LIBRARY_PATH": "/path/to/something",
            "ARCHIVY_TEMPLATE_DIR": "$APPDIR/templates"
        }
}
```

And you are done!





