import numpy as np
import argparse

def import_data(test_data):
    # Import test data
    data = np.loadtxt(test_data, delimiter=",", skiprows=1)
    data = data[np.argsort(data[:,-1])] # Sort data with ascending angle

    return data

def import_calibration(evaluation_matrix,WT_calibration):
    # Import evaluation matrix
    E = np.loadtxt(evaluation_matrix, delimiter=",")

    # Import wind tunnel calibration coefficient K_WT
    WT_data = np.loadtxt(WT_calibration, delimiter=",", skiprows=1)
    K_WT = WT_data[-1]

    return E, K_WT


if __name__ == "__main__":
    # ap = argparse.ArgumentParser
    # ap.add_argument("input_file", help="Path of the input data file")
    # args = ap.parse_args()

    # input_file = args.input_file
    input_file = "./Data/airfoil_measure.csv"
    output_folder = "./Output"

    # Import data and calibration parameters
    DATA = import_data(input_file)
    E, K_WT = import_calibration("./Calibration/E.csv","./Calibration/WT.csv")
