import streamlit as st

pg = st.navigation(
    [
        st.Page('./pages/home.py', title='Home'),
    ]
)

pg.run()