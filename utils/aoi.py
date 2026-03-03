import geopandas as gpd

def load_aoi(shapefile):
    return gpd.read_file(shapefile)

def normalize_aoi(aoi):
    return aoi.to_crs(4326)