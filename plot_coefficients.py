import numpy as np
import matplotlib.pyplot as plt
import argparse

bluepoli1 = "#102C53"
bluepoli2 = "#0BA4FF"
bluepoli3 = "#67B2C6"

def plot_coefficient(alpha, coeff, name, show_plot):
    fig, ax = plt.subplots()
    ax.plot(alpha,coeff,label="Data",marker="s",color=bluepoli1)

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend()
    plt.xlabel(r"$\alpha$ [deg]")
    plt.ylabel(f"${name}$ [-]")

    if show_plot:
        plt.show()

def plot_polar(CD,CL,show_plot):
    fig, ax = plt.subplots()
    ax.plot(CD,CL,label="Data",marker="s",color=bluepoli1)

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend()
    plt.xlabel("$C_D$ [-]")
    plt.ylabel("$C_L$ [-]")

    if show_plot:
        plt.show()    

if __name__ == "__main__":
    # ap = argparse.ArgumentParser()
    # ap.add_argument("input_file", help="Path of the input data file")
    # ap.add_argument("--plot", action="store_true", help="Show plots")
    # args = ap.parse_args()

    # input_file = args.input_file
    # show_plot = args.plot
    input_file = "./Output/coefficients.csv"
    show_plot = True

    # Import computed coefficients
    coeffs = np.loadtxt(input_file, delimiter=",", skiprows=1)
    alpha = coeffs[:,0]
    CD = coeffs[:,1]
    CL = coeffs[:,2]
    CM = coeffs[:,3]

    # Plot coefficients
    plot_coefficient(alpha, CD, "C_D", show_plot)
    plot_coefficient(alpha, CL, "C_L", show_plot)
    plot_coefficient(alpha, CM, "C_M", show_plot)

    # Plot polar
    plot_polar(CD,CL,show_plot)