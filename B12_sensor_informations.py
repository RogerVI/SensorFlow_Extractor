import requests
import json
import pandas as pd

import Z00_get_user_choice


# Derived datapoints list
def derivedDatapoints_list(project_id, headers, grouped_sensors):
    """
    Retrieves a list of derived datapoints for each group of sensors.

    Args:
        project_id (str): The project ID.
        headers (dict): Authentication headers.
        grouped_sensors (list): Sensors grouped by type.

    Returns:
        list: A list of dictionaries containing sensor types and their derived datapoints.

        Example: [{'sensor_type': 'crack_meters',
                'derivedDatapoints': [{'name': 'DX', 'code': 'DX'}, {'name': 'Temperature', 'code': 'T001'}]}]
    """
    all_deriveddatapoints = []

    for group in grouped_sensors:
        sensor_type = group['type']
        sensor_ids = list(group['sensors'].keys())

        unique_deriveddatapoints = []

        for sensor_ID in sensor_ids:
            response = requests.get(
                f'https://api.beyond-monitoring.com/api/v2/projects/{project_id}/sensors/{sensor_ID}',
                headers=headers
            )

            if response.status_code != 200:
                continue

            sensor_details = response.json()

            for dp in sensor_details.get('derivedDatapoints', []):
                if dp['name'] not in [d['name'] for d in unique_deriveddatapoints]:
                    unique_deriveddatapoints.append({
                        'name': dp['name'],
                        'code': dp['code']
                    })


        if sensor_type == 'Tiltmètres':
            if 'Temp' not in [d['name'] for d in unique_deriveddatapoints]:
                unique_deriveddatapoints.append({'name': 'Température', 'code': 'Temp'})
        if sensor_type == 'Stations météo':
            if 'PRECIPITATION_1H' not in [d['name'] for d in unique_deriveddatapoints]:
                unique_deriveddatapoints.append({'name': 'Précipitations_1h', 'code': 'PRECIPITATION_1H'})
        if sensor_type == 'Piezomètres':
            if 'Hauteur_eau' not in [d['name'] for d in unique_deriveddatapoints]:
                unique_deriveddatapoints.append({'name': 'Hauteur_eau', 'code': 'Hauteur_eau'})

        unique_deriveddatapoints = sorted(unique_deriveddatapoints, key=lambda d: d['name'])

        all_deriveddatapoints.append({
            "sensor_type": sensor_type,
            "derivedDatapoints": unique_deriveddatapoints
        })

    return sorted(all_deriveddatapoints, key=lambda x: (x["sensor_type"], x["derivedDatapoints"]))



# Select derived datapoints for each sensor type
import streamlit as st

def select_derived_datapoints(all_deriveddatapoints, project_key=None):
    """
    Streamlit interface for selecting derived datapoints for each sensor type.
    """
    selected_data = []

    for group in all_deriveddatapoints:
        sensor_type = group['sensor_type']
        derivedDatapoints = group['derivedDatapoints']

        with st.expander(f"Sélectionner les données dérivées pour {sensor_type}"):
            datapoint_names = [d['name'] for d in derivedDatapoints]
            selected_names = st.multiselect(
                f"Choix des données dérivées ({sensor_type})",
                options=datapoint_names,
                key=f"dp_{sensor_type}"
            )

        # Filtrer les objets de données sélectionnés
        selected_datapoints = [d for d in derivedDatapoints if d['name'] in selected_names]

        selected_data.append({
            "sensor_type": sensor_type,
            "selectedDerivedDatapoints": selected_datapoints
        })

    return selected_data





# Extract data for sensors
def extract_data(project_id, headers, grouped_sensors, start_time, end_time, selected_data, datapoint_type="derived"):
    """
    Extracts sensor data for the specified time range and selected datapoints.

    Args:
        project_id (str): The project ID.
        headers (dict): Authentication headers.
        grouped_sensors (list): A list of sensors grouped by type.
        start_time (str): The start time for data extraction (ISO 8601 format).
        end_time (str): The end time for data extraction (ISO 8601 format).
        selected_data (list): A list of selected datapoints grouped by sensor type.
        datapoint_type (str): The type of datapoints to retrieve (default is "derived").

    Returns:
        dict: A dictionary containing the extracted sensor data grouped by type and sensor ID.

        Example: {'crack_meters': {'64cba566841fbfae194e3e43': [{'64cba566841fbfae194e3e43': {'datapointTypes': {'DX': []}}},
        {'64cba566841fbfae194e3e43': {'datapointTypes': {'DY': []}}}],
        '651bdf3ae3cf23198ddd8698': [{'651bdf3ae3cf23198ddd8698': {'datapointTypes': {'DX': [{'v': 3.4710649999999994,
                'rv': -22.118935,
                'dv': 3.4710649999999994,
                't': '2025-01-12T00:00:00.000Z',
                'p': None,
                'e': 0}]}}},
        {'651bdf3ae3cf23198ddd8698': {'datapointTypes': {'DY': [{'v': -0.6156830000000006,
                'rv': 27.924317,
                'dv': -0.6156830000000006,
                't': '2025-01-12T00:00:00.000Z',
                'p': None,
                'e': 0}]}}}], [...]

    """
    sensor_data = {}

    for group in grouped_sensors:
        sensor_type = group['type']
        sensor_ids = list(group['sensors'].keys())

        sensor_data[sensor_type] = {}

        for sensor_id in sensor_ids:
            all_data = []  # On va stocker chaque réponse JSON ici

            for selected in selected_data:
                for datapoint in selected['selectedDerivedDatapoints']:

                    # Configuration spéciale pour les 'tiltmeters' et 'weather_stations'
                    if sensor_type == 'Tiltmètres' and datapoint['name'] == 'Température':
                        current_datapoint_type = "acquired"
                    elif sensor_type == 'Stations météo' and datapoint['name'] == 'Précipitations_1h':
                        current_datapoint_type = "acquired"
                    elif sensor_type == 'Piezomètres' and datapoint['name'] == 'Hauteur_eau':
                        current_datapoint_type = "acquired"
                    else:
                        current_datapoint_type = datapoint_type

                    json_data = {
                        'filter': {
                            'startTime': start_time,
                            'endTime': end_time,
                            'datapointTypes': [
                                {
                                    'entityId': sensor_id,
                                    'datapoint': datapoint['code'],
                                    'datapointType': current_datapoint_type
                                },
                            ],
                            'entityKind': 'Sensor',
                            'onlyLatest': False,
                            'errorStatus': [0, -7, -5],
                            'skipNullValues': None,
                            'limitLatest': None
                        },
                    }

                    response = requests.post(
                        f'https://api.beyond-monitoring.com/api/projects/{project_id}/timeseriesdata/search',
                        headers=headers,
                        json=json_data
                    )

                    if response.status_code == 200:
                        raw_data = response.json()
                        sensor_specific_data = raw_data.get('data', {})
                        if sensor_specific_data:
                            # <-- On fait un append au lieu de extend
                            all_data.append(sensor_specific_data)

            sensor_data[sensor_type][sensor_id] = all_data

    return sensor_data





# Create DataFrames by sensor type
def create_dataframes_by_type(sensor_data, grouped_sensors):
    """
    Creates pandas DataFrames for each sensor type based on the provided data.

    Args:
        sensor_data (dict): A dictionary containing sensor data grouped by type and sensor IDs.
        grouped_sensors (list): A list of grouped sensors by type.

    Returns:
        dict: A dictionary where keys are sensor types and values are DataFrames.

        Example: {'crack_meters': ID         Timestamp  FISS_2D_R+3_Paris-DX  FISS_2D_R+3_Paris-DY  \
        0   2025-01-12 00:00              3.471065             -0.615683

        ID  FISS_2D_R+4_Neuilly-DX  FISS_2D_R+4_Neuilly-DY  \
        0                 2.252419               -0.121473

            """
    df_dict = {}

    for group in grouped_sensors:
        sensor_type = group['type']
        sensor_ids = group['sensors'].keys()

        data_for_this_type = sensor_data[sensor_type]

        rows = []
        for sensor_id in sensor_ids:
            sensor_list = data_for_this_type.get(sensor_id, [])

            for sensor_dict in sensor_list:
                if sensor_id not in sensor_dict:
                    continue
                datapoint_types = sensor_dict[sensor_id].get('datapointTypes', {})

                for datatype, datapoints in datapoint_types.items():
                    for point in datapoints:
                        rows.append({
                            'Identifier': sensor_id,
                            'Datatype': datatype,
                            'Value': point['v'],
                            'Timestamp': pd.to_datetime(point['t'])
                        })

        if not rows:
            df_dict[sensor_type] = pd.DataFrame()
            continue

        df = pd.DataFrame(rows)

        # Map identifiers to their names
        df['Identifier'] = df['Identifier'].map(group['sensors'])

        # Filter to keep only timestamps where minutes are zero
        df = df[df['Timestamp'].dt.minute == 0]
        df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        df = df.reset_index(drop=True)

        # Create a new ID column combining Identifier and Datatype
        df['ID'] = df['Identifier'] + '-' + df['Datatype']

        # Keep only necessary columns
        df = df[['Timestamp', 'ID', 'Value']]

        # Check for duplicates and handle them
        if df.duplicated(subset=['Timestamp', 'ID']).any():
            print(f"Aggregation des doublons pour le type de capteur '{sensor_type}'.")
            df = df.groupby(['Timestamp', 'ID'], as_index=False).agg({'Value': 'mean'})

        # Perform the pivot operation
        df_pivot = df.pivot(index='Timestamp', columns='ID', values='Value').reset_index()

        df_dict[sensor_type] = df_pivot

    return df_dict
