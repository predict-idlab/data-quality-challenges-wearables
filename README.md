<div align="center">
<h1>:mag: Addressing Data Quality Challenges <br>in Remote Wearable Monitoring
</div>

Codebase & further details for the paper:
> Addressing Data Quality Challenges in Observational Ambulatory Studies: Analysis, methodologies and practical solutions for wrist-worn wearable monitoring

**preprint**: `TODO` - see [Citation](#citation_ref) for bibtex.

In this project, we address data quality challenges encountered in remote wearable monitoring by utilizing two distinct datasets:

1. ETRI Lifelog 2020: Accessible at ETRI Lifelog 2020<br> https://nanum.etri.re.kr/share/schung/ETRILifelogDataset2020?lang=En_us

2. mBrain21: https://www.kaggle.com/datasets/jonvdrdo/mbrain21/data

For each identified challenge, denoted as `C<ID>`, we have curated a dedicated notebook. These notebooks are specifically designed to demonstrate effective countermeasures against the respective challenges.

## 📖 Table of contents
- [📰 How is the repository structured?](#-how-is-the-repository-structured)
  - [🛠️ Installation](#installation_ref)
- [🗃️ How to acquire the data](#️-how-to-acquire-the-data)
  - [ETRI lifelog 2020](#etri-lifelog-2020)
  - [mBrain21](#mbrain21)
  - [Utilizing this repository](#utilizing-this-repository)
- [✨ Challenges & features](#-challenges--features)
  - [📷 Dashboards](#-dashboards)
    - [ETRI](#etri)
    - [mBrain](#mbrain)
  - [⌚ off-wrist detection](#-off-wrist-detection)
  - [✒️ Data annotation](#data_annotation_ref)
- [📖 Citation](#citation_ref)
- [📝 License](#license_ref)


## 📰 How is the repository structured

```txt
├── code_utils       <- module containing all shared code
│   ├── empatica     <- Empatica E4 specific code (signal processing pipelines)
│   ├── etri         <- ETRI specific code (data parsing, visualization, dashboard)
│   ├── mbrain       <- mBrain specific code (data parsing, visualization, dashboard)
│   └── utils        <- utility code (dashboard, dataframes, interaction analysis)
├── loc_data         <- local data folder in which intermediate data is stored
└── notebooks        <- Etri and mBrain specific notebooks 
    ├── etri
    └── mBrain
```


<a name="installation_ref"></a>
### 🛠️ Installation

This repository uses [poetry](https://python-poetry.org/) as dependency manager.
A specification of the dependencies is provided in the [`pyproject.toml`](pyproject.toml) and [`poetry.lock`](poetry.lock) files.

You can install the dependencies in your Python environment by executing the following steps;
1. Install poetry: https://python-poetry.org/docs/#installation
2. Activate you poetry environment by calling `poetry shell`
3. Install the dependencies by calling `poetry install`

## 🗃️ How to acquire the data
### ETRI lifelog 2020
The ETRI lifelog 2020 is made available at https://nanum.etri.re.kr/share/schung/ETRILifelogDataset2020?lang=En_us.

In order to download the dataset, you should first create an account on the ETRI Nanum website.
Afterwards, fill in the license agreement form, and upon approval, you will be able to download the dataset via the web platform.

### mBrain21
A subset of the mBrain21 dataset is made available on [Kaggle datasets](https://www.kaggle.com/datasets/jonvdrdo/mbrain21/data):
The dataset can be downloaded via the following command:
```bash
kaggle datasets download -d jonasvdd/mbrain21
```

### Utilizing this repository
Make sure that you've extended the [path_conf.py](code_utils/path_conf.py) file's hostname *if- statement* with your machine's hostname and that you've configured the paths to the `mBrain` and `ETRI` datasets.

# ✨ Challenges & features
Below, a subset of exemplified challenges and features are listed.

## 📷 Dashboards
This section elaborates on the longitudinal time series visualization dashboards for both the ETRI and mBrain datasets.

Each dashboard contains, as can be observed in the figures below, a left column with selection boxes.
The General flow to visualize a specific time series excerpt is as follows:
- Select a `folder` (in our case, all data from the ETRI and MBRAIN dataset are stored in the same folder - so you can only select from one option)
- Select an user (e.g, user30 for the ETRI dataset)
> *note*: After selection a folder and user, the time-span selection will be updated to the available time-span for the selected user-folder combination
- Select sensors (e.g. 'E4 accelerometer' and 'E4 temperature')

Finally, to visualize, press the *run interact* button.


### ETRI
Once the ETRI dataset has been downloaded and parsed via the [ETRI parsing](notebooks/etri/0_parse_etri.ipynb) notebook, the corresponding [dashboard script](code_utils/etri/dashboard.py) can be used to explore & analyse the data.
The dashboard can be run via the following command (after activating the poetry shell)

```bash
python code_utils/etri/dashboard.py
```
The output should show the following:
> *Dash is running on http://0.0.0.0:\<PORT\>*


In the dashboard screenshot below, both the wearable data and the application event labels are visualized. One can immediately observe that this participant tends to be more alone during evenings (light blue shaded area of the lower row in the upper subplot). During the weekends (indicated with a gray shaded area), this participant tends to be alone and spend a lot of time at home.

![](figures/ETRI_dashboard.png)

### mBrain
The dashboard can be run via the following command (after activating the poetry shell)
```bash
python code_utils/mBrain/dashboard.py
```
The output will show the following:
> *Dash is running on http://0.0.0.0:\<PORT\>*

Below, we provide a screenshot of the mBrain dashboard. As can be observed from the selection box on the left side, the dashboard shows the headache timeline of the participant, along with the Empatica E4 its accelerometer signal and the smartphone light data. When hovering over a headache event, as shown in the upper plot, one can see the associated characteristics of the headache event.

![](figures/MBRAIN_dashboard.png)

## ⌚ off-wrist detection
The wearable non-wear detection is demonstrated in the [C5.1_off_wrist_detection](notebooks/mBrain/C5_wearable_off_wrist.ipynb) notebook.<br><br>
Moreover, the [C7_missing_data](notebooks/mBrain/C7_missing_data.ipynb) notebook demonstrates how this off-wrist pipeline can be used to remove non-wear bouts as a preprocessing step.

Below, a screenshot of the off-wrist pipeline devised by [Böttcher et al. (2022)](https://www.nature.com/articles/s41598-022-25949-x) is shown.
![](figures/off_wrist_bottcher.png)

<a name="data_annotation_ref"></a>

## ✒️ Data annotation
The [C5.1_label_off_wrist](notebooks/mBrain/C5.1_Label_off_wrist.ipynb) mBrain notebook demonstrates how large bouts of time-series data can be annotated using [plotly-resampler](https://github.com/predict-idlab/plotly-resampler).

Below a demo is shown on how this annotation tool can be used to label `off-wrist` periods.
![](figures/annotation_demo.gif)

<a name="citation_ref"></a>
## 📖 Citation
```bibtex
@article{TODO,
  title={TODO},
  author={Van Der Donckt, Jonas and TODO},
  journal={arXiv preprint arXiv:TODO},
  year={2023},
}
```
<a name="license_ref"></a>
## 📝 License
The code is available under the *imec* [license](LICENSE).

---

<p align="center">
👤 <i>Jonas Van Der Donckt</i>
</p>
