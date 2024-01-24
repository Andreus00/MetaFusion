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
                # "dog": getRarity(1),
                # "fox": getRarity(1),
                # "gorilla": getRarity(1),
                # "penguin": getRarity(1),
                # "bull": getRarity(1),
                # "cat": getRarity(5),
                # "tiger": getRarity(5),
                # "lion": getRarity(5),
                # "panther": getRarity(5),
                # "racoon": getRarity(10),
                # "goat": getRarity(10),
                # "armadillo": getRarity(10),
                # "bee": getRarity(10),
                # "wolf": getRarity(10),
                # "bear": getRarity(10),
                # "horse": getRarity(10),
                # "cobra": getRarity(10),
                # "ant": getRarity(10),
                # "mouse": getRarity(10),
                # "bird": getRarity(20),
                # "beagle": getRarity(20),
                # "dolphin": getRarity(20),
                # "beluga": getRarity(20),
                # "chameleon": getRarity(20),
                # "spider": getRarity(20),
                # "crab": getRarity(20),
                # "coyote": getRarity(20),
                # "puma": getRarity(20),
                # "bat": getRarity(20),
                # "snake": getRarity(75),
                # "turtle": getRarity(75),
                # "elephant": getRarity(75),
                # "rhino": getRarity(75),
                # "hippo": getRarity(75),
                # "shark": getRarity(75),
                # "whale": getRarity(75),
                # "fish": getRarity(75),
                # "squid": getRarity(75),
                "robot": getRarity(1),
                "cyber dragon": getRarity(1),
                "mecha": getRarity(1),
                "super hero": getRarity(1),
                "computer scientist": getRarity(1),
                "vampire": getRarity(5),
                "zombie": getRarity(5),
                "ghost": getRarity(5),
                "alien": getRarity(5),
                "mad scientist": getRarity(10),
                "soccer player": getRarity(10),
                "basketball player": getRarity(10),
                "wizard": getRarity(10),
                "soldier": getRarity(10),
                "mechanic": getRarity(10),
                "surfer": getRarity(10),
                "pilot": getRarity(10),
                "ninja": getRarity(10),
                "blacksmith": getRarity(10),
                "astronaut": getRarity(10),
                "firefighter": getRarity(20),
                "police officer": getRarity(20),
                "chef": getRarity(20),
                "teacher": getRarity(20),
                "farmer": getRarity(20),
                "artist": getRarity(20),
                "writer": getRarity(20),
                "singer": getRarity(20),
                "actor": getRarity(20),
                "dancer": getRarity(20),
                "clown": getRarity(75),
                "pirate": getRarity(75),
                "cowboy": getRarity(75),
                "man": getRarity(75),
                "woman": getRarity(75),
                "child": getRarity(75),
                "teenager": getRarity(75),
                "old lady": getRarity(75),
                "old man": getRarity(75),
            },
            1: {
                "crown": getRarity(1),
                "tiara": getRarity(1),
                "cylinder": getRarity(1),
                "kefiah": getRarity(1),
                "headset": getRarity(1),
                "wizard hat": getRarity(5),
                "police hat": getRarity(5),
                "chef hat": getRarity(5),
                "firefighter helmet": getRarity(5),
                "flat cap": getRarity(10),
                "cowboy hat": getRarity(10),
                "soldier helmet": getRarity(10),
                "sailor hat": getRarity(10),
                "horned helmet": getRarity(10),
                "bike helmet": getRarity(10),
                "football helmet": getRarity(10),
                "top hat": getRarity(10),
                "helmet": getRarity(10),
                "baseball hat": getRarity(10),
                "beret": getRarity(10),
                "headphones": getRarity(20),
                "headband": getRarity(20),
                "headscarf": getRarity(20),
                "bandana": getRarity(20),
                "pirate hat": getRarity(20),
                "clown hairstyle": getRarity(20),
                "afro": getRarity(20),
                "mohawk": getRarity(20),
                "long hair": getRarity(20),
                "short hair": getRarity(75),
                "curly hair": getRarity(75),
                "straight hair": getRarity(75),
                "blonde hair": getRarity(75),
                "brown hair": getRarity(75),
                "black hair": getRarity(75),
                "bald": getRarity(75),
                "red hair": getRarity(75),
                "white hair": getRarity(75),
                "gray hair": getRarity(75),
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
                "sharingan eyes": getRarity(1),
                "Virtual reality headset": getRarity(1),
                "Monocle": getRarity(1),
                "3D glasses": getRarity(1),
                "Goggles": getRarity(1),
                "gold spikes": getRarity(5),
                "silver spikes": getRarity(5),
                "multiple eyes": getRarity(5),
                "white eyes": getRarity(5),
                "red eyes": getRarity(10),
                "purple eyes": getRarity(10),
                "green eyes": getRarity(10),
                "blue eyes": getRarity(10),
                "cat eyes": getRarity(10),
                "snake eyes": getRarity(10),
                "pirate eye patch": getRarity(10),
                "golden glasses": getRarity(10),
                "Safety glasses": getRarity(10),
                "Aviator glasses": getRarity(10),
                "Round glasses": getRarity(195),
                "Square glasses": getRarity(195),
                "Reading glasses": getRarity(195),
                "sunglasses": getRarity(195),
                "glasses": getRarity(195),
                "gas mask": getRarity(20),
                "medical mask": getRarity(20)
            },
            5: {
                "futuristic": getRarity(100),
                "samurai": getRarity(200),
                "anime": getRarity(300),
                "steampunk": getRarity(400),
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
