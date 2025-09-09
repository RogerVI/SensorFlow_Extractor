import requests
import streamlit as st

# 1. Obtenir la liste des capteurs d'un projet
def get_sensors(project_id, headers):
    """
    Retrieves the list of sensors for a given project.
    """
    json_data = {
        'with': ['sensorType'],
    }

    response = requests.post(
        f'https://api.beyond-monitoring.com/api/v2/projects/{project_id}/sensors/search',
        headers=headers,
        json=json_data
    )

    if response.status_code != 200:
        st.error(f"Erreur lors de la récupération des capteurs : {response.status_code} - {response.text}")
        return []

    return response.json()


# 2. Extraire les types de capteurs disponibles
def get_list_of_sensor_types(sensors):
    """
    Extracts a unique list of sensor types from the given list of sensors.
    """
    types = [sensor["sensorType"]["languages"]["fr"]["name"] for sensor in sensors]
    return sorted(set(types))


# 3. Interface Streamlit pour choisir les types de capteurs
def choose_sensor_types(unique_types, project_key=None):
    """
    Allows the user to select one or more sensor types from the list via Streamlit UI.
    """
    sensor_types = st.multiselect(
        "Sélectionnez un ou plusieurs types de capteurs :",
        unique_types
    )

    if not sensor_types:
        st.warning("Aucun type de capteur sélectionné. Merci de faire une sélection.")
        st.stop()

    return sensor_types


# 4. Grouper les capteurs par type sélectionné
def get_dict_of_id_sensors(sensors, sensor_types):
    """
    Groups sensors by their types and organizes them into dictionaries.
    """
    grouped_sensors = []

    for sensor_type in sensor_types:
        filtered = [
            sensor for sensor in sensors
            if sensor["sensorType"]["languages"]["fr"]["name"] == sensor_type
        ]

        id_dict = {
            sensor['id']: sensor['name']
            for sensor in filtered
        }
        id_dict = dict(sorted(id_dict.items(), key=lambda item: item[1]))

        grouped_sensors.append({'type': sensor_type, 'sensors': id_dict})

    return grouped_sensors
