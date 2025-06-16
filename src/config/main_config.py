import os
from typing import Any

import yaml


class MainConfig():

    def __init__(self, project_name: str, service_name: str, description: str, note: str,
                 system_integrator: str, log_path: str, log_level: str,
                 **kwargs: dict[str, Any]) -> None:
        self.project_name = project_name
        self.service_name = service_name
        self.description = description
        self.note = note
        self.system_integrator = system_integrator

        self.log_path = log_path
        self.log_level = log_level.upper()


main_config: MainConfig | None = None


def get_main_config():
    global main_config
    if main_config is None:
        main_config_raw = dict()
        main_config_path = os.path.join("src", "config", "main_config.yml")
        with open(main_config_path, encoding="utf-8") as file:
            main_config_raw: dict = yaml.load(file, Loader=yaml.FullLoader)  # type: ignore
        main_config = MainConfig(**main_config_raw)

    return main_config
