"""
Class Rule contains thresholds and its corresponding labels of an SQI.
"""
from vital_sqi.common.utils import *


class Rule:
    """ """

    def __init__(self, name, rule_def=None):
        self.name = name
        self.rule_def = rule_def

    def __setattr__(self, name, value):
        if name == 'name':
            if not isinstance(value, str):
                raise AttributeError('Name of SQI rule must be a string '
                                     'containing only letter, number, '
                                     'and hyphens')
        if name == 'rule_def':
            if not (isinstance(value, list) or value is None):
                raise AttributeError('Rule definition must be a list or None')
        super().__setattr__(name, value)

    def load_def(self, source=None):
        self.rule_def = parse_rule(self.name, source)

    def save_def(self):
        def_str = " ".join(self.rule_def)
        return def_str


rule1 = Rule(name = 'a', rule_def= [1, 1])