import mido
from mido import MidiFile
import numpy as np

def write_midi(pr, ticks_per_beat, write_path, tempo=80):
    def pr_to_list(pr):
        T, N = pr.shape
        t_last = 0
        pr_tm1 = np.zeros(N)
        list_event = []
        for t in range(T):
            pr_t = pr[t]
            mask = (pr_t != pr_tm1)
            if (mask).any():
                for n in range(N):
                    if mask[n]:
                        pitch = n
                        velocity = int(pr_t[n])
                        t_event = t - t_last
                        t_last = t
                        list_event.append((pitch, velocity, t_event))
            pr_tm1 = pr_t
        return list_event
    microseconds_per_beat = mido.bpm2tempo(tempo)
    mid = MidiFile()
    mid.ticks_per_beat = ticks_per_beat
    for instrument_name, matrix in pr.items():
        track = mid.add_track(instrument_name)
        events = pr_to_list(matrix)
        track.append(mido.MetaMessage('set_tempo', tempo=microseconds_per_beat))
        try:
            program = program_change_mapping[instrument_name]
        except:
            program = 1
        track.append(mido.Message('program_change', program=program))
        notes_on_list = []
        for event in events:
            pitch, velocity, time = event
            if velocity == 0:
                track.append(mido.Message('note_off', note=pitch, velocity=0, time=time))
                notes_on_list.remove(pitch)
            else:
                if pitch in notes_on_list:
                    track.append(mido.Message('note_off', note=pitch, velocity=0, time=time))
                    notes_on_list.remove(pitch)
                    time = 0
                track.append(mido.Message('note_on', note=pitch, velocity=velocity, time=time))
                notes_on_list.append(pitch)
    mid.save(write_path)
    return