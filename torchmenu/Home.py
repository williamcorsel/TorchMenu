import time

import streamlit as st
import yaml
from httpx import ConnectError

from torchmenu.api.model import get_version_model
from torchmenu.api.torchserve import TorchServe
from torchmenu.components.sidebar import SETTINGS_FILE_PATH, show_sidebar
from torchmenu.components.status import server_status

SESSION_KEY_TORCHSERVE = 'torchserve'


def model_status_panel(torchserve):
    try:
        models = torchserve.get_models()
    except ConnectError:
        st.error('Could not connect to Management API.')
        return

    tabs = st.tabs([model.modelName for model in models])

    for tab, model in zip(tabs, models):
        tab.write(f'Default Version: {model.defaultVersion}')

        col1, _, col2 = tab.columns([0.1, 0.8, 0.10])
        default_index = model.versions.index(model.defaultVersion)
        version_model = get_version_model(model, col1.selectbox('Model Version', model.versions, index=default_index))

        if col2.button('Set Default Model Version', key=f'{version_model.modelName}_set_default'):
            torchserve.set_model_default_version(model.modelName, version_model.modelVersion)
            st.experimental_rerun()

        model_memory_usage = int(sum([worker.memoryUsage for worker in version_model.workers]) / 1024 / 1024)
        metrics = [
            {'label': 'Workers', 'value': len(version_model.workers)},
            {'label': 'Batch Size', 'value': version_model.batchSize},
            {'label': 'Memory Usage', 'value': f'{model_memory_usage} MB'},

        ]
        for metric, col in zip(metrics, tab.columns(len(metrics))):
            col.metric(**metric)

        scale_worker_expander = tab.expander('Scale Workers')
        with scale_worker_expander.form(f'{version_model.modelName}_scale_workers', clear_on_submit=True):
            min_worker_amount = st.slider('min_workers', min_value=1, max_value=10, value=version_model.minWorkers)
            max_worker_amount = st.slider('max_workers', min_value=1, max_value=10, value=version_model.maxWorkers)

            if st.form_submit_button('Scale'):
                torchserve.scale_workers(version_model, min_worker_amount, max_worker_amount)
                st.toast('Scaled workers successfully!')
                time.sleep(1)
                st.experimental_rerun()

        raw_data_expander = tab.expander('Raw Data')
        raw_data_expander.json(version_model.model_dump_json())


def load_torchserve():
    if SESSION_KEY_TORCHSERVE in st.session_state:
        return st.session_state[SESSION_KEY_TORCHSERVE]

    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = yaml.safe_load(f)

    torchserve = TorchServe(**settings)
    st.session_state[SESSION_KEY_TORCHSERVE] = torchserve
    return torchserve


def main():
    torchserve = load_torchserve()
    show_sidebar(torchserve)

    server_status(torchserve)

    if torchserve.is_healthy():
        model_status_panel(torchserve)
    else:
        st.error('TorchServe is not reachable.')


if __name__ == '__main__':
    st.set_page_config(page_title='TorchMenu', page_icon=':bento:', layout='wide')
    main()
