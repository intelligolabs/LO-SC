# LO-SC: Local-only Split Computing for Accurate Deep Learning on Edge Devices #

Official implementation of the paper [LO-SC: Local-only Split Computing for Accurate Deep Learning on Edge Devices](https://intelligolabs.github.io/LO-SC/) accepted at the 38th International Conference on VLSI Design (VLSID 2025).

## Installation ##
**1. Repository setup:**
* `$ git clone https://github.com/intelligolabs/LO-SC`
* `$ cd LO-SC`

**2. Conda environment setup:**
* `$ conda create -n lo_sc python=3.10`
* `$ conda activate lo_sc`
* `$ pip install -r requirements.txt`

## Run LO-SC ##
To run the dimonstrative example of LO-SC, use the file `demonstrative_example.ipynb`.
For a detailed, step-by-step explanation of the code and the mathematical aspects of the proposal, refer to `optimizer_explanation.ipynb`.

## Authors ##
Luigi Capogrosso<sup>1</sup>, Enrico Fraccaroli<sup>1,2</sup>, Marco Cristani<sup>1</sup>, Franco Fummi<sup>1</sup>, Samarjit Chakraborty<sup>2</sup>

<sup>1</sup> *Department of Engineering for Innovation Medicine, University of Verona, Italy*

<sup>2</sup> *Department of Computer Science, The University of North Carolina at Chapel Hill, USA*

<sup>1</sup> `name.surname@univr.it`, <sup>2</sup> `enrifrac@cs.unc.edu`, `samarjit@cs.unc.edu`

## Citation ##
If you use [**LO-SC**](https://ieeexplore.ieee.org/abstract/document/10900702), please, cite the following paper:
```
@InProceedings{capogrosso2025sc,
    author    = {Capogrosso, Luigi and Fraccaroli, Enrico and Cristani, Marco and Fummi, Franco and Chakraborty, Samarjit},
    booktitle = {38th International Conference on VLSI Design (VLSID)},
    title     = {{LO-SC: Local-Only Split Computing for Accurate Deep Learning on Edge Devices}},
    year      = {2025},
    doi       = {10.1109/vlsid64188.2025.00089},
}
```