from pathlib import Path
import shutil
import re

from imctools.converters import ome2analysis
from imctools.io.imc.imcwriter import ImcWriter
from imctools.io.mcd.mcdparser import McdParser


def generate_scaffold(output_folder):
    for i in ['ilastik', 'info', 'analysis', 'spatialtis']:
        (output_folder / Path(i)).mkdir(exist_ok=True, parents=True)


def mcdfile2ome(mcdfile):
    mcdfile = Path(mcdfile)
    ome_folder = mcdfile.parent / Path(mcdfile.stem + '-ome')

    mcd_parser = McdParser(mcdfile)
    imc_writer = ImcWriter(ome_folder, mcd_parser)
    imc_writer.write_imc_folder(create_zip=False)

    return ome_folder


def mcd2analysis(mcdfiles, output_folder, panel_csv, analysis_stacks, metalcolumn):
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
            metalcolumn=metalcolumn)
        shutil.rmtree(ome_folder)

    fn = next(analysis_folder.glob(f'*{analysis_stacks[1][1]}.csv'))
    shutil.copy(fn, info_folder / 'full_channelmeta.csv')


def create_spatialtis_folder(output_folder):
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