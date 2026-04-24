# Importowanie niezbędnych modułów
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
import yaml
import os
import serial.tools.list_ports
import subprocess
import threading
import time
import psutil
import shutil


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


def get_runtime_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return BASE_DIR


def get_deej_executable_path():
    executable_name = 'deej.exe' if sys.platform == 'win32' else 'deej'
    search_dirs = [get_runtime_base_dir(), BASE_DIR]

    for directory in search_dirs:
        candidate = os.path.join(directory, executable_name)
        if os.path.exists(candidate):
            return candidate

    return os.path.join(get_runtime_base_dir(), executable_name)


def get_config_file_path():
    deej_path = get_deej_executable_path()
    return os.path.join(os.path.dirname(deej_path), 'config.yaml')


def ensure_persistent_config_file():
    config_file_path = get_config_file_path()
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

    if os.path.exists(config_file_path):
        return

    default_paths = [
        os.path.join(BASE_DIR, 'config.yaml'),
        os.path.join(ASSETS_DIR, 'config.yaml')
    ]

    for default_path in default_paths:
        if os.path.exists(default_path):
            shutil.copy2(default_path, config_file_path)
            return

    with open(config_file_path, 'w') as file:
        yaml.safe_dump({}, file, default_flow_style=False)


def clean_app_name(name):
    normalized = name.strip().strip('"')
    lowered = normalized.lower()

    if lowered.endswith('.exe'):
        lowered = lowered[:-4]
    if lowered.endswith('.bin'):
        lowered = lowered[:-4]

    lowered = lowered.replace('-', ' ').replace('_', ' ').strip()

    blocked_names = {
        'speech dispatcher',
        'speech dispatcher dummy',
        'speech-dispatcher',
        'speech-dispatcher-dummy',
        'sd dummy',
        'dummy',
        'playback',
        'stream',
        'output',
        'fmod audio',
        'audio stream'
    }
    if lowered in blocked_names:
        return ""

    if "chrome" in lowered:
        return "chrome"
    if "firefox" in lowered:
        return "firefox"
    if "discord" in lowered:
        return "discord"
    if "spotify" in lowered:
        return "spotify"
    if "eurotrucks2" in lowered or "euro truck" in lowered:
        return "eurotrucks2"
    if "zerohour" in lowered or "zero hour" in lowered:
        return "zerohour"

    return lowered.replace(" ", "")


def get_audio_apps_linux():
    try:
        result = subprocess.check_output(["pactl", "list", "sink-inputs"], text=True)

        def parse_value(line):
            _, value = line.split("=", 1)
            return value.strip().strip('"')

        def finalize_entry(entry, app_set):
            candidates = [
                ("application.process.binary", entry.get("application.process.binary", "")),
                ("application.name", entry.get("application.name", "")),
                ("media.name", entry.get("media.name", ""))
            ]

            wine_wrappers = {
                "wine",
                "wine64",
                "winepreloader",
                "wine64preloader",
                "wine-preloader",
                "wine64-preloader",
                "wineserver"
            }

            deferred_wrapper = ""

            for _, candidate in candidates:
                if not candidate:
                    continue
                # Odrzuć wartości będące samym ID/liczbą.
                if candidate.isdigit():
                    continue
                cleaned = clean_app_name(candidate)
                if not cleaned:
                    continue

                if cleaned in wine_wrappers:
                    deferred_wrapper = cleaned
                    continue

                if cleaned:
                    app_set.add(cleaned)
                    return

            if deferred_wrapper:
                app_set.add(deferred_wrapper)

        apps = set()
        current_entry = {}

        for raw_line in result.splitlines():
            line = raw_line.strip()

            if line.startswith("Sink Input #"):
                if current_entry:
                    finalize_entry(current_entry, apps)
                current_entry = {}
                continue

            if "=" not in line:
                continue

            if line.startswith("application.name"):
                current_entry["application.name"] = parse_value(line)
            elif line.startswith("application.process.binary"):
                current_entry["application.process.binary"] = parse_value(line)
            elif line.startswith("media.name"):
                current_entry["media.name"] = parse_value(line)

        if current_entry:
            finalize_entry(current_entry, apps)

        return sorted(apps)
    except Exception:
        return []


def get_processes_linux():
    try:
        user_name = os.getlogin()
    except OSError:
        user_name = os.environ.get("USER", "")

    result = subprocess.check_output(
        ["ps", "-u", user_name, "-o", "comm="],
        text=True
    )

    return sorted(set(line.strip() for line in result.splitlines() if line.strip()))

# Klasa dialogu do dodawania aplikacji
class AddApplicationDialog(QtWidgets.QDialog):
    def __init__(self, special_options=None, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(ASSETS_DIR, 'addapplicationdialog.ui'), self)
        self.special_options = special_options or {}
        self.tabWidget = self.findChild(QtWidgets.QTabWidget, 'tabWidget')
        self.listApplications = self.findChild(QtWidgets.QListWidget, 'listApplications')
        self.listSystem = self.findChild(QtWidgets.QListWidget, 'listSystem')
        self.okButton = self.findChild(QtWidgets.QPushButton, 'okButton')
        self.cancelButton = self.findChild(QtWidgets.QPushButton, 'cancelButton')
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.populate_lists()
        self.listApplications.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listSystem.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.setup_custom_tab()

    def setup_custom_tab(self):
        custom_tab = QtWidgets.QWidget()
        custom_layout = QtWidgets.QVBoxLayout(custom_tab)

        self.customAppInput = QtWidgets.QLineEdit()
        self.customAppInput.setPlaceholderText('Type application name, e.g. firefox')
        self.customAppInput.setStyleSheet(
            'QLineEdit { border: 2px solid #6f7a89; border-radius: 6px; padding: 6px; } '
            'QLineEdit:focus { border: 2px solid #3b82f6; }'
        )
        self.customAppInput.returnPressed.connect(self.add_custom_application)

        self.customAddButton = QtWidgets.QPushButton('Add')
        self.customAddButton.clicked.connect(self.add_custom_application)

        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.customAppInput)
        input_layout.addWidget(self.customAddButton)

        self.listCustomApplications = QtWidgets.QListWidget()
        self.listCustomApplications.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        help_label = QtWidgets.QLabel('Add custom app names manually and select them from the list below.')
        help_label.setWordWrap(True)

        custom_layout.addWidget(help_label)
        custom_layout.addLayout(input_layout)
        custom_layout.addWidget(self.listCustomApplications)

        self.tabWidget.addTab(custom_tab, 'Custom')

    def add_custom_application(self):
        raw_value = self.customAppInput.text().strip()
        if not raw_value:
            return

        custom_name = clean_app_name(raw_value)
        if not custom_name:
            QtWidgets.QMessageBox.warning(self, 'Invalid name', 'Please enter a valid application name.')
            return

        existing_items = {
            self.listCustomApplications.item(i).text()
            for i in range(self.listCustomApplications.count())
        }

        if custom_name not in existing_items:
            self.listCustomApplications.addItem(custom_name)

        self.customAppInput.clear()

    def populate_lists(self):
        applications = self.get_installed_applications()
        self.listApplications.addItems(applications)
        display_items = [v for v in self.special_options.values() if v != 'Everything Else']
        display_items.append('Everything Else')
        self.listSystem.addItems(display_items)

    def get_installed_applications(self):
        if sys.platform == 'win32':
            return self.get_installed_applications_windows()
        elif sys.platform == 'darwin':
            return self.get_installed_applications_mac()
        else:
            apps = get_audio_apps_linux()
            return apps if apps else get_processes_linux()

    def get_installed_applications_windows(self):
        return []

    def get_installed_applications_mac(self):
        try:
            applications_dir = '/Applications'
            return [item for item in os.listdir(applications_dir) if item.endswith('.app')]
        except Exception as e:
            print(f"Error retrieving applications: {e}")
            return []

    def get_selected_items(self):
        selected_apps = [self.listApplications.item(i).text() for i in range(self.listApplications.count()) if self.listApplications.item(i).isSelected()]
        selected_system = [self.listSystem.item(i).text() for i in range(self.listSystem.count()) if self.listSystem.item(i).isSelected()]
        selected_custom = [
            self.listCustomApplications.item(i).text()
            for i in range(self.listCustomApplications.count())
            if self.listCustomApplications.item(i).isSelected()
        ]

        pending_custom = clean_app_name(self.customAppInput.text().strip()) if hasattr(self, 'customAppInput') else ''
        if pending_custom and pending_custom not in selected_custom:
            selected_custom.append(pending_custom)

        special_options_reverse = {v: k for k, v in self.special_options.items()}
        selected_system_mapped = [special_options_reverse.get(item, item) for item in selected_system]
        return selected_apps + selected_system_mapped + selected_custom

# Klasa głównego menadżera konfiguracji
class DeejConfigManager(QtWidgets.QMainWindow):
    arduinoDetected = QtCore.pyqtSignal(str)
    arduinoNotDetected = QtCore.pyqtSignal()

    def __init__(self):
        super(DeejConfigManager, self).__init__()
        self.setWindowIcon(QtGui.QIcon(os.path.join(ASSETS_DIR, 'icon.png')))
        self.setWindowTitle("Mixer")
        uic.loadUi(os.path.join(ASSETS_DIR, 'mainwindow.ui'), self)
        self.deej_process = None
        self.special_options = {
            'master': 'Master Volume',
            'mic': 'Microphone Input',
            'deej.unmapped': 'Everything Else',
            'deej.current': 'Current App',
            'system': 'System Sounds'
        }
        self.config_file_path = get_config_file_path()
        ensure_persistent_config_file()
        self.arduinoDetected.connect(self.handle_arduino_detected)
        self.arduinoNotDetected.connect(self.handle_arduino_not_detected)
        self.monitoring_thread = threading.Thread(target=self.monitor_arduino, daemon=True)
        self.monitoring_thread.start()

        # Odnajdź elementy interfejsu użytkownika
        self.saveButton = self.findChild(QtWidgets.QPushButton, 'saveButton')
        self.loadButton = self.findChild(QtWidgets.QPushButton, 'loadButton')
        self.refreshButton = self.findChild(QtWidgets.QPushButton, 'refreshButton')
        self.invertSlidersCheckBox = self.findChild(QtWidgets.QCheckBox, 'invertSlidersCheckBox')
        self.baudRateSpinBox = self.findChild(QtWidgets.QSpinBox, 'baudRateSpinBox')
        self.noiseReductionComboBox = self.findChild(QtWidgets.QComboBox, 'noiseReductionComboBox')
        self.listSlider0 = self.findChild(QtWidgets.QListWidget, 'listSlider0')
        self.listSlider1 = self.findChild(QtWidgets.QListWidget, 'listSlider1')
        self.listSlider2 = self.findChild(QtWidgets.QListWidget, 'listSlider2')
        self.listSlider3 = self.findChild(QtWidgets.QListWidget, 'listSlider3')
        self.listSlider4 = self.findChild(QtWidgets.QListWidget, 'listSlider4')
        self.addButton0 = self.findChild(QtWidgets.QPushButton, 'addButton0')
        self.addButton1 = self.findChild(QtWidgets.QPushButton, 'addButton1')
        self.addButton2 = self.findChild(QtWidgets.QPushButton, 'addButton2')
        self.addButton3 = self.findChild(QtWidgets.QPushButton, 'addButton3')
        self.addButton4 = self.findChild(QtWidgets.QPushButton, 'addButton4')

        self.saveButton.clicked.connect(self.save_config)
        self.loadButton.clicked.connect(self.load_config)
        self.refreshButton.clicked.connect(self.refresh_applications)
        self.addButton0.clicked.connect(lambda: self.open_add_dialog(self.listSlider0))
        self.addButton1.clicked.connect(lambda: self.open_add_dialog(self.listSlider1))
        self.addButton2.clicked.connect(lambda: self.open_add_dialog(self.listSlider2))
        self.addButton3.clicked.connect(lambda: self.open_add_dialog(self.listSlider3))
        self.addButton4.clicked.connect(lambda: self.open_add_dialog(self.listSlider4))
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(os.path.join(ASSETS_DIR, 'icon.png')))
        show_action = QtWidgets.QAction("Show", self)
        quit_action = QtWidgets.QAction("Exit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QtWidgets.qApp.quit)
        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.load_config()
        self.detect_and_set_arduino_port()
        with open(os.path.join(ASSETS_DIR, 'dark_theme.qss'), 'r') as file:
            self.setStyleSheet(file.read())

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Running in the background",
            "Your application is still running. To exit, choose 'Exit' from the tray menu.",
            QtWidgets.QSystemTrayIcon.Information,
            2000
        )

    def detect_arduino_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if ("Arduino" in port.description or "CH340" in port.description):
                return port.device
            # Sprawdź VID i PID
            if port.vid is not None and port.pid is not None:
                if (port.vid == 0x1A86 and port.pid == 0x7523):  # CH340
                    return port.device
                if (port.vid == 0x2341):  # Oficjalne Arduino
                    return port.device
                if (port.vid == 0x0403 and port.pid == 0x6001):  # FTDI
                    return port.device
        return None


    def detect_and_set_arduino_port(self):
        arduino_port = self.detect_arduino_port()
        if arduino_port:
            self.save_arduino_port_to_config(arduino_port)
            self.arduinoDetected.emit(arduino_port)
        else:
            self.arduinoNotDetected.emit()

    def save_arduino_port_to_config(self, port):
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            config = {}
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as file:
                    config = yaml.safe_load(file) or {}
            config['com_port'] = port
            with open(self.config_file_path, 'w') as file:
                yaml.safe_dump(config, file, default_flow_style=False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save Arduino port to config.yaml: {e}")

    def get_installed_applications(self):
        if sys.platform == 'win32':
            return self.get_installed_applications_windows()
        elif sys.platform == 'darwin':
            return self.get_installed_applications_mac()
        else:
            apps = get_audio_apps_linux()
            return apps if apps else get_processes_linux()

    def get_installed_applications_windows(self):
        return []

    def get_installed_applications_mac(self):
        try:
            applications_dir = '/Applications'
            return [item for item in os.listdir(applications_dir) if item.endswith('.app')]
        except Exception as e:
            print(f"Error retrieving applications: {e}")
            return []

    def open_add_dialog(self, list_widget):
        dialog = AddApplicationDialog(self.special_options, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_items = dialog.get_selected_items()
            self.add_items_to_list_widget(list_widget, selected_items)

    def add_items_to_list_widget(self, list_widget, items):
        for item in items:
            self.add_list_item_with_button(list_widget, item, item)
        self.remove_duplicates(list_widget)

    def add_list_item_with_button(self, list_widget, descriptive_name, user_data):
        # Text is rendered by the custom QLabel below; keep QListWidgetItem text empty
        # to avoid showing the same app name twice.
        item = QtWidgets.QListWidgetItem('')
        item.setData(QtCore.Qt.UserRole, user_data)
        item.setToolTip(descriptive_name)
        button = QtWidgets.QPushButton('X')
        button.setMaximumSize(30, 30)
        button.clicked.connect(lambda: self.remove_list_item(list_widget, item))
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.addWidget(QtWidgets.QLabel(descriptive_name))
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, widget)

    def remove_list_item(self, list_widget, item):
        row = list_widget.row(item)
        list_widget.takeItem(row)

    def remove_duplicates(self, list_widget):
        seen_items = set()
        duplicates = []
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            user_data = item.data(QtCore.Qt.UserRole)
            if user_data in seen_items:
                duplicates.append(item)
            else:
                seen_items.add(user_data)
        for item in duplicates:
            row = list_widget.row(item)
            list_widget.takeItem(row)

    def refresh_applications(self):
        self.get_installed_applications()

    def save_config(self):
        config = {
            'slider_mapping': {
               0: self.get_slider_config(self.listSlider0),
               1: self.get_slider_config(self.listSlider1),
               2: self.get_slider_config(self.listSlider2),
               3: self.get_slider_config(self.listSlider3),
               4: self.get_slider_config(self.listSlider4)
            },
            'invert_sliders': self.invertSliders.isChecked(),
            'baud_rate': 9600,  # Fixed Baud Rate
            'noise_reduction': "default",  # Fixed Noise Reduction
            'com_port': self.detect_arduino_port() or "",
        }
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            with open(self.config_file_path, 'w') as file:
                yaml.safe_dump(config, file, default_flow_style=False)
            QtWidgets.QMessageBox.information(self, "Success", "Configuration saved successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

    def get_slider_config(self, list_widget):
        config = []
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            user_data = item.data(QtCore.Qt.UserRole)
            config.append(user_data)
        return config

    def load_config(self):
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as file:
                    config = yaml.safe_load(file)
                    if config:
                        self.load_slider_config(self.listSlider0, config.get('slider_mapping', {}).get(0, []))
                        self.load_slider_config(self.listSlider1, config.get('slider_mapping', {}).get(1, []))
                        self.load_slider_config(self.listSlider2, config.get('slider_mapping', {}).get(2, []))
                        self.load_slider_config(self.listSlider3, config.get('slider_mapping', {}).get(3, []))
                        self.load_slider_config(self.listSlider4, config.get('slider_mapping', {}).get(4, []))
                        self.invertSliders.setChecked(config.get('invert_sliders', False))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load configuration: {e}")

    def load_slider_config(self, list_widget, slider_config):
        list_widget.clear()
        for item in slider_config:
            descriptive_name = self.special_options.get(item, item)
            self.add_list_item_with_button(list_widget, descriptive_name, item)

    def monitor_arduino(self):
        last_port = None
        while True:
            current_port = self.detect_arduino_port()
            if current_port != last_port:
                if current_port:
                    self.save_arduino_port_to_config(current_port)
                    QtCore.QMetaObject.invokeMethod(self, 'arduinoDetected', QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, current_port))
                else:
                    QtCore.QMetaObject.invokeMethod(self, 'arduinoNotDetected', QtCore.Qt.QueuedConnection)
                last_port = current_port
            time.sleep(5)

    def handle_arduino_detected(self, port):
        QtCore.QMetaObject.invokeMethod(self, 'start_deej', QtCore.Qt.QueuedConnection)

    def handle_arduino_not_detected(self):
        QtCore.QMetaObject.invokeMethod(self, 'stop_deej', QtCore.Qt.QueuedConnection)

    @QtCore.pyqtSlot()
    def start_deej(self):
        if not self.deej_process:
            try:
                deej_path = get_deej_executable_path()
                if not os.path.exists(deej_path):
                    raise FileNotFoundError(f"deej executable not found: {deej_path}")
                print(deej_path)
                self.deej_process = subprocess.Popen(deej_path, cwd=os.path.dirname(deej_path))
                print(self.deej_process)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start deej executable: {e}")

    @QtCore.pyqtSlot()
    def stop_deej(self):
        if self.deej_process:
            self.deej_process.terminate()
            self.deej_process = None

# Funkcja główna
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DeejConfigManager()
    window.show()
    sys.exit(app.exec_())

# Uruchomienie aplikacji
if __name__ == '__main__':
    main()
