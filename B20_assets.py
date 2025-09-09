import requests
import pandas as pd
import streamlit as st

def get_assets(project_id, headers):
    """
    Retrieves the list of assets for a given project.
    """
    json_data = {
        'with': ['derivedDatapoints']
    }

    response = requests.post(
        f'https://api.beyond-monitoring.com/api/v2/projects/{project_id}/assets/search-tree',
        headers=headers,
        json=json_data
    )

    if response.status_code != 200:
        st.error(f"Erreur lors de la récupération des assets : {response.status_code}")
        return []

    return response.json().get('data', [])


def get_dict_of_id_assets(assets):
    """
    Creates a dictionary mapping asset IDs to asset names.
    """
    return {asset['id']: asset['name'] for asset in assets}


def extract_asset(project_id, headers, grouped_assets, start_time, end_time):
    """
    Extracts asset data for the specified time range.
    """
    asset_data = {}

    for asset_id in grouped_assets.keys():
        json_data = {
            'filter': {
                'startTime': start_time,
                'endTime': end_time,
                'datapointTypes': [
                    {
                        'entityId': asset_id,
                        'datapoint': 'N_moy',
                        'datapointType': 'derived'
                    }
                ],
                'entityKind': 'Asset',
                'onlyLatest': False,
                'errorStatus': [0, -7, -5],
                'skipNullValues': None,
                'limitLatest': None
            }
        }

        response = requests.post(
            f'https://api.beyond-monitoring.com/api/projects/{project_id}/timeseriesdata/search',
            headers=headers,
            json=json_data
        )

        if response.status_code != 200:
            st.warning(f"Erreur pour l'asset {asset_id} : {response.status_code}")
            continue

        asset_data[asset_id] = response.json().get('data', {})

    return asset_data


def create_dataframes_by_type(asset_data, grouped_assets):
    """
    Creates a pandas DataFrame from asset data.
    """
    rows = []

    for asset_id, asset_name in grouped_assets.items():
        sensor_data = asset_data.get(asset_id, {})

        # Gestion des erreurs dans la structure
        if 'datapointTypes' not in sensor_data:
            st.warning(f"Aucune donnée pour {asset_name}")
            continue

        if 'N_moy' not in sensor_data['datapointTypes']:
            st.warning(f"Donnée 'N_moy' manquante pour {asset_name}")
            continue

        datapoints = sensor_data['datapointTypes']['N_moy']
        for point in datapoints:
            rows.append({
                'Name': asset_name,
                'Value': point['v'],
                'Timestamp': pd.to_datetime(point['t'])
            })

    if not rows:
        st.warning("Aucune donnée asset disponible.")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df[df['Timestamp'].dt.minute == 0]
    df_pivot = df.pivot(index='Timestamp', columns='Name', values='Value').reset_index()
    df_pivot['Timestamp'] = df_pivot['Timestamp'].dt.strftime('%Y-%m-%d %H:%M')

    return df_pivot
