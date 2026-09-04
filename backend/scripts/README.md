# Model training

`train_aps_model.py` downloads and verifies the official UCI APS Failure at
Scania Trucks archive, creates disjoint fit/calibration/threshold partitions,
trains the classifier, and evaluates it once on the official test split.

Run from `backend/`:

~~~bash
poetry install
poetry run python scripts/train_aps_model.py
~~~

Use `--archive /absolute/path/to/archive.zip` to train without downloading. The
generated artifacts are written to `app/ml/artifacts/`. Do not replace the
bundled model without reviewing the regenerated metrics in `metadata.json`.

