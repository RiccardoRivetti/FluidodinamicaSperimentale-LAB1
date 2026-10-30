import numpy as np
import argparse

class Wing:
    def __init__(self, airfoil, chord, span):
        self.airfoil = airfoil
        self.chord = chord
        self.span = span

def import_data(test_data):
    # Import test data
    data = np.loadtxt(test_data, delimiter=",", skiprows=1)

    # Extract zero measure
    zero = data[0,:]
    data = np.delete(data, 0, axis=0)

    # Sort data with ascending angle
    data = data[np.argsort(data[:,-1])]

    return data, zero

def import_calibration(evaluation_matrix,WT_calibration):
    # Import evaluation matrix
    E = np.loadtxt(evaluation_matrix, delimiter=",")

    # Import wind tunnel calibration coefficient K_WT
    WT_data = np.loadtxt(WT_calibration, delimiter=",", skiprows=1)
    K_WT = WT_data[-1]

    return E, K_WT

def get_coefficients(DATA,ZERO,E,K_WT,tested_wing):
    # Get vector of angles
    alpha = DATA[:,8]

    # Compute wing parameters
    c = tested_wing.chord
    S = c*tested_wing.span

    # Compute loads in the zero wind condition
    S_zero = ZERO[0:3]
    S_zero = S_zero.reshape(3,1)
    F_zero = E @ S_zero

    # Initialize coefficients arrays
    CD = np.zeros(len(alpha))
    CL = np.zeros(len(alpha))
    CM = np.zeros(len(alpha))

    # Loop on each measure
    for i in range(len(alpha)):
        # Extract load signals
        S_loads = DATA[i,0:3]
        S_loads = S_loads.reshape(3,1)

        # Compute loads in cell axes
        F = E @ S_loads
        F -= F_zero

        # Compute loads in wind axes
        alpha_rad = np.deg2rad(alpha[i])
        D = -(F[0,0]*np.cos(alpha_rad) + F[1,0]*np.sin(alpha_rad))
        L = -(-F[0,0]*np.sin(alpha_rad) + F[1,0]*np.cos(alpha_rad))
        M = -F[2,0]

        # Compute dynamic pressure
        q = K_WT*DATA[i,5]
        # print(np.sqrt(q/(.5*1.225))*1.225*c/1.81e-5)

        # Compute coefficients
        CD[i] = D/(q*S)
        CL[i] = L/(q*S)
        CM[i] = -(M/(q*S*c) + CL[i]/4)

    return CD, CL, CM, alpha

def export_coefficients(filename, alpha, CD, CL, CM):
    CD = CD.T
    CL = CL.T
    CM = CM.T

    results = np.column_stack([alpha,CD,CL,CM])
    np.savetxt(filename,results,delimiter=",",fmt="%.6e",header="alpha,CD,CL,CM",comments="")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    args = ap.parse_args()

    input_file = args.input_file
    # input_file = "./Data/airfoil_measure.csv"
    output_folder = "./Output"

    # Define the tested wing
    tested_wing = Wing("NACA0015",0.100,0.294)

    # Import data and calibration parameters
    DATA, ZERO = import_data(input_file)
    E, K_WT = import_calibration("./Calibration/E.csv","./Calibration/WT.csv")

    # Compute load coefficients
    print("Computing coefficients...")
    CD, CL, CM, alpha = get_coefficients(DATA,ZERO,E,K_WT,tested_wing)

    # Export load coefficients
    export_coefficients(output_folder+"/coefficients.csv", alpha, CD, CL, CM)
    print("Exported coefficients in "+output_folder)