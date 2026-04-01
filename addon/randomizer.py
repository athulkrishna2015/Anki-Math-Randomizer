import random
import re
from datetime import date
from html import unescape

from aqt import mw
from aqt.utils import tooltip

from .constants import (
    CONFLICT_GROUPS,
    FIELD_BACK,
    FIELD_FRONT,
    FIELD_LAST_UPDATE,
    FIELD_SOURCE_BACK,
    FIELD_SOURCE_FRONT,
    GREEK_PATTERN,
    HTML_TAG_PATTERN,
    MODEL_NAME,
    POOLS,
    TAG_PATTERN,
    TAG_TYPE_PATTERN,
)
from .settings import get_config


def is_conflict(value_1: str, value_2: str) -> bool:
    if value_1 == value_2:
        return True

    for group in CONFLICT_GROUPS:
        if value_1 in group and value_2 in group:
            return True

    return False


def strip_markup(content: str) -> str:
    without_tags = HTML_TAG_PATTERN.sub(" ", content or "")
    return unescape(without_tags).replace("\xa0", " ")


def unique_tags(content: str) -> list[str]:
    return list(dict.fromkeys(TAG_PATTERN.findall(content or "")))


def get_static_symbols(content: str) -> list[str]:
    used = set()
    clean_content = TAG_PATTERN.sub("", strip_markup(content))

    for match in GREEK_PATTERN.findall(clean_content):
        used.add(f"\\{match}")

    clean_content = re.sub(r"\\[a-zA-Z]+", "", clean_content)
    used.update(re.findall(r"[a-zA-Z]", clean_content))
    return sorted(used)


def build_assignment_map(
    content: str,
    existing_static_symbols: list[str] | None = None,
) -> dict[str, str]:
    if not content:
        return {}

    used_symbols = (
        list(existing_static_symbols)
        if existing_static_symbols is not None
        else get_static_symbols(content)
    )
    tags = unique_tags(content)
    temp_pools = {pool_name: values[:] for pool_name, values in POOLS.items()}

    for values in temp_pools.values():
        random.shuffle(values)

    assignment_map = {}

    for tag in tags:
        type_match = TAG_TYPE_PATTERN.match(tag)
        if not type_match:
            continue

        pool = temp_pools[type_match.group(1)]
        selected = None

        for index, candidate in enumerate(pool):
            if any(is_conflict(candidate, used) for used in used_symbols):
                continue

            selected = candidate
            pool.pop(index)
            break

        if selected is None and pool:
            selected = pool.pop(0)

        if selected:
            assignment_map[tag] = selected
            used_symbols.append(selected)

    return assignment_map


def apply_assignment_map(content: str, assignment_map: dict[str, str]) -> str:
    randomized = content

    for tag in sorted(assignment_map, key=len, reverse=True):
        randomized = randomized.replace(tag, assignment_map[tag])

    return randomized


def generate_randomized_content(
    source_text: str,
    existing_static_vars: list[str] | None = None,
) -> str:
    if not source_text:
        return source_text

    assignment_map = build_assignment_map(source_text, existing_static_vars)
    return apply_assignment_map(source_text, assignment_map)


def get_note_field(note, field_name: str, default: str = "") -> str:
    try:
        value = note[field_name]
    except KeyError:
        return default

    return value or default


def escape_search_term(term: str) -> str:
    return (term or "").replace("\\", "\\\\").replace('"', '\\"')


def build_note_query(model_id: int, deck_name: str, config: dict[str, bool | int]) -> str | None:
    state_terms = []
    if config["include_due"]:
        state_terms.append("is:due")
    if config["include_new"]:
        state_terms.append("is:new")
    if config["include_learning"]:
        state_terms.append("is:learn")

    if not state_terms:
        return None

    escaped_deck_name = escape_search_term(deck_name)
    states_query = " OR ".join(state_terms)
    return f'mid:{model_id} deck:"{escaped_deck_name}" ({states_query})'


def randomize_note(note, today_string: str) -> bool:
    if get_note_field(note, FIELD_LAST_UPDATE) == today_string:
        return False

    source_front = get_note_field(note, FIELD_SOURCE_FRONT)
    source_back = get_note_field(note, FIELD_SOURCE_BACK)
    if not source_front:
        return False

    combined_source = f"{source_front} {source_back}".strip()
    assignment_map = build_assignment_map(
        combined_source,
        get_static_symbols(combined_source),
    )

    note[FIELD_FRONT] = apply_assignment_map(source_front, assignment_map)
    note[FIELD_BACK] = apply_assignment_map(source_back, assignment_map)
    note[FIELD_LAST_UPDATE] = today_string
    return True


def run_deck_randomization(new_state, old_state) -> None:
    if new_state != "review" or mw.col is None:
        return

    config = get_config()
    if not config["enabled"]:
        return

    collection = mw.col
    model = collection.models.by_name(MODEL_NAME)
    if not model:
        return

    deck = collection.decks.get(collection.decks.selected())
    if not deck:
        return

    query = build_note_query(model["id"], deck["name"], config)
    if not query:
        return

    note_ids = collection.find_notes(query)
    if not note_ids:
        return

    today_string = str(date.today())
    updated_note_ids = []

    for note_id in note_ids:
        note = collection.get_note(note_id)
        if not randomize_note(note, today_string):
            continue

        collection.update_note(note)
        updated_note_ids.append(note_id)

    if not updated_note_ids:
        return

    reviewer = getattr(mw, "reviewer", None)
    current_card = getattr(reviewer, "card", None)
    if config["refresh_reviewer"] and current_card and current_card.nid in updated_note_ids:
        mw.reset()

    if config["show_tooltip"]:
        tooltip(
            f"Math Randomizer: Randomized {len(updated_note_ids)} cards in '{deck['name']}'",
            period=int(config["tooltip_duration_ms"]),
        )
