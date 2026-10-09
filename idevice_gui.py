#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A comprehensive and modernized PyQt5 GUI for libimobiledevice tools.
This version focuses on a cleaner UI, better user experience, improved styling,
and full internationalization (i18n) support.
"""

import sys
import shlex
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QGridLayout, QGroupBox, QLabel, QLineEdit,
    QCheckBox, QComboBox, QTextEdit, QFileDialog, QRadioButton,
    QStatusBar, QProgressBar, QMessageBox, QSplitter, QAction, QActionGroup,
    QMenu, QTabBar, QStyle
)
from PyQt5.QtGui import QFont, QIcon, QTextCursor
from PyQt5.QtCore import QProcess, Qt, QSize, QSettings

# Helper class for LineEdits that accept drag-and-drop file paths
class FileDropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            self.setText(url.toLocalFile())
            event.acceptProposedAction()
        else:
            event.ignore()

class IdeviceGUITool(QMainWindow):
    """Main window for the modern iDevice & iRecovery GUI Tool."""

    def __init__(self):
        super().__init__()
        self.settings = QSettings("iDeviceGUITool_Modern", "App")
        
        self.current_lang = self.settings.value("language", "sv")
        self.init_translations()
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowIcon(self._get_icon("phone"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)
        
        # --- Menu Bar ---
        self.create_menu()

        # --- Top Bar ---
        top_bar_layout = QHBoxLayout()
        self.udid_label = QLabel()
        top_bar_layout.addWidget(self.udid_label)
        self.udid_combo = QComboBox()
        top_bar_layout.addWidget(self.udid_combo, 1)
        
        self.refresh_udid_button = QPushButton(self._get_icon("refresh"), "")
        self.refresh_udid_button.clicked.connect(self.populate_udids)
        top_bar_layout.addWidget(self.refresh_udid_button)
        self.main_layout.addLayout(top_bar_layout)

        # --- Main Splitter (Controls | Output) ---
        main_splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(main_splitter)

        # --- Top Widget: Controls ---
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0,0,0,0)
        
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setElideMode(Qt.ElideRight)
        self.tabs.setIconSize(QSize(18, 18))
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setUsesScrollButtons(True)
        self.tabs.tabBar().setMinimumHeight(30)
        self.tabs.currentChanged.connect(self.update_ui_for_current_tab)
        controls_layout.addWidget(self.tabs)
        
        # --- Bottom Widget: Output ---
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(0,0,0,0)
        self.output_group = QGroupBox()
        self.output_group_layout = QVBoxLayout(self.output_group)
        self.output_group_layout.setContentsMargins(6, 6, 6, 6)
        self.output_group_layout.setSpacing(5)
        
        self.command_display = QLineEdit()
        self.command_display.setReadOnly(True)
        self.command_display.setFont(QFont("monospace", 9))
        self.output_group_layout.addWidget(self.command_display)
        
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_group_layout.addWidget(self.output_area)
        
        output_buttons_layout = QHBoxLayout()
        self.run_button = QPushButton(self._get_icon("run"), "")
        self.run_button.clicked.connect(self.run_command)
        self.abort_button = QPushButton(self._get_icon("abort"), "")
        self.abort_button.clicked.connect(self.abort_command)
        output_buttons_layout.addWidget(self.run_button)
        output_buttons_layout.addWidget(self.abort_button)
        output_buttons_layout.addStretch()
        self.clear_output_button = QPushButton(self._get_icon("clear"), "")
        self.clear_output_button.clicked.connect(self.output_area.clear)
        output_buttons_layout.addWidget(self.clear_output_button)
        self.output_group_layout.addLayout(output_buttons_layout)
        
        output_layout.addWidget(self.output_group)
        
        main_splitter.addWidget(controls_widget)
        main_splitter.addWidget(output_widget)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        # Keep the console useful without letting it push the active tool below the screen.
        main_splitter.setSizes([max(360, self.height() - 250), 190])

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)

        # --- Create Tabs ---
        self.create_ideviceinfo_tab()
        self.create_idevicediagnostics_tab()
        self.create_idevicebackup2_tab()
        self.create_ideviceprovision_tab()
        self.create_idevicerestore_tab()
        self.create_ideviceimagemounter_tab()
        self.create_idevicecrashreport_tab()
        self.create_idevicesyslog_tab()
        self.create_idevicepair_tab()
        self.create_ideviceactivation_tab()
        self.create_idevicedebug_tab()
        self.create_idevicename_tab()
        self.create_idevicedate_tab()
        self.create_idevicescreenshot_tab()
        self.create_idevicesetlocation_tab()
        self.create_idevicenotificationproxy_tab()
        self.create_idevice_id_tab()
        self.create_idevicedebugserverproxy_tab()
        self.create_irecovery_tab()
        self.create_about_tab()
        
        # --- Final Setup ---
        self.populate_udids()
        self.retranslate_ui()
        self.update_ui_for_current_tab()

    def create_menu(self):
        menu_bar = self.menuBar()
        # View Menu
        self.view_menu = menu_bar.addMenu("")
        self.themes_menu = self.view_menu.addMenu("")
        self.themes_group = QActionGroup(self)
        self.themes_group.setExclusive(True)
        theme_names = ["Ljust", "Mörkt", "Dracula", "Matrix", "Synthwave"]
        for theme_name in theme_names:
            action = QAction(theme_name, self, checkable=True)
            action.triggered.connect(lambda checked, name=theme_name: self.apply_theme(name))
            self.themes_menu.addAction(action)
            self.themes_group.addAction(action)
        
        # Language Menu
        self.lang_menu = menu_bar.addMenu("")
        lang_group = QActionGroup(self)
        lang_group.setExclusive(True)
        sv_action = QAction("Svenska", self, checkable=True)
        sv_action.triggered.connect(lambda: self.change_language("sv"))
        en_action = QAction("English", self, checkable=True)
        en_action.triggered.connect(lambda: self.change_language("en"))
        self.lang_menu.addAction(sv_action)
        self.lang_menu.addAction(en_action)
        lang_group.addAction(sv_action)
        lang_group.addAction(en_action)

        self.save_output_action = QAction(self._get_icon("save"), "", self)
        self.save_output_action.triggered.connect(self.save_output_to_file)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.save_output_action)

        if self.current_lang == "sv": sv_action.setChecked(True)
        else: en_action.setChecked(True)

    # --- Helper methods from original file ---
    def handle_stdout(self):
        process = self.sender()
        if process:
            data = process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
            self.output_area.moveCursor(QTextCursor.End)
            self.output_area.insertPlainText(data)
            self.output_area.moveCursor(QTextCursor.End)

    def handle_stderr(self):
        process = self.sender()
        if process:
            data = process.readAllStandardError().data().decode('utf-8', errors='ignore')
            self.output_area.moveCursor(QTextCursor.End)
            self.output_area.insertHtml(f"<font color='red'>{data.replace('<', '&lt;').replace('>', '&gt;')}</font>")
            self.output_area.moveCursor(QTextCursor.End)

    def _get_icon(self, name):
        icon_map = {"phone": "smartphone", "run": "media-playback-start", "abort": "process-stop", "refresh": "view-refresh", "copy": "edit-copy", "clear": "edit-clear", "save": "document-save", "info": "help-about"}
        if QIcon.hasThemeIcon(name): return QIcon.fromTheme(name)
        if name in icon_map and QIcon.hasThemeIcon(icon_map[name]): return QIcon.fromTheme(icon_map[name])
        fallback = {
            "phone": QStyle.SP_ComputerIcon,
            "info": QStyle.SP_MessageBoxInformation,
            "run": QStyle.SP_MediaPlay,
            "abort": QStyle.SP_MediaStop,
            "refresh": QStyle.SP_BrowserReload,
            "save": QStyle.SP_DialogSaveButton,
            "clear": QStyle.SP_DialogResetButton,
        }
        return self.style().standardIcon(fallback.get(name, QStyle.SP_FileIcon))

    def closeEvent(self, event):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("theme", self.current_theme_name)
        self.settings.setValue("language", self.current_lang)
        super().closeEvent(event)
        
    def load_settings(self):
        screen = QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else None
        # Start at the requested working size on every launch.
        start_size = QSize(1280, 720)
        if available:
            width = min(start_size.width(), available.width() - 24)
            height = min(start_size.height(), available.height() - 24)
            self.resize(width, height)
            self.move(available.left() + (available.width() - width) // 2,
                      available.top() + (available.height() - height) // 2)
        else:
            self.resize(start_size)

        saved_theme = self.settings.value("theme", "Mörkt")
        self.apply_theme(saved_theme)

    def apply_theme(self, theme_name):
        self.current_theme_name = theme_name # Store the current theme name
        base_style = """
            QTabWidget::pane {{ border: 1px solid {border_color}; border-top: 0px; }}
            QTabBar::tab {{ padding: 8px 20px; border: 1px solid {border_color}; border-bottom: 0px; border-top-left-radius: 4px; border-top-right-radius: 4px; background: {tab_bg_inactive}; }}
            QTabBar::tab:selected {{ background: {tab_bg_active}; }}
            QGroupBox {{ border: 1px solid {border_color}; border-radius: 5px; margin-top: 1ex; padding: 10px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; margin-left: 10px; }}
            QLineEdit, QComboBox {{ border: 1px solid {border_color}; border-radius: 3px; padding: 5px; background-color: {input_bg}; }}
            QTextEdit {{ border: 1px solid {border_color}; background-color: {output_bg}; color: {output_text}; }}
            QPushButton {{ border: 1px solid {btn_border}; border-radius: 4px; padding: 6px 12px; background-color: {btn_bg}; }}
            QPushButton:hover {{ background-color: {btn_hover}; }}
            QPushButton:pressed {{ background-color: {btn_pressed}; }}
            QPushButton:disabled {{ background-color: #555555; border-color: #444444; color: #888888; }}
            QStatusBar {{ padding: 3px; }}
        """
        ui_font_family, ui_font_size = "Segoe UI", "9pt"
        output_font_family, output_font_size = "Consolas", "10pt"
        
        themes = {
            "Ljust": {'main_bg': '#f0f0f0', 'text': '#000000', 'border_color': '#c0c0c0', 'tab_bg_inactive': '#d0d0d0', 'tab_bg_active': '#f0f0f0', 'input_bg': '#ffffff', 'output_bg': '#ffffff', 'output_text': '#000000', 'btn_border': '#adadad', 'btn_bg': '#e1e1e1', 'btn_hover': '#e5f1fb', 'btn_pressed': '#cce4f7'},
            "Mörkt": {'main_bg': '#2e2e2e', 'text': '#e0e0e0', 'border_color': '#505050', 'tab_bg_inactive': '#2e2e2e', 'tab_bg_active': '#404040', 'input_bg': '#383838', 'output_bg': '#222222', 'output_text': '#e0e0e0', 'btn_border': '#505050', 'btn_bg': '#484848', 'btn_hover': '#606060', 'btn_pressed': '#707070'},
            "Dracula": {'main_bg': '#282a36', 'text': '#f8f8f2', 'border_color': '#44475a', 'tab_bg_inactive': '#282a36', 'tab_bg_active': '#44475a', 'input_bg': '#343746', 'output_bg': '#21222c', 'output_text': '#f8f8f2', 'btn_border': '#6272a4', 'btn_bg': '#44475a', 'btn_hover': '#50fa7b', 'btn_pressed': '#47e06e'},
            "Matrix": {'main_bg': '#000000', 'text': '#00ff00', 'border_color': '#004d00', 'tab_bg_inactive': '#050505', 'tab_bg_active': '#0a0a0a', 'input_bg': '#0a0a0a', 'output_bg': '#050505', 'output_text': '#00ff00', 'btn_border': '#004d00', 'btn_bg': '#0a0a0a', 'btn_hover': '#006600', 'btn_pressed': '#008000'},
            "Synthwave": {'main_bg': '#231942', 'text': '#f7b2dd', 'border_color': '#5e548e', 'tab_bg_inactive': '#231942', 'tab_bg_active': '#493b7c', 'input_bg': '#3b2f63', 'output_bg': '#1e152a', 'output_text': '#00ffff', 'btn_border': '#5e548e', 'btn_bg': '#493b7c', 'btn_hover': '#be95c4', 'btn_pressed': '#e0b1cb'}
        }
        
        colors = themes.get(theme_name, themes["Ljust"])
        app_style = f""" QMainWindow, QWidget {{ background-color: {colors['main_bg']}; color: {colors['text']}; font-family: {ui_font_family}; font-size: {ui_font_size}; }} {base_style.format(**colors)} """
        self.setStyleSheet(app_style)
        self.output_area.setFont(QFont(output_font_family, int(output_font_size.replace("pt", ""))))
        
        # Update the checked state in the menu
        for action in self.themes_group.actions():
            if action.text() == theme_name:
                action.setChecked(True)
                break

    def populate_udids(self):
        self.status_bar.showMessage(self.get_string("status_searching"))
        try:
            process = subprocess.run(['idevice_id', '-l'], capture_output=True, text=True, check=False)
            udids = [line for line in process.stdout.strip().split('\n') if line]
            current_selection = self.udid_combo.currentText()
            self.udid_combo.clear()
            if udids: 
                self.udid_combo.addItems(udids)
                self.udid_combo.setCurrentText(current_selection if current_selection in udids else udids[0])
            else: 
                self.udid_combo.addItem(self.get_string("no_devices_found"))
            self.status_bar.showMessage(self.get_string("status_search_done"), 3000)
        except FileNotFoundError: 
            self.udid_combo.clear()
            self.udid_combo.addItem(self.get_string("error_idevice_id_not_found"))
            self.status_bar.showMessage(self.get_string("error_idevice_id_not_found_long"), 5000)

    def generate_command(self):
        current_tab_widget = self.tabs.currentWidget()
        if not hasattr(current_tab_widget, 'generate_command_string'): return ""
        base_command = current_tab_widget.generate_command_string()
        selected_udid = self.udid_combo.currentText()
        if hasattr(current_tab_widget, 'options') and "udid" in current_tab_widget.options and " --udid " not in base_command and selected_udid and self.get_string("no_devices_found") not in selected_udid:
            parts = base_command.split(" ", 1); return f"{parts[0]} --udid {selected_udid} {parts[1]}" if len(parts) > 1 else f"{parts[0]} --udid {selected_udid}"
        return base_command

    def run_command(self):
        tab = self.tabs.currentWidget()
        if not hasattr(tab, 'process') or tab.process.state() != QProcess.NotRunning: return

        command_string = self.generate_command()
        if not command_string or command_string.startswith("echo"): 
            self.status_bar.showMessage(self.get_string("error_no_command"), 3000)
            return
        
        dangerous_commands = ["idevicerestore --erase", "idevicepair unpair", "ideviceprovision remove-all"]
        if any(cmd in command_string for cmd in dangerous_commands):
            reply = QMessageBox.warning(self, self.get_string("warning_title"), 
                                          f"{self.get_string('warning_text')}\n\n{command_string}\n\n{self.get_string('warning_info')}", 
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return
        
        self.command_display.setText(command_string)
        self.output_area.append(f"<b style='color: #3498db'>>> {command_string}</b>")
        parts = shlex.split(command_string)
        tab.process = QProcess(self)
        tab.process.readyReadStandardOutput.connect(self.handle_stdout)
        tab.process.readyReadStandardError.connect(self.handle_stderr)
        tab.process.finished.connect(self.process_finished)
        tab.process.errorOccurred.connect(self.handle_process_error)
        tab.process.start(parts[0], parts[1:])
        self.update_ui_for_current_tab()

    def abort_command(self):
        tab = self.tabs.currentWidget()
        if hasattr(tab, 'process') and tab.process.state() != QProcess.NotRunning:
            tab.process.kill()

    def process_finished(self, exitCode, exitStatus):
        process = self.sender()
        if not process: return
        tab, index = self._find_tab_by_process(process)
        if tab:
            tab_name = self.tabs.tabText(index)
            message = self.get_string("status_process_finished_error", exitCode=exitCode) if exitCode != 0 else self.get_string("status_process_finished_ok")
            if exitStatus == QProcess.CrashExit: message = self.get_string("status_process_crashed")
            self.output_area.append(f"<b style='color: #2ecc71'>[{tab_name}]: {message}</b>")

        if tab == self.tabs.currentWidget():
            self.update_ui_for_current_tab()
    
    def handle_process_error(self, error):
        process = self.sender()
        tab, index = self._find_tab_by_process(process)
        tab_name = self.tabs.tabText(index) if tab else self.get_string("unknown_tab")
        if error == QProcess.FailedToStart: 
            self.output_area.append(f"<b style='color: #e74c3c'>[{tab_name} ERROR]: {self.get_string('error_failed_to_start')}</b>")
        if tab == self.tabs.currentWidget():
            self.update_ui_for_current_tab()

    def save_output_to_file(self):
        content = self.output_area.toPlainText()
        if not content: 
            self.status_bar.showMessage(self.get_string("status_no_output_to_save"), 3000)
            return
        filePath, _ = QFileDialog.getSaveFileName(self, self.get_string("save_output_title"), "", f"{self.get_string('text_files')} (*.txt);;{self.get_string('all_files')} (*)")
        if filePath:
            try:
                with open(filePath, 'w', encoding='utf-8') as f: f.write(content)
                self.status_bar.showMessage(self.get_string("status_output_saved", path=filePath), 5000)
            except Exception as e: 
                self.status_bar.showMessage(self.get_string("error_saving_file", error=e), 5000)
                QMessageBox.critical(self, self.get_string("error_saving_title"), f"{self.get_string('error_saving_text')}\n{e}")
    
    def update_ui_for_current_tab(self):
        tab = self.tabs.currentWidget()
        self.command_display.setText(self.generate_command())
        if tab and hasattr(tab, "process"):
            is_running = tab.process.state() != QProcess.NotRunning
            self.run_button.setEnabled(not is_running)
            self.abort_button.setEnabled(is_running)
            self.progress_bar.setVisible(is_running)
            if is_running:
                self.progress_bar.setRange(0,0)
                self.status_bar.showMessage(self.get_string("status_running_command", tab_name=self.tabs.tabText(self.tabs.currentIndex())))
            else:
                self.progress_bar.setRange(0,1)
                self.status_bar.showMessage(self.get_string("status_ready"))
        else:
            self.run_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage(self.get_string("status_ready"))

    def _find_tab_by_process(self, process):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, "process") and tab.process == process:
                return tab, i
        return None, -1

    def _tab_icon(self, name):
        """Return a visible Qt icon without depending on an installed icon theme."""
        icon_map = {
            "ideviceinfo": QStyle.SP_MessageBoxInformation,
            "idevicediagnostics": QStyle.SP_ComputerIcon,
            "idevicebackup2": QStyle.SP_DriveHDIcon,
            "ideviceprovision": QStyle.SP_DialogApplyButton,
            "idevicerestore": QStyle.SP_BrowserReload,
            "ideviceimagemounter": QStyle.SP_DriveCDIcon,
            "idevicecrashreport": QStyle.SP_MessageBoxCritical,
            "idevicesyslog": QStyle.SP_ComputerIcon,
            "idevicepair": QStyle.SP_DialogYesButton,
            "ideviceactivation": QStyle.SP_DialogApplyButton,
            "idevicedebug": QStyle.SP_ToolBarHorizontalExtensionButton,
            "idevicename": QStyle.SP_FileDialogInfoView,
            "idevicedate": QStyle.SP_FileDialogDetailedView,
            "idevicescreenshot": QStyle.SP_DesktopIcon,
            "idevicesetlocation": QStyle.SP_DialogOpenButton,
            "idevicenotificationproxy": QStyle.SP_MessageBoxInformation,
            "idevice_id": QStyle.SP_FileDialogContentsView,
            "idevicedebugserverproxy": QStyle.SP_DriveNetIcon,
            "irecovery": QStyle.SP_MediaStop,
            "Om": QStyle.SP_MessageBoxInformation,
        }
        return self.style().standardIcon(icon_map.get(name, QStyle.SP_ComputerIcon))

    def _create_and_setup_tab(self, name, icon_name="phone"):
        tab = QWidget()
        # Use Qt's built-in icons first; this works even without a desktop icon theme.
        icon = self._tab_icon(name) if name != "phone" else self._get_icon(icon_name)
        index = self.tabs.addTab(tab, icon, name)
        # Keep the full command name available even when the tab text is elided.
        self.tabs.setTabToolTip(index, f"{name}  |  libimobiledevice")
        tab.process = QProcess(self)
        tab.setObjectName(name) # Store key for translation
        return tab

    def select_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, self.get_string("select_folder"))
        if directory: line_edit.setText(directory)
            
    def select_file(self, line_edit, filter="Alla Filer (*)"):
        file_name, _ = QFileDialog.getOpenFileName(self, self.get_string("select_file"), "", filter)
        if file_name: line_edit.setText(file_name)

    def _create_common_options_group(self, tab, options):
        group = QGroupBox()
        layout = QGridLayout(group)
        if "network" in options: tab.network_check = QCheckBox("--network"); layout.addWidget(tab.network_check, 0, 0)
        if "debug" in options: tab.debug_check = QCheckBox("--debug"); layout.addWidget(tab.debug_check, 0, 1)
        return group
        
    def _get_common_options_string_no_udid(self, tab):
        cmd = ""
        if hasattr(tab, 'debug_check') and tab.debug_check.isChecked(): cmd += "--debug "
        if hasattr(tab, 'network_check') and tab.network_check.isChecked(): cmd += "--network "
        return cmd
    
    def _dynamic_field_updater(self, tab, command_map):
        def update():
            command = tab.cmd_combo.currentText()
            for field_name, enabled_commands in command_map.items():
                if hasattr(tab, field_name):
                    widget = getattr(tab, field_name)
                    is_enabled = command in enabled_commands
                    if isinstance(widget, QGroupBox):
                        widget.setEnabled(is_enabled)
                    else:
                        widget.setEnabled(is_enabled)
            self.update_ui_for_current_tab()
        tab.cmd_combo.currentTextChanged.connect(update); update()
        
    # --- Internationalization (i18n) ---
    def init_translations(self):
        self.translations = {
            "window_title": {"sv": "iDevice Verktygslåda", "en": "iDevice Toolbox"},
            "udid_label": {"sv": "<b>Målenhet (UDID):</b>", "en": "<b>Target Device (UDID):</b>"},
            "refresh_button": {"sv": " Läs in enheter", "en": " Refresh Devices"},
            "theme_label": {"sv": "<b>Tema:</b>", "en": "<b>Theme:</b>"},
            "terminal_group": {"sv": "Terminal", "en": "Terminal"},
            "run_button": {"sv": " Kör Kommando", "en": " Run Command"},
            "abort_button": {"sv": " Avbryt", "en": " Abort"},
            "clear_button": {"sv": " Rensa", "en": " Clear"},
            "status_searching": {"sv": "Söker efter enheter...", "en": "Searching for devices..."},
            "no_devices_found": {"sv": "Inga enheter hittades", "en": "No devices found"},
            "status_search_done": {"sv": "Enhetssökning klar.", "en": "Device scan complete."},
            "error_idevice_id_not_found": {"sv": "Kunde inte köra 'idevice_id'", "en": "Could not run 'idevice_id'"},
            "error_idevice_id_not_found_long": {"sv": "Fel: 'idevice_id' kunde inte köras.", "en": "Error: 'idevice_id' could not be executed."},
            "error_no_command": {"sv": "Inget giltigt kommando att köra.", "en": "No valid command to execute."},
            "warning_title": {"sv": "Riskfylld Åtgärd", "en": "Risky Action"},
            "warning_text": {"sv": "Du är på väg att köra ett potentiellt farligt kommando:", "en": "You are about to execute a potentially dangerous command:"},
            "warning_info": {"sv": "Detta kan leda till dataförlust. Vill du fortsätta?", "en": "This can lead to data loss. Do you want to continue?"},
            "status_process_finished_ok": {"sv": "Processen avslutad.", "en": "Process finished."},
            "status_process_finished_error": {"sv": "Processen avslutades med felkod {exitCode}.", "en": "Process finished with exit code {exitCode}."},
            "status_process_crashed": {"sv": "Kommando avbrutet av användaren.", "en": "Command aborted by user."},
            "unknown_tab": {"sv": "Okänd flik", "en": "Unknown Tab"},
            "error_failed_to_start": {"sv": "Kommandot kunde inte startas. Är det installerat och i din PATH?", "en": "Could not start command. Is it installed and in your PATH?"},
            "status_no_output_to_save": {"sv": "Ingen utdata att spara.", "en": "No output to save."},
            "save_output_title": {"sv": "Spara Utdata", "en": "Save Output"},
            "text_files": {"sv": "Textfiler", "en": "Text Files"},
            "all_files": {"sv": "Alla filer", "en": "All Files"},
            "status_output_saved": {"sv": "Utdata sparad till {path}", "en": "Output saved to {path}"},
            "error_saving_file": {"sv": "Kunde inte spara fil: {error}", "en": "Could not save file: {error}"},
            "error_saving_title": {"sv": "Spara Fel", "en": "Save Error"},
            "error_saving_text": {"sv": "Ett fel uppstod när filen skulle sparas:", "en": "An error occurred while saving the file:"},
            "status_running_command": {"sv": "Kör kommando i fliken '{tab_name}'...", "en": "Running command in tab '{tab_name}'..."},
            "status_ready": {"sv": "Redo", "en": "Ready"},
            "select_folder": {"sv": "Välj Mapp", "en": "Select Folder"},
            "select_file": {"sv": "Välj Fil", "en": "Select File"},
            "view_menu": {"sv": "&Utseende", "en": "&View"},
            "themes_menu": {"sv": "Teman", "en": "Themes"},
            "lang_menu": {"sv": "&Språk", "en": "&Language"},
            # Add all tab names
            "ideviceinfo": {"sv": "Info", "en": "Info"},
            "idevicediagnostics": {"sv": "Diagnostik", "en": "Diagnostics"},
            "idevicebackup2": {"sv": "Backup", "en": "Backup"},
            "ideviceprovision": {"sv": "Provisionering", "en": "Provisioning"},
            "idevicerestore": {"sv": "Återställning", "en": "Restore"},
            "ideviceimagemounter": {"sv": "Image Mounter", "en": "Image Mounter"},
            "idevicecrashreport": {"sv": "Kraschrapporter", "en": "Crash Reports"},
            "idevicesyslog": {"sv": "Systemlogg", "en": "Syslog"},
            "idevicepair": {"sv": "Parkoppling", "en": "Pairing"},
            "ideviceactivation": {"sv": "Aktivering", "en": "Activation"},
            "idevicedebug": {"sv": "Debug", "en": "Debug"},
            "idevicename": {"sv": "Namn", "en": "Name"},
            "idevicedate": {"sv": "Datum & Tid", "en": "Date & Time"},
            "idevicescreenshot": {"sv": "Skärmdump", "en": "Screenshot"},
            "idevicesetlocation": {"sv": "Plats", "en": "Location"},
            "idevicenotificationproxy": {"sv": "Notifikationer", "en": "Notifications"},
            "idevice_id": {"sv": "ID", "en": "ID"},
            "idevicedebugserverproxy": {"sv": "Debug Proxy", "en": "Debug Proxy"},
            "irecovery": {"sv": "iRecovery", "en": "iRecovery"},
            "Om": {"sv": "Om", "en": "About"},
        }

    def get_string(self, key, **kwargs):
        # Use a default value to prevent crashes if a key is missing
        default = kwargs.pop('default', f"MISSING_{key}")
        return self.translations.get(key, {}).get(self.current_lang, default).format(**kwargs)

    def retranslate_ui(self):
        self.setWindowTitle(self.get_string("window_title"))
        self.udid_label.setText(self.get_string("udid_label"))
        self.refresh_udid_button.setText(self.get_string("refresh_button"))
        self.view_menu.setTitle(self.get_string("view_menu"))
        self.themes_menu.setTitle(self.get_string("themes_menu"))
        self.lang_menu.setTitle(self.get_string("lang_menu"))
        self.output_group.setTitle(self.get_string("terminal_group"))
        self.save_output_action.setText(self.get_string("save_output_title"))
        self.run_button.setText(self.get_string("run_button"))
        self.abort_button.setText(self.get_string("abort_button"))
        self.clear_output_button.setText(self.get_string("clear_button"))
        
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            key = tab.objectName()
            translated_name = self.get_string(key, default=key)
            self.tabs.setTabText(i, translated_name)
            self.tabs.setTabToolTip(i, f"{key}  |  {translated_name}")
            if hasattr(tab, 'retranslate'):
                tab.retranslate()
        self.update_ui_for_current_tab()

    def change_language(self, lang):
        self.current_lang = lang
        self.retranslate_ui()

    # --- FULL IMPLEMENTATIONS OF ALL TABS ---
    # (Copied and pasted from the original file, adapted to the new layout structure)
    
    def create_ideviceinfo_tab(self):
        tab = self._create_and_setup_tab("ideviceinfo"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); 
        query_group = QGroupBox("Frågealternativ"); qgl = QGridLayout(query_group)
        qgl.addWidget(QLabel("--domain:"), 0, 0); tab.domain_edit = QLineEdit(); qgl.addWidget(tab.domain_edit, 0, 1)
        tab.domain_combo = QComboBox(); tab.domain_combo.addItems(["-- Välj känd domän --"] + ["com.apple.disk_usage", "com.apple.mobile.battery", "com.apple.mobile.lockdownd", "com.apple.international", "com.apple.mobile.backup", "com.apple.fairplay", "com.apple.iTunes"]); qgl.addWidget(tab.domain_combo, 0, 2)
        tab.domain_combo.currentTextChanged.connect(lambda text: tab.domain_edit.setText(text) if text != "-- Välj känd domän --" else None)
        qgl.addWidget(QLabel("--key:"), 1, 0); tab.key_edit = QLineEdit(); qgl.addWidget(tab.key_edit, 1, 1)
        layout.addWidget(query_group, 0, 0)
        opts_group = QGroupBox("Formatering och anslutning"); ogl = QGridLayout(opts_group)
        tab.simple_check = QCheckBox("--simple"); ogl.addWidget(tab.simple_check, 0, 0)
        tab.xml_check = QCheckBox("--xml"); ogl.addWidget(tab.xml_check, 0, 1)
        layout.addWidget(opts_group, 0, 1); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 1, 0, 1, 2); layout.setRowStretch(2, 1)
        def generate_command_string():
            cmd = "ideviceinfo " + self._get_common_options_string_no_udid(tab)
            if tab.simple_check.isChecked(): cmd += "--simple "
            if tab.xml_check.isChecked(): cmd += "--xml "
            if tab.domain_edit.text(): cmd += f"-q {tab.domain_edit.text()} "
            if tab.key_edit.text(): cmd += f"-k {tab.key_edit.text()} "
            return cmd.strip()
        tab.generate_command_string = generate_command_string
        for w in [tab.domain_edit, tab.key_edit, tab.simple_check, tab.xml_check]:
            if isinstance(w, QLineEdit): w.textChanged.connect(self.update_ui_for_current_tab)
            else: w.stateChanged.connect(self.update_ui_for_current_tab)

    # ... The rest of the create_..._tab methods are implemented below, following the same pattern ...
    # ... This is a placeholder for brevity, the full code contains all 20+ tab creation methods ...
    # ... from the original file, adapted to the new structure. ...

    def create_ideviceactivation_tab(self):
        tab = self._create_and_setup_tab("ideviceactivation"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); layout.addWidget(QLabel("Kommando:"), 0, 0)
        tab.cmd_combo = QComboBox(); tab.cmd_combo.addItems(["activate", "deactivate", "state"]); layout.addWidget(tab.cmd_combo, 0, 1, 1, 3)
        group = QGroupBox("Alternativ"); gl = QGridLayout(group)
        tab.batch_check = QCheckBox("--batch"); gl.addWidget(tab.batch_check, 0, 0)
        gl.addWidget(QLabel("--service URL:"), 1, 0); tab.service_edit = QLineEdit(); gl.addWidget(tab.service_edit, 1, 1)
        layout.addWidget(group, 1, 0); 
        common_opts = self._create_common_options_group(tab, ["network", "debug"]); layout.addWidget(common_opts, 1, 1)
        layout.setRowStretch(2, 1)
        def generate_command_string():
            cmd = "ideviceactivation " + self._get_common_options_string_no_udid(tab)
            if tab.batch_check.isChecked(): cmd += "--batch "
            if tab.service_edit.text(): cmd += f"--service '{tab.service_edit.text()}' "
            cmd += f"{tab.cmd_combo.currentText()} "
            return cmd.strip()
        tab.generate_command_string = generate_command_string
    
    def create_idevicebackup2_tab(self):
        tab = self._create_and_setup_tab("idevicebackup2"); tab.options = ["udid", "network", "debug"]
        tab_layout = QHBoxLayout(tab); left_col, right_col = QVBoxLayout(), QVBoxLayout()
        cmd_group = QGroupBox("Kommando"); cmd_layout = QGridLayout(cmd_group); cmd_layout.addWidget(QLabel("Kommando:"), 0, 0)
        tab.cmd_combo = QComboBox(); tab.cmd_combo.addItems(["backup", "restore", "info", "list", "unback", "encryption on", "encryption off", "changepw", "cloud on", "cloud off"]); cmd_layout.addWidget(tab.cmd_combo, 0, 1); left_col.addWidget(cmd_group)
        restore_group = QGroupBox("Återställningsalternativ"); tab.restore_group = restore_group; rl = QGridLayout(restore_group); tab.restore_system_check = QCheckBox("--system"); rl.addWidget(tab.restore_system_check, 0, 0); tab.restore_noreboot_check = QCheckBox("--no-reboot"); rl.addWidget(tab.restore_noreboot_check, 0, 1); tab.restore_copy_check = QCheckBox("--copy"); rl.addWidget(tab.restore_copy_check, 1, 0); tab.restore_settings_check = QCheckBox("--settings"); rl.addWidget(tab.restore_settings_check, 1, 1); tab.restore_remove_check = QCheckBox("--remove"); rl.addWidget(tab.restore_remove_check, 2, 0); tab.restore_skipapps_check = QCheckBox("--skip-apps"); rl.addWidget(tab.restore_skipapps_check, 2, 1); rl.addWidget(QLabel("--password:"), 3, 0); tab.restore_password_edit = QLineEdit(); rl.addWidget(tab.restore_password_edit, 3, 1); left_col.addWidget(restore_group); left_col.addStretch()
        backup_group = QGroupBox("Backup-alternativ"); tab.backup_group = backup_group; bl = QVBoxLayout(backup_group); tab.backup_full_check = QCheckBox("--full"); bl.addWidget(tab.backup_full_check); bl.addStretch(); right_col.addWidget(backup_group)
        general_group = QGroupBox("Allmänna Alternativ"); gl = QGridLayout(general_group); tab.interactive_check = QCheckBox("--interactive"); gl.addWidget(tab.interactive_check, 0, 0); tab.debug_check = QCheckBox("--debug"); gl.addWidget(tab.debug_check, 0, 1); tab.network_check = QCheckBox("--network"); gl.addWidget(tab.network_check, 0, 2); gl.addWidget(QLabel("--source UDID:"), 2, 0); tab.source_udid_edit = QLineEdit(); gl.addWidget(tab.source_udid_edit, 2, 1, 1, 2); gl.addWidget(QLabel("Mapp:"), 3, 0); tab.dir_edit = FileDropLineEdit(); gl.addWidget(tab.dir_edit, 3, 1); browse_btn = QPushButton("..."); browse_btn.setToolTip("Bläddra efter mapp"); browse_btn.clicked.connect(lambda: self.select_directory(tab.dir_edit)); gl.addWidget(browse_btn, 3, 2); right_col.addWidget(general_group); right_col.addStretch(); tab_layout.addLayout(left_col); tab_layout.addLayout(right_col)
        self._dynamic_field_updater(tab, {"backup_group": ["backup"], "restore_group": ["restore"], "dir_edit": ["backup", "restore", "unback"]})
        def generate_command_string():
            cmd = "idevicebackup2 " + self._get_common_options_string_no_udid(tab); 
            if tab.interactive_check.isChecked(): cmd += "--interactive "; 
            if tab.source_udid_edit.text(): cmd += f"--source {tab.source_udid_edit.text()} "; 
            cmd += f"{tab.cmd_combo.currentText()} "
            if tab.cmd_combo.currentText() == "backup" and tab.backup_full_check.isChecked(): cmd += "--full "
            elif tab.cmd_combo.currentText() == "restore":
                if tab.restore_system_check.isChecked(): cmd += "--system "; 
                if tab.restore_noreboot_check.isChecked(): cmd += "--no-reboot "; 
                if tab.restore_copy_check.isChecked(): cmd += "--copy "; 
                if tab.restore_settings_check.isChecked(): cmd += "--settings "; 
                if tab.restore_remove_check.isChecked(): cmd += "--remove "; 
                if tab.restore_skipapps_check.isChecked(): cmd += "--skip-apps "; 
                if tab.restore_password_edit.text(): cmd += f"--password '{tab.restore_password_edit.text()}' "
            if tab.dir_edit.text(): cmd += f"'{tab.dir_edit.text()}'"
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicecrashreport_tab(self):
        tab = self._create_and_setup_tab("idevicecrashreport"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Alternativ"); gl = QGridLayout(group)
        tab.extract_check = QCheckBox("--extract"); tab.extract_check.setToolTip("Extrahera rå kraschrapport till en separat '.crash'-fil."); gl.addWidget(tab.extract_check, 0, 0); 
        tab.keep_check = QCheckBox("--keep"); tab.keep_check.setToolTip("Kopiera men ta inte bort kraschrapporter från enheten."); gl.addWidget(tab.keep_check, 0, 1)
        gl.addWidget(QLabel("Mapp:"), 1, 0); tab.dir_edit = FileDropLineEdit(); tab.dir_edit.setToolTip("Lokal mapp dit rapporterna ska flyttas."); gl.addWidget(tab.dir_edit, 1, 1)
        browse_btn = QPushButton("..."); browse_btn.setToolTip("Bläddra efter mapp"); browse_btn.clicked.connect(lambda: self.select_directory(tab.dir_edit)); gl.addWidget(browse_btn, 1, 2)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicecrashreport " + self._get_common_options_string_no_udid(tab)
            if tab.extract_check.isChecked(): cmd += "--extract "
            if tab.keep_check.isChecked(): cmd += "--keep "
            if tab.dir_edit.text(): cmd += f"'{tab.dir_edit.text()}' "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicedate_tab(self):
        tab = self._create_and_setup_tab("idevicedate"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Åtgärd"); gl = QGridLayout(group)
        tab.get_date_radio = QRadioButton("Hämta datum (standard)"); tab.get_date_radio.setChecked(True); gl.addWidget(tab.get_date_radio, 0, 0, 1, 2)
        tab.set_date_radio = QRadioButton("Ställ in datum från tidsstämpel:"); gl.addWidget(tab.set_date_radio, 1, 0)
        tab.timestamp_edit = QLineEdit(); tab.timestamp_edit.setPlaceholderText("t.ex. ÅÅÅÅ-MM-DD HH:MM:SS"); tab.timestamp_edit.setToolTip("Ange UTC-tid som ska ställas in på enheten."); gl.addWidget(tab.timestamp_edit, 1, 1)
        tab.sync_date_radio = QRadioButton("Synka med systemtid (--sync)"); gl.addWidget(tab.sync_date_radio, 2, 0, 1, 2)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicedate " + self._get_common_options_string_no_udid(tab)
            if tab.set_date_radio.isChecked() and tab.timestamp_edit.text(): cmd += f"--set '{tab.timestamp_edit.text()}' "
            elif tab.sync_date_radio.isChecked(): cmd += "--sync "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicedebug_tab(self):
        tab = self._create_and_setup_tab("idevicedebug"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Kör App"); gl = QGridLayout(group)
        gl.addWidget(QLabel("Kommando: run"), 0, 0, 1, 2)
        gl.addWidget(QLabel("Bundle ID:"), 1, 0); tab.bundle_edit = QLineEdit(); tab.bundle_edit.setToolTip("Appens unika identifierare, t.ex. com.apple.mobilesafari"); gl.addWidget(tab.bundle_edit, 1, 1)
        gl.addWidget(QLabel("Argument (valfritt):"), 2, 0); tab.args_edit = QLineEdit(); gl.addWidget(tab.args_edit, 2, 1)
        gl.addWidget(QLabel("--env NAME=VALUE:"), 3, 0); tab.env_edit = QLineEdit(); tab.env_edit.setToolTip("Sätt en miljövariabel för appen."); gl.addWidget(tab.env_edit, 3, 1)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicedebug run " + self._get_common_options_string_no_udid(tab)
            if tab.env_edit.text(): cmd += f"--env {tab.env_edit.text()} "
            if tab.bundle_edit.text(): cmd += f"{tab.bundle_edit.text()} "
            if tab.args_edit.text(): cmd += f"{tab.args_edit.text()} "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicedebugserverproxy_tab(self):
        tab = self._create_and_setup_tab("idevicedebugserverproxy"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Proxy-parametrar"); gl = QGridLayout(group)
        gl.addWidget(QLabel("Lokal port:"), 0, 0); tab.port_edit = QLineEdit(); gl.addWidget(tab.port_edit, 0, 1)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicedebugserverproxy " + self._get_common_options_string_no_udid(tab)
            if tab.port_edit.text(): cmd += f"{tab.port_edit.text()} "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicediagnostics_tab(self):
        tab = self._create_and_setup_tab("idevicediagnostics"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Diagnostik"); gl = QGridLayout(group)
        gl.addWidget(QLabel("Kommando:"), 0, 0)
        tab.cmd_combo = QComboBox(); tab.cmd_combo.addItems(["diagnostics", "mobilegestalt", "ioreg", "ioregentry", "shutdown", "restart", "sleep"]); gl.addWidget(tab.cmd_combo, 0, 1)
        gl.addWidget(QLabel("Argument (valfritt):"), 1, 0)
        tab.arg_edit = QLineEdit(); tab.arg_edit.setPlaceholderText("t.ex., All, WiFi, IOPower"); gl.addWidget(tab.arg_edit, 1, 1)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        self._dynamic_field_updater(tab, {"arg_edit": ["diagnostics", "mobilegestalt", "ioreg", "ioregentry"]})
        def generate_command_string():
            cmd = "idevicediagnostics " + self._get_common_options_string_no_udid(tab)
            cmd += f"{tab.cmd_combo.currentText()} "
            if tab.arg_edit.text(): cmd += f"{tab.arg_edit.text()} "
            return cmd.strip()
        tab.generate_command_string = generate_command_string
    
    def create_idevice_id_tab(self):
        tab = self._create_and_setup_tab("idevice_id"); tab.options = ["debug"] # UDID is a parameter here
        layout = QGridLayout(tab); group = QGroupBox("Alternativ"); gl = QGridLayout(group)
        tab.list_check = QCheckBox("Lista enheter (--list, USB)"); gl.addWidget(tab.list_check, 0, 0)
        tab.network_check = QCheckBox("Lista nätverksenheter (--network)"); gl.addWidget(tab.network_check, 1, 0)
        tab.debug_check = QCheckBox("--debug"); gl.addWidget(tab.debug_check, 2, 0)
        gl.addWidget(QLabel("UDID (för namn, valfritt):"), 0, 1); tab.udid_param_edit = QLineEdit(); gl.addWidget(tab.udid_param_edit, 0, 2)
        layout.addWidget(group, 0, 0); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevice_id "; 
            if tab.list_check.isChecked(): cmd += "-l "
            if tab.network_check.isChecked(): cmd += "-n "
            if tab.debug_check.isChecked(): cmd += "-d "
            if tab.udid_param_edit.text(): cmd += f"{tab.udid_param_edit.text()}"
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_ideviceimagemounter_tab(self):
        tab = self._create_and_setup_tab("ideviceimagemounter"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); files_group = QGroupBox("Filer"); fgl = QGridLayout(files_group)
        fgl.addWidget(QLabel("Image File:"), 0, 0); tab.image_file_edit = FileDropLineEdit(); fgl.addWidget(tab.image_file_edit, 0, 1)
        browse1 = QPushButton("..."); browse1.setToolTip("Bläddra efter image-fil"); browse1.clicked.connect(lambda: self.select_file(tab.image_file_edit)); fgl.addWidget(browse1, 0, 2)
        fgl.addWidget(QLabel("Signature File:"), 1, 0); tab.sig_file_edit = FileDropLineEdit(); fgl.addWidget(tab.sig_file_edit, 1, 1)
        browse2 = QPushButton("..."); browse2.setToolTip("Bläddra efter signatur-fil"); browse2.clicked.connect(lambda: self.select_file(tab.sig_file_edit)); fgl.addWidget(browse2, 1, 2)
        layout.addWidget(files_group, 0, 0)
        opts_group = QGroupBox("Alternativ"); ogl = QGridLayout(opts_group)
        tab.list_check = QCheckBox("--list"); ogl.addWidget(tab.list_check, 0, 0)
        tab.xml_check = QCheckBox("--xml"); ogl.addWidget(tab.xml_check, 0, 1)
        ogl.addWidget(QLabel("--imagetype:"), 1, 0); tab.imagetype_edit = QLineEdit("Developer"); ogl.addWidget(tab.imagetype_edit, 1, 1)
        layout.addWidget(opts_group, 0, 1); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 1, 0, 1, 2); layout.setRowStretch(2, 1)
        def generate_command_string():
            cmd = "ideviceimagemounter " + self._get_common_options_string_no_udid(tab)
            if tab.list_check.isChecked(): cmd += "--list "
            else:
                if tab.image_file_edit.text(): cmd += f"'{tab.image_file_edit.text()}' "
                if tab.sig_file_edit.text(): cmd += f"'{tab.sig_file_edit.text()}' "
            if tab.xml_check.isChecked(): cmd += "--xml "
            if tab.imagetype_edit.text(): cmd += f"--imagetype '{tab.imagetype_edit.text()}' "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicename_tab(self):
        tab = self._create_and_setup_tab("idevicename"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Enhetsnamn"); gl = QGridLayout(group)
        gl.addWidget(QLabel("Nytt namn (lämna tomt för att visa):"), 0, 0)
        tab.name_edit = QLineEdit(); gl.addWidget(tab.name_edit, 0, 1)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicename " + self._get_common_options_string_no_udid(tab)
            if tab.name_edit.text(): cmd += f"'{tab.name_edit.text()}' "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicenotificationproxy_tab(self):
        tab = self._create_and_setup_tab("idevicenotificationproxy"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Notifikationer"); gl = QGridLayout(group)
        gl.addWidget(QLabel("Kommando:"), 0, 0)
        tab.cmd_combo = QComboBox(); tab.cmd_combo.addItems(["post", "observe"]); gl.addWidget(tab.cmd_combo, 0, 1)
        gl.addWidget(QLabel("Notifikations-IDn:"), 1, 0)
        tab.ids_edit = QLineEdit(); tab.ids_edit.setPlaceholderText("ID1 ID2 ..."); gl.addWidget(tab.ids_edit, 1, 1)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicenotificationproxy " + self._get_common_options_string_no_udid(tab)
            cmd += f"{tab.cmd_combo.currentText()} "
            if tab.ids_edit.text(): cmd += f"{tab.ids_edit.text()} "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicepair_tab(self):
        tab = self._create_and_setup_tab("idevicepair"); tab.options = ["udid", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Parkoppling"); gl = QGridLayout(group)
        gl.addWidget(QLabel("Kommando:"), 0, 0)
        tab.cmd_combo = QComboBox(); tab.cmd_combo.addItems(["systembuid", "hostid", "pair", "validate", "unpair", "list"]); gl.addWidget(tab.cmd_combo, 0, 1)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicepair " + self._get_common_options_string_no_udid(tab)
            cmd += f"{tab.cmd_combo.currentText()}"
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_ideviceprovision_tab(self):
        tab = self._create_and_setup_tab("ideviceprovision"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); cmd_group = QGroupBox("Kommando"); cgl = QGridLayout(cmd_group)
        cgl.addWidget(QLabel("Kommando:"), 0, 0)
        tab.cmd_combo = QComboBox(); tab.cmd_combo.addItems(["install", "list", "copy", "remove", "remove-all", "dump"]); cgl.addWidget(tab.cmd_combo, 0, 1); layout.addWidget(cmd_group, 0, 0)
        args_group = QGroupBox("Argument"); agl = QGridLayout(args_group)
        agl.addWidget(QLabel("FILE:"), 0, 0); tab.file_edit = FileDropLineEdit(); agl.addWidget(tab.file_edit, 0, 1)
        b1 = QPushButton("..."); b1.setToolTip("Bläddra efter fil"); b1.clicked.connect(lambda: self.select_file(tab.file_edit)); agl.addWidget(b1, 0, 2)
        agl.addWidget(QLabel("PATH:"), 1, 0); tab.path_edit = FileDropLineEdit(); agl.addWidget(tab.path_edit, 1, 1)
        b2 = QPushButton("..."); b2.setToolTip("Bläddra efter mapp"); b2.clicked.connect(lambda: self.select_directory(tab.path_edit)); agl.addWidget(b2, 1, 2)
        agl.addWidget(QLabel("UUID:"), 2, 0); tab.uuid_edit = QLineEdit(); agl.addWidget(tab.uuid_edit, 2, 1, 1, 2); layout.addWidget(args_group, 1, 0)
        opts_group = QGroupBox("Alternativ"); ogl = QGridLayout(opts_group); tab.xml_check = QCheckBox("--xml (för 'dump')"); ogl.addWidget(tab.xml_check, 0, 0); layout.addWidget(opts_group, 0, 1)
        layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 1, 1); layout.setRowStretch(2, 1)
        self._dynamic_field_updater(tab, {"file_edit": ["install", "dump"], "path_edit": ["copy"], "uuid_edit": ["copy", "remove"], "xml_check": ["dump"]})
        def generate_command_string():
            cmd = "ideviceprovision " + self._get_common_options_string_no_udid(tab)
            if tab.xml_check.isChecked(): cmd += "--xml "
            command = tab.cmd_combo.currentText()
            cmd += f"{command} "
            if command in ["install", "dump"] and tab.file_edit.text(): cmd += f"'{tab.file_edit.text()}' "
            elif command == "copy":
                if tab.uuid_edit.text(): cmd += f"{tab.uuid_edit.text()} "
                if tab.path_edit.text(): cmd += f"'{tab.path_edit.text()}' "
            elif command == "remove" and tab.uuid_edit.text(): cmd += f"{tab.uuid_edit.text()} "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicerestore_tab(self):
        tab = self._create_and_setup_tab("idevicerestore"); tab.options = ["udid", "debug"] # No network
        layout = QGridLayout(tab); path_group = QGroupBox("Firmware"); pl = QGridLayout(path_group); pl.addWidget(QLabel("IPSW Sökväg:"), 0, 0); tab.path_edit = FileDropLineEdit(); pl.addWidget(tab.path_edit, 0, 1); b = QPushButton("..."); b.setToolTip("Bläddra efter .ipsw fil"); b.clicked.connect(lambda: self.select_file(tab.path_edit, "IPSW Files (*.ipsw);;All Files (*)")); pl.addWidget(b, 0, 2); layout.addWidget(path_group, 0, 0, 1, 2)
        basic_group = QGroupBox("Grundläggande Alternativ"); bgl = QGridLayout(basic_group); tab.latest_check = QCheckBox("Använd senaste (--latest)"); bgl.addWidget(tab.latest_check, 0, 0); tab.erase_check = QCheckBox("Radera allt (--erase)"); bgl.addWidget(tab.erase_check, 0, 1); tab.no_input_check = QCheckBox("Icke-interaktiv (--no-input)"); bgl.addWidget(tab.no_input_check, 1, 0); tab.no_action_check = QCheckBox("Ingen åtgärd (--no-action)"); bgl.addWidget(tab.no_action_check, 1, 1); tab.ipsw_info_check = QCheckBox("Visa IPSW-info (--ipsw-info)"); bgl.addWidget(tab.ipsw_info_check, 2, 0); layout.addWidget(basic_group, 1, 0)
        adv_group = QGroupBox("Avancerade/Experimentella Alternativ"); agl = QGridLayout(adv_group); tab.custom_check = QCheckBox("--custom"); agl.addWidget(tab.custom_check, 0, 0); tab.shsh_check = QCheckBox("--shsh"); agl.addWidget(tab.shsh_check, 0, 1); tab.no_restore_check = QCheckBox("--no-restore"); agl.addWidget(tab.no_restore_check, 1, 0); tab.keep_pers_check = QCheckBox("--keep-pers"); agl.addWidget(tab.keep_pers_check, 1, 1); tab.pwn_check = QCheckBox("--pwn"); agl.addWidget(tab.pwn_check, 2, 0); tab.plain_progress_check = QCheckBox("--plain-progress"); agl.addWidget(tab.plain_progress_check, 2, 1); tab.restore_mode_check = QCheckBox("--restore-mode"); agl.addWidget(tab.restore_mode_check, 3, 0); tab.ignore_errors_check = QCheckBox("--ignore-errors"); agl.addWidget(tab.ignore_errors_check, 3, 1); layout.addWidget(adv_group, 1, 1)
        params_group = QGroupBox("Parametrar"); pgl = QGridLayout(params_group); pgl.addWidget(QLabel("--ecid:"), 1, 0); tab.ecid_edit = QLineEdit(); pgl.addWidget(tab.ecid_edit, 1, 1); pgl.addWidget(QLabel("--cache-path:"), 2, 0); tab.cache_path_edit = FileDropLineEdit(); pgl.addWidget(tab.cache_path_edit, 2, 1); bc = QPushButton("..."); bc.setToolTip("Bläddra efter cache-mapp"); bc.clicked.connect(lambda: self.select_directory(tab.cache_path_edit)); pgl.addWidget(bc, 2, 2); pgl.addWidget(QLabel("--server URL:"), 3, 0); tab.server_edit = QLineEdit(); pgl.addWidget(tab.server_edit, 3, 1, 1, 2); pgl.addWidget(QLabel("--ticket PATH:"), 4, 0); tab.ticket_edit = FileDropLineEdit(); pgl.addWidget(tab.ticket_edit, 4, 1, 1, 2); pgl.addWidget(QLabel("--variant:"), 5, 0); tab.variant_edit = QLineEdit(); pgl.addWidget(tab.variant_edit, 5, 1, 1, 2); layout.addWidget(params_group, 2, 0, 1, 2); layout.addWidget(self._create_common_options_group(tab, ["debug"]), 3, 0)
        def generate_command_string():
            cmd = "idevicerestore "; opts = ["--latest", "--erase", "--no-input", "--no-action", "--ipsw-info", "--custom", "--shsh", "--no-restore", "--keep-pers", "--pwn", "--plain-progress", "--restore-mode", "--ignore-errors"]; checks = [tab.latest_check, tab.erase_check, tab.no_input_check, tab.no_action_check, tab.ipsw_info_check, tab.custom_check, tab.shsh_check, tab.no_restore_check, tab.keep_pers_check, tab.pwn_check, tab.plain_progress_check, tab.restore_mode_check, tab.ignore_errors_check]; cmd += self._get_common_options_string_no_udid(tab)
            for o, c in zip(opts, checks):
                if c.isChecked(): cmd += f"{o} "
            if tab.ecid_edit.text(): cmd += f"--ecid {tab.ecid_edit.text()} "
            if tab.cache_path_edit.text(): cmd += f"--cache-path '{tab.cache_path_edit.text()}' "
            if tab.server_edit.text(): cmd += f"--server '{tab.server_edit.text()}' "
            if tab.ticket_edit.text(): cmd += f"--ticket '{tab.ticket_edit.text()}' "
            if tab.variant_edit.text(): cmd += f"--variant '{tab.variant_edit.text()}' "
            if tab.path_edit.text(): cmd += f"'{tab.path_edit.text()}'"
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicescreenshot_tab(self):
        tab = self._create_and_setup_tab("idevicescreenshot"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Parametrar"); gl = QGridLayout(group)
        gl.addWidget(QLabel("Filnamn (valfritt):"), 0, 0); tab.file_edit = QLineEdit(); tab.file_edit.setPlaceholderText("screenshot-DATE.tiff"); gl.addWidget(tab.file_edit, 0, 1)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicescreenshot " + self._get_common_options_string_no_udid(tab)
            if tab.file_edit.text(): cmd += f"'{tab.file_edit.text()}' "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_idevicesetlocation_tab(self):
        tab = self._create_and_setup_tab("idevicesetlocation"); tab.options = ["udid", "network", "debug"]
        layout = QGridLayout(tab); group = QGroupBox("Åtgärd"); gl = QGridLayout(group)
        tab.set_loc_radio = QRadioButton("Ställ in position:"); tab.set_loc_radio.setChecked(True); gl.addWidget(tab.set_loc_radio, 0, 0, 1, 2)
        gl.addWidget(QLabel("Latitud:"), 1, 0); tab.lat_edit = QLineEdit(); gl.addWidget(tab.lat_edit, 1, 1)
        gl.addWidget(QLabel("Longitud:"), 2, 0); tab.long_edit = QLineEdit(); gl.addWidget(tab.long_edit, 2, 1)
        tab.reset_loc_radio = QRadioButton("Återställ position"); gl.addWidget(tab.reset_loc_radio, 3, 0, 1, 2)
        layout.addWidget(group, 0, 0); layout.addWidget(self._create_common_options_group(tab, ["network", "debug"]), 0, 1); layout.setRowStretch(1, 1)
        def generate_command_string():
            cmd = "idevicesetlocation " + self._get_common_options_string_no_udid(tab)
            if tab.reset_loc_radio.isChecked(): cmd += "reset"
            elif tab.set_loc_radio.isChecked(): cmd += f"-- {tab.lat_edit.text()} {tab.long_edit.text()}"
            return cmd.strip()
        tab.generate_command_string = generate_command_string
    
    def create_idevicesyslog_tab(self):
        tab = self._create_and_setup_tab("idevicesyslog"); tab.options = ["udid", "network", "debug"]
        tab_layout = QHBoxLayout(tab); filter_group = QGroupBox("Filteralternativ"); fl = QGridLayout(filter_group)
        fl.addWidget(QLabel("--match:"), 0, 0); tab.match_edit = QLineEdit(); fl.addWidget(tab.match_edit, 0, 1)
        fl.addWidget(QLabel("--trigger:"), 1, 0); tab.trigger_edit = QLineEdit(); fl.addWidget(tab.trigger_edit, 1, 1)
        fl.addWidget(QLabel("--untrigger:"), 2, 0); tab.untrigger_edit = QLineEdit(); fl.addWidget(tab.untrigger_edit, 2, 1)
        fl.addWidget(QLabel("--process:"), 3, 0); tab.process_edit = QLineEdit(); fl.addWidget(tab.process_edit, 3, 1)
        fl.addWidget(QLabel("--exclude:"), 4, 0); tab.exclude_edit = QLineEdit(); fl.addWidget(tab.exclude_edit, 4, 1)
        tab.quiet_check = QCheckBox("--quiet"); fl.addWidget(tab.quiet_check, 5, 0); tab.kernel_check = QCheckBox("--kernel"); fl.addWidget(tab.kernel_check, 5, 1); tab.no_kernel_check = QCheckBox("--no-kernel"); fl.addWidget(tab.no_kernel_check, 6, 0); tab_layout.addWidget(filter_group)
        options_group = QGroupBox("Allmänna Alternativ"); ol = QGridLayout(options_group); tab.exit_check = QCheckBox("Avsluta vid frånkoppling (--exit)"); ol.addWidget(tab.exit_check, 0, 0); tab.no_colors_check = QCheckBox("Inga färger (--no-colors)"); ol.addWidget(tab.no_colors_check, 0, 1)
        right_vbox = QVBoxLayout(); right_vbox.addWidget(options_group); right_vbox.addWidget(self._create_common_options_group(tab, ["network", "debug"])); right_vbox.addStretch(); tab_layout.addLayout(right_vbox)
        def generate_command_string():
            cmd = "idevicesyslog " + self._get_common_options_string_no_udid(tab)
            if tab.exit_check.isChecked(): cmd += "-x "; 
            if tab.no_colors_check.isChecked(): cmd += "--no-colors "
            if tab.match_edit.text(): cmd += f"-m '{tab.match_edit.text()}' "
            if tab.trigger_edit.text(): cmd += f"-t '{tab.trigger_edit.text()}' "
            if tab.untrigger_edit.text(): cmd += f"-T '{tab.untrigger_edit.text()}' "
            if tab.process_edit.text(): cmd += f"-p '{tab.process_edit.text()}' "
            if tab.exclude_edit.text(): cmd += f"-e '{tab.exclude_edit.text()}' "
            if tab.quiet_check.isChecked(): cmd += "-q "; 
            if tab.kernel_check.isChecked(): cmd += "-k "; 
            if tab.no_kernel_check.isChecked(): cmd += "-K "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_irecovery_tab(self):
        tab = self._create_and_setup_tab("irecovery"); tab.options = [] # UDID not used, only ECID
        tab_layout = QHBoxLayout(tab); group = QGroupBox("Kommandon & Filer"); gl = QGridLayout(group)
        gl.addWidget(QLabel("--command CMD:"), 0, 0); tab.cmd_edit = QLineEdit(); gl.addWidget(tab.cmd_edit, 0, 1, 1, 2)
        gl.addWidget(QLabel("--file FILE:"), 1, 0); tab.file_edit = FileDropLineEdit(); gl.addWidget(tab.file_edit, 1, 1)
        b1 = QPushButton("..."); b1.setToolTip("Bläddra efter fil"); b1.clicked.connect(lambda: self.select_file(tab.file_edit)); gl.addWidget(b1, 1, 2)
        gl.addWidget(QLabel("--payload FILE:"), 2, 0); tab.payload_edit = FileDropLineEdit(); gl.addWidget(tab.payload_edit, 2, 1)
        b2 = QPushButton("..."); b2.setToolTip("Bläddra efter payload-fil"); b2.clicked.connect(lambda: self.select_file(tab.payload_edit)); gl.addWidget(b2, 2, 2)
        gl.addWidget(QLabel("--script FILE:"), 3, 0); tab.script_edit = FileDropLineEdit(); gl.addWidget(tab.script_edit, 3, 1)
        b3 = QPushButton("..."); b3.setToolTip("Bläddra efter skriptfil"); b3.clicked.connect(lambda: self.select_file(tab.script_edit)); gl.addWidget(b3, 3, 2); tab_layout.addWidget(group)
        options_group = QGroupBox("Alternativ"); ol = QGridLayout(options_group)
        tab.mode_check = QCheckBox("--mode"); ol.addWidget(tab.mode_check, 0, 0); tab.reset_check = QCheckBox("--reset"); ol.addWidget(tab.reset_check, 0, 1)
        tab.normal_check = QCheckBox("--normal"); ol.addWidget(tab.normal_check, 1, 0); tab.query_check = QCheckBox("--query"); ol.addWidget(tab.query_check, 1, 1)
        tab.devices_check = QCheckBox("--devices"); ol.addWidget(tab.devices_check, 2, 0); tab.verbose_check = QCheckBox("--verbose"); ol.addWidget(tab.verbose_check, 2, 1)
        tab.shell_check = QCheckBox("--shell (Interaktiv)"); ol.addWidget(tab.shell_check, 3, 0)
        ol.addWidget(QLabel("--ecid ECID:"), 4, 0); tab.ecid_edit = QLineEdit(); ol.addWidget(tab.ecid_edit, 4, 1)
        right_vbox = QVBoxLayout(); right_vbox.addWidget(options_group); right_vbox.addStretch(); tab_layout.addLayout(right_vbox)
        def generate_command_string():
            cmd = "irecovery "; checks = [tab.mode_check, tab.reset_check, tab.normal_check, tab.query_check, tab.devices_check, tab.verbose_check, tab.shell_check]; opts = ["-m", "-r", "-n", "-q", "-a", "-v", "-s"]
            for o, c in zip(opts, checks):
                if c.isChecked(): cmd += f"{o} "
            if tab.ecid_edit.text(): cmd += f"-i {tab.ecid_edit.text()} "
            if tab.cmd_edit.text(): cmd += f"-c '{tab.cmd_edit.text()}' "
            if tab.file_edit.text(): cmd += f"-f '{tab.file_edit.text()}' "
            if tab.payload_edit.text(): cmd += f"-k '{tab.payload_edit.text()}' "
            if tab.script_edit.text(): cmd += f"-e '{tab.script_edit.text()}' "
            return cmd.strip()
        tab.generate_command_string = generate_command_string

    def create_about_tab(self):
        tab = self._create_and_setup_tab("Om", icon_name="info")
        layout = QVBoxLayout(tab); layout.setAlignment(Qt.AlignCenter)
        title = QLabel("iDevice Toolbox"); title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        version_label = QLabel("Version 11.0 (Moderniserad)"); version_label.setStyleSheet("font-style: italic;")
        desc_label = QLabel("Detta verktyg är ett grafiskt gränssnitt för kommandoradsverktygen i\n<a href='https://libimobiledevice.org/'>libimobiledevice</a>-projektet.\n\nDet är designat för att förenkla interaktionen med iOS-enheter."); desc_label.setWordWrap(True); desc_label.setAlignment(Qt.AlignCenter); desc_label.setOpenExternalLinks(True)
        layout.addWidget(title); layout.addWidget(version_label); layout.addSpacing(20); layout.addWidget(desc_label); layout.addStretch()
        tab.generate_command_string = lambda: "" # No command for about tab


if __name__ == '__main__':
    QApplication.setOrganizationName("iDeviceGUITool_Modern"); QApplication.setApplicationName("App")
    app = QApplication(sys.argv)
    main_win = IdeviceGUITool()
    main_win.show()
    sys.exit(app.exec_())
