__author__ = "Leland Green"
__version__ = "0.1.1"
__date_created__ = "2025-01-28"
__last_updated__ = "2025-01-29"
__email__ = "lelandgreenproductions@gmail.com"

__license__ = "Open Source" # License of this script is free for all purposes.
# At least early versions. Branch, clone, copy, download when ready.
# Just do not mutilate. If you must, always use your own bytes for that. :)
f"""
Utilities using opencv for edge detection in a GUI
---

Author: {__author__}
Version: {__version__}
Date: {__date_created__}
Last Updated: {__last_updated__}
Email: {__email__}

Requirements:
- Python 3.8 or newer
- tkinter (standard library)
- zipfile (standard library)

Install Python modules using `pip install -r python_requirements`

How to Run:
Run this script using the command `python MainWindow_ImageProcessing.py`.

License:
{__license__}

"""

# Yes. We do need this:
debug = True # Set to False to disable debug messages

import logging
import configparser
import logging
import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QSlider,
    QPushButton, QWidget, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

from edge_detection import detect_edges
import cv2

# Config file path
CONFIG_FILE_PATH = "config.ini"


# Ensure configuration file exists with default settings
def initialize_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE_PATH):
        # Create default config.ini
        config["Settings"] = {
            "last_used_image": ""
        }
        with open(CONFIG_FILE_PATH, "w") as configfile:
            config.write(configfile)
    return config


class MainWindow_ImageProcessing(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_pixmap = None
        self.edge_thickness = 2  # Default line thickness
        self.image_path = None  # To hold the currently loaded image path
        self.processed_image = None

        self.setWindowTitle("3D Image Enhancer")
        self.setGeometry(100, 100, 1280, 720)

        # Initialize configuration
        self.config = initialize_config()
        self._load_config()

        self._init_ui()
        self.load_last_used_image()

    def _init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout and Controls
        main_layout = QVBoxLayout()
        image_slider_layout = QVBoxLayout()  # For images and controls
        image_preview_layout = QHBoxLayout()  # To hold original and processed previews
        bottom_controls = QHBoxLayout()

        # Drag-and-Drop Label
        self.drag_drop_label = QLabel("Drag and Drop Images Here")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setFixedHeight(200)
        self.drag_drop_label.setStyleSheet("border: 2px dashed gray; background: #eee;")
        self.drag_drop_label.dragEnterEvent = self.drag_enter_event
        self.drag_drop_label.dropEvent = self.drop_event
        main_layout.addWidget(self.drag_drop_label)

        # Original Image Preview
        self.original_label = QLabel("Original Image")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setStyleSheet("background-color: lightgray;")
        self.original_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_preview_layout.addWidget(self.original_label)

        # Processed Image Preview
        self.preview_label = QLabel("Processed Image")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: lightgray;")
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_preview_layout.addWidget(self.preview_label)

        # Add images to the layout
        image_slider_layout.addLayout(image_preview_layout)

        # Slider for Sensitivity
        slider_label = QLabel("Edge Detection Sensitivity")
        slider_label.setAlignment(Qt.AlignCenter)
        image_slider_layout.addWidget(slider_label)

        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(10)
        self.sensitivity_slider.setMaximum(150)
        self.sensitivity_slider.setValue(50)
        self.sensitivity_slider.valueChanged.connect(self.update_preview)
        image_slider_layout.addWidget(self.sensitivity_slider)

        # Slider for Line Thickness
        line_thickness_label = QLabel("Line Thickness")
        line_thickness_label.setAlignment(Qt.AlignCenter)
        image_slider_layout.addWidget(line_thickness_label)

        self.line_thickness_slider = QSlider(Qt.Horizontal)
        self.line_thickness_slider.setMinimum(1)
        self.line_thickness_slider.setMaximum(10)
        self.line_thickness_slider.setValue(3)
        self.line_thickness_slider.valueChanged.connect(self.update_line_thickness)
        image_slider_layout.addWidget(self.line_thickness_slider)

        # Add controls and buttons
        main_layout.addLayout(image_slider_layout)

        # Buttons for Load, Process, and Save
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        bottom_controls.addWidget(self.load_button)

        self.process_button = QPushButton("Process Image")
        self.process_button.clicked.connect(self.process_image)
        bottom_controls.addWidget(self.process_button)

        self.save_button = QPushButton("Save Processed Image")
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        bottom_controls.addWidget(self.save_button)

        main_layout.addLayout(bottom_controls)
        self.central_widget.setLayout(main_layout)

    def update_line_thickness(self):
        self.edge_thickness = self.line_thickness_slider.value()
        self.update_preview()

    def update_preview(self):
        if not self.image_path:  # No image to process
            return
        try:
            low_threshold = self.sensitivity_slider.value()
            self.processed_image = detect_edges(self.image_path, low_threshold, low_threshold * 3,
                                                thickness=self.edge_thickness)
            self.display_processed_image()
        except Exception as e:
            self.show_error(str(e))

    def display_processed_image(self):
        if self.processed_image is not None:
            height, width = self.processed_image.shape
            bytes_per_line = width
            q_img = QImage(
                self.processed_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8
            )
            self.preview_label.setPixmap(
                QPixmap.fromImage(q_img).scaled(
                    self.preview_label.width(), self.preview_label.height(),
                    Qt.KeepAspectRatio
                )
            )

    ### Drag-and-Drop Handling ###
    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def drop_event(self, event):
        event.setDropAction(Qt.CopyAction)
        event.accept()
        for url in event.mimeData().urls():
            self.image_path = url.toLocalFile()
            self.load_image(self.image_path)

    def load_image(self, path=None):
        if not path:
            options = QFileDialog.Options()
            path, _ = QFileDialog.getOpenFileName(
                self, "Load Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
            )
            if not path:
                return

        self.image_path = path
        self._update_config("Settings", "last_used_image", path)

        self.image = cv2.imread(path)
        if self.image is None:
            self.show_error("Failed to load image.")
            return
        self.display_original_image()
        self.update_preview()

    def display_original_image(self):
        if self.image is not None:
            height, width, channel = self.image.shape
            q_img = QImage(self.image.data, width, height, width * 3, QImage.Format_RGB888).rgbSwapped()
            self.original_pixmap = QPixmap.fromImage(q_img)
            self.original_label.setPixmap(
                self.original_pixmap.scaled(
                    self.original_label.width(), self.original_label.height(),
                    Qt.KeepAspectRatio
                )
            )

    def process_image(self):
        if not self.image_path:
            self.show_error("Please load an image first!")
            return
        self.update_preview()
        self.save_button.setEnabled(True)

    def save_image(self):
        if not self.processed_image.any():
            self.show_error("No processed image to save.")
            return
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Processed Image", "", "Images (*.png *.jpg *.bmp)", options=options)
        if save_path:
            cv2.imwrite(save_path, self.processed_image, [cv2.IMWRITE_PNG_COMPRESSION, 9])

    def show_error(self, message):
        print(f"Error: {message}")

    def load_last_used_image(self):
        last_image_path = self.config.get("Settings", "last_used_image", fallback="")
        if last_image_path and os.path.exists(last_image_path):
            self.load_image(last_image_path)

    def _load_config(self):
        self.config.read(CONFIG_FILE_PATH)

    def _update_config(self, section, option, value):
        self.config.set(section, option, value)
        with open(CONFIG_FILE_PATH, "w") as configfile:
            self.config.write(configfile)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow_ImageProcessing()
    main_window.show()
    sys.exit(app.exec_())