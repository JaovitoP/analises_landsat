
import streamlit as st
import os
from datetime import datetime

from utils.catalog import *
from utils.indices import *
from utils.raster import *
from utils.visualization import *
from components.header import header

header()

with st.container(border=True):

    st.subheader('Selecione o intervalo de tempo')

    columns = st.columns(3)

    options= ["231_066"]

    with columns[0]:

        obt_pto = st.selectbox(
            label='Selecione a órbita ponto',
            options=options
        )

    with columns[1]:

        init_date = st.date_input(
            label='Selecione a data de início',
            value='2025-08-01'
        )

    with columns[2]:

        end_date = st.date_input(
            label='Selecione a data de fim',
            value='2025-09-26'
        )


    if st.button('Buscar Imagens'):
        with st.spinner(f'Procurando Imagens...'):
            st.session_state['items'] = search_items(
                obt_pto,
                init_date,
                end_date
            )
        
    if 'items' in st.session_state:

        items = st.session_state['items']

        num_cols = 5
            
        cols = st.columns(num_cols)
        for index, item in enumerate(items):
            col = cols[index % num_cols]
            with col:
                st.image(item.assets['thumbnail'].href, use_container_width=True, caption=f"Imagem {index}: {datetime.fromisoformat(item.properties.get('datetime').replace('Z', '+00:00')).strftime('%d/%m/%Y')} | Cobertura (%): {item.properties.get('eo:cloud_cover', 'N/A')}%")
        details = show_details(items)
        options = [
            {
                "label": f"Imagem [{i}]: Data: {datetime.fromisoformat(item.properties.get('datetime').replace('Z', '+00:00')).strftime('%d/%m/%Y')}, "
                        f"Cobertura de nuvens: {item.properties.get('eo:cloud_cover', 'N/A')}%",
                "item": item
            }
            for i, item in enumerate(items)
        ]

        labels = [opt["label"] for opt in options]

        scene_dir = "./output/vrt"
        path = "path"

        BANDAS = ["swir22", "nir08", "red"]

        if st.button('Gerar Thumbnails'):
            jpg_files = []

            with st.status('Gerando arquivos Vrt...', expanded=True) as status:
                try:
                    for it in items:
                        sat = it.id.split("_")[0]
                        data_img = it.properties["datetime"][:10].replace("-", "")
                        rowv = it.id.split("_")[1]
                        vrt = os.path.join(scene_dir, f"{sat}_{rowv}{data_img}.vrt")

                        hrefs = [f"/vsicurl/{it.assets[b].href}" for b in BANDAS if b in it.assets]

                        if not os.path.exists(vrt):
                            gdal.BuildVRT(vrt, hrefs, options=gdal.BuildVRTOptions(separate=True))

                        vrt_file = vrt
                        output_file = os.path.join("./output/thumbnails", f"{sat}_{rowv}{data_img}.jpg")
                        create_thumbnail_from_vrt(vrt_file, output_file, max_size=500, quality=95, brightness_factor=1.5)

                        jpg_files.append(output_file)
                    status.update(label="✅ Processamento concluído!", state="complete")
                except Exception as e:
                    status.write(f"❌ Erro: {e}")
                    status.update(label="Erro no processamento", state="error")

            if jpg_files:
                st.subheader("Thumbnails Geradas")

                num_cols = 5
                cols = st.columns(num_cols)

                for idx, jpg in enumerate(jpg_files):
                    col = cols[idx % num_cols]
                    with col:
                        st.image(jpg, use_container_width=True, caption=f"Thumbnail: {os.path.basename(jpg)}")

        select_img_cols = st.columns(2)

        with select_img_cols[0]:
            img_pre_label = st.selectbox("Selecione a imagem Pré-Fogo", labels)
        with select_img_cols[1]:
            img_pos_label = st.selectbox("Selecione a imagem Pós-Fogo", labels)

        img_pre = next(opt["item"] for opt in options if opt["label"] == img_pre_label)
        img_pos = next(opt["item"] for opt in options if opt["label"] == img_pos_label)
        st.session_state['img_pre'] = img_pre
        st.session_state['img_pos'] = img_pos

        thumbnail_pre = img_pre.assets['thumbnail'].href
        thumbnail_pos = img_pos.assets['thumbnail'].href

        columns = st.columns(4)
        with columns[1]:
            st.image(thumbnail_pre, caption=img_pre_label)
        with columns[2]:
            st.image(thumbnail_pos, caption=img_pos_label)

        if 'img_pre' in st.session_state:
            with st.container(border=True):
                st.title('Índices Espectrais')

                if st.button('Gerar Índices Espectrais'):

                    with st.status('Processando imagens...', expanded=True) as status:
                        
                        try:
                            status.write("🔎 Lendo bandas da imagem pré-fogo...")
                        except Exception as e:
                            status.write(f"❌ Erro: {e}")
                            status.update(label="Erro no processamento", state="error")