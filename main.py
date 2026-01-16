# Importowanie niezbędnych modułów
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
import yaml
import os
import serial.tools.list_ports
import subprocess
import threading
import time
from pycaw.pycaw import AudioUtilities

# Klasa dialogu do dodawania aplikacji
class AddApplicationDialog(QtWidgets.QDialog):
    def __init__(self, special_options=None, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.expanduser("~"), 'deej/assets', 'addapplicationdialog.ui'), self)
        self.special_options = special_options or {}
        self.listApplications = self.findChild(QtWidgets.QListWidget, 'listApplications')
        self.listSystem = self.findChild(QtWidgets.QListWidget, 'listSystem')
        self.okButton = self.findChild(QtWidgets.QPushButton, 'okButton')
        self.cancelButton = self.findChild(QtWidgets.QPushButton, 'cancelButton')
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.populate_lists()
        self.listApplications.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listSystem.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

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
            return []

    def get_installed_applications_windows(self):
        try:
            sessions = AudioUtilities.GetAllSessions()
            apps = set()
            for session in sessions:
                if session.Process:
                    try:
                        app_name = session.Process.name()
                        if app_name and app_name != "Unknown":
                            apps.add(app_name)
                    except Exception as e:
                        print(f"Error retrieving process name: {e}")
            return list(apps)
        except Exception as e:
            print(f"Error retrieving applications: {e}")
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
        special_options_reverse = {v: k for k, v in self.special_options.items()}
        selected_system_mapped = [special_options_reverse.get(item, item) for item in selected_system]
        return selected_apps + selected_system_mapped

# Klasa głównego menadżera konfiguracji
class DeejConfigManager(QtWidgets.QMainWindow):
    arduinoDetected = QtCore.pyqtSignal(str)
    arduinoNotDetected = QtCore.pyqtSignal()

    def __init__(self):
        super(DeejConfigManager, self).__init__()
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.expanduser("~"), 'deej/assets', 'icon.png')))
        self.setWindowTitle("Mixer")
        uic.loadUi(os.path.join(os.path.expanduser("~"), 'deej/assets', 'mainwindow.ui'), self)
        self.deej_process = None
        self.special_options = {
            'master': 'Master Volume',
            'mic': 'Microphone Input',
            'deej.unmapped': 'Everything Else',
            'deej.current': 'Current App',
            'system': 'System Sounds'
        }
        self.config_file_path = os.path.join(os.path.expanduser("~"), 'deej/config.yaml')
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
        self.tray_icon.setIcon(QtGui.QIcon(os.path.join(os.path.expanduser("~"), 'deej/assets', 'icon.png')))
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
        with open(os.path.join(os.path.expanduser("~"), 'deej/assets', 'dark_theme.qss'), 'r') as file:
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
            return []

    def get_installed_applications_windows(self):
        try:
            sessions = AudioUtilities.GetAllSessions()
            apps = set()
            for session in sessions:
                if session.Process:
                    try:
                        app_name = session.Process.name()
                        if app_name and app_name != "Unknown":
                            apps.add(app_name)
                    except Exception as e:
                        print(f"Error retrieving process name: {e}")
            return list(apps)
        except Exception as e:
            print(f"Error retrieving applications: {e}")
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
        item = QtWidgets.QListWidgetItem(descriptive_name)
        item.setData(QtCore.Qt.UserRole, user_data)
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
                deej_path = os.path.join(os.path.expanduser("~"), 'deej', 'deej.exe')
                print(deej_path)
                self.deej_process = subprocess.Popen(deej_path, cwd=os.path.join(os.path.expanduser("~"), 'deej'))
                print(self.deej_process)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start deej.exe: {e}")

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
