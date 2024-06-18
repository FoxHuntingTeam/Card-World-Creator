import os
import sys

from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont
from PyQt5.QtWidgets import QLabel, QTableWidget, QScrollArea, QTextEdit, QPushButton, QComboBox, QMessageBox, QDialog, \
    QVBoxLayout, QProgressBar, QFormLayout, QLineEdit, QTableWidgetItem, QFileDialog, QGraphicsDropShadowEffect
from langdetect import detect
from sqlalchemy.orm import Session
from translate import Translator

from data.config import ABOUT_MESSAGE, HELP_MESSAGE
from database import Projects, engine, Cards, Frames, ThisProject
from utils.decorators import error_logger


class CardCreationDialog(QDialog):
    def __init__(self, project_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Card")
        self.project_type = project_type
        self.setFixedWidth(300)
        layout = QVBoxLayout()

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.description_label = QLabel("Description:")
        self.description_input = QLineEdit()
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)

        self.type_label = QLabel("Type:")
        self.type_input = QComboBox()
        self.type_input.addItems(["", "Alpha", "Omega", "Delta"] if project_type == "VC" else ["", "Ordinary", "Special"])
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_input)

        self.value_label = QLabel("Value:")
        self.value_input = QComboBox()
        layout.addWidget(self.value_label)
        layout.addWidget(self.value_input)

        self.type_input.currentTextChanged.connect(self.update_value_options)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    @error_logger()
    def update_value_options(self, none=None):
        card_type = self.type_input.currentText()
        self.value_input.clear()

        if card_type == "Alpha":
            self.value_input.addItems(["1000", "2000", "3000", "4000", "5000"])
        elif card_type == "Omega":
            self.value_input.addItems(["4000", "5000", "6000", "7000", "8000"])
        elif card_type == "Delta":
            self.value_input.addItems(["7000", "8000", "9000", "10000", "11000"])
        elif card_type == "Ordinary":
            self.value_input.addItems(["1000", "2000", "3000", "4000", "5000", "6000"])
        elif card_type == "Special":
            self.value_input.addItems(["3000", "4000", "5000", "6000", "7000", "8000", "9000"])

    @error_logger()
    def submit(self, none=None):
        name = str(self.name_input.text())
        description = str(self.description_input.text())
        card_type = str(self.type_input.currentText())
        value = int(self.value_input.currentText())

        if not name or not description or not value:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        with Session(engine) as session:
                with session.begin():
                    thisproject = session.query(ThisProject).first()
                    project = session.query(Projects).filter_by(name=thisproject.name).first()
                    rar = value / 1000
                    if card_type.lower() == "omega":
                        rar -= 3
                    elif card_type.lower() == "delta":
                        rar -= 6
                    elif card_type.lower() == "special":
                        rar -= 2
                    card = session.query(Cards).filter_by(full=False, type=card_type.lower(), rarity_id=rar, project=project.name).first()
                    card.name = name
                    card.description = description
                    card.full = True
        self.accept()

class ProgressDialog(QDialog):
    def __init__(self, total_steps, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.setWindowTitle("Processing")
        self.setFixedWidth(300)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.layout = QVBoxLayout()

        self.label = QLabel("Processing...")
        self.layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(total_steps)
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)

    @error_logger()
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QtWidgets.QApplication.processEvents()

class NewProjectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Project")
        self.setFixedWidth(300)

        self.layout = QFormLayout()

        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.check_input)
        self.layout.addRow(self.name_label, self.name_edit)

        self.type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["NACAMA CARD", "Viresets Card"])
        self.type_combo.currentIndexChanged.connect(self.update_options)
        self.layout.addRow(self.type_label, self.type_combo)

        self.option_labels = []
        self.option_combos = []

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setEnabled(False)
        self.layout.addRow(self.submit_button)

        self.setLayout(self.layout)

        self.update_options()

    @error_logger()
    def update_options(self, none=None):
        for label in self.option_labels:
            self.layout.removeWidget(label)
            label.deleteLater()
        for combo in self.option_combos:
            self.layout.removeWidget(combo)
            combo.deleteLater()

        self.option_labels.clear()
        self.option_combos.clear()

        if self.type_combo.currentText() == "NACAMA CARD":
            options = ["Ordinary", "Special"]
            sub_options = [["100", "200", "300"], ["50", "100"]]
        else:
            options = ["Alpha", "Omega", "Delta"]
            sub_options = ["None", "50", "100", "150", "200", "250", "300"]

        for option in options:
            option_label = QLabel(option + ":")
            option_combo = QComboBox()
            if self.type_combo.currentText() == "NACAMA CARD":
                if option == "Ordinary":
                    option_combo.addItems(sub_options[0])
                else:
                    option_combo.addItems(sub_options[1])
            else:
                option_combo.addItems(sub_options)
            self.option_labels.append(option_label)
            self.option_combos.append(option_combo)
            self.layout.insertRow(self.layout.rowCount() - 1, option_label, option_combo)

    @error_logger()
    def check_input(self, none=None):
        if self.name_edit.text().strip():
            self.submit_button.setEnabled(True)
        else:
            self.submit_button.setEnabled(False)

    @error_logger()
    def submit(self, none=None):
        self.accept()

class DraggableLabel(QtWidgets.QLabel):
    def __init__(self, text, parent):
        super(DraggableLabel, self).__init__(text, parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet(f'''
                            QLabel {{
                                font-family: "Arial";
                                color: white;
                            }}
                            ''')
        self.old_pos = None
        self.emboss_effect = False
        self.new_x = None
        self.new_y = None

    @error_logger()
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            current_font = self.font().family()
            current_color = self.palette().color(self.foregroundRole())
            current_size = self.font().pixelSize()
            if current_color == QtCore.Qt.white:
                color = "black"
            else:
                color = "white"
            self.setStyleSheet(f'''
                                                QLabel {{
                                                    font-family: "{current_font}";
                                                    color: "{color}";
                                                    font-size: "{current_size}";
                                                }}
                                            ''')

        elif event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.pos()


    @error_logger()
    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            parent = self.parentWidget()
            img_fone = parent.findChild(QLabel, "img_fone")
            if img_fone:
                img_fone_rect = img_fone.geometry()
                img_fone_center_x = img_fone_rect.x() + img_fone_rect.width() // 2
                new_x = img_fone_center_x - self.width() // 2
                new_y = self.y()
                self.move(new_x, new_y)


    @error_logger()
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.old_pos:
            delta = event.pos() - self.old_pos
            self.new_x = self.x() + delta.x()
            self.new_y = self.y() + delta.y()
            self.new_x = max(10, min(self.new_x, 423 - self.width()))
            self.new_y = max(20, min(self.new_y, 660 - self.height()))
            self.move(self.new_x, self.new_y)

    @error_logger()
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = None

    @error_logger()
    def paintEvent(self, event):
        if self.emboss_effect:
            shadow_color = QtGui.QColor(0, 0, 0, 150)
            highlight_color = QtGui.QColor(255, 255, 255, 150)
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(shadow_color))
            painter.drawText(self.rect().adjusted(2, 2, 2, 2), QtCore.Qt.AlignCenter, self.text())
            painter.setPen(QtGui.QPen(highlight_color))
            painter.drawText(self.rect().adjusted(-2, -2, -2, -2), QtCore.Qt.AlignCenter, self.text())
            painter.setPen(QtGui.QPen(self.palette().color(QtGui.QPalette.WindowText)))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.text())
        else:
            super().paintEvent(event)


class Ui_MainWindow(object):

    def __init__(self):
        self.selected_project = None
        self.folder = None

    # --- setupUi start ---
    @error_logger()
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.resize(900, 750)
        # Create Object
        self.central_widget = QtWidgets.QWidget(MainWindow) # Central widget
        self.setup_create_object(MainWindow)

        # Register names objects
        self.setup_register_names()

        # Set Geometry
        self.setup_set_geometry()

        # Triggered
        self.setup_set_trigerred()

        # Other
        self.setup_other(MainWindow)
        # Other in other
        MainWindow.setCentralWidget(self.central_widget)
        MainWindow.setMenuBar(self.menu_bar)
        self.label_box.setReadOnly(True)
        self.tab_photoshop.setLayout(self.tab_photoshop_layout)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    @error_logger()
    def setup_create_object(self, MainWindow):
        self.menu_bar = QtWidgets.QMenuBar(MainWindow)  # Menu Bar
        self.menu_menu = QtWidgets.QMenu(self.menu_bar)  # Tab menu / Menu menu
        self.action_help = QtWidgets.QAction(MainWindow)  # Help action

        self.menu_projects = QtWidgets.QMenu(self.menu_menu)  # Menu projetc
        self.action_new_project = QtWidgets.QAction(MainWindow)  # New project button

        self.action_about = QtWidgets.QAction(MainWindow)  # Button "About"

        self.action_open_folder = QtWidgets.QAction(MainWindow)  # Open folder

        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)  # Tabs
        self.tab_statistics = QtWidgets.QWidget()  # Statistics tab
        self.tab_cards = QtWidgets.QWidget()  # Cards tab
        self.tab_photoshop = QtWidgets.QWidget()  # Photoshop tab

        self.label_statistics = QtWidgets.QLabel(self.tab_statistics)  # Statistics text

        self.button_create_card = QtWidgets.QPushButton(self.tab_cards)  # Button create card
        self.button_create_files = QtWidgets.QPushButton(self.tab_cards)  # Button files create
        self.widget_table = QTableWidget()  # Table
        self.scroll_area = QScrollArea(self.tab_cards)  # Scroll area
        self.label_box = QTextEdit(self.tab_cards)  # Box text from table

        self.img_fone = QLabel(self.tab_photoshop)  # Fone image
        self.img_frame = QLabel(self.tab_photoshop)  # Frame image
        self.button_select_file = QPushButton("Select a frame", self.tab_photoshop)  # Button select file
        self.button_save = QPushButton("Save", self.tab_photoshop)  # Button save frame settings
        self.button_photoshop = QPushButton("Photoshop", self.tab_photoshop)  # Photoshop button
        self.draggable_label1 = DraggableLabel("THIS IS NOT TEXT", self.tab_photoshop)
        self.draggable_label2 = DraggableLabel("№000", self.tab_photoshop)
        self.label_element = QtWidgets.QLabel("Element \"№\":", self.tab_photoshop)
        self.label_font_text = QtWidgets.QLabel("Font text:", self.tab_photoshop)
        self.label_font_number = QtWidgets.QLabel("Font number:", self.tab_photoshop)
        self.label_size_text = QtWidgets.QLabel("Size text:", self.tab_photoshop)
        self.label_size_number = QtWidgets.QLabel("Size number:", self.tab_photoshop)
        self.label_shadow_effect_text = QtWidgets.QLabel("Text Shadow Effect:", self.tab_photoshop)
        self.label_shadow_effect_number = QtWidgets.QLabel("Num Shadow Effect:", self.tab_photoshop)
        self.label_emboss_effect_text = QtWidgets.QLabel("Text Emboss Effect:", self.tab_photoshop)
        self.label_emboss_effect_number = QtWidgets.QLabel("Num Emboss Effect:", self.tab_photoshop)
        self.label_type = QtWidgets.QLabel("Type card:", self.tab_photoshop)
        self.label_respect = QtWidgets.QLabel("Card value:", self.tab_photoshop)

        self.box_set_type = QComboBox(self.tab_photoshop)
        self.box_set_respect = QComboBox(self.tab_photoshop)
        self.box_font_text = QtWidgets.QComboBox(self.tab_photoshop)
        self.box_font_number = QtWidgets.QComboBox(self.tab_photoshop)
        self.box_siize_text = QtWidgets.QComboBox(self.tab_photoshop)
        self.box_siize_number = QtWidgets.QComboBox(self.tab_photoshop)
        self.checkbox_shadow_effect_text = QtWidgets.QCheckBox(self.tab_photoshop)
        self.checkbox_shadow_effect_number = QtWidgets.QCheckBox(self.tab_photoshop)
        self.checkbox_emboss_effect_text = QtWidgets.QCheckBox(self.tab_photoshop)
        self.checkbox_emboss_effect_number = QtWidgets.QCheckBox(self.tab_photoshop)
        self.checkbox_element = QtWidgets.QCheckBox(self.tab_photoshop)

        self.project_button_group = QtWidgets.QActionGroup(MainWindow)  # Projects

        self.tab_photoshop_layout = QtWidgets.QVBoxLayout()

    @error_logger()
    def setup_register_names(self, none=None):
        self.label_box.setObjectName("label_box")
        self.central_widget.setObjectName("central_widget")
        self.menu_bar.setObjectName("menu_bar")
        self.menu_menu.setObjectName("menu_menu")
        self.menu_projects.setObjectName("menu_projects")
        self.action_new_project.setObjectName("action_new_project")
        self.action_open_folder.setObjectName("action_open_folder")
        self.tab_widget.setObjectName("tab_widget")
        self.tab_statistics.setObjectName("tab_statistics")
        self.label_statistics.setObjectName("label_statistics")
        self.tab_cards.setObjectName("tab_cards")
        self.button_create_card.setObjectName("button_create_card")
        self.button_create_files.setObjectName("button_create_files")
        self.action_help.setObjectName("action_help")
        self.action_help.setText("Help")
        self.tab_photoshop.setObjectName("tab_photoshop")
        self.img_fone.setObjectName("img_fone")
        self.img_frame.setObjectName("img_frame")
        self.action_about.setObjectName("action_about")

    @error_logger()
    def setup_set_geometry(self, none=None):
        self.checkbox_emboss_effect_number.setGeometry(630, 630, 30, 30)
        self.checkbox_emboss_effect_text.setGeometry(630, 580, 30, 30)
        self.checkbox_shadow_effect_number.setGeometry(630, 530, 30, 30)
        self.checkbox_shadow_effect_text.setGeometry(630, 480, 30, 30)
        self.label_size_number.setGeometry(430, 270, 150, 30)
        self.label_size_text.setGeometry(430, 220, 150, 30)
        self.label_font_number.setGeometry(430, 170, 150, 30)
        self.label_font_text.setGeometry(430, 120, 150, 30)
        self.label_type.setGeometry(430, 20, 150, 30)
        self.label_respect.setGeometry(430, 70, 150, 30)
        self.checkbox_element.setGeometry(QtCore.QRect(630, 430, 30, 30))  # Checkbox element №
        self.button_save.setGeometry(QtCore.QRect(680, 540, 200, 50))
        self.button_select_file.setGeometry(QtCore.QRect(680, 490, 200, 50))
        self.img_frame.setGeometry(QtCore.QRect(10, 20, 413, 640))
        self.img_fone.setGeometry(QtCore.QRect(10, 20, 413, 640))
        self.label_box.setGeometry(QtCore.QRect(10, 10, 650, 180))
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 900, 20))
        self.tab_widget.setGeometry(QtCore.QRect(0, 0, 900, 750))
        self.label_statistics.setGeometry(QtCore.QRect(0, 0, 900, 750))
        self.button_create_card.setGeometry(QtCore.QRect(680, 590, 200, 90))
        self.button_create_files.setGeometry(QtCore.QRect(680, 490, 200, 90))
        self.scroll_area.setGeometry(QtCore.QRect(10, 200, 650, 475))
        self.button_photoshop.setGeometry(QtCore.QRect(680, 590, 200, 70))
        self.box_set_type.setGeometry(QtCore.QRect(680, 20, 200, 30))
        self.box_set_respect.setGeometry(QtCore.QRect(680, 70, 200, 30))
        self.draggable_label1.setGeometry(QtCore.QRect(206, 100, 140, 30))
        self.draggable_label2.setGeometry(QtCore.QRect(206, 150, 60, 30))
        self.label_element.setGeometry(QtCore.QRect(430, 430, 150, 30))
        self.box_font_number.setGeometry(680, 170, 200, 30)
        self.box_siize_text.setGeometry(680, 220, 200, 30)
        self.box_siize_number.setGeometry(680, 270, 200, 30)
        self.label_shadow_effect_text.setGeometry(430, 480, 300, 30)
        self.label_shadow_effect_number.setGeometry(430, 530, 250, 30)
        self.label_emboss_effect_text.setGeometry(430, 580, 250, 30)
        self.label_emboss_effect_number.setGeometry(430, 630, 250, 30)
        self.box_font_text.setGeometry(680, 120, 200, 30)
        self.draggable_label1.setGeometry(
            QtCore.QRect(206 - self.draggable_label1.width() // 2, 100, self.draggable_label1.width(),
                         self.draggable_label1.height()))
        self.draggable_label2.setGeometry(
            QtCore.QRect(206 - self.draggable_label2.width() // 2, 150, self.draggable_label2.width(),
                         self.draggable_label2.height()))

    @error_logger()
    def setup_set_trigerred(self, none=None):
        self.checkbox_emboss_effect_number.stateChanged.connect(self.toggleEmbossEffect2)
        self.checkbox_emboss_effect_text.stateChanged.connect(self.toggleEmbossEffect1)
        self.checkbox_shadow_effect_number.stateChanged.connect(self.toggleShadowEffect2)
        self.checkbox_shadow_effect_text.stateChanged.connect(self.toggleShadowEffect1)
        self.box_siize_number.currentTextChanged.connect(self.changeSize2)
        self.box_siize_text.currentTextChanged.connect(self.changeSize1)
        self.box_font_number.currentTextChanged.connect(self.changeFont2)
        self.box_font_text.currentTextChanged.connect(self.changeFont1)
        self.button_select_file.clicked.connect(self.select_file)
        self.action_help.triggered.connect(self.show_help)
        self.button_create_files.clicked.connect(self.create_files)
        self.button_create_card.clicked.connect(self.open_card_creation_dialog)
        self.tab_widget.currentChanged.connect(self.update_statistics)
        self.action_new_project.triggered.connect(self.new_project)
        self.action_about.triggered.connect(self.show_about)
        self.action_open_folder.triggered.connect(self.open_folder)
        self.button_select_file.clicked.connect(self.select_file)
        self.load_project_type()
        self.box_set_type.currentIndexChanged.connect(self.update_third_combo)
        self.checkbox_element.stateChanged.connect(self.update_text)
        self.widget_table.cellClicked.connect(self.on_cell_clicked)
        self.button_save.clicked.connect(self.save_settings)
        self.button_photoshop.clicked.connect(self.process_photoshop)

    @error_logger()
    def setup_other(self, MainWindow):
        # Tab widget settings
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tab_widget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_widget.setIconSize(QtCore.QSize(16, 16))
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(False)
        self.tab_widget.addTab(self.tab_statistics, "Statistics")
        self.tab_widget.addTab(self.tab_cards, "Cards")
        self.tab_widget.addTab(self.tab_photoshop, "Photoshop")
        self.tab_widget.setTabVisible(0, False)
        self.tab_widget.setTabVisible(1, False)
        self.tab_widget.setTabVisible(2, False)
        # Menus
        self.menu_menu.addAction(self.action_open_folder)
        self.menu_menu.addAction(self.menu_projects.menuAction())
        self.menu_menu.addSeparator()
        self.menu_menu.addAction(self.action_about)
        self.menu_bar.addAction(self.menu_menu.menuAction())
        self.menu_bar.addAction(self.action_help)
        # Add elements
        self.box_siize_text.addItems(["6", "8", "9", "10", "11", "12", "14", "18", "24", "30", "36", "48", "60", "72"])
        self.box_siize_number.addItems(
            ["6", "8", "9", "10", "11", "12", "14", "18", "24", "30", "36", "48", "60", "72"])
        self.box_font_text.addItems(["Arial"]+[f for f in QtGui.QFontDatabase().families()])
        self.box_font_number.addItems(["Arial"]+[f for f in QtGui.QFontDatabase().families()])
        self.img_fone.setPixmap(QtGui.QPixmap("A.png"))
        self.img_frame.setPixmap(QtGui.QPixmap("B.png"))

        # Set text
        self.button_create_card.setText("Create Cards")  # Змінюємо текст кнопки
        self.button_create_files.setText("Create Files")  # Змінюємо текст кнопки
        # Set cheked
        self.checkbox_element.setChecked(True)
        self.checkbox_shadow_effect_text.setChecked(False)
        self.checkbox_shadow_effect_text.setChecked(False)
        self.checkbox_emboss_effect_text.setChecked(False)
        self.checkbox_emboss_effect_number.setChecked(False)
        # Hide
        self.img_frame.hide()
        self.draggable_label2.hide()
        self.draggable_label1.hide()
        # Table
        self.widget_table.setColumnCount(5)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget_table)
        self.widget_table.setHorizontalHeaderLabels(["Number", "Name", "Description", "Type", "Respect"])
        # Timers
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(3000)

        self.timer1 = QtCore.QTimer()
        self.timer1.timeout.connect(self.update_statistics)
        self.timer1.start(3000)

        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.load_project_type)
        self.timer2.start(3000)
        # Projects
        self.project_buttons = []
        self.names = self.get_names_projects()
        if self.names is not None:
            for name in self.names:
                if not any(button.text() == name for button in self.project_buttons):
                    action = QtWidgets.QAction(MainWindow)
                    action.setObjectName(f"action_{name}")
                    action.setText(name)
                    action.setCheckable(True)
                    self.project_button_group.addAction(action)
                    action.triggered.connect(lambda _, name=name: self.select_project(name))
                    self.menu_projects.addAction(action)
                    self.project_buttons.append(action)
        self.menu_projects.addSeparator()
        self.menu_projects.addAction(self.action_new_project)

    # --- setupUi end ---
    # --- logic MainWindow start ---
    @error_logger()
    def show_about(self, none=None):
        msg_box = QMessageBox()
        msg_box.setFixedWidth(300)
        msg_box.setWindowTitle("About")
        msg_box.setText(ABOUT_MESSAGE)
        msg_box.exec_()

    @error_logger()
    def open_folder(self, none=None):
        # Вказати шлях до файлу
        file_path = os.path.abspath(__file__)

        # Отримати директорію файлу
        folder_path = os.path.dirname(file_path)

        # Відкрити директорію у файловому провіднику
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            os.system(f"open {folder_path}")
        else:
            os.system(f"xdg-open {folder_path}")

    @error_logger()
    def get_names_projects(self, none=None):
        with Session(engine) as session:
            with session.begin():
                projects = session.query(Projects).all()
                names = []
                if projects is None or projects == []:
                    return None
                for row in projects:
                    names.append(row.name)
                return names

    @error_logger()
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Card World Creator"))
        self.menu_menu.setTitle(_translate("MainWindow", "Menu"))
        self.menu_projects.setTitle(_translate("MainWindow", "Projects"))
        self.action_about.setText(_translate("MainWindow", "About"))
        self.action_open_folder.setText(_translate("MainWindow", "Open folder"))
        self.action_new_project.setText(_translate("MainWindow", "New project"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_statistics), _translate("MainWindow", "Statistics"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_cards), _translate("MainWindow", "Cards"))

    @error_logger()
    def show_help(self, none=None):
        help_text = HELP_MESSAGE
        help_window = QtWidgets.QMessageBox()
        help_window.setFixedWidth(300)
        help_window.setWindowTitle("Help")
        help_window.setText(help_text)
        help_window.setStandardButtons(QtWidgets.QMessageBox.Ok)
        help_window.exec_()

    @error_logger()
    def new_project(self, none=None):
        new_project_dialog = NewProjectDialog()
        new_project_dialog.setFixedWidth(300)
        if new_project_dialog.exec_() == QDialog.Accepted:
            name = new_project_dialog.name_edit.text()
            project_type = new_project_dialog.type_combo.currentText()
            self.create_project_directory(name, project_type)
            if project_type == "Viresets Card":
                project_type = "VC"
            else:
                project_type = "NC"
            action = QtWidgets.QAction(self.menu_bar)
            action.setObjectName(f"action_{name}")
            action.setText(name)
            action.setCheckable(True)
            action.triggered.connect(lambda _, n=name: self.select_project(n))
            self.menu_projects.insertAction(self.menu_projects.actions()[0], action)  # Додавання нових проектів зверху
            # Додаємо новий проект у базу даних
            dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projects")
            with Session(engine) as session:
                with session.begin():
                    new_project = Projects(name=name, type=project_type, folder=dir)
                    session.add(new_project)

            self.create_cards_for_project(name, project_type, new_project_dialog)

    @error_logger()
    def create_project_directory(self, name, project_type):
        if project_type == "Viresets Card":
            project_type = "VC"
            folders = ["alpha", "omega", "delta"]
        else:
            project_type = "NC"
            folders = ["ordinary", "special"]

        parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for folder in folders:
            project_directory = os.path.join(parent_directory, "projects", name, folder)
            if not os.path.exists(project_directory):
                os.makedirs(project_directory)

    @error_logger()
    def create_cards_for_project(self, nameq, project_type, dialog):
        selections = {}
        for label, combo in zip(dialog.option_labels, dialog.option_combos):
            selections[label.text()[:-1]] = combo.currentText()
        with Session(engine) as session:
            with session.begin():
                for option, sub_option in selections.items():
                    if project_type == "VC":
                        if sub_option != "None":
                            for row in range(0, int(sub_option)):
                                rar1, rar2 = self.get_rar_vc(row, int(sub_option), option.lower())
                                card = Cards(number=self.get_number(row), rarity_id=rar1, respect=1000 * rar2,
                                             type=option.lower(), project=nameq)
                                a = session.query(Frames).filter_by(project=nameq, type=option.lower(), respect=1000 * rar2).first()
                                if a is None or a == []:
                                    a1 = Frames(project=nameq, type=option.lower(), respect=1000 * rar2)
                                    session.add_all([card,a1])
                    else:
                        for row in range(0, int(sub_option)):
                            rar1, rar2 = self.get_rar_nc(row, int(sub_option), option.lower())
                            card = Cards(number=self.get_number(row), rarity_id=rar1, respect=1000 * rar2,
                                         type=option.lower(), project=nameq)
                            a = session.query(Frames).filter_by(project=nameq, type=option.lower(),
                                                                respect=1000 * rar2).first()
                            if a is None or a == []:
                                a1 = Frames(project=nameq, type=option.lower(), respect=1000 * rar2)
                                session.add_all([card, a1])


    @error_logger()
    def select_project(self, selected_project):
        for button in self.project_buttons:
            button.setChecked(False)
        for button in self.project_buttons:
            if button.text() == selected_project:
                button.setChecked(True)
                self.on_project_checked(selected_project)

    @error_logger()
    def get_rar_nc(self, number, numbers, type):
        q = {
            "ordinary": {
                "100": [33, 49, 64, 78, 90, 100],
                "200": [45, 83, 118, 150, 180, 200],
                "300": [80, 135, 185, 230, 270, 300],
            },
            "special": {
                "50": [13, 21, 28, 34, 39, 40, 50],
                "100": [35, 60, 73, 83, 88, 90, 100],
            }
        }
        w = q.get(f"{type}")
        w = w[f"{numbers}"]
        if type == "ordinary":
            if number in range(0, w[0]):
                rar1 = 1
            elif number in range(w[0], w[1]):
                rar1 = 2
            elif number in range(w[1], w[2]):
                rar1 = 3
            elif number in range(w[2], w[3]):
                rar1 = 4
            elif number in range(w[3], w[4]):
                rar1 = 5
            elif number in range(w[4], w[5]):
                rar1 = 6
            rar2 = rar1
        else:
            if number in range(0, w[0]):
                rar1 = 1
            elif number in range(w[0], w[1]):
                rar1 = 2
            elif number in range(w[1], w[2]):
                rar1 = 3
            elif number in range(w[2], w[3]):
                rar1 = 4
            elif number in range(w[3], w[4]):
                rar1 = 5
            elif number in range(w[4], w[5]):
                rar1 = 6
            elif number in range(w[5], w[6]):
                rar1 = 7
            rar2 = rar1 + 2
        return rar1, rar2

    @error_logger()
    def get_rar_vc(self, number, numbers, type):
        q = {
            "50": [15, 28, 38, 45, 50],
            "100": [30, 56, 76, 90, 100],
            "150": [45, 84, 114, 135, 150],
            "200": [60, 112, 152, 180, 200],
            "250": [75, 140, 190, 225, 250],
            "300": [90, 168, 228, 270, 300],
            "350": [105, 196, 266, 315, 350],
            "400": [120, 224, 304, 360, 400],
            "450": [135, 252, 342, 405, 450],
        }
        w = q[str(numbers)]
        if number in range(0, w[0]):
            rar1 = 1
        elif number in range(w[0], w[1]):
            rar1 = 2
        elif number in range(w[1], w[2]):
            rar1 = 3
        elif number in range(w[2], w[3]):
            rar1 = 4
        elif number in range(w[3], w[4]):
            rar1 = 5
        rar2 = rar1
        if type == "omega":
            rar2 += 3
        elif type == "delta":
            rar2 += 6
        return rar1, rar2

    @error_logger()
    def get_number(self, num):
        num += 1
        if len(str(num)) == 1:
            num = f"00{num}"
        elif len(str(num)) == 2:
            num = f"0{num}"
        return num

    @error_logger()
    def show_ready_message(self, project_name):
        msg_box = QMessageBox()
        msg_box.setFixedWidth(300)

        msg_box.setWindowTitle("Ready")
        msg_box.setText(f"Selected project: {project_name}")

        timer = QTimer()
        timer.timeout.connect(msg_box.close)
        timer.start(3000)  # 5000 мс = 5 секунд

        msg_box.exec_()

    @error_logger()
    def on_project_checked(self, project_name):
        with Session(engine) as session:
            with session.begin():
                thisproject = session.query(ThisProject).first()
                thisproject.name = str(project_name)
                self.update_statistics()
                self.tab_widget.setTabVisible(0, True)
                self.tab_widget.setTabVisible(1, True)
                self.tab_widget.setTabVisible(2, True)
                self.show_ready_message(project_name)
                self.load_project_type()

    # --- logic MainWindow end ---
    # --- logic Statistics Tab start ---
    @error_logger()
    def update_statistics(self, none=None):
        self.label_statistics.setText(self.stat())

    @error_logger()
    def stat(self, none=None):
        with Session(engine) as session:
            with session.begin():
                this_project = session.query(ThisProject).first()
                if this_project.name is None:
                    return "The project is not selected"
                project = session.query(Projects).filter_by(name=this_project.name).first()
                r = session.query(Cards).filter_by(full=True, project=project.name).all()
                text = (f"Card created: {len(r)}\n"
                        f"\n"
                        f"You still need to make cards:\n")
                if project.type == "VC":
                    ra = session.query(Cards).filter_by(type="alpha", full=False, project=project.name).all()
                    r1a = session.query(Cards).filter_by(rarity_id=1, type="alpha", full=False,
                                                         project=project.name).all()
                    r2a = session.query(Cards).filter_by(rarity_id=2, type="alpha", full=False,
                                                         project=project.name).all()
                    r3a = session.query(Cards).filter_by(rarity_id=3, type="alpha", full=False,
                                                         project=project.name).all()
                    r4a = session.query(Cards).filter_by(rarity_id=4, type="alpha", full=False,
                                                         project=project.name).all()
                    r5a = session.query(Cards).filter_by(rarity_id=5, type="alpha", full=False,
                                                         project=project.name).all()
                    ro = session.query(Cards).filter_by(type="omega", full=False, project=project.name).all()
                    r1o = session.query(Cards).filter_by(rarity_id=1, type="omega", full=False,
                                                         project=project.name).all()
                    r2o = session.query(Cards).filter_by(rarity_id=2, type="omega", full=False,
                                                         project=project.name).all()
                    r3o = session.query(Cards).filter_by(rarity_id=3, type="omega", full=False,
                                                         project=project.name).all()
                    r4o = session.query(Cards).filter_by(rarity_id=4, type="omega", full=False,
                                                         project=project.name).all()
                    r5o = session.query(Cards).filter_by(rarity_id=5, type="omega", full=False,
                                                         project=project.name).all()
                    rd = session.query(Cards).filter_by(type="delta", full=False, project=project.name).all()
                    r1d = session.query(Cards).filter_by(rarity_id=1, type="delta", full=False,
                                                         project=project.name).all()
                    r2d = session.query(Cards).filter_by(rarity_id=2, type="delta", full=False,
                                                         project=project.name).all()
                    r3d = session.query(Cards).filter_by(rarity_id=3, type="delta", full=False,
                                                         project=project.name).all()
                    r4d = session.query(Cards).filter_by(rarity_id=4, type="delta", full=False,
                                                         project=project.name).all()
                    r5d = session.query(Cards).filter_by(rarity_id=5, type="delta", full=False,
                                                         project=project.name).all()
                    if ra is None or ra == []:
                        text += f" Alpha: None\n"
                    else:
                        text += (f" Alpha: {len(ra)}\n"
                                 f" - Ordinary: {len(r1a)}\n"
                                 f" - Rare: {len(r2a)}\n"
                                 f" - Epic: {len(r3a)}\n"
                                 f" - Legendary: {len(r4a)}\n"
                                 f" - Mythical: {len(r5a)}\n")
                    if ro is None or ro == []:
                        text += f" Omega: None\n"
                    else:
                        text += (f" Omega: {len(ro)}\n"
                                 f" - Ordinary: {len(r1o)}\n"
                                 f" - Rare: {len(r2o)}\n"
                                 f" - Epic: {len(r3o)}\n"
                                 f" - Legendary: {len(r4o)}\n"
                                 f" - Mythical: {len(r5o)}\n")
                    if rd is None or rd == []:
                        text += f" Delta: None\n"
                    else:
                        text += (f" Delta: {len(rd)}\n"
                                 f" - Ordinary: {len(r1d)}\n"
                                 f" - Rare: {len(r2d)}\n"
                                 f" - Epic: {len(r3d)}\n"
                                 f" - Legendary: {len(r4d)}\n"
                                 f" - Mythical: {len(r5d)}\n")
                else:
                    ro = session.query(Cards).filter_by(type="ordinary", full=False, project=project.name).all()
                    r1o = session.query(Cards).filter_by(rarity_id=1, type="ordinary", full=False,
                                                         project=project.name).all()
                    r2o = session.query(Cards).filter_by(rarity_id=2, type="ordinary", full=False,
                                                         project=project.name).all()
                    r3o = session.query(Cards).filter_by(rarity_id=3, type="ordinary", full=False,
                                                         project=project.name).all()
                    r4o = session.query(Cards).filter_by(rarity_id=4, type="ordinary", full=False,
                                                         project=project.name).all()
                    r5o = session.query(Cards).filter_by(rarity_id=5, type="ordinary", full=False,
                                                         project=project.name).all()
                    r6o = session.query(Cards).filter_by(rarity_id=6, type="ordinary", full=False,
                                                         project=project.name).all()
                    rs = session.query(Cards).filter_by(type="special", full=False, project=project.name).all()
                    r1s = session.query(Cards).filter_by(rarity_id=1, type="special", full=False
                                                         , project=project.name).all()
                    r2s = session.query(Cards).filter_by(rarity_id=2, type="special", full=False
                                                         , project=project.name).all()
                    r3s = session.query(Cards).filter_by(rarity_id=3, type="special", full=False
                                                         , project=project.name).all()
                    r4s = session.query(Cards).filter_by(rarity_id=4, type="special", full=False
                                                         , project=project.name).all()
                    r5s = session.query(Cards).filter_by(rarity_id=5, type="special", full=False
                                                         , project=project.name).all()
                    r6s = session.query(Cards).filter_by(rarity_id=6, type="special", full=False
                                                         , project=project.name).all()
                    r7s = session.query(Cards).filter_by(rarity_id=7, type="special", full=False
                                                         , project=project.name).all()

                    text += (f" Ordinary: {len(ro)}\n"
                             f" - Ordinary - 1000: {len(r1o)}\n"
                             f" - Unusual - 2000: {len(r2o)}\n"
                             f" - Rare - 3000: {len(r3o)}\n"
                             f" - Legendary - 4000: {len(r4o)}\n"
                             f" - Mythical - 5000: {len(r5o)}\n"
                             f" - Divine - 6000: {len(r6o)}\n"
                             f" Special: {len(rs)}\n"
                             f" - Ordinary - 3000: {len(r1s)}\n"
                             f" - Unusual - 4000: {len(r2s)}\n"
                             f" - Rare - 5000: {len(r3s)}\n"
                             f" - Legendary - 6000: {len(r4s)}\n"
                             f" - Mythical - 7000: {len(r5s)}\n"
                             f" - Mythical - 8000: {len(r6s)}\n"
                             f" - Divine - 9000: {len(r7s)}\n")
        return text
    # --- logic Statistics Tab end ---
    # --- logic Cards Tab start ---
    @error_logger()
    def create_files(self, none=None):
        with Session(engine) as session:
            with session.begin():
                thisproject = session.query(ThisProject).first()
                project = session.query(Projects).filter_by(name=thisproject.name).first()
                if project.type == "VC":
                    a_cards = session.query(Cards).filter_by(type="alpha", full=True, project=project.name).all()
                    o_cards = session.query(Cards).filter_by(type="omega", full=True, project=project.name).all()
                    d_cards = session.query(Cards).filter_by(type="delta", full=True, project=project.name).all()

                    total_steps = len(a_cards) + len(o_cards) + len(d_cards)
                    progress_dialog = ProgressDialog(total_steps)
                    progress_dialog.show()

                    current_step = 0
                    a_text = ""
                    o_text = ""
                    d_text = ""

                    for a in a_cards:
                        a_eng = self.translate_to_english(a.name, detect(a.name))
                        a_text += (f"{a.number}\n"
                                   f"{a.name}\n"
                                   f"{a_eng.upper().replace(' ', '_')}\n"
                                   f"{a.description}\n")
                        current_step += 1
                        progress_dialog.update_progress(current_step)

                    for o in o_cards:
                        o_eng = self.translate_to_english(o.name, detect(o.name))
                        o_text += (f"{o.number}\n"
                                   f"{o.name}\n"
                                   f"{o_eng.upper().replace(' ', '_')}\n"
                                   f"{o.description}\n")
                        current_step += 1
                        progress_dialog.update_progress(current_step)

                    for d in d_cards:
                        d_eng = self.translate_to_english(d.name, detect(d.name))
                        d_text += (f"{d.number}\n"
                                   f"{d.name}\n"
                                   f"{d_eng.upper().replace(' ', '_')}\n"
                                   f"{d.description}\n")
                        current_step += 1
                        progress_dialog.update_progress(current_step)

                    with open(f"{project.folder}/{project.name}/alpha.txt", 'w', encoding='utf-8') as file:
                        file.write(a_text)
                    with open(f"{project.folder}/{project.name}/omega.txt", 'w', encoding='utf-8') as file:
                        file.write(o_text)
                    with open(f"{project.folder}/{project.name}/delta.txt", 'w', encoding='utf-8') as file:
                        file.write(d_text)

                    progress_dialog.close()
                else:
                    o_cards = session.query(Cards).filter_by(type="ordinary", full=True, project=project.name).all()
                    s_cards = session.query(Cards).filter_by(type="special", full=True, project=project.name).all()

                    total_steps = len(o_cards) + len(s_cards)
                    progress_dialog = ProgressDialog(total_steps)
                    progress_dialog.show()

                    current_step = 0
                    o_text = ""
                    s_text = ""

                    for o in o_cards:
                        o_text += (f"{o.number} "
                                   f"{o.name}\n"
                                   f"{o.description}\n")
                        current_step += 1
                        progress_dialog.update_progress(current_step)

                    for s in s_cards:
                        s_text += (f"{s.number} "
                                   f"{s.name}\n"
                                   f"{s.description}\n")
                        current_step += 1
                        progress_dialog.update_progress(current_step)

                    with open(f"{project.folder}/{project.name}/ordinary.txt", 'w', encoding='utf-8') as file:
                        file.write(o_text)
                    with open(f"{project.folder}/{project.name}/special.txt", 'w', encoding='utf-8') as file:
                        file.write(s_text)


                    progress_dialog.close()

    @error_logger()
    def translate_to_english(self, text, source_language):
        translator = Translator(from_lang=source_language, to_lang="en")
        translated_text = translator.translate(text)
        return translated_text


    @error_logger()
    def on_cell_clicked(self, row, column):
        item = self.widget_table.item(row, column)
        if item:
            text = item.text()
            self.label_box.setText(text)

    @error_logger()
    def update_table(self, none=None):
        with Session(engine) as session:
                with session.begin():
                    thisproject = session.query(ThisProject).first()
                    if thisproject.name is None:
                        pass
                    else:
                        if not thisproject:
                            raise Exception("No current project found.")

                        project = session.query(Projects).filter_by(name=thisproject.name).first()
                        if not project:
                            raise Exception(f"No project found with name {thisproject.name}.")

                        # Отримання даних з бази даних
                        cards = session.query(Cards).filter_by(project=project.name).all()

                        # Очищення таблиці перед оновленням
                        self.widget_table.setRowCount(0)

                        for row_number, card in enumerate(cards):
                            self.widget_table.insertRow(row_number)
                            self.widget_table.setItem(row_number, 0, QTableWidgetItem(str(card.number)))
                            self.widget_table.setItem(row_number, 1, QTableWidgetItem(card.name))
                            self.widget_table.setItem(row_number, 2, QTableWidgetItem(card.description))
                            self.widget_table.setItem(row_number, 3, QTableWidgetItem(card.type))
                            self.widget_table.setItem(row_number, 4, QTableWidgetItem(str(card.respect)))


    @error_logger()
    def open_card_creation_dialog(self, none=None):
        with Session(engine) as session:
                with session.begin():
                    thisproject = session.query(ThisProject).first()
                    if not thisproject:
                        raise Exception("No current project found.")

                    project = session.query(Projects).filter_by(name=thisproject.name).first()
                    if not project:
                        raise Exception(f"No project found with name {thisproject.name}.")

                    dialog = CardCreationDialog(project.type, self.tab_cards)
                    dialog.exec_()

    # --- logic Cards Tab end ---
    # --- logic Photoshop Tab start ---
    @error_logger()
    def process_photoshop(self, none=None):
        with Session(engine) as session:
                with session.begin():
                    this_project = session.query(ThisProject).first()
                    cards = session.query(Cards).filter_by(project=this_project.name, full=True).all()
                    total_steps = len(cards)
                    progress_dialog = ProgressDialog(total_steps)
                    progress_dialog.show()

                    current_step = 0
                    for card in cards:
                        if card:
                            frame = session.query(Frames).filter_by(
                                project=this_project.name,
                                type=card.type,
                                respect=card.respect
                            ).first()
                            if frame:
                                name = self.translate_to_english(card.name, detect(card.name)).upper()
                                main_image_path = f'projects/{this_project.name}/{card.type}/{card.number}.png'
                                main_pixmap = QPixmap(main_image_path)
                                if not main_pixmap.isNull():
                                    frame_pixmap = QPixmap(frame.folder)
                                    if not frame_pixmap.isNull():
                                        painter = QPainter(main_pixmap)
                                        painter.drawPixmap(0, 0, frame_pixmap)

                                        # Налаштування шрифту для тексту
                                        painter.setFont(QFont(frame.font_text, frame.font_text_size))
                                        painter.setPen(QColor(frame.color_text))

                                        if frame.shadow_text:
                                            shadow_effect = QGraphicsDropShadowEffect()
                                            shadow_effect.setBlurRadius(10)
                                            shadow_effect.setColor(QColor('black'))
                                            shadow_effect.setOffset(5, 5)
                                            painter.begin(self.img_frame)
                                            painter.setGraphicsEffect(shadow_effect)

                                        if frame.embossing_text:
                                            # Відтінок для тиснення
                                            light_color = QColor('white')
                                            dark_color = QColor('gray')

                                            # Малювання темної тіні (вниз і вправо)
                                            painter.setPen(dark_color)
                                            dark_text_rect = painter.boundingRect(0, 0, 0, 0, Qt.AlignCenter, name)
                                            dark_text_rect.moveCenter(QtCore.QPoint(frame.x_text + 2, frame.y_text + 2))
                                            painter.drawText(dark_text_rect, Qt.AlignCenter, name)

                                            # Малювання світлої тіні (вгору і вліво)
                                            painter.setPen(light_color)
                                            light_text_rect = painter.boundingRect(0, 0, 0, 0, Qt.AlignCenter, name)
                                            light_text_rect.moveCenter(
                                                QtCore.QPoint(frame.x_text - 2, frame.y_text - 2))
                                            painter.drawText(light_text_rect, Qt.AlignCenter, name)

                                            # Встановлення кольору основного тексту
                                        painter.setPen(QColor(frame.color_text))
                                        text_rect = painter.boundingRect(0, 0, 0, 0, Qt.AlignCenter, name)
                                        text_rect.moveCenter(QtCore.QPoint(frame.x_text, frame.y_text))
                                        painter.drawText(text_rect, Qt.AlignCenter, name)

                                        # Налаштування шрифту для номера
                                        painter.setFont(QFont(frame.font_num, frame.font_num_size))
                                        painter.setPen(QColor(frame.color_num))
                                        num_text = f"№{card.number}" if frame.element_mumber else card.number
                                        if frame.shadow_num:
                                            shadow_effect = QGraphicsDropShadowEffect()
                                            shadow_effect.setBlurRadius(10)
                                            shadow_effect.setColor(QColor('black'))
                                            shadow_effect.setOffset(5, 5)
                                            painter.begin(self.img_frame)
                                            painter.setGraphicsEffect(shadow_effect)

                                        if frame.embossing_num:
                                            # Відтінок для тиснення
                                            light_color = QColor('white')
                                            dark_color = QColor('gray')

                                            # Малювання темної тіні (вниз і вправо)
                                            painter.setPen(dark_color)
                                            dark_num_rect = painter.boundingRect(0, 0, 0, 0, Qt.AlignCenter, num_text)
                                            dark_num_rect.moveCenter(QtCore.QPoint(frame.x_num + 2, frame.y_num + 2))
                                            painter.drawText(dark_num_rect, Qt.AlignCenter, num_text)

                                            # Малювання світлої тіні (вгору і вліво)
                                            painter.setPen(light_color)
                                            light_num_rect = painter.boundingRect(0, 0, 0, 0, Qt.AlignCenter, num_text)
                                            light_num_rect.moveCenter(QtCore.QPoint(frame.x_num - 2, frame.y_num - 2))
                                            painter.drawText(light_num_rect, Qt.AlignCenter, num_text)

                                            # Встановлення кольору основного номера
                                        painter.setPen(QColor(frame.color_num))
                                        num_rect = painter.boundingRect(0, 0, 0, 0, Qt.AlignCenter, num_text)
                                        num_rect.moveCenter(QtCore.QPoint(frame.x_num, frame.y_num))
                                        painter.drawText(num_rect, Qt.AlignCenter, num_text)
                                        painter.end()

                                        save_path = os.path.join(f"projects/{this_project.name}",
                                                                 f"{card.number}_{name.replace(' ', '_')}_{card.respect}.png")
                                        main_pixmap.save(save_path, "PNG")
                                    else:
                                        QMessageBox.critical(None, "Error", "Frame image not found.")
                                        progress_dialog.close()
                                        break
                                else:
                                    QMessageBox.critical(None, "Error", "Main image not found.")
                                    progress_dialog.close()
                                    break
                            else:
                                QMessageBox.critical(None, "Error", "No matching frame found.")
                                progress_dialog.close()
                                break
                        else:
                            QMessageBox.critical(None, "Error", "No matching card found.")
                            progress_dialog.close()
                            break
                        current_step += 1
                        progress_dialog.update_progress(current_step)
                    progress_dialog.close()


    @error_logger()
    def save_settings(self, none=None):
        with Session(engine) as session:
            with session.begin():
                center_x_label1 = self.draggable_label1.x() + (self.draggable_label1.width() // 2)
                center_y_label1 = self.draggable_label1.y() + (self.draggable_label1.height() // 2)

                center_x_label2 = self.draggable_label2.x() + (self.draggable_label2.width() // 2)
                center_y_label2 = self.draggable_label2.y() + (self.draggable_label2.height() // 2)
                this_project = session.query(ThisProject).first().name
                frame = session.query(Frames).filter_by(project=this_project, type=self.box_set_type.currentText(),
                                                        respect=self.box_set_respect.currentText()).first()
                frame.x_text = (center_x_label1 - 10) * 2
                frame.y_text = (center_y_label1 - 20) * 2
                frame.x_num = (center_x_label2 - 10) * 2
                frame.y_num = (center_y_label2 - 20) * 2
                frame.font_num = self.box_font_number.currentText()
                frame.font_text = self.box_font_text.currentText()
                frame.embossing_text = self.checkbox_emboss_effect_text.isChecked()
                frame.shadow_text = self.checkbox_shadow_effect_text.isChecked()
                frame.embossing_num = self.checkbox_emboss_effect_number.isChecked()
                frame.shadow_num = self.checkbox_shadow_effect_number.isChecked()
                frame.element_mumber = self.checkbox_element.isChecked()
                frame.font_num_size = int(self.box_siize_number.currentText()) * 2
                frame.font_text_size = int(self.box_siize_text.currentText()) * 2
                frame.folder = self.folder
                color_text = self.draggable_label1.palette().color(QtGui.QPalette.WindowText).name()
                color_num = self.draggable_label2.palette().color(QtGui.QPalette.WindowText).name()
                frame.color_text = color_text
                frame.color_num = color_num

    @error_logger()
    def toggleEmbossEffect1(self, state):
        if state == QtCore.Qt.Checked:
            self.draggable_label1.emboss_effect = True
        else:
            self.draggable_label1.emboss_effect = False
        self.draggable_label1.update()

    @error_logger()
    def toggleEmbossEffect2(self, state):
        if state == QtCore.Qt.Checked:
            self.draggable_label2.emboss_effect = True
        else:
            self.draggable_label2.emboss_effect = False
        self.draggable_label2.update()

    @error_logger()
    def toggleShadowEffect1(self, state):
        if state == QtCore.Qt.Checked:
            shadow = QtWidgets.QGraphicsDropShadowEffect(self.draggable_label1)
            shadow.setBlurRadius(20)
            shadow.setXOffset(5)
            shadow.setYOffset(5)
            shadow.setColor(QtGui.QColor(0, 0, 0, 200))
            self.draggable_label1.setGraphicsEffect(shadow)
        else:
            self.draggable_label1.setGraphicsEffect(None)


    @error_logger()
    def toggleShadowEffect2(self, state):
        if state == QtCore.Qt.Checked:
            shadow = QtWidgets.QGraphicsDropShadowEffect(self.draggable_label2)
            shadow.setBlurRadius(20)
            shadow.setXOffset(5)
            shadow.setYOffset(5)
            shadow.setColor(QtGui.QColor(0, 0, 0, 200))
            self.draggable_label2.setGraphicsEffect(shadow)
        else:
            self.draggable_label2.setGraphicsEffect(None)


    @error_logger()
    def changeFont1(self, none=None):
        current_color = self.draggable_label1.palette().color(QtGui.QPalette.WindowText).name()
        current_size = self.draggable_label1.font().pixelSize()
        self.draggable_label1.setStyleSheet(f'''
            QLabel {{
                font-family: "{self.box_font_text.currentText()}";
                color : "{current_color}";
                font-size : "{current_size}";
            }}
        ''')
        self.draggable_label1.adjustSize()


    @error_logger()
    def changeFont2(self, none=None):
        current_color = self.draggable_label2.palette().color(QtGui.QPalette.WindowText).name()
        current_size = self.draggable_label2.font().pixelSize()
        self.draggable_label2.setStyleSheet(f'''
            QLabel {{
                font-family: "{self.box_font_number.currentText()}";
                color : "{current_color}";
                font-size : "{current_size}";
            }}
        ''')
        self.draggable_label2.adjustSize()


    @error_logger()
    def changeSize1(self, none=None):
        current_color = self.draggable_label1.palette().color(QtGui.QPalette.WindowText).name()
        current_font = self.draggable_label1.font().family()
        font_size = self.box_siize_text.currentText()
        self.draggable_label1.setStyleSheet(f'''
            QLabel {{
                font-family: "{current_font}";
                font-size: {font_size}px;
                color: {current_color};                }}
        ''')
        self.draggable_label1.adjustSize()


    @error_logger()
    def changeSize2(self, none=None):
        current_color = self.draggable_label2.palette().color(QtGui.QPalette.WindowText).name()
        current_font = self.draggable_label2.font().family()
        font_size = self.box_siize_number.currentText()
        self.draggable_label2.setStyleSheet(f'''
            QLabel {{
                font-family: "{current_font}";
                font-size: {font_size}px;
                color: {current_color};
            }}
        ''')
        self.draggable_label2.adjustSize()


    @error_logger()
    def update_text(self, none=None):
        if self.checkbox_element.isChecked():
            self.draggable_label2.setText("№000")
        else:
            self.draggable_label2.setText("000")

    @error_logger()
    def load_project_type(self, none=None):
        try:
            with Session(engine) as session:
                with session.begin():
                    t = session.query(ThisProject).first()
                    q = session.query(Projects).filter_by(name=t.name).first()
                    type_project = q.type
                    if type_project == "VC" and [self.box_set_type.itemText(i) for i in
                                                 range(self.box_set_type.count())] != ["alpha", "omega", "delta"]:
                        self.box_set_type.clear()
                        self.box_set_type.addItems(["alpha", "omega", "delta"])
                    elif type_project == "NC" and [self.box_set_type.itemText(i) for i in
                                                   range(self.box_set_type.count())] != ["ordinary", "special"]:
                        self.box_set_type.clear()
                        self.box_set_type.addItems(["ordinary", "special"])
                    self.update_third_combo()
        except AttributeError:
            pass


    @error_logger()
    def update_third_combo(self, none=None):
        self.box_set_respect.clear()
        subtype = self.box_set_type.currentText()
        if subtype == "alpha":
            self.box_set_respect.addItems(["1000", "2000", "3000", "4000", "5000"])
        elif subtype == "omega":
            self.box_set_respect.addItems(["4000", "5000", "6000", "7000", "8000"])
        elif subtype == "delta":
            self.box_set_respect.addItems(["7000", "8000", "9000", "10000", "11000"])
        elif subtype == "ordinary":
            self.box_set_respect.addItems(["1000", "2000", "3000", "4000", "5000", "6000"])
        elif subtype == "special":
            self.box_set_respect.addItems(["3000", "4000", "5000", "6000", "7000", "8000", "9000"])

    @error_logger()
    def select_file(self, none=None):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Select File", "", "PNG Files (*.png);;All Files (*)",
                                                   options=options)
        if file_name:
            pixmap = QtGui.QPixmap(file_name)
            if pixmap.width() == 825 and pixmap.height() == 1280:
                self.replase_image(file_name)
                self.img_frame.setPixmap(pixmap.scaled(413, 640, QtCore.Qt.KeepAspectRatio))
                self.img_frame.show()
                self.draggable_label1.show()
                self.draggable_label2.show()
                with Session(engine) as session:
                    with session.begin():
                        this_project = session.query(ThisProject).first().name
                        frame = session.query(Frames).filter_by(project=this_project,
                                                                type=self.box_set_type.currentText(),
                                                                respect=self.box_set_respect.currentText()).first()
                        frame.folder = file_name
                self.folder = file_name
            else:
                QMessageBox.critical(None, "Error", "The image dimensions must be 825x1280 pixels.")

    @error_logger()
    def replase_image(self, i):
        img = Image.open(i)
        output_size = (413, 640)
        img.thumbnail(output_size)
        img.save("B.png")
    # --- logic Photoshop Tab end ---