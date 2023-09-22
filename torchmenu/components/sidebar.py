from pathlib import Path

import streamlit as st
import yaml

from torchmenu.api.torchserve import TorchServe, TorchServeSettings

SETTINGS_FILE_PATH = Path(__file__).parents[1] / 'settings.yaml'


def show_sidebar(torchserve: TorchServe):
    with st.sidebar:
        st.header('Settings')

        settings_dict = {
            'url': st.text_input('TorchServe URL', value=torchserve.settings.url),
            'inference_port': st.text_input('Inference Port', value=torchserve.settings.inference_port),
            'management_port': st.text_input('Management Port', value=torchserve.settings.management_port),
            'metrics_port': st.text_input('Metrics Port', value=torchserve.settings.metrics_port),
            'store_path': st.text_input('Model Store Path', value=torchserve.settings.store_path),
            'config_path': st.text_input('Config Path', value=torchserve.settings.config_path),
        }

        if st.button('Save', use_container_width=True):
            settings = TorchServeSettings(**settings_dict)

            with open(SETTINGS_FILE_PATH, 'w') as f:
                yaml.safe_dump(dict(settings), f)

            st.session_state.clear()
            st.rerun()
