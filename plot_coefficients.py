import numpy as np
import matplotlib.pyplot as plt
import argparse

bluepoli1 = "#102C53"
bluepoli2 = "#0BA4FF"
bluepoli3 = "#67B2C6"

class Polar:
    def __init__(self, alpha, CD, CL, CM):
        self.alpha = alpha
        self.CD = CD
        self.CL = CL
        self.CM = CM

def import_coefficients(filename):
    coeffs = np.loadtxt(filename, delimiter=",", skiprows=1)

    alpha = coeffs[:,0]
    CD = coeffs[:,1]
    CL = coeffs[:,2]
    CM = coeffs[:,3]

    polar = Polar(alpha,CD,CL,CM)

    return polar

def select_coefficient(polar,name):
    match name:
        case "C_D":
            return polar.CD
        case "C_L":
            return polar.CL
        case "C_M":
            return polar.CM
        case _:
            raise NameError

def plot_coefficient(polar_data, polar_xfoil, name, show_plot):
    fig, ax = plt.subplots()

    coeff_data = select_coefficient(polar_data,name)
    coeff_xfoil = select_coefficient(polar_xfoil,name)

    ax.plot(polar_data.alpha,coeff_data,label="Data",marker="s",color=bluepoli1)
    ax.plot(polar_xfoil.alpha,coeff_xfoil,label="xfoil",color=bluepoli2,linestyle="--")

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend()
    plt.xlabel(r"$\alpha$ [deg]")
    plt.ylabel(f"${name}$ [-]")

    if show_plot:
        plt.show()

def plot_polar(polar_data, polar_xfoil,show_plot):
    fig, ax = plt.subplots()

    ax.plot(polar_data.CD,polar_data.CL,label="Data",marker="s",color=bluepoli1)
    ax.plot(polar_xfoil.CD,polar_xfoil.CL,label="xfoil",color=bluepoli2,linestyle="--")

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend()
    plt.xlabel("$C_D$ [-]")
    plt.ylabel("$C_L$ [-]")

    if show_plot:
        plt.show()    

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    ap.add_argument("--plot", action="store_true", help="Show plots")
    args = ap.parse_args()

    input_file = args.input_file
    show_plot = args.plot
    # input_file = "./Output/coefficients.csv"
    # show_plot = True

    # Import computed coefficients and xfoil coefficients
    polar_data = import_coefficients(input_file)
    polar_xfoil = import_coefficients("./Output/xfoil_coefficients.csv")
    polar_xfoil.CM += polar_xfoil.CL/4
    polar_xfoil.CM = -polar_xfoil.CM

    # Plot coefficients
    plot_coefficient(polar_data, polar_xfoil, "C_D", show_plot)
    plot_coefficient(polar_data, polar_xfoil, "C_L", show_plot)
    plot_coefficient(polar_data, polar_xfoil, "C_M", show_plot)

    # Plot polar
    plot_polar(polar_data, polar_xfoil,show_plot)