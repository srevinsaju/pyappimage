# Tutorial II : Packaging Archivy
[Archivy](https://github.com/Uzay-G/archivy) is a cool
 Flask app that can be used to make
notes using Markdown and web interface, supporrted 
by an ElasticSearch engine

## Getting Started
1. Get started on a very old Linux distros, or 
an ubuntu 16.04 docker image

2. Now clone the source code of `archivy`
```bash
git clone https://github.com/Uzay-G/archivy
cd archivy
```

3. Add a `pyappimage/pyappimage.json`. this file is
a configuration file for PyAppImage to know what to build, etc.
```json
{
  "name": "archivy",
  "categories": ["Utility"],
  "
```
3. Build the AppImage by downloading and running 
`pyappimage-*.AppImage`
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

4. :tada:, you created an AppImage successfully!
Let's test it
```bash
./archivy-*.AppImage
```

Wow! It loads the flask server! Let's open the link 0.0.0.0
Now it raises a Jinja2 Template Error. This is because the 
`static`, `template` and `assets` directory is not copied
to the AppImage directly. Pyappimage only converts static
Python source code to binaries. So you have to selectively
add them to the `pyappimage/pyappimage.json`
