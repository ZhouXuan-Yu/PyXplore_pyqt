## PyXplore setup from GitHub


### 1. Clone the repository

```bash
git clone https://github.com/Bin-Cao/PyWPEM.git
cd PyWPEM
```

### 2. Create and activate a conda environment

```bash
conda create -n pyxplore python=3.10 -y
conda activate pyxplore
```

### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Quick smoke tests

This checks that the local GitHub source tree is importable:

```bash
python -c "import src.Background.BacDeduct; print('local source import ok')"
```

If you want to test the full all-in-one entrypoint:

```bash
python -c "import src.WPEM; print('src.WPEM import ok')"
```
