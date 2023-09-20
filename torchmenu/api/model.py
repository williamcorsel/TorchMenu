from typing import Dict, List, Optional

from pydantic import BaseModel, computed_field


class Worker(BaseModel):
    id: str
    startTime: str
    status: str
    gpu: bool
    memoryUsage: int


class JobQueueStatus(BaseModel):
    remainingCapacity: int
    pendingRequests: int


class VersionModel(BaseModel):
    modelName: str
    modelVersion: str
    modelUrl: str
    runtime: str
    minWorkers: int
    maxWorkers: int
    batchSize: int
    maxBatchDelay: int
    loadedAtStartup: bool
    workers: List[Worker]
    jobQueueStatus: JobQueueStatus

    @computed_field
    @property
    def name(self) -> str:
        return f'{self.modelName}:{self.modelVersion}'


class Model(BaseModel):
    modelName: str
    defaultVersion: str
    versionModels: Dict[str, VersionModel]

    @computed_field
    @property
    def versions(self) -> List[str]:
        return sorted(list(self.versionModels.keys()))


def get_version_model(model: Model, version: Optional[str] = None) -> VersionModel:
    if version is None:
        version = model.defaultVersion
    return model.versionModels[version]
