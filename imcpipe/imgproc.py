from pathlib import Path
from typing import List, Optional, Dict, Tuple

import numpy as np
from skimage.io import imread
from tifffile import imsave
from skimage import filters
from skimage.transform import rescale

from imcpipe.utils import File, create_folder


def to_ilastik(imgs: List[File],
               export: File,
               channels: List[int],
               apply_filter: str = 'median',
               filter_args: Optional[Dict] = None,
               crop_shape: Tuple[int, int] = (300, 300),
               ):
    export = Path(export)
    create_folder(export)
    for img in imgs:
        img_data = imread(img)[channels]

        # apply filter to image, smooth the image
        filtered_img = img_data.copy()
        for i, layer in enumerate(img_data):
            filtered_img[i] = getattr(filters, apply_filter).__call__(layer, filter_args)

        # summarize the stack
        summarized_img = np.mean(filtered_img, axis=0) * 100
        summarized_img = summarized_img.reshape(1, *summarized_img.shape)

        # add summarize as first channel
        filtered_img = np.vstack([summarized_img, filtered_img])

        # scale 2x
        scale2x_img = rescale(filtered_img, 2.0, channel_axis=0)

        # crop images
        c, x, y = scale2x_img.shape
        ox, oy = crop_shape
        x_start = np.random.choice(np.arange(x - ox))
        y_start = np.random.choice(np.arange(y - oy))
        crop_img = scale2x_img[:, x_start:x_start+ox, y_start:y_start+oy]
        imsave(export / f"{img.stem}_seg{img.suffix}", crop_img)





