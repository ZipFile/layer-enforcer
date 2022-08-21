"""An explicitly web-layer-labeled module based on imports."""

import fastapi

from .domain.clean import Demo  # upstream imports are allowed
