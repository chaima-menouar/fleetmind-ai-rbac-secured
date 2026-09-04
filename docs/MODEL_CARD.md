# APS failure model card

## Intended use

This model demonstrates cost-sensitive predictive maintenance on historical
heavy-truck data. It classifies whether a recorded failure is related to the
truck air pressure system (APS). The output is advisory and is not approved for
vehicle control or safety decisions.

## Data

- **Dataset:** [APS Failure at Scania Trucks](https://archive.ics.uci.edu/dataset/421/aps%2Bfailure%2Bat%2Bscania%2Btrucks)
- **DOI:** <https://doi.org/10.24432/C51S51>
- **Official development split:** 60,000 rows, including 1,000 APS failures
- **Official test split:** 16,000 rows, including 375 APS failures
- **Inputs:** 170 anonymized operational features with missing values
- **Catalog license:** CC BY 4.0

The script verifies the downloaded archive against SHA-256
`5504d0402f54faaf97ac0ca085a621645763f5cfea2eb29c592b057d43d4db89`.
The complete raw dataset is not committed to this project.

The generated model also receives its own SHA-256 in `metadata.json`. The API
checks that value before deserializing the bundled artifact, which detects an
accidentally corrupted or mismatched model file.

## Training design

The official 60,000-row development split is stratified into three disjoint
parts using random seed 42:

| Purpose | Rows | Used for |
| --- | ---: | --- |
| Fit | 42,000 | Class-balanced histogram gradient boosting |
| Calibration | 9,000 | Sigmoid score calibration |
| Threshold selection | 9,000 | Minimize the dataset's asymmetric error cost |

The official test split remains untouched until the final evaluation. The
classifier handles missing values natively. The decision threshold is 0.036,
selected without looking at the official test labels.

The dataset defines a cost of 10 for a false alert and 500 for a missed APS
failure. This is why recall and total cost matter more than raw accuracy.

## Held-out results

These metrics come from all 16,000 rows in the official test split:

| Metric | Result |
| --- | ---: |
| Recall | 93.07% |
| Precision | 53.94% |
| F1 | 68.30% |
| Balanced accuracy | 95.58% |
| ROC-AUC | 99.16% |
| Average precision | 86.61% |
| True negatives | 15,327 |
| False positives | 298 |
| False negatives | 26 |
| True positives | 349 |
| Official error cost | 15,980 |
| All-negative baseline cost | 187,500 |
| Cost reduction vs baseline | 91.48% |

The project reports precision explicitly: a high-recall operating point creates
more false alerts. It never presents the score as a guarantee.

## Reproduce the model

From `backend/`:

~~~bash
poetry install
poetry run python scripts/train_aps_model.py
~~~

The script downloads the exact official archive when it is not already present,
then regenerates the model, metadata, and 12 small demonstration samples. No
external account or paid API is required.

## Limitations

- Feature semantics are anonymized, so the model cannot explain named vehicle
  components or accept normal dashboard fields such as battery percentage.
- The target is APS-related failure, not general breakdown prediction.
- Results measure one historical Scania test split and may not transfer to a
  different fleet, geography, sensor stack, or time period.
- The included evaluation samples are for transparent demonstration, not live
  monitoring.
- Before operational use, the model would need representative current data,
  drift monitoring, calibrated service costs, security review, and human approval.
