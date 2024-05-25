"""
This file contains two non-wear detection pipelines for the EmbracePlus wristband.

NOTE: the parameters of these pipeline are *still* based on the Empatica E4 wristband.
Given that we do not have many data to perform qualitative analysis on the EmbracePlus 
wristband, we decided to use the same parameters as the Empatica E4 wristband.

Future users should validate these parameters with their own data, using the 
visualization methodology provided in the EmbracePlus notebook.

"""

from tsflex.processing import SeriesPipeline, SeriesProcessor, dataframe_func

from code_utils.empatica.generic_processing import sqi_or, sqi_smoothen

embraceplus_wrist_pipeline = SeriesPipeline(
    processors=[
        # Convert the ACC-X signal into the rolling standard devication,
        # NOTE: the avroParser provides the acclerometer data alreay in G-range, so we
        # do not need to normalize the accelerometer signal to G's
        # NOTE: the sampling frequency of the ACC signal is 64Hz instead of 32Hz
        SeriesProcessor(
            lambda ACC: ACC.rolling(64, center=True, step=20).std().rename("AI"),
            "ACC_x",
        ),
        # NOTE: the remainder of this pipeline is the same as the Empatica pipeline
        # The ACC signal is normalized to G's
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
