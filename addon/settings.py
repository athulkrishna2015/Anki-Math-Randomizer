from aqt import mw

from .constants import DEFAULT_CONFIG

ADDON_CONFIG_KEY = (__package__ or __name__).split(".")[0]


def get_addon_manager():
    return getattr(mw, "addonManager", None)


def normalize_config(raw_config: dict | None) -> dict[str, bool | int]:
    config = DEFAULT_CONFIG.copy()
    if isinstance(raw_config, dict):
        config.update({key: raw_config[key] for key in DEFAULT_CONFIG if key in raw_config})

    normalized = {
        "enabled": bool(config["enabled"]),
        "include_due": bool(config["include_due"]),
        "include_new": bool(config["include_new"]),
        "include_learning": bool(config["include_learning"]),
        "show_tooltip": bool(config["show_tooltip"]),
        "tooltip_duration_ms": int(config["tooltip_duration_ms"]),
        "refresh_reviewer": bool(config["refresh_reviewer"]),
        "ensure_note_type": bool(config["ensure_note_type"]),
    }
    normalized["tooltip_duration_ms"] = max(500, min(10000, normalized["tooltip_duration_ms"]))

    if not any(
        (
            normalized["include_due"],
            normalized["include_new"],
            normalized["include_learning"],
        )
    ):
        normalized["include_due"] = True

    return normalized


def get_config() -> dict[str, bool | int]:
    addon_manager = get_addon_manager()
    if addon_manager is None:
        return DEFAULT_CONFIG.copy()

    return normalize_config(addon_manager.getConfig(ADDON_CONFIG_KEY))


def save_config(config: dict[str, bool | int]) -> dict[str, bool | int]:
    normalized = normalize_config(config)
    addon_manager = get_addon_manager()
    if addon_manager is not None:
        addon_manager.writeConfig(ADDON_CONFIG_KEY, normalized)
    return normalized


def ensure_config() -> dict[str, bool | int]:
    normalized = get_config()
    return save_config(normalized)
