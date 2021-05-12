# IMC Analysis Pipeline

This is my own analysis pipeline for analyzing imaging mass cytometry data.
Modified from [ImcSegmentationPipeline](https://github.com/BodenmillerGroup/ImcSegmentationPipeline).

The general process of this pipeline

1. [ilastik](https://www.ilastik.org/): Train a pixel classifier
2. [CellProfiler](https://cellprofiler.org/): Gnerate mask images for cell
3. [SpatialTis](https://github.com/Mr-Milk/SpatialTis): Transfrom data into anndata object
4. [Scanpy](https://github.com/theislab/scanpy/): Identify cell type, single cell analysis
5. [SpatialTis](https://github.com/Mr-Milk/SpatialTis): Spatial analysis