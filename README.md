## Dev notes

- after ingestion and sampling done, build a new notebook for efficient sampling
- exploration and data ingestion reuse a lot of the same concepts, after pipeline is built, get exploration to use the better methods
- now, you are downloading raw, then sampling; build a pipeline that pulls raw, samples, and deletes what is not needed
- when referencing what is needed, refer sampled, not raw (as raw will be the biggest)
- there;s room for pipeline to be interrupted by a bad filename; encourage it to pass to next instead of stopping

## descriptions

This notebook ingests the [Adver-City](https://labs.cs.queensu.ca/quarrg/datasets/adver-city/) synthetic dataset for use in investigating cooperative perception in adverse weather conditions. As the dataset is larger, it selectively extracts required files (in accordance with a sampling plan) and cleans up working files along the way. The end result is clean dataset sliced into train/val/test, suitable for machine learning applications. 

A broader exploration of the dataset is provided [here](./initial_explore.ipynb).

- ensure to source virtual environment located at `./venv/bin/python` before running: `source venv/bin/activate`
- requirements have been exported to `pip freeze > requirements.txt`
- to unzip the `.7z` files, install p7zip as follows: `brew install p7zip`