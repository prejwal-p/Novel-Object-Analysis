import os
import cv2
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torchvision
from torchvision import transforms as pth_transforms
import numpy as np

from PIL import Image
from segment_anything import sam_model_registry 
from segment_anything import SamAutomaticMaskGenerator
from segment_anything import SamPredictor
from torch.utils.data import Dataset, DataLoader
import glob
torch.cuda.empty_cache()
import gc
gc.collect()

os.environ['PYTORCH_CUDA_ALLOC_CONF']='max_split_size_mb:512' #'garbage_collection_threshold:0.8,max_split_size_mb:512'



class Segmenter:
    def __init__(self):        
        self.model_checkpoint = "./SAM/sam_vit_b_01ec64.pth"
        self.device = "cuda"
        try:
            self.sam = sam_model_registry['vit_b'](checkpoint=self.model_checkpoint)
            self.sam.to(self.device)
            self.mask_generator = SamAutomaticMaskGenerator(self.sam, points_per_batch=1)
        except Exception:
            self.device = "cpu"
            self.sam = sam_model_registry['vit_b'](checkpoint=self.model_checkpoint)
            self.sam.to(self.device)
            self.mask_generator = SamAutomaticMaskGenerator(self.sam, points_per_batch=1)



    def get_arena(self, image):
        print(f"Please Wait The Arena is Being Detected (Device: {self.device}).................................")
        try:
            masks = self.mask_generator.generate(image)
        except Exception:
            self.sam = sam_model_registry['vit_b'](checkpoint=self.model_checkpoint)
            self.sam.to("cpu")
            self.mask_generator = SamAutomaticMaskGenerator(self.sam, points_per_batch=1)

        masks = self.mask_generator.generate(image)
        sorted_anns = sorted(masks, key=(lambda x: x['area']), reverse=True)
        box = np.array(sorted_anns[0]['bbox']).astype(int)

        del self.sam
        del self.mask_generator
        del sam
        del mask_generator
        torch.cuda.empty_cache()
        return box 