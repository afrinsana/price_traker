import tensorflow as tf
import numpy as np
from PIL import Image
from typing import Dict, Optional

class ProductRecognizer:
    def __init__(self, model_path: str, labels_path: str):
        self.model = tf.keras.models.load_model(model_path)
        self.labels = self._load_labels(labels_path)
        self.input_size = (224, 224)

    def _load_labels(self, path: str) -> Dict[int, str]:
        """Load label mapping from file"""
        with open(path) as f:
            return {i: line.strip() for i, line in enumerate(f.readlines())}

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Prepare image for model input"""
        img = Image.open(image_path).resize(self.input_size)
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return tf.keras.applications.efficientnet.preprocess_input(img_array)

    def recognize(self, image_path: str, top_k: int = 3) -> Optional[Dict]:
        """Recognize product from image"""
        try:
            processed_img = self.preprocess_image(image_path)
            predictions = self.model.predict(processed_img)[0]
            
            top_indices = np.argsort(predictions)[-top_k:][::-1]
            results = {
                self.labels[i]: float(predictions[i])
                for i in top_indices
            }
            
            return {
                "predictions": results,
                "best_match": max(results.items(), key=lambda x: x[1])
            }
        except Exception as e:
            print(f"Recognition error: {str(e)}")
            return None

if __name__ == "__main__":
    recognizer = ProductRecognizer(
        model_path='models/product_recognizer.h5',
        labels_path='models/labels.txt'
    )
    result = recognizer.recognize('test_product.jpg')
    print(result)
    