"""Print-size figure style and shared paper palette.

Figures are drawn at their printed width (full text width 7.0 in, column
3.4 in) so that every text element is 6.5--8 pt after placement. Scalar
fields use one muted blue--white--red language. Categorical accents retain
the original paper colors.
"""
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

TEXT_W, COL_W = 7.0, 3.4

BLUE_DARK = '#0072b2'
BLUE = '#0072b2'
BLUE_LIGHT = '#56b4e9'
CORAL = '#d55e00'
ORANGE = '#e69f00'
GREEN = '#009e73'
RED = '#c0392b'
GRAY_DARK = '#666666'
GRAY = '#999999'
GRAY_LIGHT = '#dddddd'
OFF_WHITE = '#F7F5F0'

# Low values are blue, the midpoint is warm white, and high values are red,
# matching the pressure-anomaly reference while avoiding saturated extremes.
FIELD_CMAP = LinearSegmentedColormap.from_list(
    'rgmtm_blue_white_red',
    ['#174A73', '#397CA5', '#9BC6D9', '#F7F5F0', '#F2C1AE', '#D66950', '#8F2635'],
    N=256,
)


def apply():
    mpl.rcParams.update({'font.size': 7, 'axes.titlesize': 7.5, 'axes.labelsize': 7, 'xtick.labelsize': 6.5,
                         'ytick.labelsize': 6.5, 'legend.fontsize': 6.5, 'lines.linewidth': .9, 'axes.linewidth': .6,
                         'xtick.major.width': .6, 'ytick.major.width': .6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
                         'pdf.fonttype': 42, 'savefig.dpi': 300})
