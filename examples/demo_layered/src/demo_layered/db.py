"""An explicitly db-layer-labeled module based on imports."""

import sqlalchemy

from .domain.clean import Demo  # upstream imports are allowed
