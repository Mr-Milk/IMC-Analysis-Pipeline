import os
import re
import shutil
from pathlib import Path
from typing import Union, List, Tuple
from urllib.request import urlopen

import pandas as pd
from PIL import Image
from imctools.converters import ome2analysis
from imctools.io.imc.imcwriter import ImcWriter
from imctools.io.mcd.mcdparser import McdParser

File = Union[Path, str]

CP_PIPE1 = "https://raw.githubusercontent.com/Mr-Milk/IMC-Analysis-Pipeline/main/cp4-pipe/1-prepare-ilastik.cppipe"
CP_PIPE2 = "https://raw.githubusercontent.com/Mr-Milk/IMC-Analysis-Pipeline/main/cp4-pipe/2-segment_ilastik.cppipe"


def generate_scaffold(output_folder: File) -> None:
    """Create a scaffold under the output_folder

    :param output_folder:

    """
    for i in ['ilastik', 'info', 'analysis', 'spatialtis', 'cp_pipelines']:
        (output_folder / Path(i)).mkdir(exist_ok=True, parents=True)

    for url, pipe in zip([CP_PIPE1, CP_PIPE2], ["1-prepare-ilastik.cppipe", "2-segment_ilastik.cppipe"]):
        response = urlopen(url).read().decode('utf-8')
        with open(output_folder / 'cp_pipelines' / pipe, "w") as dest_file:
            dest_file.write(response)


def mcdfile2ome(mcdfile: File) -> Path:
    mcdfile = Path(mcdfile)
    ome_folder = mcdfile.parent / Path(mcdfile.stem + '-ome')

    mcd_parser = McdParser(mcdfile)
    imc_writer = ImcWriter(ome_folder, mcd_parser)
    imc_writer.write_imc_folder(create_zip=False)

    return ome_folder


def mcd2analysis(mcdfiles: List,
                 output_folder: File,
                 panel_csv: File,
                 analysis_stacks: Tuple,
                 metal_column: str,
                 low_dim_filter: int = 200,
                 ) -> None:
    output_folder = Path(output_folder)
    analysis_folder = output_folder / 'analysis'
    info_folder = output_folder / 'info'
    generate_scaffold(output_folder)

    for mcdfile in mcdfiles:
        ome_folder = mcdfile2ome(mcdfile)
        ome2analysis.omefolder_to_analysisfolder(
            ome_folder,
            analysis_folder,
            panel_csv_file=panel_csv,
            analysis_stacks=analysis_stacks,
            metalcolumn=metal_column)
        shutil.rmtree(ome_folder)

    fn = next(analysis_folder.glob(f'*{analysis_stacks[1][1]}.csv'))
    shutil.copy(fn, info_folder / 'full_channelmeta.csv')

    for img in (output_folder / 'analysis').glob("*.tiff"):
        (w, h) = Image.open(img).size
        if (w <= low_dim_filter) & (h < low_dim_filter):
            try:
                os.remove(img)
                os.remove(f"{'/'.join(img.parts[0:-1])}/{img.stem}.csv")
            except Exception as e:
                pass


def create_spatialtis_folder(output_folder: File) -> None:
    output_folder = Path(output_folder)
    mask_img = {re.search(r'(.*?)_seg', f.name)[1]: f for f in (output_folder / 'analysis').glob("*_mask*")}
    full_img = {re.search(r'(.*?)_full', f.name)[1]: f for f in (output_folder / 'analysis').glob("*_full*")}

    spatialtis_folder = output_folder / 'spatialtis'
    spatialtis_folder.mkdir(exist_ok=True)
    for i, (k, v) in enumerate(mask_img.items()):
        dest = spatialtis_folder / k
        dest.mkdir(exist_ok=True)
        shutil.copy(v, dest)
        shutil.copy(full_img[k], dest)
    print(f"The entry for sptialtis is at {spatialtis_folder}")


def panel_csv_checker(panel_csv: File, metal_column: str) -> Path:
    panel_csv = Path(panel_csv)
    checked_csv = panel_csv.parent / f"{panel_csv.stem}_checked.csv"

    meta = pd.read_csv(panel_csv)
    meta['channel_number'] = [int(re.search(r'\d.*', i)[0]) for i in meta[metal_column]]
    meta['metal_name'] = [re.search(r'[a-zA-Z]{2}', i)[0] for i in meta[metal_column]]
    meta = meta.sort_values('channel_number')
    meta[metal_column] = [m + str(c) for m, c in meta[['metal_name', 'channel_number']].values]

    del meta['channel_number']
    del meta['metal_name']

    meta.to_csv(checked_csv)

    return checked_csv
