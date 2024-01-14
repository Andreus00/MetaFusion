from dataclasses import dataclass
from typing import Listg, Dict
from random import choice


class WordExtractor(object):

    def __init__(self) -> None:
        self.collections = {}
        test_collection = {
            0: {
                "dog": 100,
                "cat": 200,
                "fish": 300,
                "bird": 400,
            },
            1: {
                "hat": 100,
                "cap": 200,
                "helmet": 300,
                "busby hat": 400,
            },
            2: {
                "sword": 100,
                "magic wand": 200,
                "shuriken": 300,
                "baseball glove": 400,
            },
            3: {
                "blue and gold": 100,
                "red and black": 200,
                "purple and black": 300,
                "green and red": 400,
            },
            4: {
                "sun glasses": 100,
                "red eyes": 200,
                "purple eyes": 300,
                "blindfold": 400,
            },
            5: {
                "futuristic": 100,
                "samurai": 200,
                "anime": 300,
                "realistic": 400,
            },
        }
        self.addCollection(1, test_collection[0])
    
    def addCollection(self, collection: int, prompts: Dict[str, int]):
        self.collections[collection] = prompts

    def generate_prompt(self, index:int, collection_id: int, type_id: int, packet_id: int, prompt_id: int):
        '''
        Randomly get a prompt.
        '''
        collection = self.collections[collection_id]

        prompt_type = collection[type_id]

        possible_prompts = list(prompt_type.keys())
        extracted_index = prompt_id % len(possible_prompts)
        prompt = possible_prompts[extracted_index]

        prompt_type[prompt] -= 1
        if prompt_type[prompt] == 0:
            del prompt_type[prompt]

        return prompt
