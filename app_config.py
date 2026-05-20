import torch
from torchvision import transforms

# device config
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# model config
CLASS_NAMES = [
    'Cassava Bacterial Blight (CBB)',
    'Cassava Brown Streak Disease (CBSD)',
    'Cassava Green Mottle (CGM)',
    'Cassava Mosaic Disease (CMD)',
    'Healthy'
]

# image transformation
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ui colors
COLORS = {
    "primary": "#27ae60",
    "secondary": "#2c3e50",
    "bg": "#f4f7f6",
    "card": "#ffffff",
    "text": "#34495e",
    "header": "#1a252f",
    "danger": "#e74c3c",
    "overlay": "#1c1c1c"
}
