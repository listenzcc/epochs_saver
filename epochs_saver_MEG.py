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


'''
# Function: Setting evrionment for the script.
# Output: root_path, directory of project.
# Output: time_stamp, string of beginning time of the script.
# Output: results_dir, directory for storing results.
# Output: read_save_stuff, stuffs of read and save files.
'''
root_dir = os.path.join('/nfs/cell_a/userhome/zcc/documents', 'RSVP_experiment')
time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S')

freq_l, freq_h = 0.5, 30  # Hz
tmin, t0, tmax = -0.2, 0, 1.1  # Second

results_dir = os.path.join(root_dir, 'epochs_saver', 'epochs_freq_0.5_30_crop_n0.2_p1.1')
if not os.path.exists(results_dir):
    os.mkdir(results_dir)

read_save_stuff = {}

read_save_stuff['S01'] = dict(
        file_path   = os.path.join('/nfs/diskstation/zccdata/RSVP_data/rawdata', '20190326_RSVP_MEG_zhangchuncheng', 'S01_lixiangTHU_20190326_%02d.ds'),
        range_run   = range(4, 11),
        epochs_path = os.path.join(results_dir, 'meg_S01_epochs_%d-epo.fif'))

read_save_stuff['S02'] = dict(
        file_path   = os.path.join('/nfs/diskstation/zccdata/RSVP_data/rawdata', '20190326_RSVP_MEG_maxuelin', 'S02_lixiangTHU_20190326_%02d.ds'),
        range_run   = range(4, 12),
        epochs_path = os.path.join(results_dir, 'meg_S02_epochs_%d-epo.fif'))

'''
# Function: Reading raw_files.
'''

for stuff in read_save_stuff.values():

    print('-'*80)
    for e in stuff.items():
        print(e[0], e[1])

    file_path = stuff['file_path']
    epochs_path = stuff['epochs_path']

    fir_design = 'firwin'

    for run_idx in stuff['range_run']:
        print(run_idx)

        raw = mne.io.read_raw_ctf(file_path % run_idx, preload=True)
        raw = raw.filter(freq_l, freq_h, fir_design=fir_design)

        '''
        # Function: Get epochs.
        # Output: epochs, resampled epochs of norm and odd stimuli.
        '''

        event_id = dict(odd=1, norm=2)
        freq_resample = 200  # Hz
        reject = dict()

        stim_channel = 'UPPT001'
        events = mne.find_events(raw, stim_channel=stim_channel)

        picks = mne.pick_types(
            raw.info, meg=True, ref_meg=False, exclude='bads')

        epochs = mne.Epochs(raw, picks=picks, events=events, event_id=event_id,
                            tmin=tmin, tmax=tmax, baseline=None, detrend=1,
                            reject=reject, preload=True)

        epochs.resample(freq_resample, npad='auto')

        '''
        # Function: Save epochs.
        # Output: None.
        '''
        epochs.save(epochs_path % run_idx, verbose=True)
