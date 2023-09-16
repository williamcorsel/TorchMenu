import streamlit as st

from torchmenu.api.torchserve import TorchServe


def server_status(torchserve: TorchServe, container: st.container = st):
    torchserve_status = ':green[Healthy]' if torchserve.is_healthy() else ':red[Unhealthy]'
    container.header(f'TorchServe Status: {torchserve_status}')
