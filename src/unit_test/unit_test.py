import unittest
import stats_functions


class TestStatsFunctions(unittest.TestCase):

    
    phrase_1 = 'N'
    phrase_0 = ''
    phrase_complete = "Hey this is a test"

    #### Word count ####
    def test_count_words_1(phrase_1):
        assert stats_functions.count_words(phrase_1) == 1, "Should be 1"

    def test_count_words_0(phrase_0):
        assert stats_functions.count_words(phrase_0) == 0, "Should be 0"

    def test_count_words_complete(phrase_complete):
        assert stats_functions.count_words(phrase_complete) == 5, "Should be 5"

    #### Character count ####
        
    def test_count_characters_1(phrase_1):
        assert stats_functions.count_characters(phrase_1) == 1, "Should be 1"
    
    def test_count_characters_0(phrase_0):
        assert stats_functions.count_characters(phrase_0) == 0, "Should be 0"
    
    def test_count_characters_complete(phrase_complete):
        assert stats_functions.count_characters(phrase_complete) == 18, "Should be 18"
    


    if __name__ == "__main__":
        test_count_words_1(phrase_1)
        print("Word count 1 passed")

        test_count_words_0(phrase_0)
        print("Word count 0 passed")

        test_count_words_complete(phrase_complete)
        print("Word count long phrase passed")

        test_count_characters_1(phrase_1)
        print("Character count 1 passed")

        test_count_characters_0(phrase_0)
        print("Character count 0 passed")

        test_count_characters_complete(phrase_complete)
        print("Character count long phrase passed")
    