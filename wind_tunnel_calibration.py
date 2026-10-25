import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import argparse

bluepoli1 = "#102C53"
bluepoli2 = "#0BA4FF"
bluepoli3 = "#67B2C6"

def get_pressure_data(filename):
    data = np.loadtxt(wind_file, delimiter=",", skiprows=1)

    ch0 = data[:,3]
    ch1 = data[:,4]
    ch2 = data[:,5]

    return ch0, ch1, ch2

def write_report(filename, input_file, regr, s):
    with open(filename, "w") as f:
        f.write("WIND TUNNEL CALIBRATION\n")
        f.write(f"Data: {input_file}\n")
        f.write(f"Pressure transducer sensitivity = {s:.3f} Pa/V\n")

        f.write("\n--- Fit ch1-ch0 = K*ch2 ---\n")
        f.write(f"slope = {regr.slope:.6f}\n")
        f.write(f"intercept = {regr.intercept:.6f}\n")
        f.write(f"R^2 = {regr.rvalue**2:.6f}\n")
        f.write(f"standard error = {regr.stderr:.6f}\n")

def plot_regression(ch0, ch1, ch2, regr, output_folder,show_plot):
    x_data = ch2
    y_data = ch1-ch0

    x_regr = np.linspace(0,np.max(x_data)*1.15)
    y_regr = regr.intercept + x_regr*regr.slope

    fig, ax = plt.subplots()
    ax.scatter(x_data,y_data,label="Data",marker="s",color=bluepoli1,zorder=2)
    ax.plot(x_regr,y_regr,label=f"Linear regression ($R^2 = {regr.rvalue**2:.6f}$)",
            color=bluepoli2,linestyle="--",zorder=1)

    ax.set_xlim(0,np.max(x_regr))
    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend()
    plt.xlabel("ch1 - ch0 [V]")
    plt.ylabel("ch2 [V]")

    plt.savefig(output_folder+"/WT_regression.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_folder+"/WT_regression.pdf", bbox_inches="tight")

    if show_plot:
        plt.show()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("wind_file", help="Path of the wind data file")
    ap.add_argument("-s", type=float, default=200, help="Pressure tranducer sensitivity") 
    ap.add_argument("--plot", action="store_true", help="Show the regression plot")
    args = ap.parse_args()

    wind_file = args.wind_file
    s = args.s
    show_plot = args.plot


    # wind_file = "./Data/wind_measure.csv"
    output_folder = "./Calibration"

    # Extract pressure data
    ch0, ch1, ch2 = get_pressure_data(wind_file)

    # Linear regression with law ch1-ch0 = K*ch2
    regr = stats.linregress(ch2,ch1-ch0)
    K = regr.slope

    # Results
    results = np.array([K, s, K*s])
    results = results.reshape(1,3)
    np.savetxt(output_folder+"/WT.csv",results,delimiter=",",fmt="%.6e",
               header="Voltage scaling,Sensitivity,Calibration coefficient",comments="")
    print("Wind tunnel calibration results saved in " + output_folder)

    # Write output report
    write_report(output_folder+"/WT_calibration_report.txt",wind_file,regr,s)
    print("Wind tunnel calibration report saved in " + output_folder)

    # Plot regression
    plot_regression(ch0,ch1,ch2,regr,output_folder,show_plot)