import logging
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated

from torchmenu.api.model import Model, VersionModel

LOGGER = logging.getLogger(__name__)


def file_exists_or_empty(path: str) -> str:
    assert len(path) <= 0 or Path(path).is_file(), f'File not found at {path}'
    return path


def dir_exists_or_empty(path: str) -> str:
    assert len(path) <= 0 or Path(path).is_dir(), f'Directory not found at {path}'
    return path


FilePath = Annotated[str, AfterValidator(file_exists_or_empty)]
DirPath = Annotated[str, AfterValidator(dir_exists_or_empty)]


class TorchServeSettings(BaseModel):
    url: str
    inference_port: int
    management_port: int
    metrics_port: int
    store_path: DirPath
    config_path: FilePath


class TorchServe:
    def __init__(self,
                 settings: TorchServeSettings
                 ) -> None:
        self.settings = settings
        self.inference_url = f'{self.settings.url}:{self.settings.inference_port}'
        self.management_url = f'{self.settings.url}:{self.settings.management_port}'
        self.metrics_url = f'{self.settings.url}:{self.settings.metrics_port}'

    def is_healthy(self) -> bool:
        with httpx.Client(base_url=self.inference_url) as client:
            try:
                response = client.get('/ping')
            except httpx.ConnectError:
                return False
            return response.status_code == 200

    def get_models(self) -> List[Model]:
        with httpx.Client(base_url=self.management_url) as client:
            response = client.get('/models')
            data = response.json()

        models = [self.get_model(model['modelName']) for model in data['models']]

        return models

    def get_model(self, model_name: str) -> Model:
        version_models = self.get_all_version_models(model_name=model_name)
        default_version = self.get_default_model_version(model_name=model_name)

        return Model(
            modelName=model_name,
            defaultVersion=default_version,
            versionModels=version_models
        )

    def get_default_model(self, model_name: str) -> VersionModel:
        route = f'/models/{model_name}'

        with httpx.Client(base_url=self.management_url) as client:
            response = client.get(route)
            data = response.json()[0]

        return VersionModel(**data)

    def get_version_model(self, model_name: str, version: str) -> VersionModel:
        route = f'/models/{model_name}/{version}'

        with httpx.Client(base_url=self.management_url) as client:
            response = client.get(route)
            data = response.json()

        return VersionModel(**data)

    def get_all_version_models(self, model_name: str) -> Dict[str, VersionModel]:
        route = f'/models/{model_name}/all'

        with httpx.Client(base_url=self.management_url) as client:
            response = client.get(route)
            data = response.json()

        return {model['modelVersion']: VersionModel(**model) for model in data}

    def get_default_model_version(self, model_name: str) -> str:
        default_version_model = self.get_default_model(model_name=model_name)
        return default_version_model.modelVersion

    def get_model_versions(self, model_name: str) -> List[str]:
        route = f'/models/{model_name}/all'

        with httpx.Client(base_url=self.management_url) as client:
            response = client.get(route)
            data = response.json()

        versions = [model['modelVersion'] for model in data['models']]

        return versions

    def scale_workers(self, model: VersionModel, min_workers: int, max_workers: int, synchronous: bool = False,
                      timeout: int = -1) -> None:
        route = f'/models/{model.modelName}/{model.modelVersion}'
        params = {
            'min_worker': min_workers,
            'max_worker': max_workers,
            'synchronous': synchronous,
            'timeout': timeout
        }

        with httpx.Client(base_url=self.management_url) as client:
            response = client.put(route, params=params)

        return response.status_code == 200

    def register_model(self, model_url: str, batch_size: int = 1, initial_workers: int = 0,
                       model_name: Optional[str] = None):
        route = '/models'
        params = {
            'url': model_url,
            'batch_size': batch_size,
            'initial_workers': initial_workers
        }
        if model_name:
            params['model_name'] = model_name

        with httpx.Client(base_url=self.management_url) as client:
            response = client.post(route, params=params, timeout=None)

        return response.status_code == 200

    def unregister_model(self, model_name: str, version: str):
        route = f'/models/{model_name}'
        if version:
            route += f'/{version}'

        with httpx.Client(base_url=self.management_url) as client:
            response = client.delete(route)

        return response.status_code == 200

    def set_model_default_version(self, model_name: str, version: str):
        route = f'/models/{model_name}/{version}/set-default'

        with httpx.Client(base_url=self.management_url) as client:
            response = client.put(route)

        return response.status_code == 200
