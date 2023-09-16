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

        with st.form('register_model', clear_on_submit=True):
            model_url = st.text_input('Model URL')
            batch_size = st.number_input('Batch Size', min_value=1, value=1)
            initial_workers = st.number_input('Initial Workers', min_value=0, value=0)
            model_name = st.text_input('Model Name (Optional)')

            if st.form_submit_button('Register Model'):
                torchserve.register_model(model_url, batch_size, initial_workers, model_name)
                st.experimental_rerun()
    else:
        st.error('TorchServe is not reachable.')


if __name__ == '__main__':
    main()
