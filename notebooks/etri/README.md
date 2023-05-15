## Etri 2020 lifelog dataset
### 1. Obtaining access to the ETRI 2020 lifelog dataset

1. make an account on the [website](https://nanum.etri.re.kr/share/schung/ETRILifelogDataset2020?lang=En_us)
2. navigate to the dataset page and fill in the online data license agreement form
3. download the dataset, which consists of 9 `.7z` files, in the `raw` directory, which should be configured as the `etri_path` (and consequently `_etri_root_path`) in the [code_utils/path_conf.py](../../code_utils/path_conf.py) file. This should result in the following directory structure:

```txt
<_etri_root_dir>
└── raw
    ├── README
    ├── user01-06.7z
    ├── user07-10.7z
    ├── user11-12.7z
    ├── user21-25.7z
    ├── user26-30.7z
    ├── user_info_2020.csv
    ├── user_sleep_2020.csv
    └── user_survey_2020.csv
```

### 2. Extracting the dataset

The bulk of the dataset (i.e. the wearable, smartphone, and label data) is compressed in `.7z` format.
Extract these `.7z` files in the `interim` directory, which should be configured as the `etri_path` (and consequently `_etri_root_path`) in the [code_utils/path_conf.py](../../code_utils/path_conf.py) file. This should result in the following directory structure:

```txt
<_etri_root_dir>
├── interim
│   ├── user01-06           <-- The extracted .7z folder  
│   │   ├── user01          <-- USER ID folder
│   │   │   ├── 1598759880  <-- DAY folder
│   │   │   │   ├── 1598759880_label.csv  <-- labels for the day
│   │   │   │   ├── e4Acc   <-- folder containing the Empatica E4 acc data
│   │   │   │   ├── e4Bvp   <-- E4 blood volume pulse data
│   │   │   │   ├── e4Edaa  <-- E4 skin conductance data
│   │   │   │   ├── e4Hr    <-- E4 heart rate data
│   │   │   │   ├── e4Temp  <-- E4 skin temperature data
│   │   │   │   ├── mAcc    <-- Phone accelerometer data
│   │   │   │   ├── mGps    <-- Phone location data
│   │   │   │   ├── mGyr    <-- Phone gyroscope data
│   │   │   │   └── mMag    <-- Phone magnetometer data
│   │   │   └── 1598832660
│   │   ├── ...
│   │   └── user06
│   ├── user07-10
│   ├── user11-12
│   ├── user21-25
│   └── user26-30
└── raw
    ├── README
    ├── user01-06.7z
    ├── ...
    └── user_survey_2020.csv
```

### 3. Processing the dataset

The [parse etri](0_parse_etri.ipynb) notebook parses the interim data and saves it in the `processed` directory, which should be configured as the `etri_path` (and consequently `_etri_root_path`) in the [code_utils/path_conf.py](../../code_utils/path_conf.py) file. 

Specifically, the notebook does the following:
* Wearable and smartphone data:
    * parses the data; and timestamp of the files 
    * converts the 
    * splits the user data by day, and saves the data in parquet format, using the:<br>
    `<sig_name>_<year>_<month>_<day>.parquet`<br>
    format
* Labels:
    * parses the labels (using the mapping dict in [this file](../../code_utils/datasets/etri_mapping_dicts.py))
    * saves all the labels in a single parquet format file

This should result in the following directory structure:

```txt 
<_etri_root_dir>
├── interim
│   ├── ...
│   └── user26-30
├── processed
│   ├── labels.parquet      <-- The labels for all users and all days
│   ├── user01              <-- User folder, which contains the data for all days 
│   │   ├── e4Acc_2020_08_31.parquet
│   │   ├── e4Bvp_2020_08_31.parquet
│   │   ├── e4Eda_2020_08_31.parquet
│   │   ├── e4Hr_2020_08_31.parquet
│   │   ├── e4Temp_2020_08_31.parquet
│   │   ├── mAcc_2020_08_31.parquet
│   │   ├── mGyr_2020_08_31.parquet
│   │   ├── mGps_2020_08_31.parquet
│   │   ├── mGyr_2020_08_31.parquet
│   │   ├── mMag_2020_08_31.parquet
│   │   ├── ...parquet
│   │   └── mMag_2020_09_04.parquet
│   ├── user02
│   ├── user03
│   ├── user04
│   ├── user05
│   ├── user06
│   ├── user07
│   ├── user08
│   ├── user09
│   ├── user10
│   ├── user11
│   ├── user12
│   ├── user21
│   ├── user22
│   ├── user23
│   ├── user24
│   ├── user25
│   ├── user26
│   ├── user27
│   ├── user28
│   ├── user29
│   └── user30
└── raw
    ├── README
    ├── user01-06.7z
    ├── ...
    └── user_survey_2020.csv
```
