
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np
import pandas as pd
import plotnine as gg
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QWidget,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
)

from chessproc.ChessPlotterColourScheme import ChessPlotterColourScheme as cpcs


# Element dimension constants
XPOS = 100
YPOS = 100
WIN_WIDTH = 725
WIN_HEIGHT = 725

BUTTON_HEIGHT = 30
BUTTON_WIDTH = 60
GAMES_WIDTH = 150
COMBO_HEIGHT = 30
COMBO_WIDTH = 250


class ChessPlotterView(QMainWindow):

    """
    Main window of application
    """

    def __init__(self) -> None:
        super().__init__(parent = None)
        self.setWindowTitle('ChessPlotter')
        self.setGeometry(XPOS, YPOS, WIN_WIDTH, WIN_HEIGHT)
        self.setMinimumHeight(500)
        self.setStyleSheet(f"background-color: {cpcs.background}; color: {cpcs.white}")

        # Create central widget and central layout, assign layout to widget
        cWidget = QWidget(self)
        self.centralLayout = QVBoxLayout()
        cWidget.setLayout(self.centralLayout)
        self.setCentralWidget(cWidget)

        # Create the filtering and controls
        self.add_user_select()

        # Create the plot inputs
        self.add_plot_inputs()

        # Create the plot selection
        self.add_plot_select()

        # Create the plot area
        self.add_canvas()

        # Set up the add user dialog
        self.adduser = AddUserPopUp(self)

        # Set up the filesave dialog
        self.file_save = FileSaveDialog(self)

        # Show all the widgets
        self.show()
    
    def add_user_select(self):
        """Create controls for plot"""
        # Set up layout
        self.userLayout = QHBoxLayout()
        self.centralLayout.addLayout(self.userLayout)

        # Create controls
        self.username_input = QComboBox()
        self.username_refresh = QPushButton("&Refresh")
        self.add_dialog = QPushButton("&Add")
        self.game_count_label = QLabel()

        # Set dimensions of controls
        self.username_input.setFixedSize(COMBO_WIDTH, COMBO_HEIGHT)
        self.username_refresh.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.add_dialog.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.game_count_label.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)

        # Add controls to layout
        self.userLayout.addWidget(self.username_input)
        self.userLayout.addWidget(self.username_refresh)
        self.userLayout.addWidget(self.add_dialog)
        self.userLayout.addWidget(self.game_count_label)

    def add_plot_inputs(self):
        # Set up layout
        self.plot_inputs_layout = QFormLayout()
        self.centralLayout.addLayout(self.plot_inputs_layout)

        # Create Controls
        self.player_colour_select = QComboBox()
        self.player_colour_select.addItems(["White and Black", "White", "Black"])
        self.player_colour_select.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)
        self.remove_opponents = QLineEdit()
        self.remove_opponents.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)
        # self.remove_opponents.setPlaceholderText("MagnusCarlsen FabianoCaruana ...")
        self.opening_select = QLineEdit()
        self.opening_select.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)
        # self.opening_select.setPlaceholderText("B10 D00 ...")
        self.number_select = QLineEdit("6")
        self.number_select.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)

        # Add controls to layout
        self.plot_inputs_layout.addRow("Colour:", self.player_colour_select)
        self.plot_inputs_layout.addRow("Opponents to remove:", self.remove_opponents)
        self.plot_inputs_layout.addRow("Openings", self.opening_select)
        self.plot_inputs_layout.addRow("Number of Items:", self.number_select)

    def add_plot_select(self):
        # Set up layout
        self.plot_select_layout = QHBoxLayout()
        self.centralLayout.addLayout(self.plot_select_layout)

        # Create controls
        self.plot_select = QComboBox()
        self.generate_plot = QPushButton("Plot")
        self.save_plot = QPushButton("Save")
        self.filtered_game_count_label = QLabel()

        # Set dimensions of controls
        self.plot_select.setFixedSize(COMBO_WIDTH, COMBO_HEIGHT)
        self.generate_plot.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.save_plot.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.filtered_game_count_label.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)

        # Add controls to layout
        self.plot_select_layout.addWidget(self.plot_select)
        self.plot_select_layout.addWidget(self.generate_plot)
        self.plot_select_layout.addWidget(self.save_plot)
        self.plot_select_layout.addWidget(self.filtered_game_count_label)
    
    def add_canvas(self, fig = None):
        # Make placeholder figure
        if fig is None:
            data = pd.DataFrame({"points": np.random.random(10)})
            fig = (gg.ggplot(data, gg.aes(x="data.index", y="points")) + gg.geom_point()).draw()

        # Add to layout
        self.canvas = FigureCanvasQTAgg(fig)
        self.centralLayout.addWidget(self.canvas)

    def popup(self):
        wind = AddUserPopUp(self)
        wind.exec()


class AddUserPopUp(QDialog):

    """
    Window for adding new users
    """
    
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle('Add Username')

        # Create widgets
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)
        self.username_check = QPushButton("Check")
        self.username_check.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)

        self.username_data = QLabel("Enter a username...")
        self.username_data.setFixedSize(GAMES_WIDTH, BUTTON_HEIGHT)
        self.username_add = QPushButton("Add")
        self.username_add.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)

        # Set up layouts
        self.popup_layout = QVBoxLayout()
        self.check_layout = QHBoxLayout()
        self.add_layout = QHBoxLayout()

        self.popup_layout.addLayout(self.check_layout)
        self.popup_layout.addLayout(self.add_layout)
        self.check_layout.addWidget(self.username_input)
        self.check_layout.addWidget(self.username_check)
        self.add_layout.addWidget(self.username_data)
        self.add_layout.addWidget(self.username_add)
        self.setLayout(self.popup_layout)
    

class FileSaveDialog(QDialog):

    """
    File save window used to save the plots.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)

        # Initialize file save window
        self.file_save_window = QFileDialog()
        self.file_save_window.setFileMode(QFileDialog.FileMode.AnyFile)
        self.file_save_window.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.file_save_window.setDirectory(str(Path(__file__).parent.parent) + "/plots/")
        self.file_save_window.setDefaultSuffix(".png")
    
    def window_open(self) -> str:
        """Spawn the window and return the entered filepath"""
        selected_filepath, _ = self.file_save_window.getSaveFileName()
        print(selected_filepath)
        return selected_filepath


if __name__ == "__main__":
    app = QApplication([])
    window = ChessPlotterView()
    sys.exit(app.exec())
