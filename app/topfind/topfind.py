# -*- coding: utf-8 -*-
"""

    @author: acejudo - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.2
"""

import time
import zipfile
from datetime import date
from multiprocessing import Process
from typing import Any, Tuple

import streamlit as st
from PIL import Image

from app.gui.utils.filters import input_app_filters, input_video_filters, input_podcast_filters, input_news_filters
from app.gui.utils.input_processing import transform_dictionary, process_filters
from app.topfind.utils.plots import load_time_table, plot_dataframe_lengths, transform_byte_objects, \
    plot_count_over_time
from app.topfind.utils.post_filters import app_filter, video_filter, podcast_filter, news_filter
from resourcescraper.filter.app_filter import AppFilter
from resourcescraper.filter.news_filter import NewsFilter
from resourcescraper.filter.podcast_filter import PodcastFilter
from resourcescraper.filter.video_filter import VideoFilter
from resourcescraper.resource_scraper.app_scraper import AppScraper
from resourcescraper.resource_scraper.news_scraper import NewsScraper
from resourcescraper.resource_scraper.video_scraper import VideoScraper
from resourcescraper.resource_scraper.podcast_scraper import PodcastScraper

groups = {
    "cancerTypes": {
        "breast": ["Cáncer de mama", "Neoplasia mamaria", "Carcinoma de mama", "Tumor de mama", "Cancer mamario",
                   "Tumor maligno mamario", "Tumor maligno de mama", "Neoplasia maligna de mama",
                   "Cáncer de la glándula mamaria", "Carcinoma mamario", "Tumor mamario", "Adenocarcinoma mamario",
                   "Carcinoma ductal", "Carcinoma ductal invasivo", "CDI", "Carcinoma ductal infiltrante",
                   "Carcinoma ductal in situ", "CDIS", "Carcinoma lobulillar", "Carcinoma lobulillar invasivo",
                   "Carcinoma lobulillar infiltrante", "Carcinoma lobulillar in situ", "CLIS", "Carcinoma intraductal",
                   "Cáncer de seno", "Angiosarcoma del seno", "Angiosarcoma de mama", "Tumor de seno",
                   "Carcinoma de seno", "Adenocarcinoma de seno", "Neoplasia de seno", "Neoplasia maligna de seno",
                   "Breast cancer", "Breast neoplasia", "Breast carcinoma", "Breast tumor", "Breast tumour",
                   "Malignant breast tumour", "Malignant breast tumor", "Malignant breast neoplasm",
                   "Cancer of the mammary gland", "Adenocarcinoma of the breast", "Ductal carcinoma",
                   "Invasive ductal carcinoma", "IDC", "Infiltrating ductal carcinoma", "Ductal carcinoma in situ",
                   "DCIS", "Lobular carcinoma", "Invasive lobular carcinoma", "ILC", "Infiltrating lobular carcinoma",
                   "Lobular carcinoma in situ", "LCIS", "Intraductal carcinoma", "Angiosarcoma of the breast"],
        "prostate": ["Cáncer de próstata", "Cáncer de la glándula prostática", "Cáncer prostático",
                     "Carcinoma de próstata", "Carcinoma de la glándula prostática", "Carcinoma prostático",
                     "Neoplasia de próstata", "Neoplasia de la glándula prostática", "Neoplasia prostática",
                     "Tumor de próstata", "Tumor de la glándula prostática", "Tumor prostático",
                     "Adenocarcinoma de próstata", "Adenocarcinoma de la glándula prostática",
                     "Adenocarcinoma prostático", "Neoplasia maligna", "neoplasia maligna de prostata",
                     "neoplasia maligna de la glándula prostática", "neoplasia maligna prostática", "Prostate cancer",
                     "Prostate gland cancer", "Carcinoma of the prostate", "Carcinoma of the prostate gland",
                     "Prostatic carcinoma", "Neoplasia of the prostate", "Neoplasia of the prostate gland",
                     "Prostatic neoplasm", "Prostate tumour", "Prostate gland tumour", "Adenocarcinoma of the prostate",
                     "Adenocarcinoma of the prostate gland", "Prostatic adenocarcinoma", "Prostatic neoplasia"],
        "colorectal": ["Cáncer colorrectal", "Cancer de colon", "cancer de recto", "cancer rectal",
                       "cancer del intestino grueso", "carcinoma de colon", "carcinoma de recto",
                       "carcinoma colorrectal", "carcinoma rectal", "carcinoma del intestino grueso",
                       "neoplasia de colon", "neoplasia de recto", "neoplasia colorrectal", "neoplasia rectal",
                       "neoplasia del intestino grueso", "tumor de colon", "tumor de recto", "tumor colorrectal",
                       "tumor rectal", "tumor del intestino grueso", "Bowel cancer", "Colon carcinoma", "Rectal cancer",
                       "Colon cancer", "Rectal cancer", "Colorectal carcinoma", "Colorectal cancer",
                       "Colorectal neoplasm", "Colorectal tumour", "Large bowel cancer", "Colon neoplasm",
                       "Colon neoplasm", "Colon carcinoma", "Colon tumour"],
        "hodgkin": ["Linfoma de Hodgkin", "Enfermedad de Hodgkin", "Linfogranulomatosis de Hodgkin",
                    "Linfoma de células de Reed-Sternberg", "hodgkin lymphoma", "Hodgkins disease", "Hodgkins lymphoma"],
        "pediatric": ["Cáncer pediátrico", "Cancer de sangre infantil", "cancer de sangre en niños",
                      "cancer de sangre juvenil", "cancer de sangre en edad pediátrica",
                      "cancer de sangre en edad infantil", "cancer de sangre en jóvenes",
                      "cancer de sangre en edad temprana", "neoplasia maligna de la sangre infantil",
                      "neoplasia maligna de la sangre en niños", "neoplasia maligna de la sangre juvenil",
                      "neoplasia maligna de la sangre en edad pediátrica",
                      "neoplasia maligna de la sangre en edad infantil", "neoplasia maligna de la sangre en jóvenes",
                      "neoplasia maligna de la sangre en edad temprana", "leucemia infantil", "leucemia en niños",
                      "leucemia juvenil", "leucemia en edad pediátrica", "leucemia en edad infantil",
                      "leucemia en jóvenes", "leucemia en edad temprana", "Tumor cerebral en niños",
                      "tumor cerebral infantil", "tumor cerebral juvenil", "tumor cerebral en edad pediátrica",
                      "tumor cerebral en jóvenes", "tumor cerebral en edad temprana", "tumor de cerebro en niños",
                      "tumor de cerebro infantil", "tumor de cerebro juvenil", "tumor de cerebro en edad pediátrica",
                      "tumor de cerebro en jóvenes", "tumor de cerebro en edad temprana", "cancer cerebral en niños",
                      "cancer cerebral infantil", "cancer cerebral juvenil", "cancer cerebral en edad pediátrica",
                      "cancer cerebral en jóvenes", "cancer cerebral en edad temprana", "cancer de cerebro en niños",
                      "cancer de cerebro infantil", "cancer de cerebro juvenil", "cancer de cerebro en edad pediátrica",
                      "cancer de cerebro en jóvenes", "cancer de cerebro en edad temprana",
                      "tumoración cerebral en niños", "tumoración cerebral infantil", "tumoración cerebral juvenil",
                      "tumoración cerebral en edad pediátrica", "tumoración cerebral en jóvenes",
                      "tumoración cerebral en edad temprana",  "Pediatric brain and CNS cancer",
                      "childhood brain cancer", "childhood brain neoplasm", "childhood brain neoplasia",
                      "Pediatric leukemia", "Childhood acute leukemia", "Childhood leukaemia", "Malignant lymphocytosis",
                      "Acute lymphocytic leukaemia", "T-cell lymphoma", "T-cell leukaemia", "Acute lymphoblastic" ],
        "bone": ["Cáncer de hueso", "bone cancer"],
        "rare": ["Cáncer raro", "rare cancer"],
        "melanoma": ["Melanoma", "Cáncer de melanoma", "Melanoma cutáneo", "Melanoma de la piel", "Cutaneous melanoma",
                     "Skin melanoma",  "Melanoma", "Melanoma cancer", "Melanoma of the skin"],
        "lung": ["Cáncer de pulmón", "Carcinoma pulmonar", "Neoplasia pulmonar", "Carcinoma broncogénico",
                 "Cáncer pulmonar", "Lung carcinoma", "Lung neoplasm", "Bronchogenic carcinoma", "Lung cancer"],
        "pancreatic": ["Cáncer de páncreas", "Carcinoma de páncreas", "Neoplasia de páncreas", "Carcinoma pancreático",
                       "Adenocarcinoma del páncreas", "pancreatic cancer", "Pancreatic carcinoma",
                       "Adenocarcinoma of the pancreas",  "Pancreatic neoplasm", "Pancreatic carcinoma",
                       "Pancreatic adenocarcinoma"],
        "stomach": ["Cáncer de estómago", "Carcinoma gástrico", "Neoplasia gástrica", "Cáncer gástrico",
                    "Carcinoma gástrico", "stomach cancer",  "Gastric cancer",  "Gastric carcinoma", "Gastric neoplasm",
                    "Gastric neoplasm", "Gastric cancer", "Gastric carcinoma"],
        "bladder": ["Cáncer de vejiga", "Carcinoma de vejiga", "Neoplasia de vejiga",
                    "Carcinoma de células transicionales de la vejiga", "bladder cancer",
                    "Transitional cell carcinoma of the bladder",  "Bladder carcinoma", "Bladder neoplasm",
                    "Transitional cell carcinoma of the bladder", "Transitional cell carcinoma of the bladder"],
        "non-hodgkin": ["Linfoma no Hodgkin", "Enfermedad linfática no Hodgkin", "NHL","Non-Hodgkins lymphoma"],
        "liver": ["Cáncer de higado", "Carcinoma hepático", "Neoplasia hepática", "Carcinoma de hígado",
                  "Carcinoma hepático", "liver cancer", "Liver carcinoma", "Hepatic carcinoma", "Hepatic neoplasm",
                  "Liver carcinoma"],
        "kidney": ["Cáncer de riñón", "Carcinoma renal", "Neoplasia renal", "Carcinoma de células renales",
                   "Carcinoma renal", "Cáncer renal", "kidney cancer", "Renal cell carcinoma", "Kidney carcinoma",
                   "Renal Carcinoma", "Renal Neoplasm", "Renal Cell Carcinoma", "Renal Cancer"],
        "multiple myeloma": ["Mieloma múltiple", "Enfermedad mieloproliferativa", "Mieloma plasmocítico",
                             "Enfermedad de Kahler",  "Plasma cell myeloma", "Kahler disease",  "Multiple Myeloma",
                             "Myeloproliferative Disease", "Plasmacytic Myeloma", "Kahlers Disease"],
        "thyroid": ["Cáncer de tiroides", "Carcinoma tiroideo", "Neoplasia tiroidea", "Cáncer de la glándula tiroides",
                    "Thyroid carcinoma", "Thyroid gland cancer", "Thyroid neoplasm", "Thyroid gland cancer",
                    "Thyroid cancer"],
        "oral cavity": ["Cáncer de la cavidad oral", "Carcinoma oral", "Neoplasia oral", "Cáncer oral",
                        "Carcinoma de la cavidad oral"],
        "esophagus": ["Cáncer del esófago", "Carcinoma esofágico", "Neoplasia esofágica", "Cáncer esofágico",
                      "Carcinoma esofágico"],
        "larynx": ["Cáncer de laringe", "Carcinoma laríngeo", "Neoplasia laríngea", "Cáncer laríngeo",
                   "Carcinoma laríngeo"],
        "corpus uteri": ["Cáncer del cuerpo uterino", "Carcinoma del cuerpo uterino", "Neoplasia del cuerpo uterino",
                         "Cáncer uterino", "Carcinoma uterino", "Cáncer del cuerpo uterino"],
        "ovarian": ["Cáncer de ovario", "neoplasia ovárica", "tumor ovárico", "carcinoma ovárico", "Cáncer ovariano"],
        "endometrial": ["Cáncer de endometrio", "Carcinoma endometrial", "Cáncer endometrial del útero"],
        "testicular": ["Cáncer testicular", "neoplasia testicular", "tumor testicular", "carcinoma testicular",
                       "Tumor de células germinales testiculares"],
        "neuroblastoma": ["Neuroblastoma", "Tumor neuroblástico", "Neuroblastoma pediátrico"],
        "wilms": ["Tumor de Wilms", "Tumor renal infantil", "Neoplasia renal infantil", "Carcinoma renal de Wilms",
                  "Tumor renal de Wilms"]
    },
    "thematicAreas": {
        "adverseEvents": ["Efectos secundarios", "Reacciones adversas", "Complicaciones", "Efectos adversos",
                          "Toxicidades", "Efectos nocivos", "Efectos tóxicos adversos", "Efectos secundarios tóxicos"],
        "nutrition": ["Nutrición", "Alimentación", "comida", "dieta", "Asesoramiento nutricional"],
        "mentalHealth": ["Salud mental", "Trastorno mental", "Bienestar emocional", "Ayuda psiquiátrica",
                         "Asesoramiento", "Terapia", "Psicooncología", "Incertidumbre", "Acompañamiento psicológico",
                         "Soporte psicológico", "Aceptación"],
        "qol": ["Calidad de vida", "Satisfacción vital", "Dignidad de vida", "Nivel de vida",
                "Sensación de satisfacción", "Sensación de satisfacción"],
        "jobSecurityAccessToEmployment": ["Seguridad laboral", "Acceso al empleo", "Formación laboral",
                                          "reinserción laboral", "desarrollo profesional", "seguridad en el trabajo",
                                          "seguridad laboral", "trabajo seguro", "acceso al trabajo",
                                          "entrar en el mercado laboral", "encontrar empleo", "obtener empleo ",
                                          "Estabilidad profesional", "disponibilidad de empleo",
                                          "oportunidades de empleo", "perspectivas de empleo"],
        "survivorshipCare": ["Cuidado para sobrevivientes", "Apoyo postratamiento", "seguimiento a largo plazo",
                             "cuidados posteriores", "Acompañamiento"],
        "AYACare": ["Intimidad", "relaciones maritales", "salud reproductiva", "función sexual", "concepción",
                    "procreación", "Relaciones sexuales", "Narrativas", "relatos", "historias", "testimonios",
                    "Experiencias"],
        "lateEffects": ["Efectos tardíos", "Seguimiento", "Condición residual", "Secuelas",
                        "Consecuencias a largo plazo", "Impactos persistentes", "Efectos adversos", "toxicidad",
                        "efectos secundarios", "efectos colaterales", "reacción adversa"],
        "wellbeing": ["Bienestar", "Confort", "alegría", "felicidad", "Tranquilidad"],
        "meditation": ["Meditación", "Reflexión", "Introspección", "Autoexamen", "Concentración", "Calma",
                       "Autoconocimiento"],
        "co-morbidity": ["Comorbilidad", "Afecciones concurrentes", "afecciones coexistentes", "enfermedad concurrente",
                         "afecciones múltiples", "afecciones comórbidas", "Morbilidad asociada"],
        "rehabilitation": ["Recuperar", "Rehabilitación", "Restauración", "recuperación", "recuperación", "mejora",
                           "Actividades de la vida diaría", "AVDs", "adaptación", "aprendizaje", "Cambio corporal"],
        "physicalActivity": ["Actividad física", "Ejercicio", "Aptitud física", "Gasto energético", "Actividad activa",
                             "Movimiento", "Esfuerzo", "Deporte", "Movilidad"],
        "socialRehabilitation": ["Rehabilitación social", "Rehabilitación psicosocial", "Rehabilitación psiquiátrica"],
        "sexualLife": ["Vida sexual", "Intimidad", "relaciones maritales", "salud reproductiva", "función sexual",
                       "concepción", "procreación", "Relaciones sexuales"],
        "lifeStyle": ["Estilo de vida", "Hábitos", "patrones", "rutinas", "puesto", "supervivencia", "sobrevivencia",
                      "existencia"],
        "empowermentOfCancerSurvivorship": ["Empoderamiento de los supervivientes de cáncer", "autosuficiencia",
                                            "independencia"],
        "inequalitiesInSurvivorship": ["Desigualdades en la supervivencia", "Disparidades", "prejuicios",
                                       "desequilibrios", "trato injusto", "Barreras Financieras"],
        "prevention": ["Prevención", "Precaución", "anticipación", "vigilancia"],
        "cancerInformation": ["Información sobre el cáncer", "Concienciación", "conocimiento", "educación",
                              "iluminación"],
        "personalExperiences": ["Biografías y experiencias personales", "Narrativas", "relatos", "historias",
                                "testimonios", "Experiencias"]
    },
    "targetGroups": {
        "adult": ["adulto"],
        "child": ["niño", "niña"],
        "man": ["hombre"],
        "woman": ["mujer"]
    }
}

groups = transform_dictionary(groups)
groups = {}

@st.cache_data
def convert_df(df):
    """

    """
    return df.to_csv(index=False).encode('utf-8')


def write():
    """
    Creates the Streamlit page.
    """
    st.set_page_config(page_title='topFIND', page_icon="utils/topFIND_icon.png", layout="wide",
                       initial_sidebar_state="collapsed"
                       )

    logo = Image.open("app/topfind/utils/topFIND_icon.png", "r")


    hide_default_format = """
           <style>
           #MainMenu {visibility: hidden; }
           footer {visibility: hidden;}
           </style>
           """
    st.markdown(hide_default_format, unsafe_allow_html=True)
    _, col1, _ = st.columns([1, 1, 1])
    with col1:
        st.image(logo, width=300)
    _, col, _ = st.columns([0.2, 0.8, 0.2])


    st.session_state.disabled = False

    with col.container():
        left, middle, right = st.columns([0.54, 0.1, 0.2])
        with left:
            query_input = st.text_input("Query")
        with middle:
            lang = st.selectbox("Language", ["en", "es", "cs", "sl", "it"])
        with right:
            st.write('')
            st.write('')
            run = st.button("**Search**", key="but_a", disabled=st.session_state.disabled)

    col1, col2, col3, col4, col5 = col.columns([1, 1, 1, 1, 2.3])
    option_1 = col1.checkbox('Apps', value=True)
    option_2 = col2.checkbox('Videos', value=True)
    option_3 = col3.checkbox('Podcasts', value=True)
    option_4 = col4.checkbox('News', value=True)
    option_adv = col5.toggle('*Advanced*')
    apps_filters, video_filters, podcast_filters, news_filters = [{} for i in range(4)]
    if option_adv:
        if option_1:
            advanced_expander1 = col1.expander('Filters', True)
            with advanced_expander1:
                apps_filters = input_app_filters()
        if option_2:
            advanced_expander2 = col2.expander('Filters', True)
            with advanced_expander2:
                video_filters = input_video_filters()
        if option_3:
            advanced_expander3 = col3.expander('Filters', True)
            with advanced_expander3:
                podcast_filters = input_podcast_filters()
        if option_4:
            advanced_expander4 = col4.expander('Filters', True)
            with advanced_expander4:
                news_filters = input_news_filters()

    t = col.empty()

    if run:
        st.divider()
        st.session_state.download = False
        if query_input == "":
            t.error("Query can not be empty")
        else:
            with st.status("Searching for resources...", expanded=True) as status:
                # progress_text = 'Searching for resources...'
                # my_bar = st.progress(0, text=progress_text)
                st.session_state.disabled = True

                current_date = date.today()
                formatted_date = current_date.strftime("%d_%m_%Y")

                byte_objects = []
                byte_objects_df = {}
                durations = []

                if option_1:
                    # Apps
                    processed_apps_filters = process_filters(apps_filters, 'apps')
                    apps_df, duration, filters = load_apps(query_input, processed_apps_filters, lang)
                    # Map dataframe for visualization
                    apps_df["genres"] = apps_df["genres"].map(lambda x: str(x))
                    apps_df["languageCodesISO2A"] = apps_df["languageCodesISO2A"].map(lambda x: str(x))

                    apps_csv = convert_df(app_filter(apps_df))
                    byte_objects.append(apps_csv)
                    byte_objects_df['Apps'] = app_filter(apps_df)
                    durations.append(round(duration, 2))

                    # my_bar.progress(25, text='Apps found')
                    st.write('Apps found')
                if option_2:
                    # Videos
                    processed_videos_filters = process_filters(video_filters, 'videos')
                    videos_df, duration, filters = load_videos(query_input, processed_videos_filters, lang)
                    st.write(processed_videos_filters)

                    videos_csv = convert_df(video_filter(videos_df))
                    byte_objects.append(videos_csv)
                    byte_objects_df['Videos'] = video_filter(videos_df)
                    durations.append(round(duration, 2))

                    # my_bar.progress(50, text='Videos found')
                    st.write('Videos found')
                if option_3:
                    # Podcasts
                    processed_podcasts_filters = process_filters(podcast_filters, 'podcasts')
                    podcasts_df, duration, filters = load_podcasts(query_input, processed_podcasts_filters, lang)
                    podcasts_df["languages"] = podcasts_df["languages"].map(lambda x: str(x))

                    podcasts_csv = convert_df(podcast_filter(podcasts_df))
                    byte_objects.append(podcasts_csv)
                    byte_objects_df['Podcasts'] = podcast_filter(podcasts_df)
                    durations.append(round(duration, 2))

                    # my_bar.progress(75, text='Podcasts found')
                    st.write('Podcasts found')
                if option_4:
                    # News
                    processed_news_filters = process_filters(news_filters, 'news')
                    news_df, duration, filters = load_news(query_input, processed_news_filters, lang)

                    news_csv = convert_df(news_filter(news_df))
                    byte_objects.append(news_csv)
                    byte_objects_df['News'] = news_filter(news_df)
                    durations.append(round(duration, 2))

                    # my_bar.progress(95, text='News found')
                    st.write('News found')

                st.session_state.byte_objects = byte_objects_df
                st.session_state.labels = byte_objects_df.keys()
                st.session_state.durations = durations

                # my_bar.progress(100, text='Resources loaded!')
                status.update(label="Resources loaded!", state="complete", expanded=False)

            summary, table, pie_chart = st.columns(3)

            summary.write('#')
            summary.write('#')
            summary.write('#')

            table.write('##')
            table.write('##')

            summary.header('Summary')

            loading_times = load_time_table(byte_objects_df, byte_objects_df.keys(), durations)
            table.dataframe(loading_times)

            resource_pie = plot_dataframe_lengths(byte_objects_df, byte_objects_df.keys())
            pie_chart.pyplot(resource_pie)

            st.divider()

            title_trends, trends = st.columns([0.25, 0.75])

            title_trends.write('#')
            title_trends.write('#')
            title_trends.write('#')

            title_trends.header('Trends')

            trend_graph = transform_byte_objects(byte_objects_df)
            fig = plot_count_over_time(trend_graph)
            trends.altair_chart(fig, use_container_width=True)

            # Open the zip file in write mode
            with zipfile.ZipFile(f'{formatted_date}_{query_input.replace(" ", "_").lower()}.zip', 'w') as zip_file:
                # Iterate over the byte objects and labels simultaneously
                for i, (byte_obj, label) in enumerate(zip(byte_objects, byte_objects_df.keys())):
                    # Create a filename for the byte object
                    filename = f'{formatted_date}_{query_input.replace(" ", "_").lower()}_{label.lower()}.csv'

                    # Add the byte object to the zip file
                    zip_file.writestr(filename, byte_obj)
            with open(f'{formatted_date}_{query_input.replace(" ", "_").lower()}.zip', "rb") as file:
                col.download_button(
                    label="Download",
                    data=file,
                    file_name=f'{formatted_date}_{query_input.replace(" ", "_").lower()}.zip',
                    mime="application/zip",
                    key="custom-download-button",
                    help="Download the resources file here"
                )

            t.empty()


def start_search(query: str):
    """
    Starts the search process.

    Args:
        query (str): The search query.
    """
    p1 = Process(target=load_podcasts, args=query)
    p1.start()
    p2 = Process(target=load_videos, args=query)
    p2.start()
    p3 = Process(target=load_apps, args=query, )
    p3.start()
    p1.join()
    p2.join()
    p3.join()
    print("Finished")


def load_news(query:str, filters=None, lang:str='it') -> Tuple[Any, float, dict[Any, list]]:
    """
    Returns news DataFrame, the elapsed time and the applied filters.

    Args:
        query (str): The search query.
        filters ():
        lang (str): The search language.

    Returns:
        Dataframe with the news.
        float: Float of the time needed to retrieve the news.
         dict[Any, list]: DataFrame o applied filters.
    """
    start = time.time()
    if filters is None:
        filters = [('keywords_search', True)]
    news = NewsScraper(queries=[query], country='es', language=lang, groups=groups)()
    print("Total news found: " + str(len(news)))
    # news.to_csv('../../resources/news/news_before_filtered.csv', index=False)
    filtered_news = NewsFilter(news, [query])()
    print("Total filtered news: " + str(len(filtered_news)))
    # filtered_news.to_csv('../../resources/news/news_filtered.csv', index=False)
    end = time.time()
    print(f'Time: {"{:.2f}".format(end - start)}s')
    filter_df = {x: [v] for x, v in filters}
    return filtered_news, end - start, filter_df


def load_videos(query: str, filters:list=None, lang: str='it') -> Tuple[Any, float, dict[Any, list]]:
    """
    Returns videos DataFrame, the elapsed time and the applied filters.

    Args:
        query (str): The search query.
        filters (list): List of applied filters.
        lang (str): The search language.

    Returns:
        Dataframe with the videos.
        float: Float of the time needed to retrieve the videos.
        dict[Any, list]: DataFrame o applied filters.

    """
    api_service_name = "youtube"
    api_version = "v3"
    if filters is None:
        filters = [('keywords', True), ('language', lang), ('licensed', False), ('duration', 1800), ('views', 100),
                   ('likes', 0), ('subscribers', 0), ('recent_update', 5)]

    start = time.time()

    videos = VideoScraper([query], api_service_name, api_version, groups=groups)()
    print("Total apps found: " + str(len(videos)))
    # videos.to_csv('../../resources/videos/videos.csv', index=False)
    videos = VideoFilter(videos, filters, [query], [])()
    # videos.to_csv('../../resources/videos/videos_filtered.csv', index=False)
    end = time.time()
    print(f'Time: {"{:.2f}".format(end - start)}s')
    filter_df = {x: [v] for x, v in filters}
    return videos, end - start, filter_df


def load_podcasts(query: str, filters:list=None, lang:str='it') -> Tuple[Any, float, dict[Any, list]]:
    """
    Returns podcasts DataFrame, the elapsed time and the applied filters.

    Args:
        query (str): The search query.
        filters (list): List of applied filters.
        lang (str): The search language.

    Returns:
        Dataframe with the podcasts.
        float: Float of the time needed to retrieve the podcasts.
        dict[Any, list]: DataFrame o applied filters.
    """
    start = time.time()
    if filters is None:
        filters = [('free', True), ('recent_update', 5), ('language', lang), ('keywords_search', True)]
    podcasts = PodcastScraper([query], groups=groups, lang=lang, country="ES")()
    print("Total podcasts found: " + str(len(podcasts)))
    podcasts = PodcastFilter(podcasts, [query], filters)()
    # podcasts.to_csv('../../resources/podcast/podcasts_filtered.csv', index=False)
    end = time.time()
    print(f'Time: {"{:.2f}".format(end - start)}s')
    filter_df = {x: [v] for x, v in filters}
    return podcasts, end - start, filter_df


def load_apps(query:str, filters:list=None, lang:str='it') -> Tuple[Any, float, dict[Any, list]]:
    """
    Returns apps DataFrame, the elapsed time and the applied filters.

    Args:
        query (str): The search query.
        filters (list): List of applied filters.
        lang (str): The search language.

    Returns:
        Dataframe with the podcasts.
        float: Float of the time needed to retrieve the apps.
        dict[Any, list]: DataFrame o applied filters.
    """
    if filters is None:
        filters = [('keywords_search', True), ('privacy_policy', True), ('score', 3), ('free', True),
                   ('recent_update', 5), ('developer_has_website', True), ('language', lang)]
    start = time.time()
    apps = AppScraper([query], groups=groups, lang=lang, country="ES")()
    print("Total apps found: " + str(len(apps)))
    # apps.to_csv('../../resources/apps/apps.csv', index=False)
    apps = AppFilter(apps, [query], filters)()
    # apps.to_csv('../../resources/apps/apps_filtered.csv', index=False)
    end = time.time()
    apps.to_csv('~/apps.csv', index=False)
    print(f'Time: {"{:.2f}".format(end - start)}s')
    filter_df = {x: [v] for x, v in filters}
    return apps.reset_index(drop=True), end - start, filter_df


if __name__ == '__main__':
    if 'but_a' not in st.session_state:
        st.session_state.disabled = False
    write()
