import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
import file_manager as fm
from app_config import DEVICE, TRANSFORM, CLASS_NAMES

class PlantDetector:
    def __init__(self, model_name='best_resnet50_cassava.pth'):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        if self.model is not None:
            return True
        
        try:
            model_path = fm.get_model_path(self.model_name)
            
            # resnet50 reconstruct
            self.model = models.resnet50(weights=None)
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Linear(num_ftrs, len(CLASS_NAMES))
            
            # weight loading
            self.model.load_state_dict(torch.load(model_path, map_location=DEVICE))
            self.model = self.model.to(DEVICE)
            self.model.eval()
            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def predict(self, image_path):
        if self.model is None:
            if not self.load_model():
                return None
        
        try:
            # preprocessing
            image = Image.open(image_path).convert('RGB')
            input_tensor = TRANSFORM(image)
            input_batch = input_tensor.unsqueeze(0).to(DEVICE)

            # inference
            with torch.no_grad():
                output = self.model(input_batch)

            # results processing
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            max_prob, predicted_idx = torch.max(probabilities, 0)

            predicted_class = CLASS_NAMES[predicted_idx.item()]
            confidence = max_prob.item() * 100
            
            return predicted_class, confidence
        except Exception as e:
            print(f"Prediction error for {image_path}: {e}")
            return None
