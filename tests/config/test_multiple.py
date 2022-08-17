from unittest.mock import Mock, sentinel

from layer_enforcer.config.interfaces import Config
from layer_enforcer.config.multiple import MultipleConfigLoader
from layer_enforcer.config.testing import StaticConfigLoader


class TestMultipleConfigLoader:
    def test_load(self) -> None:
        default_config = Config()
        ml1 = Mock()
        ml2 = Mock()
        cl = MultipleConfigLoader(
            [
                ml1,
                ml2,
                StaticConfigLoader(sentinel.config),
            ]
        )

        assert cl.load(default_config) is sentinel.config

        ml1.load.assert_called_once_with(default_config)
        ml2.load.assert_called_once_with(ml1.load.return_value)
