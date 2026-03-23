# PyXplore Desktop

<p align="center">
  <img src="logos/Logo.png" width="200" alt="PyXplore Logo"/>
</p>

<p align="center">
  <strong>Desktop Application for X-ray Diffraction Analysis and AI-driven Structure Refinement</strong>
</p>

<p align="center">
  <a href="https://github.com/ZhouXuan-Yu/PyXplore_pyqt">GitHub Repository</a> ·
  <a href="https://pyxplore.netlify.app/">Algorithm Documentation</a> ·
  <a href="https://arxiv.org/abs/2602.16372">Paper (arXiv)</a>
</p>

---

## Overview

**PyXplore Desktop** is a PyQt5-based desktop application that provides a graphical interface for the [PyXplore (PyWPEM)](https://github.com/Bin-Cao/PyWPEM) library. It integrates comprehensive X-ray diffraction (XRD) analysis capabilities with AI-driven structure refinement, enabling researchers to perform complex crystallographic analyses through an intuitive desktop environment.

---

## Features

### Core Analysis Modules

| Module | Description |
|--------|-------------|
| **Background Deduction** | Remove background from XRD data using FFT filtering and Savitzky-Golay smoothing |
| **CIF Preprocess** | Parse CIF files, calculate crystallographic parameters, and visualize unit cells |
| **XRD Simulation** | Simulate XRD patterns from crystal structures with configurable parameters |
| **XRD Refinement** | Full pattern decomposition and lattice constant refinement using the WPEM method |
| **Amorphous Analysis** | Gaussian mixture model peak fitting and Radial Distribution Function (RDF) calculation |
| **XPS Analysis** | X-ray photoelectron spectroscopy decomposition and peak fitting |
| **EXAFS Analysis** | Extended X-ray absorption fine structure analysis with Fourier/wavelet transforms |
| **Batch Processing** | Process multiple files with consistent parameters |

### Key Capabilities

- **Multi-format Support**: Import CSV, TXT, DAT, XRDML and other common data formats
- **Interactive Visualization**: Real-time plotting with zoom, pan, and export capabilities
- **AI-assisted Refinement**: WPEM-based optimization for accurate quantitative phase analysis
- **Extinction & Wyckoff Handling**: Symmetry-aware preprocessing for structural filtering
- **Multi-modal Analysis**: Integrated support for XRD, XPS, and XAS techniques

---

## Installation

### Prerequisites

- Python 3.8+
- Conda environment (recommended: RAG environment for TensorFlow compatibility)
- Windows/Linux/macOS

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ZhouXuan-Yu/PyXplore_pyqt.git
   cd PyXplore_pyqt
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_desktop.txt
   ```

3. **Run the application**:
   ```bash
   cd desktop_app
   python run.py
   ```

   Or use the batch script:
   ```bash
   cd desktop_app
   run.bat
   ```

---

## User Interface

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  PyXplore Desktop                                    [─][□][×]  │
├─────────────────────────────────────────────────────────────────┤
│  File  Edit  View  Tools  Help                                  │
├────────────┬────────────────────────────────────────────────────┤
│            │                                                     │
│  📁 Background     │                                              │
│  📁 CIF Preprocess│          Content Area                        │
│  📁 XRD Simulation│    (Dynamic based on selected module)       │
│  📁 XRD Refinement │                                              │
│  📁 Amorphous      │                                              │
│  📁 XPS            │                                              │
│  📁 EXAFS          │                                              │
│  📁 Batch          │                                              │
│            │                                                     │
├────────────┴────────────────────────────────────────────────────┤
│  Status: Ready                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Module Descriptions

#### Background Deduction
- Import XRD, Raman, or XPS data files
- FFT-based low-frequency filtering
- Savitzky-Golay smoothing for background extraction
- Configurable parameters: filter percentage, split number, polynomial order

#### CIF Preprocess
- Parse CIF crystallographic files
- Calculate lattice constants (a, b, c, α, β, γ)
- Generate atomic coordinate tables
- Optional structure relaxation using M3Gnet

#### XRD Simulation
- Simulate diffraction patterns from crystal structures
- Configurable wavelength (CuKα, CoKα, MoKα, custom)
- Super cell generation and solid solution modeling
- Peak broadening based on grain size
- Zero shift correction

#### XRD Refinement
- WPEM-based full pattern decomposition
- Multi-phase quantitative analysis
- Lattice constant optimization
- R-factor reporting (Rp, Rwp)

#### Amorphous Analysis
- **Peak Fitting**: Gaussian mixture model for amorphous peak deconvolution
- **RDF Calculation**: Radial distribution function computation from diffraction data

#### XPS Analysis
- Peak decomposition for photoelectron spectra
- Support for multiple atomic species and satellite peaks
- Pseudo-Voigt function fitting

#### EXAFS Analysis
- k-space processing and weighting
- Fourier transform to R-space
- Wavelet transform option for enhanced resolution

#### Batch Processing
- Process multiple files in sequence
- Template-based parameter management
- Progress tracking and result export

---

## Project Structure

```
PyXplore_pyqt/
├── desktop_app/
│   ├── main.py                 # Application entry point
│   ├── run.py                  # Launch script
│   ├── run.bat                 # Windows launch script
│   ├── app/
│   │   ├── main_window.py      # Main window (QMainWindow)
│   │   ├── base_page.py        # Base class for module pages
│   │   ├── config.py           # Configuration management
│   │   ├── utils.py            # Utility functions
│   │   └── modules/            # Functional modules
│   │       ├── background/     # Background deduction
│   │       ├── cif_preprocess/ # CIF preprocessing
│   │       ├── xrd_simulation/ # XRD simulation
│   │       ├── xrd_refinement/ # XRD refinement
│   │       ├── amorphous/      # Amorphous analysis
│   │       ├── xps/           # XPS analysis
│   │       ├── exafs/         # EXAFS analysis
│   │       └── batch/         # Batch processing
│   ├── requirements.txt        # Desktop app dependencies
│   └── ConvertedDocuments/    # Sample data files
├── src/                        # PyXplore core library
├── logos/                      # Application logos
├── docs/                       # Documentation
└── requirements.txt           # Core dependencies
```

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Frontend Framework | PyQt5 5.15+ |
| Visualization | Matplotlib + FigureCanvasQTAgg |
| Data Processing | NumPy, Pandas, SciPy |
| Core Algorithms | PyXplore (WPEM, M3Gnet) |
| AI/ML | TensorFlow (via M3Gnet) |

---

## Scientific Reference

If you use **PyXplore Desktop** in your research, please cite:

```bibtex
@article{cao2026wpem,
  title={AI-Driven Structure Refinement of X-ray Diffraction},
  author={Bin Cao, Qian Zhang, Zhenjie Feng, Taolue Zhang, Jiaqiang Huang, Lu-Tao Weng, Tong-Yi Zhang},
  journal={arXiv preprint},
  year={2026},
  url={https://arxiv.org/abs/2602.16372v1}
}
```

---

## License

This project is released under the MIT License.

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## Contact

For questions or support, please contact:
- **Email**: bcao686@connect.hkust-gz.edu.cn
- **Affiliation**: Hong Kong University of Science and Technology (Guangzhou)
