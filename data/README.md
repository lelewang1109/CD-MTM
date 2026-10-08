# Public input data

`data/real` is a local symbolic link to the shared public-data cache at
`/Users/lele/Desktop/MergeTreeMaps/data/real`. It is excluded from the
supplement because the cache is about 13 GB.

The final evaluation expects these files:

| Relative path | SHA-256 |
|---|---|
| `ERA5_MSLP/ERA5_MSLP_19991117_20000114_12h_arco_expanded.nc` | `77d91ddeb8d61c839065ef20e7290a53c5d77bab5782b7a08dfb62f7c7eadb2f` |
| `ERA5_MSLP/ERA5_MSLP_20131201_20140131_12h_arco_expanded.nc` | `72445bfb47c1a5980ff991b881c3a77ebf9031996bf99dced03d9c884c65df09` |
| `wildfire/wildfire.json` | `2a8dd31bf6d222d7de673c7e7b2af94550660f1996b0a5db256d97f2b9c2ed9f` |

The ERA5 subsets come from the public ARCO-ERA5 mirror. The wildfire input is
from Franke et al., Zenodo record 11234747. The manuscript documents the exact
extraction and preprocessing protocol.

