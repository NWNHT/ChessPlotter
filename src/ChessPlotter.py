
import sys
from functools import wraps
import logging

from PyQt6 import QtCore, QtWidgets
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
)

from ChessPlotterModel import ChessPlotterModel
from ChessPlotterView import ChessPlotterView
from chessproc.ChessPlots import ChessPlots
from chessproc.ChessPlotterColourScheme import ChessPlotterColourScheme as cpcs


# Logging level
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")


def update_view_counts(method):
    """Decorator to update the view with the game counts"""
    @wraps(method)
    def _int(self, *method_args, **method_kwargs):
        game_count, filtered_game_count = method(self, *method_args, **method_kwargs)
        self.view.game_count_label.setText(f"Total Games: {game_count}")
        self.view.filtered_game_count_label.setText(f"Remaining Games: {filtered_game_count}")
    return _int

class ChessPlotter:

    def __init__(self, view: ChessPlotterView):
        self.model: ChessPlotterModel = ChessPlotterModel(plotter=ChessPlots())
        self.view:  ChessPlotterView  = view

        # Make signal -> slot connections
        self.make_connections()
        
        # Populate the username and plot list
        self.update_username_list()
        self.update_plot_list()
    
    def make_connections(self):
        """Make connections from view to model"""
        # Link username selection
        self.view.username_input.currentIndexChanged.connect(self.change_to_username)
        self.view.username_refresh.clicked.connect(self.refresh_username)
        self.view.add_dialog.clicked.connect(self.show_dialog)

        # Link game filter controls
        self.view.player_colour_select.currentIndexChanged.connect(self.change_to_colour)
        self.view.remove_opponents.editingFinished.connect(self.change_to_remove_opponent)
        self.view.opening_select.editingFinished.connect(self.change_to_opening_select)
        self.view.number_select.editingFinished.connect(self.change_to_number_select)

        # Link plot selection
        self.view.generate_plot.clicked.connect(self.change_plot)

        # Link plot save
        self.view.save_plot.clicked.connect(self.save_figure)

        # Link user check button
        self.view.adduser.username_check.clicked.connect(self.check_user)

        # Link user add button
        self.view.adduser.username_add.clicked.connect(self.add_user)

    @update_view_counts
    def change_to_username(self, idx):
        """Call model setter for username"""
        return self.model.set_username(idx)

    @update_view_counts
    def change_to_colour(self, idx):
        """Call model setter for colour"""
        return self.model.set_colour(idx)

    @update_view_counts
    def change_to_remove_opponent(self):
        """Call model setter for remove opponents"""
        return self.model.set_remove(self.view.remove_opponents.text())
    
    @update_view_counts
    def change_to_opening_select(self):
        """Call model setter for opening selection"""
        return self.model.set_opening(self.view.opening_select.text())

    @update_view_counts
    def change_to_number_select(self):
        """Call model setter for number selection"""
        return self.model.set_number_items(self.view.number_select.text())

    def update_username_list(self):
        """Refresh the username combobox with the usernames listed in the model"""
        self.view.username_input.clear()
        self.view.username_input.addItems(self.model.username_list)
    
    def update_plot_list(self):
        """Populate the available plot list"""
        self.view.plot_select.clear()
        self.view.plot_select.addItems(self.model.get_plot_list())

    def change_plot(self):
        """Change plot shown in window"""
        # This is the dumbest way to do this
        # I just nuke the previous plot widget and create new one in its place.
        # ?: Is there a better/faster way to do this?

        # Get the current selection of the plot combobox
        combo_input = self.view.plot_select.currentText()

        # Remove previous figure and insert new figure
        self.view.centralLayout.removeWidget(self.view.canvas)
        self.view.canvas.setParent(None) # This is important so that the figure is actually removed from display
        self.view.add_canvas(self.model.set_plot(combo_input=combo_input))

    def refresh_username(self):
        """Refresh the currently selected player/username"""
        return self.model.refresh_user_parquet()

    def show_dialog(self):
        """Show Add User dialog when the main window Add button is pushed"""
        self.view.adduser.exec()
    
    def save_figure(self):
        self.model.save_figure()

    def check_user(self):
        """Call to model to check the current username entered, print out response"""
        # Check the username
        self.view.adduser.username_data.setText(self.model.check_username(username=self.view.adduser.username_input.text()))
        
        # TODO: Potentially make the Add button appear and disappear

    def add_user(self):
        """Upon clicking of 'Add' button in popup, attempt to download pgn files, process files, and create parquet file."""
        username = self.view.adduser.username_input.text()
        logging.warning(f"Starting to add user {username}")
        # Check if the username is valid, escape if not
        if not self.model.check_valid_username(username=username):
            self.view.adduser.username_data.setText("Username not checked.")
            return

        # Download the files once confirmed valid
        self.view.adduser.username_data.setText("Valid Username, fetching...")
        if not self.model.download_by_username(username=username):
            self.view.adduser.username_data.setText("Error on download")
            return

        # Create the parquet file
        self.view.adduser.username_data.setText("Data downloaded, processing...")

        if not self.model.create_parquet(username=username):
            self.view.adduser.username_data.setText("Error on parquet")
            return
        self.view.adduser.username_data.setText("Data is ready.")

        # Update the username select combobox
        self.model.update_username_list()
        self.update_username_list()


if __name__ == '__main__':
    app = QApplication([])
    window = ChessPlotterView()
    obj = ChessPlotter(window)
    sys.exit(app.exec())
