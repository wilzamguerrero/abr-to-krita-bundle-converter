## Procreate to Krita Brush Converter

This is an experimental set of scripts to convert Procreate .brush and .brushset files, Photoshop .abr files, or Clip Studio Paint .sut files to Krita .kpp brush preset files. The scripts are __very unfinished and broken__. Do not expect properly functional brushes at this stage.

Due to differences in brush engines between the applications, there are limitations on what would be convertable even with a proper correct and finished implementation.

It is called "Procreate to Krita Brush Converter" as it originally only supported Procreate .brush files.

### Usage

The main scripts are written in standard Python. They are meant to be run from the command line.

However, it can also be used as a Krita plugin with a very basic GUI and functionality limited to conversion of Procreate brushes.
The GUI script requires PyQt5 or PyQt6.

#### procreate_to_kpp.py

The Procreate to Krita brush converter itself, which relies on the other scripts.
It can be given an input KPP file to copy the base for the settings from, but it's not required.

`python3 /pathto/procreate_to_kpp.py /pathto/example.brush --input /pathto/template.kpp /pathto/example.kpp`
where example.brush is a Procreate brush file, and template.kpp is a Krita brush preset file whose settings will be copied to the new preset example.kpp, and then modified by the script.

`python3 /pathto/procreate_to_kpp.py /pathto/example.brushset /pathto/output/`
Same as above, but without a template, and each brush in the brushset will be converted and output into the /pathto/output/ folder as [brushfilepath].kpp.

`python3 /pathto/procreate_to_kpp.py /pathto/example.brushset /pathto/output/ --bundle /pathto/output/example.bundle`
Same as above, but each preset will also be output into example.bundle.

Note: Using a bundle is the *recommended way*, to make sure brushtip and texture work in Krita versions older than 5.2.9.

Note2: If the script outputs a warning about requiring external resources, that means the brushtip/texture is (probably) not contained in the .brush file and will be missing.

#### procreate/procreate_brush_parser.py

Used for examining Procreate .brush or .brushset files.

`python3 /pathto/procreate_brush_parser.py /pathto/example.brush --dump_plist /pathto/example.txt`
Dumps the raw brush settings of example.brush in plaintext dictionary form to example.txt. This does not include any embedded resources (thumbnail, brushtips, patterns, etc), which may be manually extracted by renaming the file to example.brush.zip.

`python3 /pathto/procreate_brush_parser.py /pathto/example.brushset --dump_plist /pathto/output/`
Same as --dump_plist above, but dumps the settings of each brush in a .brushset into files called [brushfilepath].txt in a folder /pathto/output/.

`python3 /pathto/procreate_brush_parser.py /pathto/example.brush --setting authorName`
Prints the fetched value of the "authorName" setting of example.brush. Setting names can be found in procreate_to_kpp.py or in a dumped brush file. If used with a .brushset, prints the name of each brush before its value.

`python3 /pathto/procreate_brush_parser.py /pathto/example.brush --setting_curve dynamicsPressureSizeCurve`
Same as --setting above, but for curves.

#### kpp/kpp_brush_parser.py

Used for examining Krita .kpp (Krita PaintOp Preset) files.

`python3 /pathto/kpp_brush_parser.py /pathto/example.kpp --dump_xml /pathto/example.xml`
Dumps the raw brush settings of example.kpp in plaintext XML form to example.xml. This **does** include any embedded resources (brushtips, patterns) in the text output, so take care.

#### converter_gui.py

Basic GUI frontend for procreate_to_kpp.py.

It remembers its settings in a `settings.ini` file stored next to the script.

#### abr_to_kpp.py

The A(dobe Photoshop) BR(ush) to Krita brush converter itself, which relies on the other scripts.

`python3 /pathto/abr_to_kpp.py /pathto/example.abr --bundle /pathto/output/example.bundle`
where example.abr is the ABR file to convert and example.bundle is the new Krita resource bundle to create with any brush presets, brushtips, and patterns found.

`python3 /pathto/abr_to_kpp.py /pathto/example.abr --output /pathto/output/ --bundle /pathto/output/example.bundle`
Same as above, but /pathto/output/ is a folder where brushes minus brushtips or patterns will be output.

`python3 /pathto/abr_to_kpp.py pathto/example.abr --input /pathto/template.kpp --output /pathto/output/ --bundle /pathto/output/example.bundle`
Same as above, but template.kpp is a Krita brush preset file whose settings will be copied to the new presets.

#### abr/abr_parser.py

Used for examining A(dobe Photoshop) BR(ush) files.

`python3 /pathto/abr_parser.py /pathto/example.abr --dump_path /pathto/example.txt`
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
