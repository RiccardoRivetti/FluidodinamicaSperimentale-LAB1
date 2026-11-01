import numpy as np
import argparse

class Wing:
    def __init__(self, airfoil, chord, span, thickness, shape_factor):
        self.airfoil   = airfoil
        self.chord     = chord
        self.span      = span
        self.thickness = thickness # Percentage of chord
        self.surface   = chord*span
        self.volume    = chord*span*chord*thickness
        self.shape_factor = shape_factor

class TestSection:
    def __init__(self, length, width, height, pressure_gradient):
        self.length = length
        self.width  = width
        self.height = height
        self.area   = width*height
        self.pressure_gradient = pressure_gradient
        

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

def get_dynamic_pressure(signal,K_WT):
    return K_WT*signal

def get_coefficients(DATA,ZERO,E,q,test_wing):
    # Get vector of angles
    alpha = DATA[:,8]

    # Compute wing parameters
    c = test_wing.chord
    S = test_wing.surface

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

        # Compute coefficients
        CD[i] = D/(q[i]*S)
        CL[i] = L/(q[i]*S)
        CM[i] = -(M/(q[i]*S*c) + CL[i]/4)

    return CD, CL, CM, alpha

def get_solid_blockage(test_wing, test_section):
    K1 = 0.90
    A = test_section.area # Test section area
    V_mod = test_wing.volume # Volume of the wing

    epsilon_sb = K1*V_mod/(A**1.5)

    return epsilon_sb

def get_wake_blockage(test_wing, test_section, CD):
    c = test_wing.chord
    h = test_section.height

    epsilon_wb = c/(2*h)*CD

    return epsilon_wb

def get_buoyancy(test_wing, test_section, q):
    lambda_2 = test_wing.shape_factor
    t = test_wing.thickness*test_wing.chord
    S = test_wing.surface
    dP_dx = test_section.pressure_gradient

    CD_B = np.pi/2 * lambda_2 * t**2 * dP_dx * 1/(q*S)

    return CD_B

def get_corrections(CD, CL, CM, q, test_wing, test_section):
    # Initialize corrected coefficients
    n_coeffs = len(CD)
    CD_corr = np.zeros(n_coeffs)
    CL_corr = np.zeros(n_coeffs)
    CM_corr = np.zeros(n_coeffs)

    # Add corrections
    for i in range(n_coeffs):
        # Add horizontal buoyancy to CD
        CD_B = get_buoyancy(test_wing, test_section, q[i])
        CD_corr[i] = CD[i] - CD_B

        # Compute correction parameters for blockage
        c = test_wing.chord
        h = test_section.height

        epsilon_sb = get_solid_blockage(test_wing,test_section)
        epsilon_wb = get_wake_blockage(test_wing,test_section,CD[i])
        epsilon = epsilon_sb + epsilon_wb

        sigma = (np.pi**2)/48 * (c**2)/(h**2)

        # Add corrections to CL
        CL_corr[i] = CL[i]*(1 - 2*epsilon - sigma)

        # Add corrections to CM
        CM_corr[i] = CM[i]*(1 - 2*epsilon) + 0.25*sigma*CL[i]

    return CD_corr, CL_corr, CM_corr

def export_coefficients(filename, alpha, CD, CL, CM):
    CD = CD.T
    CL = CL.T
    CM = CM.T

    results = np.column_stack([alpha,CD,CL,CM])
    np.savetxt(filename,results,delimiter=",",fmt="%.6e",header="alpha,CD,CL,CM",comments="")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    args = ap.parse_args()

    input_file = args.input_file
    # input_file = "./Data/airfoil_measure.csv"
    output_folder = "./Output"

    # Define the experiment parameters
    test_wing = Wing("NACA0015",0.100,0.294,0.15,3.43)
    test_section = TestSection(1,0.3,0.45,10)

    # Import data and calibration parameters
    DATA, ZERO = import_data(input_file)
    E, K_WT = import_calibration("./Calibration/E.csv","./Calibration/K_WT.csv")

    # Compute vector of dynamic pressures
    q = get_dynamic_pressure(DATA[:,5],K_WT)

    # Compute load coefficients
    print("Computing coefficients...")
    CD, CL, CM, alpha = get_coefficients(DATA,ZERO,E,q,test_wing)

    # Compute corrected coefficients
    print("Computing corrections...")
    CD_corr, CL_corr, CM_corr = get_corrections(CD, CL, CM, q, test_wing, test_section)

    # Export load coefficients
    export_coefficients(output_folder+"/coefficients_measured.csv", alpha, CD, CL, CM)
    export_coefficients(output_folder+"/coefficients_corrected.csv", alpha, CD_corr, CL_corr, CM_corr)
    print("Exported coefficients in "+output_folder)

if __name__ == "__main__":
    main()