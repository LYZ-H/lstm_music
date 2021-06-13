#!/usr/bin/env python
# -*- coding: utf8 -*-

from mido import MidiFile
from unidecode import unidecode
import numpy as np
import midi.write_midi as write_midi
import os
import midi.utils as utils
import time
#######
# Pianorolls dims are  :   TIME  *  PITCH


class Read_midi(object):
    def __init__(self, song_path, quantization):
        ## Metadata
        self.__song_path = song_path
        self.__quantization = quantization

        ## Pianoroll
        self.__T_pr = None

        ## Private misc
        self.__num_ticks = None
        self.__T_file = None

    @property
    def quantization(self):
        return self.__quantization

    @property
    def T_pr(self):
        return self.__T_pr

    @property
    def T_file(self):
        return self.__T_file

    def get_total_num_tick(self):
        mid = MidiFile(self.__song_path)
        num_ticks = 0
        for i, track in enumerate(mid.tracks):
            tick_counter = 0
            for message in track:
                time = float(message.time)
                tick_counter += time
            num_ticks = max(num_ticks, tick_counter)
        self.__num_ticks = num_ticks

    def get_pitch_range(self):
        mid = MidiFile(self.__song_path)
        min_pitch = 200
        max_pitch = 0
        for i, track in enumerate(mid.tracks):
            for message in track:
                if message.type in ['note_on', 'note_off']:
                    pitch = message.note
                    if pitch > max_pitch:
                        max_pitch = pitch
                    if pitch < min_pitch:
                        min_pitch = pitch
        return min_pitch, max_pitch

    def get_time_file(self):
        mid = MidiFile(self.__song_path)
        ticks_per_beat = mid.ticks_per_beat
        self.get_total_num_tick()
        self.__T_file = int((self.__num_ticks / ticks_per_beat) * self.__quantization)
        return self.__T_file

    def read_file(self):
        mid = MidiFile(self.__song_path)
        ticks_per_beat = mid.ticks_per_beat

        self.get_time_file()
        T_pr = self.__T_file
        N_pr = 128
        pianoroll = {}

        def add_note_to_pr(note_off, notes_on, pr):
            pitch_off, _, time_off = note_off
            match_list = [(ind, item) for (ind, item) in enumerate(notes_on) if item[0] == pitch_off]
            if len(match_list) == 0:
                print("Try to note off a note that has never been turned on")
                return
            pitch, velocity, time_on = match_list[0][1]
            pr[time_on:time_off, pitch] = velocity
            ind_match = match_list[0][0]
            del notes_on[ind_match]
            return
        counter_unnamed_track = 0
        for i, track in enumerate(mid.tracks):
            pr = np.zeros([T_pr, N_pr])
            time_counter = 0
            notes_on = []
            for message in track:
                time = float(message.time)
                time_counter += time / ticks_per_beat * self.__quantization
                time_pr = int(round(time_counter))
                if message.type == 'note_on':
                    pitch = message.note
                    velocity = message.velocity
                    if velocity > 0:
                        notes_on.append((pitch, velocity, time_pr))
                    elif velocity == 0:
                        add_note_to_pr((pitch, velocity, time_pr), notes_on, pr)
                elif message.type == 'note_off':
                    pitch = message.note
                    velocity = message.velocity
                    add_note_to_pr((pitch, velocity, time_pr), notes_on, pr)
            pr = pr.astype(np.int16)
            if np.sum(np.sum(pr)) > 0:
                name = unidecode(track.name)
                name = name.rstrip('\x00')
                if name == u'':
                    name = 'unnamed' + str(counter_unnamed_track)
                    counter_unnamed_track += 1
                if name in pianoroll.keys():
                    pianoroll[name] = np.maximum(pr, pianoroll[name])
                else:
                    pianoroll[name] = pr
        return pianoroll


def music_to_matrix(music_path):
    music_dict = Read_midi(music_path, 4).read_file()
    return utils.dict_to_matrix(music_dict)


def write_music(music_matrix):
    script_dir = os.path.dirname(__file__)
    open(os.path.join(script_dir, 'music_data', 'data.txt'), "w").close()
    f = open(os.path.join(script_dir, 'music_data', 'data.txt'),'a' ,encoding='UTF-8')
    for line in music_matrix:
        f.write(str(line)[1:-1].replace('\'','')+'\n')

def create_music(predict_result):
    script_dir = os.path.dirname(__file__)
    music_dict = {}    
    music_dict['y g2O zfrom ug 1/2  for 88P Comp.ZUN']=np.array(predict_result)    
    write_midi.write_midi(music_dict, 3, os.path.join(script_dir, 'output_music', time.strftime("%Y%m%d-%H%M%S") + '-predict.mid'), 80)




    
    
