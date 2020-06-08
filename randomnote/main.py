#!/usr/bin/env python
from collections import namedtuple
from os import path
import argparse
import random
import time

import pygame as pg
from pygame import midi

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
BACKGROUND_COLOR = BLACK
NOTES_RANGE = (36, 96)
NOTE_SPEED = 50
WINDOW_SIZE = (150, 30)

def asset_path(name):
    return path.join(path.dirname(path.realpath(__file__)), "assets",  name)


class WantQuit(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='midi_in_id', default=3, type=int,
                        help="midi input device id")
    parser.add_argument('-o', dest='midi_out_id', default=0, type=int,
                        help="midi output device id")
    return parser.parse_args()


def note2mynoterepr(note):
    index = note - 36
    octave = index // 12 + 2
    offset = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A",
              "B"][index % 12]

    snote = ["C{}", "C{}#", "D{}", "D{}#", "E{}", "F{}", "F{}#", "G{}", "G{}#",
             "A{}", "A{}#", "B{}", "B{}#"][index % 12].format(octave)
    return f"{snote}  -  {octave}{offset}"


class RNWindow(object):
    def __init__(self, midiin_id, midiout_id):
        self.midiin_id = midiin_id
        self.midiout_id = midiout_id
        pg.init()
        pg.fastevent.init()
        midi.init()
        self._screen = pg.display.set_mode(WINDOW_SIZE)
        self._clock = pg.time.Clock()
        self._midin = midi.Input(midiin_id)
        self._midout = midi.Output(midiout_id)
        self._font = pg.font.Font('freesansbold.ttf', 32)
        self.note = 0
        self.render_text("")

    def render_text(self, text):
        self._text_surf = self._font.render(text, True, GREEN, BLACK)

    def draw(self):
        self._screen.fill(BACKGROUND_COLOR)
        self._screen.blit(self._text_surf, (0, 0))
        pg.display.update()

    def update(self):
        pass

    def draw_note(self):
        pg.draw.circle(self._screen, BLACK, NOTES.get(self._note).pos, 5)

    def next_note(self):
        self._midout.note_off(self.note, NOTE_SPEED)
        self.note = random.randint(*NOTES_RANGE)
        self.render_text(note2mynoterepr(self.note))
        self._midout.note_on(self.note, NOTE_SPEED)

    def process_events(self):
        if self._midin.poll():
            rawevents = self._midin.read(10)
            mevents = midi.midis2events(rawevents, self.midiin_id)
            for mevent in mevents:
                pg.fastevent.post(mevent)

        for event in pg.fastevent.get():
            if event.type == midi.MIDIIN:
                print(event)
                if event.data1 == self.note:
                    self.next_note()
            if event.type == pg.QUIT:
                raise WantQuit()

    def quit(self):
        self._midout.note_off(self.note, NOTE_SPEED)
        pg.quit()

    def run(self):
        self.next_note()
        while True:
            self.process_events()
            self.update()
            self.draw()
            self._clock.tick(20)


def main():
    try:
        args = parse_args()
        win = RNWindow(args.midi_in_id, args.midi_out_id)
        win.run()
    except WantQuit:
        win.quit()


if __name__ == "__main__":
    main()
