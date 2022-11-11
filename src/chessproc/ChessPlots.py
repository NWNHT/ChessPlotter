
from functools import partialmethod
import logging
from typing import List

import pandas as pd
import plotnine as gg

from .ChessPlotterColourScheme import ChessPlotterColourScheme as cpcs
from .PlotnineElements import PlotnineElements as pe, blank


class ChessPlots:

    """
    Class containing all of the plots for ChessPlotter.

    There is a single 'public' method __call__ which is to be used by the ChessPlotterModel to generate
    a ggplot object.  Additional plots can be added by including the method which accepts a dataframe and
    adding an entry to the self.plots list.
    """

    def __init__(self):
        self.plots = {"ELO Difference Density":     ChessPlots._elo_difference_density,
                 "ELO Difference Histogram":        ChessPlots._elo_difference_histogram,
                 "Game Length Density":             ChessPlots._game_length_density,
                 "Top Openings":                    ChessPlots._opening_top_partial,
                 "Top Openings - Fill":             ChessPlots._opening_top_partial_fill,
                 "Single Opening Results":          ChessPlots._opening_single,
                 "Game Termination Type":           ChessPlots._termination_type_partial,
                 "Game Termination Type - Fill":    ChessPlots._termination_type_partial_fill}
        
        self.username = self.colour = self.remove = self.opening = self.number_items = None
    
    def __call__(self, plot_selection: str, 
                       game_data: pd.DataFrame, 
                       username: str,
                       colour: tuple[bool, str], 
                       remove: List[str], 
                       opening: List[str], 
                       number_items: int) -> gg.ggplot:
        """On call, check which plot has been selected and return the result of the function"""

        self.username = username
        self.colour = colour[1]
        self.remove = remove
        self.opening = opening
        self.number_items = number_items

        return self.plots[plot_selection](self, game_data)

    def _elo_difference_density(self, game_data: pd.DataFrame) -> gg.ggplot:
        """Plot density of elo difference, coloured by result"""
        return (gg.ggplot(game_data, gg.aes(fill='factor(player_result)', x='elo_difference')) 
                    + gg.geom_density(colour=cpcs.white, alpha = cpcs.alpha)
                    + gg.scale_fill_manual(values=cpcs.colour3, name=f"{game_data.Username.iloc[0]} Result", labels=("Loss", "Draw", "Win"))

                    + gg.ggtitle("ELO Difference Density")
                    + gg.xlab("ELO Difference")

                    + gg.scale_x_continuous(limits=cpcs.elo_limits, expand=(0,0))

                    + gg.theme(text=gg.element_text(colour=cpcs.text, size=cpcs.label_size))
                    + gg.theme(plot_title=gg.element_text(size=cpcs.title_size, ha='left'))
                    + gg.theme(axis_title=gg.element_text(size=cpcs.axis_size))
                    + gg.theme(axis_text=gg.element_text(size=cpcs.label_size))
                    + gg.theme(axis_title_y=blank, axis_text_y=blank)
                    + gg.theme(panel_grid_major_x=gg.element_line(colour=cpcs.axis))
                    + gg.theme(figure_size=cpcs.figure_size)
                    + gg.theme(legend_position=cpcs.legend_position, legend_title=gg.element_text(size=cpcs.legend_title_size), legend_text=gg.element_text(size=cpcs.legend_text_size))

                    + pe.background_colour(colour=cpcs.background)
                    + pe.remove_grid(minor=True, y_major=True)
                    + pe.remove_ticks(major=True, minor=True))

    def _elo_difference_histogram(self, game_data: pd.DataFrame) -> gg.ggplot:
        """Plot a histogram of elo difference, coloured by result"""
        return (gg.ggplot(game_data, gg.aes(x="elo_difference", fill='factor(player_result)')) 
                    + gg.geom_histogram(colour="gray", binwidth=8)
                    + gg.scale_fill_manual(values=["black", "lightgray", "white"], name=f"{game_data.Username.iloc[0]} Result", labels=("Loss", "Draw", "Win"))

                    + gg.ggtitle("ELO Difference Histogram")
                    + gg.xlab("ELO Difference")

                    + gg.scale_x_continuous(limits=cpcs.elo_limits, expand=(0,0))

                    + gg.theme(text=gg.element_text(colour=cpcs.text, size=cpcs.label_size))
                    + gg.theme(plot_title=gg.element_text(size=cpcs.title_size, ha='left'))
                    + gg.theme(axis_title=gg.element_text(size=cpcs.axis_size))
                    + gg.theme(axis_text=gg.element_text(size=cpcs.label_size))
                    + gg.theme(axis_title_y=blank, axis_text_y=blank)
                    + gg.theme(panel_grid_major_x=gg.element_line(colour=cpcs.axis))
                    + gg.theme(figure_size=cpcs.figure_size)
                    + gg.theme(legend_position=cpcs.legend_position, legend_title=gg.element_text(size=cpcs.legend_title_size), legend_text=gg.element_text(size=cpcs.legend_text_size))

                    + pe.background_colour(colour=cpcs.background)
                    + pe.remove_grid(minor=True, y_major=True)
                    + pe.remove_ticks(major=True, minor=True))

    def _game_length_density(self, game_data: pd.DataFrame) -> gg.ggplot:
        """Plot game length density for a player"""
        return (gg.ggplot(game_data, gg.aes(fill='factor(player_result)', x='game_length')) 
                    + gg.geom_density(colour="white", alpha = 0.3)
                    + gg.scale_fill_manual(values=pe.colour3, name=f"{game_data.Username.iloc[0]} Result", labels=("Loss", "Draw", "Win"))

                    + gg.ggtitle("Game Length Density")
                    + gg.xlab("Game Length [moves]")

                    + gg.scale_x_continuous(limits=[0, 150], expand=(0,0))

                    + gg.theme(text=gg.element_text(colour=cpcs.text, size=cpcs.label_size))
                    + gg.theme(plot_title=gg.element_text(size=cpcs.title_size, ha='left'))
                    + gg.theme(axis_title=gg.element_text(size=cpcs.axis_size))
                    + gg.theme(axis_text=gg.element_text(size=cpcs.label_size))
                    + gg.theme(axis_title_y=blank, axis_text_y=blank)
                    + gg.theme(panel_grid_major_x=gg.element_line(colour=cpcs.axis))
                    + gg.theme(figure_size=cpcs.figure_size)
                    + gg.theme(legend_position=cpcs.legend_position, legend_title=gg.element_text(size=cpcs.legend_title_size), legend_text=gg.element_text(size=cpcs.legend_text_size))

                    + pe.background_colour(colour=cpcs.background)
                    + pe.remove_grid(minor=True, y_major=True)
                    + pe.remove_ticks(major=True, minor=True))

    def _opening_top(self, game_data: pd.DataFrame, geom_bar_position: str, xlab: str) -> gg.ggplot:
        """Plot stacked horizontal bars for the top n openings for a given colour for a player"""

        # Reorder ECO column by popularity but now considering colour
        # - Gets the value counts(ordered), gets the index(ECO), as strings to remove existing category
        plot_data = game_data.copy(deep=True)
        plot_data['ECO'] = game_data['ECO'].values.reorder_categories(new_categories=game_data['ECO'].value_counts().index.astype(str), ordered=True)

        # Filter out all openings not in the top 'n'
        # This will be limited by the min of the listed openings or number
        top_n_openings = list(game_data.ECO.value_counts()[:min(len(plot_data.ECO.unique()), int(self.number_items))].keys())

        
        return (gg.ggplot(plot_data.query('ECO in @top_n_openings'), gg.aes(x='ECO', fill="factor(Result)")) 
                    + gg.geom_bar(position=geom_bar_position, colour="black")
                    + gg.scale_fill_manual(values=["white", "gray", "black"], name="Result", labels=("White", "Draw", "Black"))
                    + gg.coord_flip()

                    + gg.ggtitle(f'Opening Results for {self.username} {f"playing {self.colour}" if len(self.colour) > 0 else ""}')
                    + gg.xlab("Opening [ECO]")
                    + gg.ylab(xlab)

                    + gg.theme(text=gg.element_text(colour=cpcs.text, size=cpcs.label_size))
                    + gg.theme(plot_title=gg.element_text(size=cpcs.title_size, ha='left'))
                    + gg.theme(axis_title=gg.element_text(size=cpcs.axis_size))
                    + gg.theme(axis_text=gg.element_text(size=cpcs.label_size))
                    + gg.theme(panel_grid_major_x=gg.element_line(colour=cpcs.axis))
                    + gg.theme(figure_size=cpcs.figure_size)
                    + gg.theme(legend_position=cpcs.legend_position, legend_title=gg.element_text(size=cpcs.legend_title_size), legend_text=gg.element_text(size=cpcs.legend_text_size))

                    + pe.background_colour(colour=cpcs.background)
                    + pe.remove_grid(minor=True, y_major=True)
                    + pe.remove_ticks(major=True, minor=True))

    # _opening_top partial methods
    _opening_top_partial = partialmethod(_opening_top, geom_bar_position='stack', xlab="Game Count")
    _opening_top_partial_fill = partialmethod(_opening_top, geom_bar_position='fill', xlab="Game Fraction")

    def _opening_single(self, game_data: pd.DataFrame) -> gg.ggplot:
        """Plot the results for the opening for the player playing black and white"""

        # How to select the opening to show
        # - if there is something in eco then apply filter
        # - If eco is empty then fall back to most common
        # - If after filter it the dataframe has no length then fall back to most common
        plot_data = game_data.copy(deep=True)
        if len(self.opening) > 0 and len(self.opening[0]) > 0:
            eco_data = plot_data.query('ECO == @self.opening[0]')
            if len(eco_data) > 0:
                plot_data = eco_data
            else:
                common = plot_data['ECO'].value_counts().keys()[0]
                plot_data = plot_data.query('ECO == @common')
        else:
            common = plot_data['ECO'].value_counts().keys()[0]
            plot_data = plot_data.query('ECO == @common')
        
        """Plot results of opening(given by ECO) for black and white"""
        return (gg.ggplot(plot_data, gg.aes('player_colour', fill='factor(player_result)'))
                + gg.geom_bar(position='stack', colour="black")
                + gg.scale_fill_manual(values=["black", "lightgray", "white"], name=f"{plot_data.Username.iloc[0]} Result", labels=("Loss", "Draw", "Win"))
                + gg.coord_flip()
                
                + gg.ggtitle(f"Results of Opening {plot_data.ECO.iloc[0]}")
                + gg.xlab("Player Colour")
                + gg.ylab("Game Count")

                + gg.theme(text=gg.element_text(colour=cpcs.text, size=cpcs.label_size))
                + gg.theme(plot_title=gg.element_text(size=cpcs.title_size, ha='left'))
                + gg.theme(axis_title=gg.element_text(size=cpcs.axis_size))
                + gg.theme(axis_text=gg.element_text(size=cpcs.label_size))
                + gg.theme(panel_grid_major_x=gg.element_line(colour=cpcs.axis))
                + gg.theme(figure_size=cpcs.figure_size)
                + gg.theme(legend_position=cpcs.legend_position, legend_title=gg.element_text(size=cpcs.legend_title_size), legend_text=gg.element_text(size=cpcs.legend_text_size))

                + pe.background_colour(colour=cpcs.background)
                + pe.remove_grid(minor=True, y_major=True)
                + pe.remove_ticks(major=True, minor=True))

    def _termination_type(self, game_data: pd.DataFrame, geom_bar_position: str, xlab: str) -> gg.ggplot:
        """Plot of termination type by result for a player"""
        plot_data = game_data.copy(deep=True)
        plot_data["Termination"] = plot_data["Termination"].apply(lambda x: x.split(' ', 1)[1])
        return (gg.ggplot(plot_data, gg.aes('factor(player_result)', fill='Termination')) 
                    + gg.geom_bar(position=geom_bar_position, alpha=0.6)
                    + gg.coord_flip()

                    + gg.scale_x_discrete(name=f"{plot_data.Username.iloc[0]} Result", labels=["Loss", "Draw", "Win"])
                    + gg.scale_fill_manual(values=[*cpcs.colour5, *cpcs.colour4], labels=["Draw - Agreement", "Draw - Insufficient Material", "Draw - Repetition", "Draw - Stalemate", "Draw - Timeout vs. Insufficient Material", "Won - Abandoned", "Won - Checkmate", "Won - Resignation", "Won - Time"])

                    + gg.ggtitle("Game Termination Type")
                    + gg.ylab(xlab)

                    + gg.theme(text=gg.element_text(colour=cpcs.text, size=cpcs.label_size))
                    + gg.theme(plot_title=gg.element_text(size=cpcs.title_size, ha='left'))
                    + gg.theme(axis_title=gg.element_text(size=cpcs.axis_size))
                    + gg.theme(axis_text=gg.element_text(size=cpcs.label_size))
                    + gg.theme(panel_grid_major_x=gg.element_line(colour=cpcs.axis))
                    + gg.theme(figure_size=cpcs.figure_size)
                    + gg.theme(legend_position=(0.9, 0.5), legend_direction='vertical', legend_title=gg.element_text(size=cpcs.legend_title_size), legend_text=gg.element_text(size=cpcs.legend_text_size))

                    + pe.background_colour(colour=cpcs.background)
                    + pe.remove_grid(minor=True, y_major=True)
                    + pe.remove_ticks(major=True, minor=True))
    
    # _termination_type partial methods
    _termination_type_partial = partialmethod(_termination_type, geom_bar_position='stack', xlab="Game Count")
    _termination_type_partial_fill = partialmethod(_termination_type, geom_bar_position='fill', xlab="Game Fraction")
