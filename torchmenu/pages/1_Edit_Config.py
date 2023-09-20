from pathlib import Path
from typing import List

import streamlit as st

from torchmenu.components.sidebar import show_sidebar
from torchmenu.components.status import server_status
from torchmenu.Home import load_torchserve


def config_validation(lines: List[str]) -> bool:
    for line in lines:
        if len(line.strip()) <= 0 or line.startswith('#'):
            continue
        if '=' not in line:
            return False
    return True


def main():
    torchserve = load_torchserve()
    show_sidebar(torchserve)
    server_status(torchserve)

    if torchserve.is_healthy():
        config_path = Path(torchserve.settings.config_path)

        if not config_path.is_file():
            st.error(f'Config file not found at \"{config_path}\"')
            return

        with open(config_path, 'r') as f:
            lines = f.readlines()

        st.subheader('Config')

        with st.form('config', clear_on_submit=False):
            lines = st.text_area('Config', value=''.join(lines), height=500)
            lines = lines.split('\n')
            lines = [line + '\n' for line in lines if len(line.strip()) > 0]
            if st.form_submit_button('Save'):
                print(lines)
                if not config_validation(lines):
                    st.error('Config file is invalid.')
                else:
                    with open(config_path, 'w') as f:
                        f.writelines(lines)
                    st.success('Config file saved successfully.')


if __name__ == '__main__':
    main()
