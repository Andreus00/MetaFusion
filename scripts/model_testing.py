import torch
import diffusers
from PIL import Image
import numpy as np

prompt = "a 3D wizard wearing a wizard hat, red and black, with a book in his hand, reading glasses, steampunk style, upper bust, ultra realistic, 4k, frontal view"

char_mask = torch.from_numpy(np.array(Image.open("/home/andrea/Documenti/Computer Science/Blockchain/project/MetaFusion/data/masks/test_3.png"))[:, :, :3]).to("cuda").unsqueeze(0).permute(0, 3, 1, 2).half() / 255.0
hat_mask = torch.from_numpy(np.array(Image.open("/home/andrea/Documenti/Computer Science/Blockchain/project/MetaFusion/data/masks/hat.png"))[:, :, :3]).to("cuda").unsqueeze(0).permute(0, 3, 1, 2).half() / 255.0
handoff_mask = torch.from_numpy(np.array(Image.open("/home/andrea/Documenti/Computer Science/Blockchain/project/MetaFusion/data/masks/handoff.png"))[:, :, :3]).to("cuda").unsqueeze(0).permute(0, 3, 1, 2).half() / 255.0
glasses_mask = torch.from_numpy(np.array(Image.open("/home/andrea/Documenti/Computer Science/Blockchain/project/MetaFusion/data/masks/glasses.png"))[:, :, :3]).to("cuda").unsqueeze(0).permute(0, 3, 1, 2).half() / 255.0

final_mask = char_mask# + hat_mask + handoff_mask + glasses_mask
print(final_mask.shape)

model = diffusers.AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", cache_dir = "./cache/models/", torch_dtype=torch.float16).to("cuda")

pipeline = diffusers.AutoPipelineForImage2Image.from_pipe(model).to("cuda")

with torch.no_grad():
    image = pipeline(prompt, image=final_mask, strength=0.8, guidance_scale=0.0, num_inference_steps=8).images[0]
    image.save(f"test.png")
