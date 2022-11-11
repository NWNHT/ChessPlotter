
import plotnine as gg

class ChessPlotterColourScheme:

    """
    This class is just a container for a number of constants used for consistent plotting.
    """

    # Colour sets
    colour2 = ["#1e8ef0", "#ff4f00"]
    colour3 = ["#1e8ef0", "#16e276", "#ff4f00"]
    colour4 = ["#1e8ef0", "#16e276", "#ff4f00", "#dd1616"]
    colour5 = ["#1e8ef0", "#16e276", "#17c903", "#ff4f00", "#dd1616"]

    # Colours
    background      = "#666666" # lightgray
    text            = "#FFFFFF" # white
    white           = "#FFFFFF" # white
    black           = "#000000" # black
    draw            = "#999999" # gray
    axis            = "#999999"

    # Text size
    title_size = 20
    axis_size = 16
    legend_title_size = 14
    legend_text_size = 12
    label_size = 12

    # Legend Position
    legend_position = (0.8, 0.90)

    # Legend labels
    legend_result = ["Win", "Draw", "Loss"]
    legend_colour = ["Black", "White"]

    # Axis Limits
    elo_limits = (-150, 150)

    # Blank element
    blank = gg.element_blank()

    # Opacity
    alpha = 0.3

    # Figure size
    figure_size = (20, 10)
