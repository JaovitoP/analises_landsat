import pystac_client
import geopandas as gpd
import streamlit as st
from shapely import wkt
from osgeo import gdal
import numpy as np
from PIL import Image
import os

def get_catalog():
    service='https://data.inpe.br/bdc/stac/v1/'
    catalog = pystac_client.Client.open(service)
    return catalog

def show_collections():
    catalog = get_catalog()
    for collection in catalog.get_collections():
        print(f"{collection.title}: {collection.id}", end="\n"*2)

def search_items(obt_pto, init_date, end_date):
    catalog = get_catalog()
    collection = ["landsat-2"]
    date_range = f'{init_date}/{end_date}'
    item_search = catalog.search(
        collections=[collection],
        datetime=date_range,
        query={
            "bdc:tile": {"eq": obt_pto.replace("_", "")}
        }
    )
    items = list(item_search.item_collection())
    items = sorted(items, key=lambda x: x.datetime)
    return items
    

def show_details(items):
    details = []
    for i, item in enumerate(items):
        date = item.properties.get('datetime', 'N/A')
        
        cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')
        if isinstance(cloud_cover, (float, int)):
            cloud_cover_str = f"{cloud_cover:.1f}%"
        else:
            cloud_cover_str = str(cloud_cover)
        
        tile_id = item.properties.get('tileId', 'N/A')
        
        details.append(
            f"Imagem [{i}]: Data: {date}, Cobertura de nuvens: {cloud_cover_str}, Tile_ID: {tile_id}"
        )
    return details


def get_items_with_aoi_within(aoi, items):
    aoi_geom = aoi.geometry.values[0]
    items_within_aoi = []
    
    for idx, item in enumerate(items):
        footprint_wkt = item.properties['Footprint']
        
        if "geography" in footprint_wkt:
            footprint_wkt = footprint_wkt.replace("geography'SRID=4326;", "")
        
        footprint_wkt = footprint_wkt.strip("'")
        
        try:
            footprint_geom = wkt.loads(footprint_wkt)
        except Exception as e:
            st.write(f"Erro ao carregar geometria WKT do item {idx + 1}: {e}")
            continue 
        
        
        if aoi_geom.within(footprint_geom):
            items_within_aoi.append(item)
    
    return items_within_aoi

def create_thumbnail_from_vrt(vrt_path, output_path, max_size=500, quality=95, brightness_factor=1.2):
    """
    Cria um thumbnail a partir de um arquivo VRT em UInt16 com ajuste de brilho
    brightness_factor: fator de aumento de brilho (1.0 = sem mudança, >1.0 = mais claro)
    """
    try:
        # Abre o dataset VRT
        dataset = gdal.Open(vrt_path)
        if dataset is None:
            raise Exception("Não foi possível abrir o arquivo VRT")

        # Informações do dataset
        width = dataset.RasterXSize
        height = dataset.RasterYSize
        num_bands = dataset.RasterCount
        print(f"Dimensões: {width}x{height}")
        print(f"Número de bandas: {num_bands}")

        # Verifica se há pelo menos 3 bandas
        if num_bands < 3:
            raise Exception("O arquivo VRT precisa ter pelo menos 3 bandas (RGB)")

        # Lê as bandas RGB
        r = dataset.GetRasterBand(1).ReadAsArray()
        g = dataset.GetRasterBand(2).ReadAsArray()
        b = dataset.GetRasterBand(3).ReadAsArray()

        # Diagnóstico dos valores
        print(f"Valores R - min: {r.min()}, max: {r.max()}, tipo: {r.dtype}")
        print(f"Valores G - min: {g.min()}, max: {g.max()}, tipo: {g.dtype}")
        print(f"Valores B - min: {b.min()}, max: {b.max()}, tipo: {b.dtype}")

        # Normaliza os valores UInt16 (0-65535) para 0-255
        rgb_array = np.dstack((r, g, b))
        if rgb_array.dtype == np.uint16:
            print("Normalizando valores UInt16 para 0-255...")
            rgb_array = (rgb_array / 65535.0 * 255).astype(np.float32)  # Usa float32 temporariamente

            # Ajuste de brilho
            print(f"Aplicando fator de brilho: {brightness_factor}")
            rgb_array = rgb_array * brightness_factor
            # Limita os valores para não ultrapassar 255
            rgb_array = np.clip(rgb_array, 0, 255).astype(np.uint8)
        else:
            raise Exception(f"Tipo de dado inesperado: {rgb_array.dtype}")

        # Calcula novas dimensões
        scale = min(max_size/width, max_size/height)
        aspect_ratio = width / height
        if width > height:
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:
            new_width = int(max_size * aspect_ratio)
            new_height = max_size

        # Cria e redimensiona a imagem
        img = Image.fromarray(rgb_array, mode="RGB")
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Salva como JPEG
        img_resized.save(output_path, "JPEG", quality=quality)
        
        dataset = None
        print(f"Thumbnail salvo em: {output_path}")

    except Exception as e:
        print(f"Erro: {str(e)}")