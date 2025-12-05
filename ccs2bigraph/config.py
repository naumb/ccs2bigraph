"""
Configuration Store 

All optional options set by argparse will hold their default values here.
"""

from importlib.resources import files
from importlib.resources.abc import Traversable

# Paths for the template
control_template: Traversable = files('ccs2bigraph.templates').joinpath('controls.big')
bigraphs_template: Traversable = files('ccs2bigraph.templates').joinpath('bigraphs.big')
reactions_template: Traversable = files('ccs2bigraph.templates').joinpath('reactions.big')
brs_template: Traversable = files('ccs2bigraph.templates').joinpath('brs.big')