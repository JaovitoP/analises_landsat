import numpy as np

import os

import warnings
warnings.filterwarnings("ignore")

import rasterio
from rasterio import Affine
from rasterio.crs import CRS
from rasterio.windows import from_bounds
from rasterio.warp import Resampling, reproject, transform


def transforme_20m (asset, transforme, crs):
    '''Reamostragem de dados de 20 para 10 mts'''

    tranform_20 = Affine(20.0, 0.0, transforme.c,
                         transforme.d,-20.0,transforme.f)

    array_20 = np.zeros((int(asset.shape[0]/2), int(asset.shape[1]/2)), dtype=asset.dtype)

    reproject(
        source=asset.data, 
        destination=array_20,
        src_transform=transforme,
        src_crs=crs,
        dst_transform=tranform_20,
        dst_crs=crs,
        src_nodata=0,
        dst_nodata=0,
        resampling=Resampling.nearest
    )
    return array_20


def read(uri: str, bbox: list, masked: bool = True, crs: str = None):
    source_crs = CRS.from_string('EPSG:4326')
    
    if crs:
        source_crs = CRS.from_string(crs)

    w, s, e, n = bbox
        
    with rasterio.open(uri) as dataset:
        transformer = transform(source_crs, dataset.crs, [w, e], [s, n])
        window = from_bounds(transformer[0][0], transformer[1][0], 
                             transformer[0][1], transformer[1][1], dataset.transform)
        
        box_trasform = rasterio.transform.from_bounds(transformer[0][0], transformer[1][0],
                                                      transformer[0][1], transformer[1][1], window.width, window.height)
        
        return dataset.read(1, window=window, masked=masked)*0.0001, box_trasform


def save_rgb_in_geotiff_format(crs, transform, *args):
    os.makedirs('./output', exist_ok=True)
    
    file_paths = []
    for img_index, image in enumerate(args):
        height, width, num_bands = image.shape
        file_name = f'./output/rgb_image{img_index}.tif'
        
        with rasterio.open(
            file_name,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=num_bands,
            dtype=image.dtype,
            crs=crs,
            transform=transform
        ) as dst:
            for band_index in range(num_bands):
                dst.write(image[:, :, band_index], band_index + 1)
        
        file_paths.append(file_name)
    
    return file_paths