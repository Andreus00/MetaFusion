from dataclasses import dataclass
from typing import List, Dict
from random import choice
import hashlib
from enum import Enum
import random
class PromptRareness(Enum):
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    VERY_RARE = 3


class WordExtractor(object):

    def __init__(self) -> None:
        self.collections = {}
        test_collection = {
            0: {
                "dog": [100, PromptRareness.VERY_RARE],
                "cat": [200, PromptRareness.RARE],
                "racoon": [300, PromptRareness.UNCOMMON],
                "bird": [400, PromptRareness.COMMON],
            },
            1: {
                "police hat": [100, PromptRareness.VERY_RARE],
                "crown": [200, PromptRareness.RARE],
                "helmet": [300, PromptRareness.UNCOMMON],
                "baseball hat": [400, PromptRareness.COMMON],
            },
            2: {
                "sword": [100, PromptRareness.VERY_RARE],
                "magic wand": [200, PromptRareness.RARE],
                "shuriken": [300, PromptRareness.UNCOMMON],
                "baseball glove": [400, PromptRareness.COMMON],
            },
            3: {
                "blue and gold": [100, PromptRareness.VERY_RARE],
                "red and black": [200, PromptRareness.RARE],
                "purple and black": [300, PromptRareness.UNCOMMON],
                "green and red": [400, PromptRareness.COMMON],
            },
            4: {
                "sun glasses": [100, PromptRareness.VERY_RARE],
                "red eyes": [200, PromptRareness.RARE],
                "purple eyes": [300, PromptRareness.UNCOMMON],
                "blindfold": [400, PromptRareness.COMMON],
            },
            5: {
                "futuristic": [100, PromptRareness.VERY_RARE],
                "samurai": [200, PromptRareness.RARE],
                "anime": [300, PromptRareness.UNCOMMON],
                "steampunk": [400, PromptRareness.COMMON],
            },
        }
        self.addCollection(1, test_collection)
        self.addCollection(2, test_collection)
    
    def addCollection(self, collection: int, prompts: Dict[str, int]):
        self.collections[collection] = prompts

    def generate_prompt(self, collection_id: int, type_id: int, prompt_id: int):
        '''
        Randomly get a prompt.
        '''
        random.seed(prompt_id)

        collection = self.collections[collection_id]

        prompt_type = collection[type_id]

        possible_prompts = list(prompt_type.keys())
        possible_prompts_likelihood = [prompt_type[prompt][0] for prompt in possible_prompts]
        extracted_index = random.choices(range(len(possible_prompts)), weights=possible_prompts_likelihood)[0]
        prompt = possible_prompts[extracted_index]
        rarity = prompt_type[prompt][1]

        prompt_type[prompt][0] -= 1
        if prompt_type[prompt][0] == 0:
            del prompt_type[prompt]

        return prompt
