import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# -----------------------------
# Load ECG Record
# -----------------------------
record_name = "a01"   # sample record
record = wfdb.rdrecord(record_name, pn_dir="apnea-ecg")

ecg_signal = record.p_signal[:, 0]   # single lead ECG
fs = record.fs

print("Sampling Frequency:", fs)
print("ECG Signal Length:", len(ecg_signal))

# -----------------------------
# Plot Raw ECG
# -----------------------------
plt.figure(figsize=(12, 4))
plt.plot(ecg_signal[:3000])
plt.title("Raw Single-Lead ECG Signal")
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.tight_layout()
plt.show()
