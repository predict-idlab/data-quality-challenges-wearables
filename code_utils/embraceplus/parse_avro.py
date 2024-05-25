from pathlib import Path
from typing import List, Union

import fastavro
import pandas as pd


class AvroParser:
    """A static class to parse Embrace+ avro files."""

    # constants
    TS_COL = "timestampStart"
    FS_COL = "samplingFrequency"
    VAL_COL = "values"

    # ------------------------------- Helper functions ------------------------------
    @staticmethod
    def _get_timestamps(signal_dict, val_col="values") -> pd.Series:
        # TODO -> I'm not sure whether the current timestamps are timezones aware
        start_time = pd.to_datetime(signal_dict[AvroParser.TS_COL] * 1000, unit="ns")
        return pd.date_range(
            start_time,
            # end=start_time  # alternative way to calculate the end time
            # + pd.to_timedelta(
            #     1000 * len(signal_dict[val_col]) / signal_dict[AvroParser.FS_COL],
            #     unit="ms",
            # ),
            periods=len(signal_dict[val_col]),
            freq=pd.to_timedelta(1000 / signal_dict[AvroParser.FS_COL], unit="ms"),
        )

    @staticmethod
    def _scale_imu_df(df, imu_params, cols) -> pd.DataFrame:
        o_min, o_max = imu_params["digitalMin"], imu_params["digitalMax"]
        n_min, n_max = imu_params["physicalMin"], imu_params["physicalMax"]
        df[cols] = (df[cols] - o_min) / (o_max - o_min) * (n_max - n_min) + n_min
        return df

    @staticmethod
    def _parse_imu_record(imu_dict, prefix: str = "") -> pd.DataFrame:
        df_imu = pd.DataFrame(
            {
                f"{prefix}_x".lstrip("_"): imu_dict["x"],
                f"{prefix}_y".lstrip("_"): imu_dict["y"],
                f"{prefix}_z".lstrip("_"): imu_dict["z"],
            }
        )

        # Edge case: if the IMU data is empty -> return an empty dataframe
        if df_imu.empty:
            df_imu["timestamp"] = pd.Series([], dtype="datetime64[ns]")
            return df_imu

        df_imu["timestamp"] = AvroParser._get_timestamps(imu_dict, val_col="x")
        df_imu = AvroParser._scale_imu_df(
            df_imu,
            imu_params=imu_dict["imuParams"],
            cols=df_imu.columns.difference(["timestamp"]),
        )
        return df_imu

    @staticmethod
    def _parse_single_modality(s_dict, col_name) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                col_name: s_dict[AvroParser.VAL_COL],
                "timestamp": AvroParser._get_timestamps(s_dict),
            }
        )
        return df

    # ------------------------------ Main functions ---------------------------------
    def parse_record(record_dict) -> dict:
        """Parse a single record of an Embrace+ avro file."""
        data = record_dict["rawData"]
        return {
            "acc": AvroParser._parse_imu_record(data["accelerometer"], prefix="ACC"),
            "gyro": AvroParser._parse_imu_record(data["gyroscope"], prefix="GYRO"),
            "eda": AvroParser._parse_single_modality(data["eda"], col_name="EDA"),
            "bvp": AvroParser._parse_single_modality(data["bvp"], col_name="BVP"),
            "tmp": AvroParser._parse_single_modality(data["temperature"], "TMP"),
            "metadata": {
                k: record_dict[k]
                for k in set(record_dict.keys()).difference({"rawData"})
            },
        }

    @staticmethod
    def parse_avro_file(file_path: Union[str, Path]) -> List[dict]:
        """Parse all records of an Embrace+ avro file.

        Returns:
            List[dict]: A list of dictionaries, where each dictionary represents a
            single record. Each record contains the following keys
            - "acc": A pandas DataFrame containing the accelerometer data
            - "gyro": A pandas DataFrame containing the gyroscope data
            - "eda": A pandas DataFrame containing the EDA data
            - "bvp": A pandas DataFrame containing the BVP data
            - "tmp": A pandas DataFrame containing the temperature data
            - "metadata": A dictionary containing the metadata of the record

        """
        with open(file_path, "rb") as f:
            records = [AvroParser.parse_record(record) for record in fastavro.reader(f)]
        for r in records:
            r["metadata"]["filePath"] = str(file_path)
        return records

    @staticmethod
    def merge_avro_data(avros: List[dict]) -> dict:
        def _concat_dfs(dfs) -> pd.DataFrame:
            return (
                pd.concat(dfs, axis=0).sort_values("timestamp").reset_index(drop=True)
            )

        return {
            "acc": _concat_dfs([a["acc"] for a in avros]),
            "gyro": _concat_dfs([a["gyro"] for a in avros]),
            "eda": _concat_dfs([a["eda"] for a in avros]),
            "bvp": _concat_dfs([a["bvp"] for a in avros]),
            "tmp": _concat_dfs([a["tmp"] for a in avros]),
        }
