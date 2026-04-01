from aqt import gui_hooks

from .model import setup_model
from .randomizer import run_deck_randomization
from .ui import install_config_action

gui_hooks.profile_did_open.append(setup_model)
gui_hooks.profile_did_open.append(install_config_action)
gui_hooks.state_did_change.append(run_deck_randomization)
