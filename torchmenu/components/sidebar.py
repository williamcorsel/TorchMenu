from pathlib import Path

import streamlit as st
import yaml

from torchmenu.api.torchserve import TorchServe

SETTINGS_FILE_PATH = Path(__file__).parents[1] / 'settings.yaml'


def show_sidebar(torchserve: TorchServe):
    with st.sidebar:
        st.header('Settings')
        settings = {
            'url': st.text_input('TorchServe URL', value=torchserve.base_url),
            'inference_port': st.text_input('Inference Port', value=torchserve.inference_port),
            'management_port': st.text_input('Management Port', value=torchserve.management_port),
            'metrics_port': st.text_input('Metrics Port', value=torchserve.metrics_port),
        }

        if st.button('Save', use_container_width=True):
            with open(SETTINGS_FILE_PATH, 'w') as f:
                yaml.safe_dump(settings, f)
            st.session_state.clear()
            st.experimental_rerun()

        st.header('Actions')
        if st.button('Reload', use_container_width=True):
            st.session_state.clear()
            st.experimental_rerun()


def save_settings(settings):
    with open(SETTINGS_FILE_PATH, 'w') as f:
        yaml.safe_dump(settings, f)

    torchserve = TorchServe(**settings)
    return torchserve
