# PyXplore Desktop

A desktop application for X-ray diffraction analysis based on the PyXplore (PyWPEM) library.

## Features

- **Background Deduction**: Remove background from XRD data using FFT and Savitzky-Golay filtering
- **CIF Preprocess**: Parse CIF files and calculate crystallographic parameters
- **XRD Simulation**: Simulate XRD patterns from crystal structures
- **XRD Refinement**: Full pattern decomposition and lattice constant refinement using WPEM method
- **Amorphous Analysis**: Amorphous peak fitting and RDF calculation
- **XPS Analysis**: X-ray photoelectron spectroscopy decomposition
- **EXAFS Analysis**: Extended X-ray absorption fine structure analysis
- **Batch Processing**: Process multiple files at once

## Requirements

- Python 3.8+
- PyQt5 5.15+
- PyXplore library (included in src/)
- Conda environment: RAG (for TensorFlow compatibility)
- Other dependencies listed in requirements.txt

## Installation

1. Make sure you have conda installed and the RAG environment available:
   ```bash
   conda env list
   ```

2. Install dependencies in RAG environment (if not already installed):
   ```bash
   conda run -n RAG pip install -r requirements.txt
   ```

3. Make sure the PyXplore source is in the correct location:
   - The `src` folder should be in the parent directory of `desktop_app`

4. Run the application:

**Option A: Using batch script**
```bash
cd desktop_app
run.bat
```

**Option B: Using Python script**
```bash
cd desktop_app
python run.py
```

**Option C: Direct conda run**
```bash
conda run -n RAG python desktop_app/main.py
```

## Usage

### Background Deduction

1. Select the XRD data file (CSV, TXT, DAT, or XRDML format)
2. Set the parameters:
   - Spectrum type (XRD, Raman, XPS)
   - Wavelength
   - Low frequency filter percentage
   - Background split number
   - SG filter window length
   - Polynomial order
3. Click "Start Processing"
4. Save the results

### CIF Preprocess

1. Select a CIF file
2. Set parameters:
   - X-ray wavelength
   - 2θ range
   - Whether to show unit cell
   - Whether to calculate extinction
3. Click "Parse CIF"
4. Export parameters if needed

### XRD Simulation

1. Select a CIF file
2. Set simulation parameters:
   - Wavelength
   - 2θ range
   - Super cell settings
   - Grain size
   - Peak width
   - Zero shift
3. Click "Start Simulation"
4. Save results

### XRD Refinement

1. Select the required data files:
   - Original data
   - Background-removed data
   - Background data
2. Add CIF files for the crystal phases
3. Set refinement parameters:
   - Wavelength
   - Variance
   - bta (PV function parameter)
   - Maximum iterations
   - CPU cores
   - Mode (REFINEMENT or ANALYSIS)
4. Click "Start Refinement"

### Amorphous Analysis

Two tabs available:
- **Amorphous Peak Fitting**: Fit amorphous peaks using Gaussian mixture model
- **RDF Calculation**: Calculate radial distribution function

### XPS Analysis

1. Select the data files
2. Add atom identifiers (element, electronic state, binding energy)
3. Set parameters
4. Click "Start Fitting"

### EXAFS Analysis

1. Select XAFS data file
2. Set parameters:
   - k-axis power
   - R-space maximum distance
   - k-point cutoff
   - Spline order
   - Window size
   - Transform method (Fourier/Wavelet)
3. Click "Start Analysis"

### Batch Processing

1. Select processing mode:
   - Batch Background Deduction
   - Batch CIF Preprocess
   - Batch XRD Simulation
2. Add files or select a directory
3. Click "Start Batch Processing"

## Project Structure

```
desktop_app/
├── main.py                 # Application entry point
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration
│   ├── utils.py            # Utility functions
│   ├── base_page.py        # Base page class
│   ├── main_window.py      # Main window
│   ├── modules/            # Functional modules
│   │   ├── background/     # Background deduction
│   │   ├── cif_preprocess/ # CIF preprocess
│   │   ├── xrd_simulation/ # XRD simulation
│   │   ├── xrd_refinement/ # XRD refinement
│   │   ├── batch/         # Batch processing
│   │   ├── history/        # History records
│   │   ├── xps/           # XPS analysis
│   │   ├── exafs/         # EXAFS analysis
│   │   └── amorphous/     # Amorphous analysis
│   ├── widgets/           # Custom widgets
│   └── resources/         # Resources (icons, styles)
├── modules/              # Reserved module slot
└── requirements.txt       # Python dependencies
```

## Build / Packaging

This project uses **PyInstaller** to package the application into a standalone `.exe` for Windows.

### Prerequisites

```bash
pip install pyinstaller
```

### Quick Build (Windows)

Double-click or run in terminal:

```bash
build.bat
```

Or use the Python script (cross-platform):

```bash
python build.py
```

### Build Modes

| Mode | Command | Output |
|------|---------|--------|
| Default (onedir) | `build.bat` or `python build.py` | `dist/PyXplore_Desktop/PyXplore_Desktop.exe` |
| Single file | `python build.py onefile` | `dist/PyXplore_Desktop.exe` |
| Clean only | `python build.py clean` | Deletes `dist/` and `build/` |
| Check deps | `python build.py check` | Verifies all dependencies |

### Files Created by Build

```
PyXplore_Desktop/              # ← dist/
├── PyXplore_Desktop.exe       # ← 主程序
├── output/                    # ← 用户数据目录（程序自动创建）
├── temp/                      # ← 临时文件目录
└── ...依赖文件...
```

### Notes

- **打包后的 `output/` 和 `temp/` 目录位于 exe 同级目录**，而不是程序内部
- 如果需要自定义 exe 图标，请准备一个 `.ico` 文件，修改 `PyXplore_Desktop.spec` 中的 `icon` 字段
- TensorFlow 体积较大（约 500MB），首次打包耗时较长，请耐心等待
- 如果打包后运行出错，可先尝试 `python build.py rebuild --no-clean` 查看详细错误信息

## License

MIT License - See LICENSE file for details.

## Citation

If you use PyXplore Desktop in your research, please cite:

```bibtex
@article{cao2026wpem,
  title={AI-Driven Structure Refinement of X-ray Diffraction},
  author={Bin Cao, Qian Zhang, Zhenjie Feng, Taolue Zhang, Jiaqiang Huang, Lu-Tao Weng, Tong-Yi Zhang},
  journal={arXiv preprint},
  year={2026},
  url={https://arxiv.org/abs/2602.16372v1}
}
```

## Author

Bin Cao - Hong Kong University of Science and Technology (Guangzhou)

For questions or support, please contact: bcao686@connect.hkust-gz.edu.cn