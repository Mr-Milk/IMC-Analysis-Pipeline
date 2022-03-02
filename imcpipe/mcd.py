from pathlib import Path
from typing import Optional, Union, List, Dict

from imctools.io.imc.imcwriter import ImcWriter
from imctools.io.mcd.mcdparser import McdParser

from imcpipe.utils import create_folder, File


def mcd2ome(mcdfile: File,
            export: File,
            min_height: int = 10,
            min_width: int = 10,
            metadata: bool = False,
            slide: bool = False,
            channels: Optional[List[str]] = None,
            verbose: bool = False
            ):
    """Convert `.mcd` to `.ome.tiff` file

    Args:
        mcdfile:
        export:
        min_height:
        min_width:
        metadata:
        slide:
    """
    mcdfile = Path(mcdfile)
    export = Path(export)

    mcd_parser = McdParser(mcdfile)
    session = mcd_parser.session

    if export.is_file():
        raise NotADirectoryError(f"Cannot export to {export}, not a directory.")
    create_folder(export)

    mcd_xml = mcd_parser.get_mcd_xml()
    if metadata:
        meta_folder = create_folder(export / 'metadata')
        # Save XML metadata if available
        if mcd_xml is not None:
            with open(meta_folder / (session.metaname + "_schema.xml"), "wt") as f:
                f.write(mcd_xml)
        # Save session data in json
        session.save(meta_folder / (session.metaname + "_session.json"))

    if slide:
        slide_folder = create_folder(export / 'slide')
        for key in session.slides.keys():
            mcd_parser.save_slide_image(key, slide_folder)
        for key in session.panoramas.keys():
            mcd_parser.save_panorama_image(key, slide_folder)

    # Save acquisition images in OME-TIFF format
    for acquisition in session.acquisitions.values():
        if not ((acquisition.max_x < min_width) | (acquisition.max_y < min_height)):
            acquisition_data = mcd_parser.get_acquisition_data(acquisition.id)
            if acquisition_data.is_valid:
                # Calculate channels intensity range
                valid_channels = []
                for ch in acquisition.channels.values():
                    img = acquisition_data.get_image_by_name(ch.name)

                    if img is not None:
                        valid_channels.append(ch.name)
                #         ch.min_intensity = round(float(img.min()), 4)
                #         ch.max_intensity = round(float(img.max()), 4)

                export_name = f"{session.name}_slide{acquisition.slide.id}_ROI{acquisition.id}"
                export_name = export_name.replace(" ", "_")
                export_name = export_name.replace(".", "_")
                export_name += ".ome.tiff"
                if verbose:
                    print(f"{len(valid_channels)} channels in {export_name}", ", ".join(valid_channels))

                acquisition_data.save_ome_tiff(
                    export / export_name,
                    xml_metadata=mcd_xml,
                    names=channels,
                )
