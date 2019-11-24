![Map Stitcher](./assets/logo.png)

# Table of Contents

- [Overview](#overview)
- [Examples](#examples)
- [Dependencies](#dependencies)
- [Attribution](#attribution)
- [License](#license)

# Overview
Map stitcher is a simple script that is configured to download tiled map layers, and stitch them together to create a world map.

# Examples
To test map stitcher with the provided example.yaml config, run the following command
```
python main.py --config example.yaml --file-ext .jpg
```

This will create a world map in the directory
```
CURRENT_DIRECTORY/output/EPOCH_TIME/world-map.jpg
```

Please run ```python main.py -h``` to see more advanced runtime options

# Dependencies
* python 3.6
* jinja2
* progressbar2
* pillow
* pyyaml

Execute the following to install the previously mentioned dependencies

```
pip3 install jinja2
pip3 install progressbar2
pip3 install pyyaml
pip3 install Pillow
```

# Attribution
* <https://pyyaml.org/wiki/PyYAML>
* <https://pypi.org/project/progressbar2/>
* <https://github.com/python-pillow/Pillow>
* <https://github.com/pallets/jinja>

# License
Apache License, Version 2.0. See LICENSE file.