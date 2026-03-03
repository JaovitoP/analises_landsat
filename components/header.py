import streamlit as st

def header():
    st.set_page_config(
            layout='wide',
            page_icon='🗺️'
        )

    st.logo(image='assets/logotipo_conjugado.svg')

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    menu = {
        "Sistemas": ["Sistema 1", "Sistema 2"],
        "Dados": ["Download CSV", "API"],
        "Relatórios": ["Mensal", "Anual"],
        "Sobre": ["Institucional", "Equipe"]
    }

    logo_col, menu_col = st.columns([1, 3])

    with logo_col:
        st.image(
            image="assets/logotipo_conjugado.svg",
            width=180,
        )

    with menu_col:
        with st.container(horizontal=True, horizontal_alignment="right"):
            for item, opcoes in menu.items():
                with st.popover(item, type="tertiary"):
                    for opcao in opcoes:
                        st.button(opcao, type="tertiary")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)