from dataclasses import dataclass
from typing import List, Dict, Union
from random import choice
import hashlib
from enum import Enum
import random

NUM_PROMPTS_PER_CATEGORY = 1000


def getRarity(rarity: int, num_elements_per_rarity: int):
    '''
    Get the rarity of a prompt.
    Considers the number of prompts per category.
    '''
    return [rarity, rarity / (NUM_PROMPTS_PER_CATEGORY * num_elements_per_rarity)]
class WordExtractor(object):

    def __init__(self) -> None:
        '''
        Initialize the word extractor.

        tot 6000
        per category 1000

        common:     675 67,5%
        bronze:     200 20,0%
        silver:     100 10.0%
        gold:       20  2,0%
        mythic:     5   0,5%
        '''
        self.collections = {}

        # we added a collection for testing purposes
        test_collection = {
            0: {
                "dog": getRarity(1, 5),
                "fox": getRarity(1, 5),
                "gorilla": getRarity(1, 5),
                "penguin": getRarity(1, 5),
                "bull": getRarity(1, 5),
                "cat": getRarity(5, 4),
                "tiger": getRarity(5, 4),
                "lion": getRarity(5, 4),
                "panther": getRarity(5, 4),
                "racoon": getRarity(10, 10),
                "goat": getRarity(10, 10),
                "armadillo": getRarity(10, 10),
                "bee": getRarity(10, 10),
                "wolf": getRarity(10, 10),
                "bear": getRarity(10, 10),
                "horse": getRarity(10, 10),
                "cobra": getRarity(10, 10),
                "ant": getRarity(10, 10),
                "mouse": getRarity(10, 10),
                "bird": getRarity(20, 10),
                "beagle": getRarity(20, 10),
                "dolphin": getRarity(20, 10),
                "beluga": getRarity(20, 10),
                "chameleon": getRarity(20, 10),
                "spider": getRarity(20, 10),
                "crab": getRarity(20, 10),
                "coyote": getRarity(20, 10),
                "puma": getRarity(20, 10),
                "bat": getRarity(20, 10),
                "snake": getRarity(75, 9),
                "turtle": getRarity(75, 9),
                "elephant": getRarity(75, 9),
                "rhino": getRarity(75, 9),
                "hippo": getRarity(75, 9),
                "shark": getRarity(75, 9),
                "whale": getRarity(75, 9),
                "fish": getRarity(75, 9),
                "squid": getRarity(75, 9),
            },
            1: {
                "police hat": getRarity(100, 1),
                "crown": getRarity(200, 1),
                "helmet": getRarity(300, 1),
                "baseball hat": getRarity(400, 1),
            },
            2: {
                "sword": getRarity(100, 1),
                "magic wand": getRarity(200, 1),
                "shuriken": getRarity(300, 1),
                "baseball glove": getRarity(400, 1),
            },
            3: {
                "blue and gold": getRarity(100, 1),
                "red and black": getRarity(200, 1),
                "purple and black": getRarity(300, 1),
                "green and red": getRarity(400, 1),
            },
            4: {
                "sun glasses": getRarity(100, 1),
                "red eyes": getRarity(200, 1),
                "purple eyes": getRarity(300, 1),
                "blindfold": getRarity(400, 1),
            },
            5: {
                "futuristic": getRarity(100, 1),
                "samurai": getRarity(200, 1),
                "anime": getRarity(300, 1),
                "steampunk": getRarity(400, 1),
            },
        }

        self.addCollection(1, test_collection)
    
    def addCollection(self, collectionId: int, collection_prompts: Dict[int, Dict[str, List[Union[int, float]]]]):
        '''
        Add a collections of prompts.
        '''
        self.collections[collectionId] = collection_prompts

    def generate_prompt(self, collection_id: int, type_id: int, prompt_id: int):
        '''
        Randomly get a prompt from a collection.
        '''
        random.seed(prompt_id)

        collection = self.collections[collection_id]

        prompt_type = collection[type_id]

        possible_prompts = list(prompt_type.keys())
        possible_prompts_likelihood = [prompt_type[prompt][1] for prompt in possible_prompts]
        extracted_index = random.choices(range(len(possible_prompts)), weights=possible_prompts_likelihood)[0]
        prompt = possible_prompts[extracted_index]
        rarity = prompt_type[prompt][1]

        prompt_type[prompt][0] -= 1
        if prompt_type[prompt][0] <= 0:
            del prompt_type[prompt]

        return prompt, rarity
