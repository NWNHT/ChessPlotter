
from datetime import datetime
import logging
from typing import List, Optional

from functools import wraps
from matplotlib.figure import Figure
import os
import pandas as pd
import plotnine as gg

from chessproc.pgnproc import construct_parquet_by_username, get_parquet_by_username, download_by_username_list_better, get_player_game_count
from chessproc.dfproc import remove_opponent

def update_game_count(method):
    """Decorator for all ChessPlot methods that update the data filters, applies filters and updates counts"""
    @wraps(method)
    def _int(self, *args, **kwargs):
        method(self, *args, **kwargs)
        self.apply_filters()
        return (self.update_game_dataframe_count(), self.update_filtered_game_dataframe_count())
    return _int

class ChessPlotterModel:

    def __init__(self, plotter, filepath: str = "/Users/lucasnieuwenhout/Documents/Programming/Python/Projects/ChessPlotter/pgns/"):
        self.filepath = filepath

        # Set up some default and given values
        self.username_list = self.get_parquet_list()
        self.username: str = self.username_list[0]
        self.colour: tuple[bool, str] = (True, "")
        self.remove: List[str] = []
        self.opening: List[str] = []
        self.number_items: int = 6
        self.valid_usernames = set() 

        # Data holds the dataframe of the current user, plot holds the plot
        self.data: Optional[pd.DataFrame] = get_parquet_by_username(self.username)
        self.filtered_data: Optional[pd.DataFrame] = self.data
        self.apply_filters()

        # Game counting
        self.data_count: int = len(self.data)
        self.filtered_data_count: int = len(self.filtered_data)

        # Set up plotting
        self.plotter = plotter
        self.plot: Optional[gg.ggplot] = None # Potentially set up spash screen?
        self.figure: Optional[Figure] = None
    
    def set_plot(self, combo_input):
        """On pushing of generate plot button, update the plot with a call to the plotter"""
        # Get the new plot, save and convert to figure
        # self.plot = self.plotter(combo_input, self.filtered_data, self.username, self.colour, self.remove, self.opening, self.number_items)
        # self.figure = self.plot.draw()
        try:
            self.plot = self.plotter(combo_input, self.filtered_data, self.username, self.colour, self.remove, self.opening, self.number_items)
            self.figure = self.plot.draw()
        except:
            logging.warning("Error generating plot, plot not updated.")

        # return the figure to the controller for display to the view
        return self.figure
    
    def get_plot_list(self):
        """Update plot list with available plots"""
        return self.plotter.plots.keys()
    
    def get_parquet_list(self) -> List:
        """Update usernames list with available parquet files"""
        # TODO: Add some handling for condition where there are no parquet files, might fail on opening
        lst = sorted([file[:-8] for file in os.listdir(self.filepath) if file.endswith('.parquet')])
        return lst
    
    def update_username_list(self) -> None:
        """Update the username list because the format of the function above doesn't facilitate this"""
        self.username_list = self.get_parquet_list()
    
    @update_game_count
    def set_username(self, idx):
        # Update the username selected
        self.username = self.username_list[idx]
        # Update the stored dataframe
        self.update_game_dataframe()

    @update_game_count
    def set_colour(self, idx):
        if idx == 0:
            self.colour = (True, "")
        elif idx == 1:
            self.colour = (False, "White")
        elif idx == 2:
            self.colour = (False, "Black")
        else:
            logging.exception("Unexpected value being set to colour.")
        logging.warning(f"Colour updated to {self.colour} with index {idx}.")

    @update_game_count
    def set_remove(self, line_input):
        self.remove = line_input.split(' ')
        logging.warning(f"Remove updated to {self.remove} with input {line_input}.")

    @update_game_count
    def set_opening(self, line_input):
        self.opening = line_input.split(' ')
        logging.warning(f"Opening updated to {self.opening} with input {line_input}.")

    @update_game_count
    def set_number_items(self, line_input):
        if line_input == "":
            self.number_items = 6
        else:
            self.number_items = line_input
        logging.warning(f"Number updated to {self.number_items} with input {line_input}.")

    def update_game_dataframe(self):
        """Load a different parquet file as view is updated"""
        logging.warning(f"Username changed to {self.username}.")
        self.data = get_parquet_by_username(self.username)
        logging.warning(f"Data updated: {self.data['Black'].value_counts().keys()[0]}")
    
    def apply_filters(self):
        """Apply selection filters to the raw dataframe"""
        # Filter by colour
        if not self.colour[0]:
            self.filtered_data = self.data.query('player_colour == @self.colour[1]')
        else:
            self.filtered_data = self.data
        logging.warning(f"After colour: {len(self.filtered_data)}")

        # Remove any opponents
        self.filtered_data = remove_opponent(self.filtered_data, *self.remove)
        logging.warning(f"After remove: {len(self.filtered_data)}")

        # Select by opening ECO
        if len(self.opening) > 0 and len(self.opening[0]) > 0:
            self.filtered_data = self.filtered_data.query('ECO in @self.opening')
        logging.warning(f"After opening: {len(self.filtered_data)}")

        # TODO: Add filter for number of items, could require more thought

    def update_game_dataframe_count(self):
        """Update game count for the unfiltered dataframe"""
        self.data_count = len(self.data)
        return self.data_count

    
    def update_filtered_game_dataframe_count(self):
        """Update the game count for the filtered dataframe"""
        self.filtered_data_count = len(self.filtered_data)
        return self.filtered_data_count
    
    @update_game_count
    def refresh_user_parquet(self):
        """Make requests for archives, update parquet file and dataframe"""
        download_by_username_list_better([self.username])
        self.update_game_dataframe()
    
    def check_username(self, username: str) -> str:
        """Return the string to be put in the popup window when a username is checked"""
        username_game_count = get_player_game_count(username=username)
        # Update the status, add username to valid list if valid
        if username_game_count is None:
            logging.warning(f"Username {username} found invalid")
            return "Invalid Username"
        else:
            self.valid_usernames.add(username)
            logging.warning(f"Username {username} added to valid list")
            return f"{username_game_count} rated games found."
    
    def check_valid_username(self, username: str) -> bool:
        """A check if the username given is in the valid username list"""
        return username in self.valid_usernames
    
    def download_by_username(self, username: str) -> bool:
        """Download the pgns for the given username"""
        try:
            download_by_username_list_better(usernames=[username])
            logging.warning(f"Data downloaded for {username}")
            return True
        except:
            logging.warning(f"Data NOT downloaded for {username}")
            return False
    
    def create_parquet(self, username: str) -> bool:
        """Construct parquet for given username"""
        try:
            construct_parquet_by_username(username=username)
            logging.warning(f"Constructed parquet for {username}")
            return True
        except:
            logging.warning(f"Error constructing parquet for {username}")
            return False
    
    def save_figure(self, selected_filename):
        """Given filename selected in view QFileDialog, save figure as png"""
        save_filepath = self.filepath + "../plots/"
        filename = save_filepath + self.username + "---" + datetime.now().isoformat() + ".png"
        try:
            self.plot.save(filename=selected_filename, format="png", width=20, height=10)
            logging.warning("Plot saved with selected filename.")
        except:
            try:
                self.plot.save(filename=filename, format="png", width=20, height=10)
                logging.warning("Plot saved with default filename.")
            except:
                logging.warning("Plot not saved, error saving.")



if __name__ == "__main__":
    ob = ChessPlotterModel()
    print(ob.data)
    print("ran")
