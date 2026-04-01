import re
from pathlib import Path

MODEL_NAME = "Math Randomizer (Daily Static)"

FIELD_SOURCE_FRONT = "Source Front"
FIELD_SOURCE_BACK = "Source Back"
FIELD_FRONT = "Front"
FIELD_BACK = "Back"
FIELD_LAST_UPDATE = "LastUpdate"
REQUIRED_FIELDS = (
    FIELD_SOURCE_FRONT,
    FIELD_SOURCE_BACK,
    FIELD_FRONT,
    FIELD_BACK,
    FIELD_LAST_UPDATE,
)

TAG_PATTERN = re.compile(r"(?:VL|Vl|VG|Vg|VN|VV)\d+")
TAG_TYPE_PATTERN = re.compile(r"(VL|Vl|VG|Vg|VN|VV)")
GREEK_PATTERN = re.compile(
    r"\\("
    r"alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|"
    r"xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|"
    r"Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega"
    r")"
)
HTML_TAG_PATTERN = re.compile(r"</?[A-Za-z][^>]*?>")

CARD_TEMPLATE_NAME = "Card 1"
CARD_FRONT_TEMPLATE = "{{Front}}"
CARD_BACK_TEMPLATE = "{{FrontSide}}\n<hr id=answer>\n{{Back}}"
DEFAULT_MODEL_CSS = (
    ".card { font-family: arial; font-size: 20px; text-align: center; "
    "color: black; background-color: white; }"
)

ADDON_DIR = Path(__file__).resolve().parent
SUPPORT_DIR = ADDON_DIR / "Support"
KOFI_URL = "https://ko-fi.com/D1D01W6NQT"

SUPPORT_DESTINATIONS = (
    {
        "title": "UPI",
        "description": "Scan with any UPI app or copy the UPI ID.",
        "value_label": "UPI ID",
        "value": "athulkrishnasv2015-2@okhdfcbank",
        "copy_label": "Copy UPI ID",
        "filename": "UPI.jpg",
    },
    {
        "title": "Bitcoin",
        "description": "Use the QR code for BTC or copy the wallet address.",
        "value_label": "BTC wallet",
        "value": "bc1qrrek3m7sr33qujjrktj949wav6mehdsk057cfx",
        "copy_label": "Copy BTC wallet",
        "filename": "BTC.jpg",
    },
    {
        "title": "Ethereum",
        "description": "Use the QR code for ETH or copy the wallet address.",
        "value_label": "ETH wallet",
        "value": "0xce6899e4903EcB08bE5Be65E44549fadC3F45D27",
        "copy_label": "Copy ETH wallet",
        "filename": "ETH.jpg",
    },
)

DEFAULT_CONFIG = {
    "enabled": True,
    "include_due": True,
    "include_new": True,
    "include_learning": True,
    "show_tooltip": True,
    "tooltip_duration_ms": 3000,
    "refresh_reviewer": True,
    "ensure_note_type": True,
}

CONFLICT_GROUPS = [
    ["I", "l", "1", "|"],
    ["O", "o", "0", "Q", "\\Theta", "\\theta"],
    ["v", "\\nu", "\\upsilon"],
    ["u", "\\mu"],
    ["w", "\\omega"],
    ["x", "\\chi", "\\times"],
    ["p", "\\rho"],
    ["B", "\\beta"],
]


def get_char_range(start: int, end: int) -> list[str]:
    return [chr(i) for i in range(start, end + 1)]


POOLS = {
    "VL": get_char_range(65, 90),
    "Vl": get_char_range(97, 122),
    "VG": [
        "\\Gamma",
        "\\Delta",
        "\\Theta",
        "\\Lambda",
        "\\Xi",
        "\\Pi",
        "\\Sigma",
        "\\Upsilon",
        "\\Phi",
        "\\Psi",
        "\\Omega",
    ],
    "Vg": [
        "\\alpha",
        "\\beta",
        "\\gamma",
        "\\delta",
        "\\epsilon",
        "\\zeta",
        "\\eta",
        "\\theta",
        "\\iota",
        "\\kappa",
        "\\lambda",
        "\\mu",
        "\\nu",
        "\\xi",
        "\\pi",
        "\\rho",
        "\\sigma",
        "\\tau",
        "\\upsilon",
        "\\phi",
        "\\chi",
        "\\psi",
        "\\omega",
    ],
    "VN": [str(i) for i in range(2, 10)],
}
POOLS["VV"] = POOLS["VL"] + POOLS["Vl"] + POOLS["VG"] + POOLS["Vg"]
