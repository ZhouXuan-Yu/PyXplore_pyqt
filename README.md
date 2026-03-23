

<p align="center">
  <img src="https://github.com/Bin-Cao/TCGPR/assets/86995074/28f69830-4ece-43b3-a887-e78fdb25bcab" width="140" alt="PyWPEM Logo"/>
</p>

<p align="center">
  <strong>Python Toolkit for X-ray Diffraction Simulation, Analysis, and AI-driven Structure Refinement</strong> 

</p>

<p align="center">
  <a href="https://bin-cao.github.io/PyWPEM/">Project Homepage</a> ·  
  <a href="https://pyxplore.netlify.app/">Algorithm Documentation</a> ·
  <a href="https://arxiv.org/abs/2602.16372">Paper (arXiv)</a> ·
  <a href="https://www.researchgate.net/publication/400962382_Supplementary_Information_for_AI-Driven_Structure_Refinement_of_X-ray_Diffraction?_sg%5B0%5D=Dtl5qCZhJGfQkbUlv7_PX1Kx7TwdxuOHNLZVyFl1KGrHUSRNKl2vANa2VizCBgzhvFZHOprN-9U2OY37DKVt7bfexdXMbmSSl2dV9rdY.wb_SKqOPT-AERbwQd_WLh7pYYIbpMj0u3f0wWIKra43GjGnKbuLqobFTgQ1YfutJIXWN8RGFN5y9oCoEcEyeoQ&_tp=eyJjb250ZXh0Ijp7ImZpcnN0UGFnZSI6ImxvZ2luIiwicGFnZSI6InByb2ZpbGUiLCJwcmV2aW91c1BhZ2UiOiJwcm9maWxlIiwicG9zaXRpb24iOiJwYWdlQ29udGVudCJ9fQ">Supplementary Information</a> ·
  <a href="https://www.pepy.tech/projects/PyXplore">Download Statistics</a>
</p>






<p align="center">
  <img width="600" src="https://github.com/user-attachments/assets/e37ee8c4-8bdd-4de0-b27e-2ce7270a8a07" />
</p>

Other tools include [XQueryer](https://github.com/Bin-Cao/XQueryer) for initial structure inference and [PRDNet](https://github.com/Bin-Cao/PRDNet) for crystal property prediction.

 
---

## Overview [![PyPI Downloads](https://static.pepy.tech/personalized-badge/pyxplore?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/pyxplore)

**[PyXplore](https://pyxplore.netlify.app/)** is a modular Python framework for **X-ray diffraction (XRD) simulation, decomposition, quantitative analysis, and AI-assisted structure refinement**.

It integrates:

* Physics-based diffraction modeling
* EM-based Bragg optimization
* Structure graph construction
* Extinction and Wyckoff analysis
* Amorphous phase quantification
* AI-driven structural refinement

The toolkit is designed for reproducible scientific workflows in materials characterization and AI for Science research.



Install from PyPI and [Install the dependencies](https://github.com/Bin-Cao/PyWPEM/blob/main/INSTALL.md):

```bash
pip install PyXplore
```

Upgrade to the latest version:

```bash
pip install --upgrade PyXplore
```


---

## Key Features

* **XRD Simulation**
  Accurate diffraction pattern generation from crystallographic information.

* **Peak Decomposition & Quantitative Analysis**
  WPEM-based decomposition and volume fraction determination.

* **Bragg Law Optimization (EM Framework)**
  Expectation-Maximization-based parameter solving.

* **Extinction & Wyckoff Handling**
  Symmetry-aware preprocessing and structural filtering.

* **Graph-Based Structure Representation**
  Crystal graph construction for downstream machine learning tasks.

* **Amorphous Structure Analysis**
  RDF-based quantitative evaluation.

* **Multi-modal Extension**
  Integrated modules for XAS and XPS analysis.

---

## Architecture Overview

```text
PyWPEM/
├── WPEM.py
├── XRDSimulation/
├── EMBraggOpt/
├── Refinement/
├── StructureOpt/
├── GraphStructure/
├── Extinction/
├── Amorphous/
├── Background/
├── Plot/
├── DecomposePlot/
├── WPEMXAS/
├── WPEMXPS/
└── refs/
```

The design follows a **physics-consistent, modular architecture**, enabling independent or pipeline-based execution.

---

## Tables & Figures

<p align="center">
  <img width="450" src="https://github.com/user-attachments/assets/da5bd320-3651-4223-b862-06fb5ce1f96a" />
</p>

<p align="center">
  <img width="700" src="https://github.com/user-attachments/assets/50b1aacc-6a4f-4b58-95fb-a4094da60055" />
</p>

---

## Scientific Reference

If you use **PyWPEM** in your research, please cite:

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

[![Star History Chart](https://api.star-history.com/svg?repos=Bin-Cao/PyWPEM&type=Date)](https://star-history.com/#Bin-Cao/PyWPEM&Date)





---

## Contributing

We welcome contributions from the community.

* Report bugs via Issues
* Propose features
* Submit pull requests
* Contact for academic collaboration

Please ensure code readability, documentation clarity, and scientific correctness before submission.

---

## License

This project is released under the MIT License.

Free for academic and commercial use.
Please cite related publications when used in scientific research.

---

<table>
  <tr>
    <td width="160" align="center" valign="top">
      <img src="https://github.com/user-attachments/assets/7e77bd5a-42d6-45db-b8e6-2c82cac81b9d" width="140" style="border-radius: 50%;"/>
    </td>
    <td valign="top">
      <b>For any inquiries or assistance, feel free to contact Mr. CAO Bin at:</b><br>
      📧 Email: <a href="mailto:bcao686@connect.hkust-gz.edu.cn">bcao686@connect.hkust-gz.edu.cn</a><br><br>
      Cao Bin is a PhD candidate at the <b>Hong Kong University of Science and Technology (Guangzhou)</b>, 
      under the supervision of Professor <a href="https://gbaaa.org.hk/en-us/article/67">Zhang Tong-Yi</a>. His research focuses on 
      <b>AI for science</b>, especially intelligent crystal-structure analysis and discovery. 
      Learn more about his work on his 
      <a href="https://bin-cao.github.io/">homepage</a>.
    </td>
  </tr>
</table>
