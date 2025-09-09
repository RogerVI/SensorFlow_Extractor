import streamlit as st
import os
from pathlib import Path
import datetime
import pandas as pd

from B00_login import login
from B10_select_project_id import project_id
from B11_sensors_list import get_sensors, get_list_of_sensor_types, choose_sensor_types, get_dict_of_id_sensors
from B12_sensor_informations import derivedDatapoints_list, select_derived_datapoints, extract_data, create_dataframes_by_type
from B20_assets import get_assets, get_dict_of_id_assets, extract_asset, create_dataframes_by_type as create_assets_df
from B30_excel_file import export_dict_of_dfs_to_excel
from PIL import Image

st.set_page_config(page_title="API Beyond Interface", layout="wide")
logo = Image.open("SIXENSE_logo.png")
st.image(logo, width=200)
st.title("Application API Beyond Monitoring")

# --- AUTHENTIFICATION ---
st.header("1. Connexion")
email = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")

if email and password:
    headers = login(email, password)

    # --- PROJET ---
    st.header("2. Sélection du projet")

    # 🔹 FICHIER DANS LE REPO (à la racine)
    FILE_IN_REPO = Path(__file__).parent / "projects_list.txt"
    if not FILE_IN_REPO.exists():
        st.error(
            f"❌ `projects_list.txt` introuvable à la racine du repo :\n- {FILE_IN_REPO}\n"
            "Ajoute ce fichier au dépôt (même dossier que ce script)."
        )
        st.stop()

    file_path = str(FILE_IN_REPO)

    project_id_val, project_name = project_id(file_path)
    project_key = project_id_val
    st.success(f"Projet sélectionné : {project_name}")

    # --- DATES ---
    st.header("3. Période d'analyse")
    start_date = st.date_input("Date de début", datetime.date.today())
    end_date = st.date_input("Date de fin", datetime.date.today())
    start_time = f"{start_date}T00:00:00.000Z"
    end_time = f"{end_date}T23:59:59.000Z"

    # --- CAPTEURS ---
    st.header("4. Données capteurs")
    df_sensors = pd.DataFrame()
    if st.checkbox("📡 Télécharger les données capteurs"):
        sensors = get_sensors(project_id_val, headers)
        unique_types = get_list_of_sensor_types(sensors)
        sensor_types = choose_sensor_types(unique_types, project_key=project_key)
        grouped_sensors = get_dict_of_id_sensors(sensors, sensor_types)

        all_datapoints = derivedDatapoints_list(project_id_val, headers, grouped_sensors)
        selected_data = select_derived_datapoints(all_datapoints, project_key=project_key)
        raw_sensor_data = extract_data(project_id_val, headers, grouped_sensors, start_time, end_time, selected_data)
        df_sensors = create_dataframes_by_type(raw_sensor_data, grouped_sensors)
        st.success("Données capteurs téléchargées.")

    # --- ASSETS ---
    st.header("5. Données assets")
    df_assets = pd.DataFrame()
    if st.checkbox("🏗️ Télécharger les données assets"):
        assets = get_assets(project_id_val, headers)
        grouped_assets = get_dict_of_id_assets(assets)
        raw_asset_data = extract_asset(project_id_val, headers, grouped_assets, start_time, end_time)
        df_assets = create_assets_df(raw_asset_data, grouped_assets)
        st.success("Données assets téléchargées.")

    # --- EXPORT ---
    st.header("6. Export Excel")
    if st.button("📤 Générer et proposer le fichier Excel"):
        excel_bytes = export_dict_of_dfs_to_excel(df_sensors, extra_df=df_assets)
        filename = f"{project_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Veuillez renseigner vos identifiants pour vous connecter.")
