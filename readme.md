# ABR to Krita Bundle Converter

Convert Photoshop `.abr` brush files into Krita resource bundles (`.bundle`).

## Installation

1. Copy the `abr_to_krita_bundle_converter/` folder and `abr_to_krita_bundle_converter.desktop` to your Krita Python plugins folder:
   - **Linux:** `~/.local/share/krita/pykrita/`
   - **Flatpak:** `~/.var/app/org.kde.krita/data/krita/pykrita/`
2. Restart Krita
3. Enable it in **Settings → Configure Krita → Python Plugin Manager → ABR to Krita Bundle Converter**

## Usage

1. Go to **Tools → Scripts → Convert ABR brushes to bundle...**
2. Select your `.abr` file
3. Click **Convert** — the `.bundle` is saved in the same folder as the `.abr` file
4. Import it in Krita via **Settings → Manage Resources → Import Bundle/Resource**

## Credits

Based on [procreate-to-krita-brush-converter](https://invent.kde.org/freyalupen/procreate-to-krita-brush-converter/) by **Freya Lupen** (GPL-3.0-or-later).

## License

GPL-3.0-or-later
Same as above, but also dumps any material data found into folders with the brushes' names in the folder /pathto/output/.
