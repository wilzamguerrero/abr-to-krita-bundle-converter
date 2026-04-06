## ABR to Krita Bundle Converter

A tool to convert Photoshop `.abr` brush files to Krita resource bundles (`.bundle`).

Each brush is converted to a Krita paintop preset (`.kpp`), with its brushtip image used as the preset thumbnail. All presets are tagged with the name of the source ABR file for easy organization inside Krita.

### Features

- Converts all brushes from an `.abr` file (Photoshop brush format v6–10)
- Extracts brushtip images and patterns and includes them in the bundle
- Uses the brushtip image as the KPP thumbnail preview
- Tags all presets with the ABR filename for easy filtering in Krita
- Progress bar during conversion

### Installation (Krita plugin)

1. Copy the `abr_to_krita_bundle_converter/` folder and `abr_to_krita_bundle_converter.desktop` file to your Krita Python plugins folder:
   - Linux: `~/.local/share/krita/pykrita/`
   - Flatpak: `~/.var/app/org.kde.krita/data/krita/pykrita/`
2. Restart Krita
3. Enable the plugin in **Settings → Configure Krita → Python Plugin Manager → ABR to Krita Bundle Converter**

### Usage (Krita plugin)

1. Open the converter from **Tools → Scripts → Convert ABR brushes to bundle...**
2. Select your `.abr` file
3. Click **Convert** — the bundle is saved automatically in the same folder with the same name (e.g. `MyBrushes.abr` → `MyBrushes.bundle`)
4. Import the bundle in Krita via **Settings → Manage Resources → Import Bundle**

### Usage (command line)

```
python3 abr_to_krita_bundle_converter/abr_to_kpp.py /path/to/example.abr --bundle /path/to/output.bundle
```

Optional flags:
- `--output /path/to/folder/` — also save individual `.kpp` files to a folder
- `--input /path/to/template.kpp` — use an existing KPP as settings base

### Requirements

- Python 3.10+
- Pillow (`pip install Pillow`)
- PyQt5 or PyQt6 (for the Krita plugin GUI)

### Notes

- Brushes with sampled brushtips (the majority) will show the actual brushtip image as the preset thumbnail
- Parametric/computed brushes will show a generic thumbnail
- Patterns with encoding errors are skipped but the rest of the conversion continues

Dumps the raw brush settings of every brush in example.abr in a single plaintext dictionary form to example.txt.

`python3 /pathto/abr_parser.py /pathto/example.abr --dump_path /pathto/example.txt --dump_images_path /pathto/output/`
Same as above, but also dumps any brushtips or patterns found into the folder /pathto/output/ as PNG files.

#### sut_to_kpp.py

The Clip Studio Paint SU(b) T(ool) to Krita brush converter itself, which relies on the other scripts.

`python3 /pathto/abr_to_kpp.py /pathto/example.sut --output /pathto/output/example.kpp`
where example.sut is the SUT file to convert and example.kpp is the new brush preset, with any brushtip or pattern embedded.

`python3 /pathto/abr_to_kpp.py /pathto/example.sut --input /pathto/template.kpp --output /pathto/output/example.kpp`
Same as above, but template.kpp is a Krita brush preset file whose settings will be copied to the new presets.

`python3 /pathto/abr_to_kpp.py /pathto/examples/ --bundle /pathto/output/example.bundle`
where /pathto/examples/ is a folder containing .sut files, and example.bundle is the new Krita resource bundle to create with the brush presets.

#### sut/sut_parser.py

Used for examining Clip Studio Paint SU(b) T(ool) files.

`python3 /pathto/sut_parser.py /pathto/example.sut --dump_path /pathto/example.txt`
Dumps key/values from the database of example.sut to a text file example.txt. BLOB values in the database are attempted to be parsed.

`python3 /pathto/sut_parser.py /pathto/examples/ --dump_path /pathto/output/`
Dumps key/values of .sut files in /pathto/examples to text files in /pathto/output/.

`python3 /pathto/sut_parser.py /pathto/examples/ --dump_path /pathto/output/ --dump_images_path /pathto/output/`
Same as above, but also dumps any material data found into folders with the brushes' names in the folder /pathto/output/.
