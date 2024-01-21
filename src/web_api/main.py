import hydra
import uvicorn
from omegaconf import OmegaConf
from .api import set_database
from .api import app, database


if __name__ == '__main__':
    cfg = None
    with hydra.initialize(version_base=None, config_path="../../conf", job_name="web_api"):
        cfg = hydra.compose(config_name="webapi_config")
        print(OmegaConf.to_yaml(cfg))
    database = hydra.utils.instantiate(cfg.db)
    set_database(database)
    uvicorn.run("src.web_api.api:app", **cfg.api)