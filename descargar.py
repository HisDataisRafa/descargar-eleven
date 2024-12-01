import os
import requests
import streamlit as st
from io import BytesIO
from zipfile import ZipFile

# Configuración
BASE_URL = "https://api.elevenlabs.io/v1"

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

def download_audio(api_key, history_item_id):
    """Descarga un archivo de audio dado su ID y lo devuelve como BytesIO."""
    url = f"{BASE_URL}/history/{history_item_id}/audio"
    response = requests.get(
        url,
        headers={"xi-api-key": api_key},
        stream=True
    )

    if response.status_code == 200:
        audio = BytesIO(response.content)
        return audio
    else:
        st.error(f"Error al descargar audio con ID {history_item_id}: {response.text}")
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
                files_downloaded = []
                for item in history_items:
                    history_item_id = item["history_item_id"]
                    filename = f"{item['date_unix']}_{history_item_id}.mp3"
                    audio = download_audio(api_key, history_item_id)
                    if audio:
                        files_downloaded.append((filename, audio))

                # Crear archivo ZIP con todos los audios
                if files_downloaded:
                    zip_buffer = BytesIO()
                    with ZipFile(zip_buffer, "w") as zipf:
                        for filename, audio in files_downloaded:
                            zipf.writestr(filename, audio.getvalue())
                    
                    zip_buffer.seek(0)

                    # Agregar botón para descargar el ZIP
                    st.download_button(
                        label="Descargar todos los audios como ZIP",
                        data=zip_buffer,
                        file_name="audios_descargados.zip",
                        mime="application/zip",
                    )
                st.success("¡Descarga completa!")
            else:
                st.warning("No se encontraron audios en el historial.")

if __name__ == "__main__":
    main()
