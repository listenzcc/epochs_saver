# coding: utf-8
'''
This script is to load EEG RSVP dataset,
and save epochs as fif file.
'''

import mne
import numpy as np
import os
import time
import matplotlib.pyplot as plt

'''
# Function: Setting evrionment for the script.
# Output: root_path, directory of project.
# Output: time_stamp, string of beginning time of the script.
# Output: id_string, customer identifier string.
# Output: results_dir, directory for storing results.
'''
root_dir = os.path.join('D:\\', 'RSVP_MEG_experiment')
time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S')
results_dir = os.path.join(root_dir, 'epochs_saver', 'epochs')
if not os.path.exists(results_dir):
    os.mkdir(results_dir)

'''
# Function: Reading raw_files.
'''
file_dir = os.path.join(root_dir, 'rawdata', '20190402_RSVP_EEG_maxuelin',
                        'mxl%d.cnt')
freq_l, freq_h = 0.1, 7  # Hz
fir_design = 'firwin'

'''
# Function: Preparing motage for EEG dataset
# Output: motage, motage of standard_1020
'''
motage = mne.channels.read_montage('standard_1020')


def shift_events(events, raw, picks=[47], kernel=np.ones(100)):
    ts = np.squeeze(raw.get_data(picks=picks))
    ts_convolve = np.convolve(kernel, ts, 'same')
    new_events = events.copy()
    for j, onset in enumerate(events[:, 0]):
        ts_tmp = ts_convolve[onset+300: onset+400]
        maxidx = np.where(ts_tmp == ts_tmp.max())[0][0]
        new_events[j, 0] = onset + maxidx
    return new_events


def plot_epochs_PZ(epochs, picks=[47]):
    mne.viz.plot_epochs_image(epochs, picks=picks, show=False)


for run_idx in range(1, 11):
    print(run_idx)

    raw = mne.io.read_raw_cnt(file_dir % run_idx,
                              motage, stim_channel='STI 014',
                              preload=True)
    raw = raw.filter(freq_l, freq_h, fir_design=fir_design)

    '''
    # Function: Get epochs.
    # Output: epochs, resampled epochs of norm and odd stimuli.
    '''
    events = mne.find_events(raw)
    events_shift = shift_events(events, raw)
    event_id = dict(odd=1, norm=2)
    tmin, t0, tmax = -0.2, 0, 1  # Seconds
    freq_resample = 200  # Hz
    reject = dict()

    picks = mne.pick_types(raw.info, eeg=True, exclude='bads')

    if False:
        epochs = mne.Epochs(raw, picks=picks, events=events, event_id=event_id,
                            tmin=tmin, tmax=tmax, baseline=None, detrend=1,
                            reject=reject, preload=True)

    epochs_shift = mne.Epochs(raw, picks=picks, event_id=event_id,
                              events=events_shift,
                              tmin=tmin, tmax=tmax, baseline=None, detrend=1,
                              reject=reject, preload=True)

    if False:
        plot_epochs_PZ(epochs['odd'])
        plot_epochs_PZ(epochs_shift['odd'])
        plot_epochs_PZ(epochs['norm'])
        plot_epochs_PZ(epochs_shift['norm'])
        plt.show()

    epochs_shift.resample(freq_resample, npad='auto')

    '''
    # Function: Save epochs.
    # Output: None.
    '''
    epochs.save(os.path.join(results_dir, 'eeg_mxl_epochs_%d-epo.fif' %
                             run_idx), verbose=True)
