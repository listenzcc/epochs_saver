# coding: utf-8
'''
This script is to load MEG RSVP dataset,
and save epochs as fif file.
'''

import mne
import numpy as np
import os
import time
import matplotlib.pyplot as plt


def shift_events(events, raw, ch_name='MZP01-4503', half_length=30):
    kernel = np.concatenate(
        [np.array(range(1, half_length)), np.array(range(half_length, 0, -1))])

    picks = [raw.info['ch_names'].index(ch_name)]

    ts = np.squeeze(raw.get_data(picks=picks))
    ts_convolve = np.convolve(kernel, ts, 'same')

    new_events = events.copy()
    for j, onset in enumerate(events[:, 0]):
        ts_tmp = ts_convolve[onset+360: onset+480]
        maxidx = np.where(ts_tmp == ts_tmp.max())[0][0]

        new_onset = onset + maxidx
        while new_onset in new_events[0:j, 0]:
            new_onset -= 1

        new_events[j, 0] = new_onset

    return new_events


def plot_epochs_PZ(epochs, ch_name='MZP01-4503'):
    picks = [epochs.info['ch_names'].index(ch_name)]
    mne.viz.plot_epochs_image(epochs, picks=picks, show=False)


'''
# Function: Setting evrionment for the script.
# Output: root_path, directory of project.
# Output: time_stamp, string of beginning time of the script.
# Output: results_dir, directory for storing results.
'''
root_dir = os.path.join('/nfs/cell_a/userhome/zcc/documents', 'RSVP_experiment')
time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S')
results_dir = os.path.join(root_dir, 'epochs_saver', 'epochs_freq_0.5_30_crop_n0.2_p1.1')
if not os.path.exists(results_dir):
    os.mkdir(results_dir)

'''
# Function: Reading raw_files.
'''
file_dir = os.path.join('/nfs/diskstation/zccdata/RSVP_data/rawdata', '20190326_RSVP_MEG_zhangchuncheng', 'S01_lixiangTHU_20190326_%02d.ds')
freq_l, freq_h = 0.5, 30  # Hz
fir_design = 'firwin'

for run_idx in range(4, 11):
    print(run_idx)

    raw = mne.io.read_raw_ctf(file_dir % run_idx, preload=True)
    raw = raw.filter(freq_l, freq_h, fir_design=fir_design)

    '''
    # Function: Get epochs.
    # Output: epochs, resampled epochs of norm and odd stimuli.
    '''

    event_id = dict(odd=1, norm=2)
    tmin, t0, tmax = -0.2, 0, 1.1  # Second
    freq_resample = 200  # Hz
    reject = dict()

    stim_channel = 'UPPT001'
    events = mne.find_events(raw, stim_channel=stim_channel)
    # events_shift = shift_events(events, raw)

    picks = mne.pick_types(
        raw.info, meg=True, ref_meg=False, exclude='bads')

    epochs = mne.Epochs(raw, picks=picks, events=events, event_id=event_id,
                        tmin=tmin, tmax=tmax, baseline=None, detrend=1,
                        reject=reject, preload=True)

    # epochs_shift = mne.Epochs(raw, picks=picks, event_id=event_id,
    #                           events=events_shift,
    #                           tmin=tmin, tmax=tmax, baseline=None, detrend=1,
    #                           reject=reject, preload=True)

    show = False
    if show:
        plot_epochs_PZ(epochs['odd'])
        # plot_epochs_PZ(epochs_shift['odd'])
        plot_epochs_PZ(epochs['norm'])
        # plot_epochs_PZ(epochs_shift['norm'])
        plt.show()

    epochs.resample(freq_resample, npad='auto')
    # epochs_shift.resample(freq_resample, npad='auto')

    '''
    # Function: Save epochs.
    # Output: None.
    '''
    epochs.save(os.path.join(results_dir, 'meg_zcc_epochs_%d-epo.fif' %
                             run_idx), verbose=True)
    # epochs_shift.save(os.path.join(results_dir, 'meg_mxl_epochs_%d-eposhift.fif' %
    #                                run_idx), verbose=True)
