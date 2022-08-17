from typing import List

from .interfaces import Config, ConfigLoader


class MultipleConfigLoader(ConfigLoader):
    def __init__(self, config_loaders: List[ConfigLoader]) -> None:
        self.config_loaders = config_loaders

    def load(self, config: Config) -> Config:
        for config_loader in self.config_loaders:
            config = config_loader.load(config)

        return config
