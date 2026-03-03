import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import streamlit as st
from folium.plugins import MousePosition, Fullscreen

from datetime import datetime

def show_map(aoi):
    f = folium.Figure()
    centro = aoi.geometry.centroid.iloc[0]
    mapa = folium.Map(location=[centro.y, centro.x],
               zoom_start=10,
               tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
               attr="Esri World Imagery"
        ).add_to(f)

    folium.GeoJson(aoi).add_to(mapa)

    MousePosition().add_to(mapa)

    Fullscreen().add_to(mapa)

    st_folium(mapa, width="100%", height=600)

def show_selected_areas_on_map(aoi, imagem_pre, imagem_pos):
    f = folium.Figure()

    centro = aoi.geometry.centroid.iloc[0]
    center_lat, center_lon = centro.y, centro.x

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10).add_to(f)

    tif_img_pre = imagem_pre.assets['TCI'].href
    tif_img_pos = imagem_pos.assets['TCI'].href

    title_img_pre = datetime.fromisoformat(
        imagem_pre.properties['datetime']
    ).strftime("%d/%m/%y %H:%M")

    title_img_pos = datetime.fromisoformat(
        imagem_pos.properties['datetime']
    ).strftime("%d/%m/%y %H:%M")

    tms_url_1 = f"https://data.inpe.br/bdc/tms/tiles/WebMercatorQuad/{{z}}/{{x}}/{{y}}?url={tif_img_pre}"

    folium.TileLayer(
        tiles=tms_url_1,
        attr="INPE Sentinel-2",
        name=title_img_pre,
        overlay=True,
        control=True
    ).add_to(m)

    tms_url_2 = f"https://data.inpe.br/bdc/tms/tiles/WebMercatorQuad/{{z}}/{{x}}/{{y}}?url={tif_img_pos}"

    folium.TileLayer(
        tiles=tms_url_2,
        attr="INPE Sentinel-2",
        name=title_img_pos,
        overlay=True,
        control=True
    ).add_to(m)

    folium.GeoJson(
        aoi,
        name="AOI",
        style_function=lambda x: {
            'color': 'red',
            'weight': 2,
            'fill': False
        }
    ).add_to(m)

    MousePosition().add_to(m)

    Fullscreen().add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, width="100%", height=600)       

def plot_pre_pos(rgb_pre, rgb_pos):

    fig, axes = plt.subplots(
        1, 2,
        figsize=(14,7),
        constrained_layout=True
    )

    axes[0].axis('off')
    axes[0].imshow((rgb_pre * 255).astype(np.uint8), interpolation='nearest')
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")


    axes[1].axis('off')
    axes[1].imshow((rgb_pos * 255).astype(np.uint8), interpolation='nearest')

    st.pyplot(fig)
    plt.close(fig)


def plot_ndvi(ndvi_pre, ndvi_pos):
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    ndvi_pre_plot = axes[0].imshow(ndvi_pre, cmap="RdYlGn", vmin=-0.2, vmax=0.65, interpolation='nearest')
    axes[0].axis("off")
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    cbar_pre = plt.colorbar(ndvi_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NDVI Value")
    
    ndvi_pos_plot = axes[1].imshow(ndvi_pos, cmap="RdYlGn", vmin=-0.2, vmax=0.65, interpolation='nearest')
    axes[1].axis("off")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")
    cbar_pos = plt.colorbar(ndvi_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NDVI Value")
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    

def plot_nbr(nbr_pre, nbr_pos):
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    nbr_pre_plot = axes[0].imshow(nbr_pre, cmap="RdYlGn", vmin=-0.35, vmax=0.35, interpolation='nearest')
    axes[0].axis("off")
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    cbar_pre = plt.colorbar(nbr_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NBR Value")
    
    nbr_pos_plot = axes[1].imshow(nbr_pos, cmap="RdYlGn", vmin=-0.35, vmax=0.35, interpolation='nearest')
    axes[1].axis("off")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")
    cbar_pos = plt.colorbar(nbr_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NBR Value")
    
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)


def plot_nbrswir(nbrswir_pre, nbrswir_pos):

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    nbrswir_pre_plot = axes[0].imshow(nbrswir_pre, cmap="RdYlGn", vmin=-0.15, vmax=0.15, interpolation='nearest')
    axes[0].axis("off")
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    cbar_pre = plt.colorbar(nbrswir_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NBRSWIR Value")
    
    nbrswir_pos_plot = axes[1].imshow(nbrswir_pos, cmap="RdYlGn", vmin=-0.15, vmax=0.15, interpolation='nearest')
    axes[1].axis("off")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")
    cbar_pos = plt.colorbar(nbrswir_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NBRSWIR Value")
    
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)

def plot_difference_between_indices(ndvi_dif, nbr_dif, nbrswir_dif):
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 7))

    ndvi_dif_plot = axes[0].imshow(ndvi_dif, cmap="PuOr", vmin=-0.15, vmax=0.25, interpolation='nearest')
    axes[0].set_title("NDVI Diferença (Pré - Pós Fogo)")
    axes[0].axis("off")
    cbar_ndvi = plt.colorbar(ndvi_dif_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_ndvi.set_label("NDVI Difference")

    nbr_dif_plot = axes[1].imshow(nbr_dif, cmap="PuOr", vmin=-0.15, vmax=0.25, interpolation='nearest')
    axes[1].set_title("NBR Diferença (Pré - Pós Fogo) ")
    axes[1].axis("off")
    cbar_nbr = plt.colorbar(nbr_dif_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_nbr.set_label("NBR Difference")

    nbrswir_dif_plot = axes[2].imshow(nbrswir_dif, cmap="PuOr", vmin=-0.15, vmax=0.25, interpolation='nearest')
    axes[2].set_title("NBR_Swir  Diferença (Pré - Pós Fogo) ")
    axes[2].axis("off")
    cbar_nbr = plt.colorbar(nbrswir_dif_plot, ax=axes[2], fraction=0.03, pad=0.04)
    cbar_nbr.set_label("NBR_Swir Difference")

    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)