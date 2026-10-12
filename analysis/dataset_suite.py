"""Dataset membership for the revised paper; archives remain available explicitly."""
REAL_DATASETS = ('era5', 'wildfire', 'olr', 'pm25')
SYNTHETIC_DATASETS = ('ring', 'gaussians')
PAPER_DATASETS = REAL_DATASETS + SYNTHETIC_DATASETS
PROXY_DATASETS = PAPER_DATASETS
LABELS = dict(era5='ERA5 1999/2000', wildfire='Wildfire 2019',
              oisst='OISST 2024', olr='OLR 2024', pm25='PM2.5 Jan 2000', ring='Ring', gaussians='Gaussians',
              era5_2014='ERA5 2013/14 (archive)')

RETIRED_DATASETS = ('era5_2014', 'oisst')
