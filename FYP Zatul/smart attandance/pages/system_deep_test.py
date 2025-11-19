from deepface import DeepFace
import os

# Sample test image (one cropped from camera or dataset)
img_path = r"C:\Users\Luqman Nurhakim\Desktop\Python\Fyp Zatul\smart attandance\pages\aina.jpg"  # make sure this exists

# Path to dataset
db_path = r"C:\Users\Luqman Nurhakim\Desktop\Python\Fyp Zatul\smart attandance\training_dataset"

if not os.path.exists(db_path):
    print("❌ Dataset path NOT found")
else:
    print("✅ Dataset path found!")


# Run ArcFace recognition
matches = DeepFace.find(
    img_path=img_path,
    db_path=db_path,
    model_name="ArcFace",
    distance_metric="cosine"
)

print(matches[0])  # See if matches are found