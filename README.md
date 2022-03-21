# (Super preliminary and naive) LCLS mockup Epics system

## Env Setup

Make sure you have conda set up, open up a terminal and create a new conda env from `environment.yml` by running:

```bash
conda env create -f environment.yml
```

## Usage

### Start the Epics server

First activate the `lcls-mockup` conda env in a terminal:

```bash
conda activate lcls-mockup
```

Then start the Epics server:

```bash
python start_epics_server.py
```

### Play with the Epics server

Open up the `epics_pv_test.ipynb` notebook after activating the `lcls-mockup` env, then go through the cells and change them as you like. Good luck!

## Dev

### Change the mockup system logics

Have a look at `write` method in `myDriver` class. Also here is the [docs](https://pcaspy.readthedocs.io/en/latest/tutorial.html).
