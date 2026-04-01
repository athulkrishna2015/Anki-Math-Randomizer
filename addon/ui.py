from aqt import mw
from aqt.qt import (
    QApplication,
    QCheckBox,
    QDesktopServices,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPixmap,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    Qt,
    QUrl,
    QVBoxLayout,
    QWidget,
)
from aqt.utils import tooltip

from .constants import DEFAULT_CONFIG, KOFI_URL, SUPPORT_DESTINATIONS, SUPPORT_DIR
from .settings import (
    ADDON_CONFIG_KEY,
    ensure_config,
    get_addon_manager,
    normalize_config,
    save_config,
)

ALIGN_CENTER = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter")
TEXT_SELECTABLE_BY_MOUSE = getattr(
    getattr(Qt, "TextInteractionFlag", Qt),
    "TextSelectableByMouse",
)
KEEP_ASPECT_RATIO = getattr(
    getattr(Qt, "AspectRatioMode", Qt),
    "KeepAspectRatio",
)
SMOOTH_TRANSFORMATION = getattr(
    getattr(Qt, "TransformationMode", Qt),
    "SmoothTransformation",
)
BUTTON_ROLE = getattr(QDialogButtonBox, "ButtonRole", QDialogButtonBox)
STANDARD_BUTTON = getattr(QDialogButtonBox, "StandardButton", QDialogButtonBox)


def exec_dialog(dialog: QDialog) -> int:
    exec_method = getattr(dialog, "exec", None) or getattr(dialog, "exec_", None)
    return exec_method()


def open_external_url(url: str) -> None:
    QDesktopServices.openUrl(QUrl(url))


def copy_support_value(label: str, value: str) -> None:
    QApplication.clipboard().setText(value)
    tooltip(f"Copied {label}", period=2000)


def create_body_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    return label


def create_general_tab(config: dict[str, bool | int]) -> tuple[QWidget, dict[str, object]]:
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(12)

    intro_label = create_body_label(
        "Configure when Math Randomizer runs and how much feedback it shows during review."
    )
    layout.addWidget(intro_label)

    automation_group = QGroupBox("Review Automation")
    automation_layout = QVBoxLayout(automation_group)

    enabled_checkbox = QCheckBox("Enable automatic randomization when entering review")
    enabled_checkbox.setChecked(bool(config["enabled"]))
    automation_layout.addWidget(enabled_checkbox)

    include_due_checkbox = QCheckBox("Process due cards")
    include_due_checkbox.setChecked(bool(config["include_due"]))
    automation_layout.addWidget(include_due_checkbox)

    include_new_checkbox = QCheckBox("Process new cards")
    include_new_checkbox.setChecked(bool(config["include_new"]))
    automation_layout.addWidget(include_new_checkbox)

    include_learning_checkbox = QCheckBox("Process learning cards")
    include_learning_checkbox.setChecked(bool(config["include_learning"]))
    automation_layout.addWidget(include_learning_checkbox)

    automation_layout.addWidget(
        create_body_label("At least one review-state option will remain enabled when you save.")
    )
    layout.addWidget(automation_group)

    feedback_group = QGroupBox("Feedback")
    feedback_layout = QFormLayout(feedback_group)

    show_tooltip_checkbox = QCheckBox("Show a summary tooltip after updates")
    show_tooltip_checkbox.setChecked(bool(config["show_tooltip"]))
    feedback_layout.addRow(show_tooltip_checkbox)

    tooltip_duration_spin = QSpinBox()
    tooltip_duration_spin.setRange(500, 10000)
    tooltip_duration_spin.setSingleStep(250)
    tooltip_duration_spin.setSuffix(" ms")
    tooltip_duration_spin.setValue(int(config["tooltip_duration_ms"]))
    feedback_layout.addRow("Tooltip duration", tooltip_duration_spin)

    refresh_reviewer_checkbox = QCheckBox(
        "Refresh the reviewer immediately if the current card was updated"
    )
    refresh_reviewer_checkbox.setChecked(bool(config["refresh_reviewer"]))
    feedback_layout.addRow(refresh_reviewer_checkbox)
    layout.addWidget(feedback_group)

    maintenance_group = QGroupBox("Note Type Maintenance")
    maintenance_layout = QVBoxLayout(maintenance_group)

    ensure_note_type_checkbox = QCheckBox(
        "Create or repair the Math Randomizer note type on profile open"
    )
    ensure_note_type_checkbox.setChecked(bool(config["ensure_note_type"]))
    maintenance_layout.addWidget(ensure_note_type_checkbox)
    maintenance_layout.addWidget(
        create_body_label(
            "The addon still uses the LastUpdate field to avoid re-randomizing the same note more than once per day."
        )
    )
    layout.addWidget(maintenance_group)
    layout.addStretch(1)

    controls = {
        "enabled": enabled_checkbox,
        "include_due": include_due_checkbox,
        "include_new": include_new_checkbox,
        "include_learning": include_learning_checkbox,
        "show_tooltip": show_tooltip_checkbox,
        "tooltip_duration_ms": tooltip_duration_spin,
        "refresh_reviewer": refresh_reviewer_checkbox,
        "ensure_note_type": ensure_note_type_checkbox,
    }

    def refresh_controls() -> None:
        enabled = enabled_checkbox.isChecked()
        include_due_checkbox.setEnabled(enabled)
        include_new_checkbox.setEnabled(enabled)
        include_learning_checkbox.setEnabled(enabled)
        show_tooltip_checkbox.setEnabled(enabled)
        tooltip_duration_spin.setEnabled(enabled and show_tooltip_checkbox.isChecked())
        refresh_reviewer_checkbox.setEnabled(enabled)

    enabled_checkbox.toggled.connect(refresh_controls)
    show_tooltip_checkbox.toggled.connect(refresh_controls)
    controls["refresh"] = refresh_controls
    refresh_controls()
    return tab, controls


def read_config_from_controls(controls: dict[str, object]) -> dict[str, bool | int]:
    return {
        "enabled": controls["enabled"].isChecked(),
        "include_due": controls["include_due"].isChecked(),
        "include_new": controls["include_new"].isChecked(),
        "include_learning": controls["include_learning"].isChecked(),
        "show_tooltip": controls["show_tooltip"].isChecked(),
        "tooltip_duration_ms": controls["tooltip_duration_ms"].value(),
        "refresh_reviewer": controls["refresh_reviewer"].isChecked(),
        "ensure_note_type": controls["ensure_note_type"].isChecked(),
    }


def apply_config_to_controls(controls: dict[str, object], config: dict[str, bool | int]) -> None:
    normalized = normalize_config(config)
    controls["enabled"].setChecked(bool(normalized["enabled"]))
    controls["include_due"].setChecked(bool(normalized["include_due"]))
    controls["include_new"].setChecked(bool(normalized["include_new"]))
    controls["include_learning"].setChecked(bool(normalized["include_learning"]))
    controls["show_tooltip"].setChecked(bool(normalized["show_tooltip"]))
    controls["tooltip_duration_ms"].setValue(int(normalized["tooltip_duration_ms"]))
    controls["refresh_reviewer"].setChecked(bool(normalized["refresh_reviewer"]))
    controls["ensure_note_type"].setChecked(bool(normalized["ensure_note_type"]))
    controls["refresh"]()


def create_support_image_label(filename: str) -> QLabel:
    image_label = QLabel()
    image_label.setAlignment(ALIGN_CENTER)
    image_label.setMinimumSize(320, 320)

    pixmap = QPixmap(str(SUPPORT_DIR / filename))
    if pixmap.isNull():
        image_label.setText(f"Missing QR image: {filename}")
        return image_label

    image_label.setPixmap(
        pixmap.scaled(
            360,
            360,
            KEEP_ASPECT_RATIO,
            SMOOTH_TRANSFORMATION,
        )
    )
    return image_label


def create_selectable_value_label(value: str) -> QLabel:
    label = QLabel(value)
    label.setWordWrap(True)
    label.setTextInteractionFlags(TEXT_SELECTABLE_BY_MOUSE)
    return label


def create_support_card(item: dict[str, str]) -> QGroupBox:
    group = QGroupBox(item["title"])
    layout = QHBoxLayout(group)
    layout.setSpacing(16)
    layout.addWidget(create_support_image_label(item["filename"]))

    details_layout = QVBoxLayout()
    details_layout.addWidget(create_body_label(item["description"]))
    details_layout.addWidget(QLabel(item["value_label"]))
    details_layout.addWidget(create_selectable_value_label(item["value"]))

    copy_button = QPushButton(item["copy_label"])
    copy_button.clicked.connect(
        lambda _checked=False, item=item: copy_support_value(
            item["value_label"],
            item["value"],
        )
    )
    details_layout.addWidget(copy_button)
    details_layout.addStretch(1)

    layout.addLayout(details_layout, 1)
    return group


def create_kofi_group() -> QGroupBox:
    group = QGroupBox("Ko-fi")
    layout = QVBoxLayout(group)
    layout.addWidget(
        create_body_label(
            "This configuration window uses native Qt widgets only. Use the button below to open the Ko-fi page in your browser."
        )
    )

    button_row = QHBoxLayout()
    open_button = QPushButton("Open Ko-fi Page")
    open_button.clicked.connect(lambda _checked=False: open_external_url(KOFI_URL))
    button_row.addWidget(open_button)

    copy_button = QPushButton("Copy Ko-fi Link")
    copy_button.clicked.connect(
        lambda _checked=False: copy_support_value("Ko-fi link", KOFI_URL)
    )
    button_row.addWidget(copy_button)
    button_row.addStretch(1)
    layout.addLayout(button_row)
    layout.addWidget(create_selectable_value_label(KOFI_URL))
    return group


def create_support_tab() -> QWidget:
    tab = QWidget()
    root_layout = QVBoxLayout(tab)
    root_layout.setContentsMargins(0, 0, 0, 0)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    content = QWidget()
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(12, 12, 12, 12)
    content_layout.setSpacing(12)

    content_layout.addWidget(
        create_body_label(
            "Support Math Randomizer through Ko-fi or direct payments. The QR codes below are kept large for easy scanning."
        )
    )
    content_layout.addWidget(create_kofi_group())

    for item in SUPPORT_DESTINATIONS:
        content_layout.addWidget(create_support_card(item))

    content_layout.addStretch(1)
    scroll_area.setWidget(content)
    root_layout.addWidget(scroll_area)
    return tab


def show_config_dialog() -> None:
    current_config = ensure_config()

    dialog = QDialog(mw)
    dialog.setWindowTitle("Math Randomizer Configuration")
    dialog.setMinimumSize(900, 720)

    root_layout = QVBoxLayout(dialog)
    header_label = QLabel("Math Randomizer")
    root_layout.addWidget(header_label)
    root_layout.addWidget(
        create_body_label(
            "Use the General tab for addon behavior and the Support tab for donation options."
        )
    )

    tabs = QTabWidget()
    general_tab, controls = create_general_tab(current_config)
    tabs.addTab(general_tab, "General")
    tabs.addTab(create_support_tab(), "Support")
    root_layout.addWidget(tabs, 1)

    button_box = QDialogButtonBox()
    reset_button = button_box.addButton("Reset to Defaults", BUTTON_ROLE.ResetRole)
    cancel_button = button_box.addButton(STANDARD_BUTTON.Cancel)
    save_button = button_box.addButton(STANDARD_BUTTON.Save)

    reset_button.clicked.connect(
        lambda _checked=False: apply_config_to_controls(controls, DEFAULT_CONFIG)
    )
    cancel_button.clicked.connect(dialog.reject)

    def save_and_close() -> None:
        new_config = read_config_from_controls(controls)
        if not any(
            (
                new_config["include_due"],
                new_config["include_new"],
                new_config["include_learning"],
            )
        ):
            tooltip(
                "At least one card state must be enabled. Keeping Due cards enabled.",
                period=2500,
            )

        normalized = save_config(new_config)
        apply_config_to_controls(controls, normalized)
        tooltip("Math Randomizer settings saved", period=2000)
        dialog.accept()

    save_button.clicked.connect(save_and_close)
    root_layout.addWidget(button_box)
    exec_dialog(dialog)


def install_config_action() -> None:
    addon_manager = get_addon_manager()
    if addon_manager is not None:
        ensure_config()
        addon_manager.setConfigAction(ADDON_CONFIG_KEY, show_config_dialog)
