# -*- coding: utf-8 -*-
"""Various non-DataFrame related utilities."""

__author__ = "Jonas Van Der Donckt"

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Union

import numpy as np


def rolling_window(a: np.ndarray, window: int) -> np.ndarray:
    """Expand an n-dimensional array into windows of size `window`.

    .. TODO::
        investigate the code behavior on n-dimensional arrays, with n > 1

    .. TODO::
        If necessary -> stride can be used

    :param a: The array which will be expanded
    :param window: The size of the window
    :return: The expanded array
    """
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def kth_diag_indices(a: np.ndarray, k: int):
    """Obtain the k'th diagonal's indices from matrix `a`.

    usage::
        >>> a[kth_diag_indices(a, k=10)] # obtain the tenth diagonal to the right

    :param a: The matrix of which the diagonal
    :param k: The index which we will use to calculate the diagonal
    """
    assert np.atleast_2d(a)
    rows, cols = np.diag_indices_from(a)
    if k < 0:
        return rows[-k:], cols[:k]
    elif k > 0:
        return rows[:-k], cols[k:]
    else:
        return rows, cols


def remove(path: str):
    """Remove file or folder (depends on what path is).

    :param path: file or folder path, could either be relative or absolute.
    """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


def get_creation_date(file_path: str) -> float:
    """Get the creation date of a file.

    Try to get the date that a file was created, falling back to when it was last
    modified if that isn't possible.

    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        return os.path.getctime(file_path)
    else:
        stat = os.stat(file_path)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def get_last_modified(file_path: Union[str, Path]) -> float:
    """Get the last modified time of the given path.

    Parameters
    ----------
    file_path: Union[str, Path]
        The path from which we want to obtain the last modified time.

    Returns
    -------
    float

    """
    stat = os.stat(file_path)
    return stat.st_mtime


def unzip_inplace(
    root_dir: Path, recursive=True, prev_matches: List[str] = None
) -> List[str]:
    """Unzip the `.zip` files in `root_dir`.

    Note
    ----
    Will use a case insensitive regex-match on the `.zip` extension

    Parameters
    ----------
    root_dir : Path
        The root directory where the zips will reside
    recursive : bool, optional
        If set `True` a recursive search query will be executed. Otherwise, only matches
        in the `root_dir` will be outputted, by default True
    prev_matches : List[str], optional
        A list of previous matches, by default None

    Returns
    -------
    List[str]
        The list of already unzipped files (=prev matches + newly unzipped mathes).

    """
    assert root_dir.is_dir()
    prev_matches = [] if not isinstance(prev_matches, list) else prev_matches.copy()

    if recursive:
        matches = list(root_dir.rglob("*.[zZ][iI][pP]"))
    else:
        matches = list(root_dir.glob("*.[zZ][iI][pP]"))

    zip_file: Path
    for zip_file in matches:
        if str(zip_file) in prev_matches:
            print(f"file {zip_file} already unzipped")
            continue

        print(f"unzipping {zip_file}")
        subprocess.run(f"unzip -o {zip_file} -d {zip_file.parent}".split())
        prev_matches.append(str(zip_file))
    return prev_matches


def write_list_file(data: List[str], file_path: Union[str, Path]):
    """Write a list of strings to a file.

    Parameters
    ----------
    data : List[str]
        The data (a list of strings), e.g., all parsed files so far.
    file_path: Union[str, Path]
        The path to where the data will be written.

    """
    file_path = Path(file_path)
    assert file_path.parent.exists()
    with open(file_path, mode="w") as f:
        f.write("\n".join(data))


def read_file(file_path: Union[str, Path]) -> List[str]:
    """Read data from a file.

    Parameters
    ----------
    file_path: Union[str, Path]
        The file path.

    Returns
    -------
    List[str]
        A list where each item reprents the corresponding line, encoded as a string.

    """
    file_path = Path(file_path)
    assert file_path.is_file()
    with open(file_path, mode="r") as f:
        output = list(map(lambda x: x.strip(), f.readlines()))
    return output
