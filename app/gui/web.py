import streamlit as st
from PIL import Image

from app.gui.modules.apps import apps
from app.gui.modules.news import news
from app.gui.modules.podcasts import podcasts
from app.gui.modules.project_metadata import project_metadata
from app.gui.modules.videos import videos


def write():
    """
    Displays a Streamlit app interface for the topFIND project. It sets the page configuration, displays the topFIND
    logo, and allows users to input project-specific metadata categories. It also displays tabs for Apps, Videos,
    Podcasts, and News, and calls the apps() function to display the corresponding content for the selected tab.
    """
    st.set_page_config(page_title='topFIND', page_icon="app/gui/utils/topFIND_icon.png", layout="centered",
                       initial_sidebar_state="collapsed"
                       )

    hide_default_format = """
               <style>
               #MainMenu {visibility: hidden; }
               footer {visibility: hidden;}
               </style>
               """
    st.markdown(hide_default_format, unsafe_allow_html=True)

    logo = Image.open("app/gui/utils/topFIND_logo.png", "r")
    st.image(logo, width=750)

    st.write("## Inputs")

    with st.expander("Project-specific metadata categories"):
        new_metadata = project_metadata()

    tab_apps, tab_videos, tab_podcasts, tab_news = st.tabs(["Apps", "Videos", "Podcasts", "News"])

    with tab_apps:
        apps(new_metadata)

    with tab_videos:
        videos(new_metadata)

    with tab_podcasts:
        podcasts(new_metadata)

    with tab_news:
        news(new_metadata)


if __name__ == '__main__':
    write()
