import os
import requests
import streamlit as st

# Configuración
BASE_URL = "https://api.elevenlabs.io/v1"
DOWNLOAD_FOLDER = "downloads"

# Crear la carpeta de descargas si no existe
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_history_items(api_key):
    """Obtiene todos los ítems del historial."""
    items = []
    next_id = None

    while True:
        params = {"page_size": 100}
        if next_id:
            params["start_after_history_item_id"] = next_id

        response = requests.get(
            f"{BASE_URL}/history",
            headers={"xi-api-key": api_key},
            params=params
        )

        if response.status_code != 200:
            st.error(f"Error al obtener el historial: {response.text}")
            break

        data = response.json()
        items.extend(data.get("history", []))

        if not data.get("has_more"):
            break

        next_id = data.get("last_history_item_id")
    
    return items

def download_audio(api_key, history_item_id, filename):
    """Descarga un archivo de audio dado su ID."""
    url = f"{BASE_URL}/history/{history_item_id}/audio"
    response = requests.get(
        url,
        headers={"xi-api-key": api_key},
        stream=True
    )

    if response.status_code == 200:
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
    else:
        st.error(f"Error al descargar {filename}: {response.text}")
        return None

def main():
    st.title("Descarga de Audios - ElevenLabs")
    st.write("Descarga automáticamente todos los audios generados usando la API de ElevenLabs.")

    # Campo para ingresar el API Key
    api_key = st.text_input("Introduce tu API Key de ElevenLabs:", type="password")

    if st.button("Iniciar Descarga"):
        if not api_key:
            st.error("Por favor, introduce tu API Key antes de continuar.")
        else:
            with st.spinner("Obteniendo historial de audios..."):
                history_items = get_history_items(api_key)

            if history_items:
                st.success(f"Se encontraron {len(history_items)} audios.")
                for item in history_items:
                    history_item_id = item["history_item_id"]
                    filename = f"{item['date_unix']}_{history_item_id}.mp3"
                    filepath = download_audio(api_key, history_item_id, filename)
                    if filepath:
                        st.write(f"Descargado: {filename}")
                st.success("¡Descarga completa!")
            else:
                st.warning("No se encontraron audios en el historial.")

if __name__ == "__main__":
    main()
