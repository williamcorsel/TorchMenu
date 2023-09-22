import time

import streamlit as st
import yaml
from httpx import ConnectError

from torchmenu.api.model import get_version_model
from torchmenu.api.torchserve import TorchServe, TorchServeSettings
from torchmenu.components.sidebar import SETTINGS_FILE_PATH, show_sidebar
from torchmenu.components.status import server_status

SESSION_KEY_TORCHSERVE = 'torchserve'


def model_status_panel(torchserve):
    try:
        models = torchserve.get_models()
    except ConnectError:
        st.error('Could not connect to Management API.')
        return

    if len(models) == 0:
        st.info('No models found. Add them on the Registration page.')
        return

    tabs = st.tabs(sorted([model.modelName for model in models]))

    for tab, model in zip(tabs, models):
        tab.write(f'Default Version: {model.defaultVersion}')

        model_select_col, _, set_default_col, unregister_col = tab.columns([0.15, 0.55, 0.15, 0.15])
        default_index = model.versions.index(model.defaultVersion)
        version_model = get_version_model(model, model_select_col.selectbox('Model Version', model.versions,
                                                                            index=default_index))

        if set_default_col.button('Set Default', key=f'{version_model.name}_set_default'):
            torchserve.set_model_default_version(model.modelName, version_model.modelVersion)
            st.rerun()

        if unregister_col.button('Unregister', key=f'{version_model.name}_unregister'):
            with st.spinner('Unregistering model...'):
                torchserve.unregister_model(model.modelName, version_model.modelVersion)
                st.rerun()

        model_memory_usage = int(sum([worker.memoryUsage for worker in version_model.workers]) / 1024 / 1024)
        metrics = [
            {'label': 'Workers', 'value': len(version_model.workers)},
            {'label': 'Batch Size', 'value': version_model.batchSize},
            {'label': 'Memory Usage', 'value': f'{model_memory_usage} MB'},

        ]
        for metric, col in zip(metrics, tab.columns(len(metrics))):
            col.metric(**metric)

        scale_worker_expander = tab.expander('Scale Workers')
        with scale_worker_expander.form(f'{version_model.name}_scale_workers', clear_on_submit=True):
            min_worker_amount = st.number_input('min_workers', min_value=0, value=version_model.minWorkers)
            max_worker_amount = st.number_input('max_workers', min_value=0, value=version_model.maxWorkers)

            if st.form_submit_button('Scale'):
                if min_worker_amount > max_worker_amount:
                    st.error('min_workers cannot be greater than max_workers.')
                    return
                torchserve.scale_workers(version_model, min_worker_amount, max_worker_amount)
                st.toast('Scaled workers successfully!')
                time.sleep(1)
                st.rerun()

        raw_data_expander = tab.expander('Raw Data')
        raw_data_expander.json(version_model.model_dump_json())


def load_torchserve():
    if SESSION_KEY_TORCHSERVE in st.session_state:
        return st.session_state[SESSION_KEY_TORCHSERVE]

    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings_dict = yaml.safe_load(f)
        settings = TorchServeSettings(**settings_dict)

    torchserve = TorchServe(settings)
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
