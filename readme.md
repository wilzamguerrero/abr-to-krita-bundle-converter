# ABR to Krita Bundle Converter

Convert Photoshop `.abr` brush files into Krita resource bundles (`.bundle`) — ready to import directly into Krita.

Each brush becomes a Krita paintop preset (`.kpp`) with its brushtip as thumbnail, and all presets are automatically tagged with the ABR filename so they're easy to find inside Krita.

## Features

- Converts all brushes from an `.abr` file (Photoshop brush format v6–10)
- Extracts brushtip images and patterns and includes them in the bundle
- Uses the brushtip image as the preset thumbnail preview
- Tags all presets with the ABR filename for easy filtering in Krita
- Simple GUI with progress bar, available as a Krita plugin

## Installation

1. Copy the `abr_to_krita_bundle_converter/` folder and `abr_to_krita_bundle_converter.desktop` to your Krita Python plugins folder:
   - **Linux:** `~/.local/share/krita/pykrita/`
   - **Flatpak:** `~/.var/app/org.kde.krita/data/krita/pykrita/`
2. Restart Krita
3. Enable it in **Settings → Configure Krita → Python Plugin Manager → ABR to Krita Bundle Converter**

## Usage

### As a Krita plugin

1. Go to **Tools → Scripts → Convert ABR brushes to bundle...**
2. Click the folder icon and select your `.abr` file
3. Click **Convert**

The `.bundle` file is saved in the same folder as the `.abr` file with the same name.

4. Import the bundle in Krita via **Settings → Manage Resources → Import Bundle/Resource**

### From the command line

```bash
python3 abr_to_krita_bundle_converter/abr_to_kpp.py file.abr --bundle output.bundle
```

Optional flags:
- `--output /path/to/folder/` — also save individual `.kpp` files
- `--input template.kpp` — use an existing KPP as the base settings

## Requirements

- Python 3.10+
- [Pillow](https://pypi.org/project/Pillow/) (`pip install Pillow`)
- PyQt5 or PyQt6 (included with Krita)

## Notes

- Sampled brushes (most ABR brushes) will show the actual brushtip as thumbnail
- Parametric/computed brushes will show a generic thumbnail
- Patterns with errors are skipped; the rest of the conversion continues normally

## Credits

Based on [procreate-to-krita-brush-converter](https://invent.kde.org/freyalupen/procreate-to-krita-brush-converter/) by **Freya Lupen**, licensed under GPL-3.0-or-later.

This fork focuses on Photoshop ABR brush conversion and adds a simplified GUI with progress feedback.

## License

GPL-3.0-or-later
Same as above, but also dumps any material data found into folders with the brushes' names in the folder /pathto/output/.
