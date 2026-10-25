import numpy as np
import argparse

g = 9.80665 # Gravity

def get_hook_mass(data_weight,hook_file):
    data_hook = np.loadtxt(hook_file, delimiter=",", skiprows=1)

    v1 = data_weight[0,0:3].T
    v2 = data_weight[1,0:3].T
    m1 = data_weight[0,6].T
    m2 = data_weight[1,6].T
    s = (v2-v1)/(m2-m1) # sensitivity per kg

    v_hook = data_hook[0:3].T

    s = s.reshape(3, 1)
    m_hook, res, rank, sv = np.linalg.lstsq(s, v_hook, rcond=None)
    m_hook = m_hook[0] # in kg

    return m_hook

def get_loads_vector(DATA):
    n_measures = len(DATA[:,0])
    loads = np.zeros((n_measures,3))

    for i in range(n_measures):
        m = DATA[i,6]
        b = DATA[i,7]/1000 # mm -> m
        theta = np.deg2rad(DATA[i,8])

        W = m*g
        loads[i,0] = W*np.sin(theta)   # Fx = W*sin(theta)
        loads[i,1] = W*np.cos(theta)   # Fy = W*cos(theta)
        loads[i,2] = W*b*np.sin(theta) # Mz = W*b*sin(theta)

    return loads

def get_signals_vector(DATA):
    signals = DATA[:,0:3]

    return signals

def get_calibration_matrix(F,S):
    K, res, rank, sv = np.linalg.lstsq(F, S, rcond=None)
    K = K.T

    E = np.linalg.inv(K)

    print("--- Generated calibration and evaluation matrices --")
    # print("rank(F)=", rank)
    # print("cond(F)=", sv[0] / sv[-1])

    rank_F = rank
    cond_F = sv[0] / sv[-1]

    return K, E, rank_F, cond_F

def write_report(filename, K, E, rank_F, cond_F, F, S, input_file):
    with open(filename, "w") as f:
        f.write("LOAD CELL CALIBRATION\n")
        f.write(f"Data: {input_file}\n")

        F_n = F / np.abs(F).max(axis=0)  # column-normalized, independent of unit
        f.write("\n--- Checks on the fit ---\n")
        f.write(f"rank(F) = {rank_F}\n")
        f.write(f"cond(F) = {cond_F:.6f}\n")
        f.write(f"cond(F), normalized = {np.linalg.cond(F_n):.6f}\n")

        f.write("\n--- Checks on the result ---\n")
        f.write(f"rank(K) = {np.linalg.matrix_rank(K)}\n")
        f.write(f"cond(K) = {np.linalg.cond(K):.6f}\n")

        R = S - F @ K.T                              # (N,3)
        dof = F.shape[0] - 3
        sigma = np.sqrt((R**2).sum(axis=0) / dof)    # fit noise per channel
        f.write("\n--- Residuals on the signal ---\n")
        # f.write(f"K = {K:.6f}\n")
        print("K =\n", K, file=f)
        print("E =\n", E, file=f)
        print("signal residuals [uV/V] =\n", R * 1e6, file=f)
        print("fit sigma [uV/V] =", sigma * 1e6, file=f)
        print("max error [% FS] =", np.abs(R).max(axis=0) / np.abs(S).max(axis=0) * 100, file=f)

        F_est = S @ E.T                              # F = E @ S for each test
        err_F = F_est - F
        f.write("\n--- Error on the reconstructed loads ---\n")
        print("load error [N, N, N*m] =\n", err_F,file=f)
        print("load RMSE =", np.sqrt((err_F**2).mean(axis=0)),file=f)

        cov_unit = np.linalg.inv(F.T @ F)
        se_K = np.sqrt(np.outer(sigma**2, np.diag(cov_unit)))   # same shape as K
        f.write("\n--- Uncertainty on the sensitivities ---\n")
        print("standard errors of K =\n", se_K, file=f)

        f.write("\n--- Crosstalk: each column of K divided by its own diagonal element ---\n")
        print("normalized crosstalk =\n", K / np.diag(K)[None, :],file=f)
        

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("weight_file", help="Path of the weight data file")
    args = ap.parse_args()
    weight_file = args.weight_file

    # weight_file = "./DATA/weights_measure.csv"
    hook_file = "./DATA/hook_measure.csv"
    output_folder = "./Calibration"

    DATA = np.loadtxt(weight_file, delimiter=",", skiprows=1)

    # Compute hook mass and add correction to data
    m_hook = get_hook_mass(DATA,hook_file)
    DATA[:,6] += m_hook

    # Build vector of loads
    F = get_loads_vector(DATA)

    # Build vector of signals
    S = get_signals_vector(DATA)

    # Build calibration and evaluation matrices
    K, E, rank_F, cond_F = get_calibration_matrix(F,S)

    # Save output in files
    np.savetxt(output_folder+"/K.csv",K,delimiter=",",fmt="%.6e")
    np.savetxt(output_folder+"/E.csv",E,delimiter=",",fmt="%.6e")
    print("Load cell calibration and evaluation matrices saved in " + output_folder)

    # Write output report
    write_report(output_folder+"/LC_calibration_report.txt",K, E, rank_F, cond_F, F, S, weight_file)
    print("Load cell calibration report saved in " + output_folder)