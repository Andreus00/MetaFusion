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
                "warhammer space marine": getRarity(10),
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
                "diamond": getRarity(1),
                "lightsaber": getRarity(1),
                "chainsaw": getRarity(1),
                "fireball": getRarity(1),
                "dragon egg": getRarity(1),
                "pistol": getRarity(5),
                "rifle": getRarity(5),
                "bow and arrow": getRarity(5),
                "shield": getRarity(5),
                "axe": getRarity(10),
                "spear": getRarity(10),
                "hammer": getRarity(10),
                "knife": getRarity(10),
                "magic wand": getRarity(10),
                "guitar": getRarity(10),
                "microphone": getRarity(10),
                "lightning": getRarity(10),
                "fire extinguisher": getRarity(10),
                "poker cards": getRarity(10),
                "kitty": getRarity(20),
                "dumbbells": getRarity(20),
                "ninja star": getRarity(20),
                "football": getRarity(20),
                "smarphone": getRarity(20),
                "can of beer": getRarity(20),
                "can of soda": getRarity(20),
                "laptop": getRarity(20),
                "sword": getRarity(20),
                "toy car": getRarity(20),
                "soccer ball": getRarity(75),
                "book": getRarity(75),
                "basketball": getRarity(75),
                "flower": getRarity(75),
                "bowling ball": getRarity(75),
                "scissors": getRarity(75),
                "boxing gloves": getRarity(75),
                "camera": getRarity(75),
                "baseball glove": getRarity(75),
                "ice cream": getRarity(75),
            },

            3: {
                "navy blue and platinum": getRarity(1),
                "lavender and gold": getRarity(1),
                "chocolate and silver": getRarity(1),
                "bronze and silver": getRarity(1),
                "bronze and gold": getRarity(1),
                "tangerine and platinum": getRarity(5),
                "silver and cyan": getRarity(5),
                "pink and lavender": getRarity(5),
                "teal and platinum": getRarity(5),
                "yellow and indigo": getRarity(10),
                "steel blue and gold": getRarity(10),
                "cranberry and silver": getRarity(10),
                "yellow and silver": getRarity(10),
                "lilac and silver": getRarity(10),
                "rose and silver": getRarity(10),
                "emerald and coral": getRarity(10),
                "blue and mustard": getRarity(10),
                "lime and red": getRarity(10),
                "red and platinum": getRarity(10),
                "royal blue and bronze": getRarity(20),
                "ruby and ivory": getRarity(20),
                "amethyst and sage green": getRarity(20),
                "forest green and crimson": getRarity(20),
                "wine and pearl": getRarity(20),
                "violet and bronze": getRarity(20),
                "turquoise and magenta": getRarity(20),
                "olive green and coral": getRarity(20),
                "lime green and copper": getRarity(20),
                "sapphire and copper": getRarity(20),
                "blue and gold": getRarity(75),
                "mint green and bronze": getRarity(75),
                "peacock blue and brass": getRarity(75),
                "ruby and copper": getRarity(75),
                "charcoal and bronze": getRarity(75),
                "purple and black": getRarity(75),
                "green and red": getRarity(75),
                "navy blue and brass": getRarity(75),
                "red and black": getRarity(75),
                "maroon and olive": getRarity(75),
            },
            4: {
                "sharingan eyes": getRarity(1),
                "Virtual reality headset": getRarity(1),
                "Monocle": getRarity(1),
                "3D glasses": getRarity(1),
                "laser eyes": getRarity(1),
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
                "gas mask": getRarity(20),
                "medical mask": getRarity(20),
                "Round glasses": getRarity(195),
                "Square glasses": getRarity(195),
                "Reading glasses": getRarity(195),
                "sunglasses": getRarity(195),
                "glasses": getRarity(195),
            },
            5: {
                "2D, cartoonish": getRarity(1),
                "3D, fantasy": getRarity(1),
                "3D, western": getRarity(1),
                "3D, robotic": getRarity(1),
                "3D, zombie apocalypse": getRarity(1),
                "3D, post-apocalyptic": getRarity(5),
                "2D, Van Gogh painting": getRarity(5),
                "2D, Picasso painting": getRarity(5),
                "2D, Dali painting": getRarity(5),
                "2D, renaissance painting": getRarity(10),
                "3D, futuristic": getRarity(10),
                "3D, samurai": getRarity(10),
                "2D, cubism painting": getRarity(10),
                "2D, surrealism painting": getRarity(10),
                "3D, baroque painting": getRarity(10),
                "3D, ancient Roman": getRarity(10),
                "3D, ancient Greek": getRarity(10),
                "2D, ancient Egyptian": getRarity(10),
                "3D, cyberpunk": getRarity(10),
                "2D, ancient Chinese": getRarity(20),
                "2D, ancient Indian": getRarity(20),
                "2D, ancient Japanese": getRarity(20),
                "2D, 35 mm photo": getRarity(20),
                "2D, polaroid photo": getRarity(20),
                "2D, digital photo": getRarity(20),
                "2D, oil painting": getRarity(20),
                "2D, watercolor painting": getRarity(20),
                "2D, acrylic painting": getRarity(20),
                "3D, Gothic": getRarity(20),
                "2D, ink drawing": getRarity(75),
                "2D, charcoal drawing": getRarity(75),
                "2D, pencil drawing": getRarity(75),
                "3D, steampunk": getRarity(75),
                "2D, pastel drawing": getRarity(75),
                "3D, clay sculpture": getRarity(75),
                "3D, stone sculpture": getRarity(75),
                "3D, wood sculpture": getRarity(75),
                "3D, metal sculpture": getRarity(75),
                "3D, medieval": getRarity(75),
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
