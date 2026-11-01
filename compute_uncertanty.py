import numpy as np
import argparse
from experimental_setup import Wing

def import_data(test_data):
    # Import test data
    data = np.loadtxt(test_data, delimiter=",", skiprows=1)

    # Extract zero measure
    zero = data[0,:]
    data = np.delete(data, 0, axis=0)
    zero = np.tile(zero, (len(data[:,0]),1))

    # Sort data with ascending angle
    data = data[np.argsort(data[:,-1])]

    return data, zero

def get_force_and_uncertanty(signal, E, Sigma, FtF_inv):
    F = signal @ E.T
    h = np.einsum('ij,jk,ik->i', F, FtF_inv, F)  # Leverage for each row
    cov_base = E @ Sigma @ E.T # Covariance of F
    u = np.sqrt((1 + h)[:, None] * np.diag(cov_base)[None, :])

    return F, u

def get_calibration_uncertanties(S_on, S_off, E, Sigma, FtF_inv):
    F_on, u_on = get_force_and_uncertanty(S_on, E , Sigma, FtF_inv)
    F_off, u_off = get_force_and_uncertanty(S_off, E , Sigma, FtF_inv)
    F = F_on - F_off
    uF = np.hypot(u_on,u_off)
    u_Fx, u_Fy, u_Mz = uF.T

    return u_Fx, u_Fy, u_Mz

def get_sensitivity_coefficients(name, alpha, D, L):
    match name:
        case "C_D":
            c_Fx = -np.cos(alpha)
            c_Fy = -np.sin(alpha)
            c_alpha = L

            return c_Fx, c_Fy, c_alpha
        
        case "C_L":
            c_Fx = np.sin(alpha)
            c_Fy = -np.cos(alpha)
            c_alpha = -D

            return c_Fx, c_Fy, c_alpha

        case _:
            raise NameError

def get_load_uncertanty(u_alpha, u_Fx, u_Fy, c_Fx, c_Fy, c_alpha):
    return np.sqrt((c_Fx*u_Fx)**2 + (c_Fy*u_Fy)**2 + (c_alpha*u_alpha)**2)

def get_uncertanties(alpha, D, L ,M, u_alpha, u_Fx, u_Fy, u_Mz, q, S):
    # Initialize array of uncertanty
    n_points = len(alpha)
    u_CD = np.zeros(n_points)
    u_CL = np.zeros(n_points)

    # Loop through all angles
    for i in range(n_points):
        # Get sensitivity for CD
        c_Fx, c_Fy, c_alpha = get_sensitivity_coefficients("C_D",alpha[i],D[i],L[i])
        u_D = get_load_uncertanty(u_alpha, u_Fx[i], u_Fy[i], c_Fx, c_Fy, c_alpha)
        u_CD[i] = u_D/(q[i]*S)

        # Get sensitivity for CL
        c_Fx, c_Fy, c_alpha = get_sensitivity_coefficients("C_L",alpha[i],D[i],L[i])
        u_L = get_load_uncertanty(u_alpha, u_Fx[i], u_Fy[i], c_Fx, c_Fy, c_alpha)
        u_CL[i] = u_L/(q[i]*S)

    return u_CD, u_CL

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    args = ap.parse_args()
    
    input_file = args.input_file
    output_folder = "./Output"

    # Import calibration uncertanty data
    cal = np.load("./Calibration/LC_calibration_uncertainty.npz")
    E, Sigma, FtF_inv = cal["E"], cal["Sigma"], cal["FtF_inv"]

    # Import test data
    DATA,ZERO = import_data(input_file)

    # Import measuerd loads
    LOADS = np.loadtxt("./Output/loads_measured.csv", delimiter=",", skiprows=1)
    alpha = LOADS[:,0]
    D = LOADS[:,1]
    L = LOADS[:,2]
    M = LOADS[:,3]

    # Import measuerd dynamic pressure
    q_file = np.loadtxt("./Output/dynamic_pressure.csv", delimiter=",", skiprows=1)
    q = q_file[:,1]

    # Define wing
    test_wing = Wing("NACA0015",0.100,0.294,0.15,3.43,0.030196676)
    
    # Extract signals
    S_on  = DATA[:,0:3]
    S_off = ZERO[:,0:3]

    # Get calibration and angle uncertanties
    u_Fx, u_Fy, u_Mz = get_calibration_uncertanties(S_on, S_off, E, Sigma, FtF_inv)
    u_alpha = np.deg2rad(0.2)

    # Compute uncertanties on coefficients
    u_CD, u_CL = get_uncertanties(np.deg2rad(alpha), D, L ,M, u_alpha, u_Fx, u_Fy, u_Mz, q, test_wing.surface)

    # Export uncertanties
    np.savetxt(output_folder+"/coefficients_uncertanties.csv",np.column_stack((alpha,u_CD,u_CL)),
               delimiter=",",fmt="%.6e",header="alpha,u_CD,u_CL",comments="")
    print("Exported uncertanties in "+output_folder)

if __name__ == "__main__":
    main()