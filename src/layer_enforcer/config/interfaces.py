from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Set

from layer_enforcer.interfaces import Layer


@dataclass
class Config:
    modules: Set[str] = field(default_factory=set)
    ignore: Set[str] = field(default_factory=set)
    layers: Set[Layer] = field(default_factory=set)
    tree_factory_module: str = "layer_enforcer.grimp:new_grimp_tree"


class ConfigLoader(metaclass=ABCMeta):
    @abstractmethod
    def load(self, config: Config) -> Config:
        """Load config.

        Args:
            config: Config to update.

        Returns:
            Updated config.
        """
