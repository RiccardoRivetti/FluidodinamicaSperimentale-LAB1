# Fluidodinamica Sperimentale - Lab 1: Wind Tunnel Force Measurements

Data-processing code for **Laboratory 1** of the *Fluidodinamica Sperimentale* (Experimental Fluid Dynamics) course, A.Y. 2026/27, Politecnico di Milano.

The lab measures the aerodynamic loads on a **NACA 0015** wing model in a low-speed wind tunnel using a load-cell balance. This repository contains the full Python pipeline: balance calibration, wind tunnel calibration, load and coefficient computation, wind tunnel corrections, comparison with XFOIL, and uncertainty estimation.

## Experiment at a glance

| Item | Value |
|---|---|
| Airfoil | NACA 0015 (15% thickness) |
| Chord | 100 mm |
| Span | 294 mm |
| Angle of attack | -4° to 18°, in steps of 2° |
| Force measurement | Load-cell balance, acquired with NI 9237 (signals in V/V) |
| Dynamic pressure | Pressure transducers (Delta OHM HD4V8T, 10 mbar), acquired with NI 9205 |
| Reference solver | XFOIL |

## Pipeline overview

```
load_cell_calibration.py ──┐
                           ├──> compute_loads.py ──> compute_uncertanty.py ──> plot_coefficients.py
wind_tunnel_calibration.py ┘            ▲
                                        │
                              experimental_setup.py
                          (wing and test section geometry)
```

1. **Balance calibration** (`load_cell_calibration.py`): identifies the calibration matrix **K** of the load-cell balance with a global least-squares fit. Known masses are applied through a lever arm at several angles; the mass of the hook is estimated separately and added to the applied masses.
2. **Wind tunnel calibration** (`wind_tunnel_calibration.py`): linear regression between the pressure signal across the contraction and the dynamic pressure at the test section, at several tunnel speeds. The slope gives the tunnel calibration coefficient, so that the dynamic pressure follows from the transducer signal during the tests.
3. **Load computation** (`compute_loads.py`): converts the raw balance signals into forces, then into lift and drag coefficients (C<sub>L</sub>, C<sub>D</sub>) as a function of the angle of attack. It also applies the wind tunnel corrections (horizontal buoyancy, solid blockage, wake blockage) following Barlow et al.
4. **Uncertainty analysis** (`compute_uncertanty.py`): propagates the measurement uncertainties to C<sub>L</sub> and C<sub>D</sub> with the root-sum-square (RSS) method.
5. **Plots** (`plot_coefficients.py`): produces the C<sub>L</sub>-α and C<sub>D</sub>-α curves, with measured, corrected and XFOIL results, and uncertainty bars.

`experimental_setup.py` defines the `Wing` and `TestSection` classes (airfoil, chord, span, thickness, shape factor, volume; test section dimensions and pressure gradient) shared by the other scripts.

## Repository structure

```
.
├── Calibration/                 # Calibration results (balance and wind tunnel)
├── Data/                        # Processed data and tabulated results
├── Figures/                     # Plots produced by the scripts
├── Output/                      # Script outputs
├── raw/                         # Raw acquisitions
├── xfoil/                       # XFOIL inputs and results for comparison
├── compute_loads.py
├── compute_uncertanty.py
├── experimental_setup.py
├── load_cell_calibration.py
├── plot_coefficients.py
├── wind_tunnel_calibration.py
├── LICENSE
└── README.md
```

## Getting started

### Requirements

- Python 3.9 or later
- NumPy, pandas, Matplotlib, SciPy

```bash
git clone https://github.com/RiccardoRivetti/FluidodinamicaSperimentale-LAB1.git
cd FluidodinamicaSperimentale-LAB1
pip install numpy pandas matplotlib scipy
```

### Running the analysis

Run the scripts from the repository root, in this order:

```bash
python load_cell_calibration.py Data/weights_measure.csv
python wind_tunnel_calibration.py Data/wind_measure.csv
python compute_loads.py Data/airfoil_measure.csv
python compute_uncertanty.py Data/airfoil_measure.csv
python plot_coefficients.py Output/coefficients.csv --plot
```

Make sure the input CSV files (balance calibration, hook mass, tunnel calibration and airfoil measurements) are in place before running, and check the paths set at the top of each script.

## Methods in brief

- **Balance calibration:** the signals-to-loads relation is a matrix identified over all calibration points at once, so cross-talk between channels is accounted for.
- **Dynamic pressure:** during the airfoil tests, q is obtained from the tunnel calibration slope applied to the transducer signal.
- **Corrections:** horizontal buoyancy (from the streamwise pressure gradient in the test section), solid blockage and wake blockage, with the empirical factors taken from Barlow, Rae and Pope.
- **Uncertainty:** RSS propagation on C<sub>L</sub> and C<sub>D</sub>. Since only a single acquisition per angle is available, repeated measurements would be needed to quantify the random component of the error.

## License

Distributed under the GNU General Public License v3.0. See [`LICENSE`](LICENSE) for details.

## Author

Riccardo Rivetti
