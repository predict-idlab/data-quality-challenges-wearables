"""
This file contains two non-wear detection pipelines for the Empatica E4 wristband.

The first pipeline is based on the work of Bottcher et al.
see: https://www.nature.com/articles/s41598-022-25949-x
The second pipeline is a revised iteration of the first pipeline
"""

from tsflex.processing import SeriesPipeline, SeriesProcessor, dataframe_func

from code_utils.processing import mean_resample, sqi_or, sqi_smoothen, std_sum

# fmt: off
# ----------------------------------------
# The wrist pipeline of Bottcher et al.
wrist_pipeline_bottcher = SeriesPipeline(
    processors=[
        # On body status movement: AI > 0.2
        # note: the AI is computed by the per axis 10s rolling STD-sum
        SeriesProcessor(
            dataframe_func(std_sum),
            tuple(["ACC_x", "ACC_y", "ACC_z"]),
            name="AI",
            scaling_factor=64,  # normalize the accelerometer signal to G's
            n=32 * 10,
            step=1,
            center=True,
        ),
        SeriesProcessor(lambda AI: (AI > 0.2).rename("AI_SQI"), "AI"),
        # On body status EDA: > 0.05 microsiemens
        SeriesProcessor(lambda EDA: (EDA > 0.05).rename("EDA_SQI"), "EDA"),
        # On body status TMP: 25 < TMP < 40
        SeriesProcessor(lambda TMP: ((TMP > 25) & (TMP < 40)).rename("TMP_SQI"), "TMP"),
        # Reindex the TMP_SQI and movement AI_SQI to the EDA_SQI its index
        # This eases the binary SQI logic
        SeriesProcessor(lambda EDA_SQI, TMP_SQI: TMP_SQI.reindex(EDA_SQI.index, method="bfill", fill_value=True),
            tuple(["EDA_SQI", "TMP_SQI"]),
        ),
        SeriesProcessor(
            lambda EDA_SQI, AI_SQI: AI_SQI.reindex(EDA_SQI.index, method="bfill", fill_value=True),
            tuple(["EDA_SQI", "AI_SQI"]),
        ),
        #  Per minute sum
        SeriesProcessor(mean_resample, "EDA_SQI", new_freq="1min", label="left", name="EDA_SQI_mean"),
        SeriesProcessor(mean_resample, "AI_SQI", new_freq="1min", label="left", name="AI_SQI_mean"),
        SeriesProcessor(mean_resample, "TMP_SQI", new_freq="1min", label="left", name="TMP_SQI_mean"),
        # at least one modality showing as on body (>1%) to be considered on body
        SeriesProcessor(mean_resample, "EDA_SQI", new_freq="1min", label="left", name="EDA_SQI_mean"),
        SeriesProcessor(lambda SQI: (SQI.dropna() > 0.01).rename(SQI.name + "_bin"), "EDA_SQI_mean"),
        SeriesProcessor(mean_resample, "AI_SQI", new_freq="1min", label="left", name="AI_SQI_mean"),
        SeriesProcessor(lambda SQI: (SQI.dropna() > 0.01).rename(SQI.name + "_bin"), "AI_SQI_mean"),
        SeriesProcessor(mean_resample, "TMP_SQI", new_freq="1min", label="left", name="TMP_SQI_mean"),
        SeriesProcessor(lambda SQI: (SQI.dropna() > 0.01).rename(SQI.name + "_bin"), "TMP_SQI_mean"),
        # Or masking
        SeriesProcessor(
            sqi_or,
            tuple(["EDA_SQI_mean_bin", "TMP_SQI_mean_bin", "AI_SQI_mean_bin"]),
            output_name="On_Wrist_SQI",
        ),
    ]
)
# fmt: on

# ----------------------------------------
# Our wrist pipeline
wrist_pipeline = SeriesPipeline(
    processors=[
        # Convert the ACC-X signal into the rolling standard devication,
        # representing the Activity Index (AI)
        SeriesProcessor(
            # normalize the accelerometer signal to G's
            lambda ACC: (ACC / 64).rolling(32, center=True, step=10).std().rename("AI"),
            "ACC_x",
        ),
        # Calculate the signal SQI's
        SeriesProcessor(lambda EDA: (EDA > 0.03).rename("EDA_SQI"), "EDA"),
        # TODO -> incorporate rate of change in the wrist-SQI
        SeriesProcessor(lambda TMP: (TMP > 32).rename("TMP_SQI"), "TMP"),
        SeriesProcessor(lambda AI: (AI > 0.1).rename("AI_SQI"), "AI"),
        # Reindex the TMP_SQI and movement AI_SQI to the EDA_SQI its index
        # This eases the binary SQI logic
        SeriesProcessor(
            lambda EDA_SQI, TMP_SQI: TMP_SQI.reindex(
                EDA_SQI.index, method="bfill", fill_value=True
            ),
            tuple(["EDA_SQI", "TMP_SQI"]),
        ),
        SeriesProcessor(
            lambda EDA_SQI, AI_SQI: AI_SQI.reindex(
                EDA_SQI.index, method="bfill", fill_value=True
            ),
            tuple(["EDA_SQI", "AI_SQI"]),
        ),
        # Binary SQI logic: OR all the SQI's together
        # i.e. => on wrist when HIGH EDA OR HIGH skin temperature OR High movement
        SeriesProcessor(
            sqi_or, tuple(["EDA_SQI", "TMP_SQI", "AI_SQI"]), output_name="On_Wrist_SQI"
        ),
        # Smooth the wrist-SQI at both sides
        SeriesProcessor(
            sqi_smoothen,
            "On_Wrist_SQI",
            fs=4,
            min_ok_ratio=0.55,
            window_s=60,
            flip=False,
            center=True,
            output_name="On_Wrist_SQI_smoothened",
        ),
        SeriesProcessor(
            sqi_smoothen,
            "On_Wrist_SQI_smoothened",
            fs=4,
            min_ok_ratio=0.5,
            window_s=60,
            flip=True,
            center=True,
            output_name="On_Wrist_SQI_smoothened",
        ),
    ]
)
