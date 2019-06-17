# coding: utf-8
'''
This script is to load MEG RSVP dataset,
and save epochs as fif file.
'''

import mne
import os
import time

'''
# Function: Setting evrionment for the script.
# Output: root_path, directory of project.
# Output: time_stamp, string of beginning time of the script.
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
file_dir = os.path.join(root_dir, 'rawdata', '20190326_RSVP_MEG_maxuelin',
                        'S02_lixiangTHU_20190326_%02d.ds')
freq_l, freq_h = 0.5, 30  # Hz
fir_design = 'firwin'

for run_idx in range(4, 12):
    print(run_idx)

    raw = mne.io.read_raw_ctf(file_dir % run_idx, preload=True)
    raw = raw.filter(freq_l, freq_h, fir_design=fir_design)

    '''
    # Function: Get epochs.
    # Output: epochs, resampled epochs of norm and odd stimuli.
    '''
    picks = mne.pick_types(
        raw.info, meg=True, ref_meg=False, exclude='bads')
    stim_channel = 'UPPT001'
    events = mne.find_events(raw, stim_channel=stim_channel)
    event_id = dict(odd=1, norm=2)
    tmin, t0, tmax = -0.2, 0, 1  # Second
    freq_resample = 200  # Hz
    reject = dict()

    epochs = mne.Epochs(raw, picks=picks, events=events, event_id=event_id,
                        tmin=tmin, tmax=tmax, baseline=None, detrend=1,
                        reject=reject, preload=True)
    epochs.resample(freq_resample, npad='auto')

    '''
    # Function: Save epochs.
    # Output: None.
    '''
    epochs.save(os.path.join(results_dir, 'meg_mxl_epochs_%d-epo.fif' %
                             run_idx), verbose=True)
