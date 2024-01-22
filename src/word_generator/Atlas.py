from dataclasses import dataclass
from typing import List, Dict, Union
from random import choice
import hashlib
from enum import Enum
import random

NUM_PROMPTS_PER_CATEGORY = 1000


def getRarity(rarity: int):
    '''
    Get the rarity of a prompt.
    Considers the number of prompts per category.
    '''
    return [rarity, rarity / NUM_PROMPTS_PER_CATEGORY]
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
                "dog": getRarity(1),
                "fox": getRarity(1),
                "gorilla": getRarity(1),
                "penguin": getRarity(1),
                "bull": getRarity(1),
                "cat": getRarity(5),
                "tiger": getRarity(5),
                "lion": getRarity(5),
                "panther": getRarity(5),
                "racoon": getRarity(10),
                "goat": getRarity(10),
                "armadillo": getRarity(10),
                "bee": getRarity(10),
                "wolf": getRarity(10),
                "bear": getRarity(10),
                "horse": getRarity(10),
                "cobra": getRarity(10),
                "ant": getRarity(10),
                "mouse": getRarity(10),
                "bird": getRarity(20),
                "beagle": getRarity(20),
                "dolphin": getRarity(20),
                "beluga": getRarity(20),
                "chameleon": getRarity(20),
                "spider": getRarity(20),
                "crab": getRarity(20),
                "coyote": getRarity(20),
                "puma": getRarity(20),
                "bat": getRarity(20),
                "snake": getRarity(75),
                "turtle": getRarity(75),
                "elephant": getRarity(75),
                "rhino": getRarity(75),
                "hippo": getRarity(75),
                "shark": getRarity(75),
                "whale": getRarity(75),
                "fish": getRarity(75),
                "squid": getRarity(75),
            },
            1: {
                "police hat": getRarity(100),
                "crown": getRarity(200),
                "helmet": getRarity(300),
                "baseball hat": getRarity(400),
            },
            2: {
                "sword": getRarity(100),
                "magic wand": getRarity(200),
                "shuriken": getRarity(300),
                "baseball glove": getRarity(400),
            },
            3: {
                "blue and gold": getRarity(100),
                "red and black": getRarity(200),
                "purple and black": getRarity(300),
                "green and red": getRarity(400),
            },
            4: {
                "sun glasses": getRarity(100),
                "red eyes": getRarity(200),
                "purple eyes": getRarity(300),
                "blindfold": getRarity(400),
            },
            5: {
                "futuristic": getRarity(100),
                "samurai": getRarity(200),
                "anime": getRarity(300),
                "steampunk": getRarity(400),
            },
        }

        self.addCollection(1, test_collection)
        self.addCollection(2, test_collection)
    
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
