import streamlit as st

from torchmenu.components.sidebar import show_sidebar
from torchmenu.components.status import server_status
from torchmenu.Home import load_torchserve


def main():
    torchserve = load_torchserve()
    show_sidebar(torchserve)
    server_status(torchserve)

    if torchserve.is_healthy():
        st.subheader('Register a new model')

        with st.form('register_model', clear_on_submit=False):
            url_col, name_col = st.columns(2)
            model_url = url_col.text_input('Model URL')
            model_name = name_col.text_input('Model Name (Optional)')

            batch_size_col, initial_workers_col = st.columns(2)
            batch_size = batch_size_col.number_input('Batch Size', min_value=1, value=1)
            initial_workers = initial_workers_col.number_input('Initial Workers', min_value=0, value=0)

            if st.form_submit_button('Register Model'):
                with st.spinner('Registering model...'):
                    torchserve.register_model(model_url, batch_size, initial_workers, model_name)
                    st.experimental_rerun()
    else:
        st.error('TorchServe is not reachable.')


if __name__ == '__main__':
    st.set_page_config(
        page_title='TorchMenu',
        page_icon=':bento:',
        layout='wide'
    )
    main()
