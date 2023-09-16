from pathlib import Path
from socket import gethostname
from inspect import getsourcefile

if gethostname() == "gecko":
    # -------------- ETRI PATHS --------------
    _etri_root_dir = Path("/media/etri/")
    # The path which contains raw etri .7z files, combined with the metadata
    etri_path = _etri_root_dir / "raw"

    # The path which contains extracted raw etri .7z files
    interim_etri_path = _etri_root_dir / "interim"

    # The location where we store the processed daily and tz-aware etri data
    processed_etri_path = _etri_root_dir / "processed"

    # --------------- MBRAIN PATHS ---------------
    _mbrain_root_dir = Path("/media/aaa_contextaware/raw/mbrain")

    # The path which contains the metadata for the mbrain data
    mbrain_metadata_path = _mbrain_root_dir / "metadata"

    # The location in which the processed daily and tz-aware mbrain data is stored
    processed_mbrain_path = _mbrain_root_dir / "obelisk_dump"

else:
    raise NotImplementedError()

loc_data_dir = Path(getsourcefile(lambda: 0)).parent.parent.absolute() / "loc_data"

assert etri_path.exists()
assert interim_etri_path.exists()

assert mbrain_metadata_path.exists()
assert processed_mbrain_path.exists()

assert loc_data_dir.exists()
