from anki.consts import MODEL_STD
from aqt import mw

from .constants import (
    CARD_BACK_TEMPLATE,
    CARD_FRONT_TEMPLATE,
    CARD_TEMPLATE_NAME,
    DEFAULT_MODEL_CSS,
    MODEL_NAME,
    REQUIRED_FIELDS,
)
from .settings import get_config


def ensure_required_fields(model) -> None:
    existing_field_names = {field["name"] for field in model["flds"]}

    for field_name in REQUIRED_FIELDS:
        if field_name not in existing_field_names:
            mw.col.models.add_field(model, mw.col.models.new_field(field_name))


def ensure_template(model) -> None:
    if model["tmpls"]:
        return

    template = mw.col.models.new_template(CARD_TEMPLATE_NAME)
    template["qfmt"] = CARD_FRONT_TEMPLATE
    template["afmt"] = CARD_BACK_TEMPLATE
    mw.col.models.add_template(model, template)


def setup_model() -> None:
    if mw.col is None:
        return

    config = get_config()
    if not config["ensure_note_type"]:
        return

    model = mw.col.models.by_name(MODEL_NAME)
    if model is None:
        model = mw.col.models.new(MODEL_NAME)
        model["type"] = MODEL_STD

        for field_name in REQUIRED_FIELDS:
            mw.col.models.add_field(model, mw.col.models.new_field(field_name))

        template = mw.col.models.new_template(CARD_TEMPLATE_NAME)
        template["qfmt"] = CARD_FRONT_TEMPLATE
        template["afmt"] = CARD_BACK_TEMPLATE
        mw.col.models.add_template(model, template)
        model["css"] = DEFAULT_MODEL_CSS
        mw.col.models.add(model)
        return

    ensure_required_fields(model)
    ensure_template(model)
