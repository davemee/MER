# -*- coding: utf-8 -*-

import unittest
import subprocess


class SanityCheckTests(unittest.TestCase):

    def test_no_annotations(self):
        """Nothing should be returned if there are no annotations.

        https://github.com/LLCampos/IBELight/issues/7"""

        bash_command = 'bash get_entities.sh 1 T "not a entity" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        self.assertEqual('', result)

    def test_not_match_mid_word(self):
        """https://github.com/LLCampos/IBELight/issues/10"""
        bash_command = 'bash get_entities.sh 1 A "nicotinic acid amide, isonicotinic acid amide" ChEMBL'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotations = ('1\tA\t0\t14\t0.621077\tnicotinic acid\tunknown\t1\n'
                               '1\tA\t22\t39\t0.647044\tisonicotinic acid\tunknown\t1\n'
                               '1\tA\t0\t20\t0.666192\tnicotinic acid amide\tunknown\t1\n')

        self.assertEqual(correct_annotations, result)

    def test_return_character_offset(self):
        """Annotation offsets returned should be character offsets, not byte
        offsets."""

        # https://github.com/LLCampos/IBELight/issues/11
        bash_command_1 = 'bash get_entities.sh 1 A "‘ oxygen" ChEBI'
        result_1 = subprocess.check_output(bash_command_1, shell=True)

        correct_annotation_1 = '1\tA\t2\t8\t0.441889\toxygen\tunknown\t1\n'

        self.assertEqual(correct_annotation_1, result_1)

        # https://github.com/LLCampos/IBELight/issues/14

        bash_command_2 = 'bash get_entities.sh 1 T "µ testosterone" ChEBI'
        result_2 = subprocess.check_output(bash_command_2, shell=True)

        correct_annotation_2 = '1\tT\t2\t14\t0.59757\ttestosterone\tunknown\t1\n'

        self.assertEqual(correct_annotation_2, result_2)

        # https://github.com/LLCampos/IBELight/issues/15

        bash_command_3 = 'bash get_entities.sh 1 T " water" ChEBI'
        result_3 = subprocess.check_output(bash_command_3, shell=True)

        correct_annotation_3 = '1\tT\t1\t6\t0.378665\twater\tunknown\t1\n'

        self.assertEqual(correct_annotation_3, result_3)

    def test_ignore_full_stop(self):
        """Terms should be annotated even if followed by a full stop.

        https://github.com/LLCampos/IBELight/issues/2"""

        bash_command = 'bash get_entities.sh 1 T "I love testosterone." ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = '1\tT\t7\t19\t0.59757\ttestosterone\tunknown\t1\n'

        self.assertEqual(correct_annotation, result)

    def test_terms_with_more_than_2_words_should_be_recognized(self):
        """https://github.com/LLCampos/IBELight/issues/3"""

        bash_command = 'bash get_entities.sh 1 T "Cetyl trimethyl ammonium bromide" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\tT\t16\t24\t0.519102\tammonium\tunknown\t1\n'
                              '1\tT\t25\t32\t0.486102\tbromide\tunknown\t1\n'
                              '1\tT\t0\t32\t0.711461\tCetyl trimethyl ammonium bromide\tunknown\t1\n')

        self.assertEqual(correct_annotation, result)

    def test_word_position_indexes_consider_multi_whitespaces(self):
        """"https://github.com/LLCampos/IBELight/issues/12"""

        bash_command = 'bash get_entities.sh 1 A "the  potassium" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\tA\t5\t14\t0.54488\tpotassium\tunknown\t1\n')

        self.assertEqual(correct_annotation, result)

    def test_ignore_comma(self):
        """Terms should be annotated even if followed by a comma.

        https://github.com/LLCampos/IBELight/issues/13"""

        bash_command = 'bash get_entities.sh 1 A "water, potassium, oxygen" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\tA\t0\t5\t0.378665\twater\tunknown\t1\n'
                              '1\tA\t7\t16\t0.54488\tpotassium\tunknown\t1\n'
                              '1\tA\t18\t24\t0.441889\toxygen\tunknown\t1\n')

        self.assertEqual(correct_annotation, result)

    def test_annotate_words_between_parenthesis(self):
        """https://github.com/LLCampos/IBELight/issues/16"""

        bash_command = 'bash get_entities.sh 1 T "(water)" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\tT\t1\t6\t0.378665\twater\tunknown\t1\n')

        self.assertEqual(correct_annotation, result)

    def test_special_characters_are_retained_in_output(self):
        """https://github.com/LLCampos/IBELight/issues/17"""

        bash_command = 'bash get_entities.sh 1 T "N-methyl-D-aspartate" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\tT\t0\t20\t0.666192\tN-methyl-D-aspartate\tunknown\t1\n')

        self.assertEqual(correct_annotation, result)

    def test_case_insensitivity(self):

        bash_command = 'bash get_entities.sh 1 T "Water" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\tT\t0\t5\t0.378665\tWater\tunknown\t1\n')

        self.assertEqual(correct_annotation, result)

    def test_match_utf8_in_vocab_with_utf8_in_text(self):

        bash_command = 'bash get_entities.sh 1 T "α-amilase α-amilase" alpha-amylase'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\tT\t0\t9\t0.54488\tα-amilase\tunknown\t1\n'
                              '1\tT\t10\t19\t0.54488\tα-amilase\tunknown\t1\n')

        self.assertEqual(correct_annotation, result)


if __name__ == '__main__':
    unittest.main()