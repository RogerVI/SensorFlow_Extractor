import streamlit as st

def read_projects(file_path):
    """
    Reads projects from a .txt file and returns them as a list of tuples (name, id).
    """
    projects = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if ':' in line:
                    name, project_id = line.split(':')
                    projects.append((name.strip(), project_id.strip()))
    except FileNotFoundError:
        st.error(f"Fichier introuvable : {file_path}")
        return None
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        return None

    return projects

def project_id(file_path):
    """
    Displays a Streamlit dropdown to select a project.

    Returns:
        tuple: (project_id, project_name)
    """
    projects = read_projects(file_path)

    if not projects:
        st.warning("Aucun projet disponible.")
        st.stop()

    project_names = [name for name, _ in projects]
    selected_name = st.selectbox("Sélectionnez un projet :", project_names)

    for name, pid in projects:
        if name == selected_name:
            return pid, name

    # Fallback (ne devrait pas arriver)
    st.error("Projet sélectionné invalide.")
    st.stop()
