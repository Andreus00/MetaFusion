import torch

class Prompt:
    '''
    Utility class used to assemble a prompt.
    '''

    def __init__(self, starter="a ", trailer="with clothes, dressed, upper bust, ultra realistic, 4k, frontal view"):
        self.starter =  starter
        self.character = self.hat = self.tool = self.color = self.eyes = self.style = ""
        self.trailer = trailer

    def set_character(self, character):
        if character:
            self.character = f"{self.starter} {character.name}"
        return self
    
    def set_hat(self, hat):
        if hat:
            self.hat = f"with a {hat.name}"
        return self

    def set_color(self, color):
        if color:
            self.color = f"{color.name}"
        return self

    def set_tool(self, tool):
        if tool:
            self.tool = f"{tool.name} in his hand"
        return self

    def set_eyes(self, eyes):
        if eyes:
            self.eyes = f"{eyes.name}"
        return self

    def set_style(self, style):
        if style:
            self.style = f"{style.name} style"
        return self

    def build(self):
        prompt = self.starter
        prompt += f" {self.character}"
        if self.hat:
            prompt += f" wearing a {self.hat} on the head"
        if self.color:
            prompt += f", {self.color}"
        if self.tool:
            prompt += f", with {self.tool} in his hand"
        if self.eyes:
            prompt += f", {self.eyes}"
        if self.style:
            prompt += f", {self.style} style"
        prompt += f", {self.trailer}"

        return prompt
