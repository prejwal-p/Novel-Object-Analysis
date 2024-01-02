import lvm_read
from scipy.fft import fft, fftfreq
import numpy as np
import os
import matplotlib.pyplot as plt
import sys
from parameters_gui import Get_Parameters
from scipy import signal
import pandas as pd
plt.close('all')

path = sys.argv[1]
get_parameters = Get_Parameters()

lvm_files = [i for i in os.listdir(path) if i.endswith(".lvm")]

if len(lvm_files) == 0:
    sys.exit("No LVM Files Found")

folders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

 
for file in folders:
    print(f"\n\n*******************************Demodulating LVM File - {file}*******************************\n")
    lvms = [f for f in lvm_files if file in f]
    base_path = os.path.join(path, file)

    if not os.path.exists(os.path.join(base_path, "guppy")):
        os.mkdir(os.path.join(base_path, "guppy"))
        guppy_path = os.path.join(base_path, "guppy")
    else:
        guppy_path = os.path.join(base_path, "guppy")

    if not os.path.exists(os.path.join(path, file.split(".")[0], "lvm_plots")):
        os.mkdir(os.path.join(base_path, "lvm_plots"))
        plot_path = os.path.join(base_path, "lvm_plots")
    else:
        plot_path = os.path.join(base_path, "lvm_plots") 

    parameters = get_parameters.get_json(save_path=base_path)

#    if parameters["lvm_color_channel"] == "red":
#        lvm = [f for f in lvms if "_Red" in f]
#    elif parameters["lvm_color_channel"] == "green":
#        lvm = [f for f in lvms if "_Green" in f]
#    else:
#        sys.exit()
    signal_band = [190, 210]
    
    if os.path.exists(os.path.join(path, lvms[0] + ".pkl")):
        pickle_read = True
    else:
        pickle_read = False

    # Begin Analysing The Data
    data = lvm_read.read(os.path.join(path, lvms[0]), read_from_pickle=pickle_read)
    data_vals = data[0]["data"]

    y1 = []
    timestamps = []
    for i in range(len(data_vals)):
        y1.append(data_vals[i][1])
        timestamps.append(data_vals[i][0])

    #Fourier Plot
    N = len(y1)
    T = data[0]["Delta_X"][0]
    yf = fft(y1)
    xf = fftfreq(N, T)[:N//2]
    plt.figure()
    n = 2.0/N * np.abs(yf[0:N//2])
    plt.plot(xf[1:], n[1:])
    plt.grid()
    plt.savefig(os.path.join(plot_path, file + "_fft.png"))

    #Power Plot
    fs = 1/data[0]["Delta_X"][0]
    plt.figure()
    f, Pxx_den = signal.periodogram(y1, fs)
    plt.semilogy(f[1:], Pxx_den[1:])
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.savefig(os.path.join(plot_path, file + "_periodogram.png"))

    k = 1
    demodSig_control = []
    demodSig_signal = []
    N_samples = int(0.05*fs)

    for _ in range(1, int(len(y1)/N_samples)-1):
        ySig_sub = y1[k:k+N_samples]
        fft_result = np.fft.fft(ySig_sub)
        freqs = np.fft.fftfreq(len(ySig_sub), 1/fs)

        control_band = [473, 493]

        control_indices = np.where((freqs >= control_band[0]) & (freqs <= control_band[1]))[0]
        signal_indices = np.where((freqs >= signal_band[0]) & (freqs <= signal_band[1]))[0]

        power_control = np.sum(np.abs(fft_result[control_indices]**2))
        power_signal = np.sum(np.abs(fft_result[signal_indices]**2))

        demodSig_control.append(power_control)
        demodSig_signal.append(power_signal)

        k += N_samples 


    fig, axs = plt.subplots(nrows=2, ncols=1)
    axs[0].plot(demodSig_control)
    axs[0].set_title("Control")
    axs[1].plot(demodSig_signal)
    axs[1].set_title("Signal")
    plt.savefig(os.path.join(plot_path, file + "_demodulated.png"))

    signal_data = pd.DataFrame({"timestamps": np.arange(0, len(demodSig_signal)/20, 0.05), "data":demodSig_signal, "sampling_rate":[np.nan for _ in range(len(demodSig_signal))]})
    signal_data["sampling_rate"].iloc[0] = 20

    control_data = pd.DataFrame({"timestamps": np.arange(0, len(demodSig_control)/20, 0.05), "data":demodSig_control, "sampling_rate":[np.nan for _ in range(len(demodSig_control))]})
    control_data["sampling_rate"].iloc[0] = 20

    if "_Ch1" in file or "_Ch2" in file:
        filename = file.split("_Ch")[0]
    else:
        filename = file
        
    control_data.to_csv(os.path.join(guppy_path, filename + "_C.csv"), index=False)
    signal_data.to_csv(os.path.join(guppy_path, filename + "_S.csv"), index=False)

    plt.close('all')