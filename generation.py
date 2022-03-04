#!/bin/false
# Not for execution

DEFAULT_AGE = 3


class GenerationTracker:
    def __init__(self):
        self.last_chosen = dict()
        self.generation = 1

    def get_weights(self, additive_offset=None):
        if additive_offset is None:
            additive_offset = 0
        return {o: (self.generation - last_time + additive_offset) ** 2 for o, last_time in self.last_chosen.items()}

    def notify_join(self, option):
        assert option not in self.last_chosen
        self.last_chosen[option] = self.generation - DEFAULT_AGE

    def notify_leave(self, option):
        assert option in self.last_chosen
        del self.last_chosen[option]

    def notify_chosen(self, chosen_option):
        self.generation += 1
        self.last_chosen[chosen_option] = self.generation

    def to_dict(self):
        return dict(g=self.generation, lc=self.last_chosen)

    @staticmethod
    def from_dict(d):
        gt = GenerationTracker()
        gt.generation = d['g']
        gt.last_chosen = d['lc']
        return gt

    @staticmethod
    def combine_weights(coeff1, weights1, coeff2, weights2):
        return {p: coeff1 * w + coeff2 * weights2[p] for p, w in weights1.items() if p in weights2}
