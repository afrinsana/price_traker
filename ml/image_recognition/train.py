import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os
import mlflow

class ProductRecognizerTrainer:
    def __init__(self):
        self.input_size = (224, 224)
        self.batch_size = 32
        self.epochs = 10
        self.train_dir = os.path.join('data', 'products', 'train')
        self.model_dir = os.path.join('models')
        self.model_path = os.path.join(self.model_dir, 'product_recognition.h5')
        self.classes = self._get_classes()
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)

    def _get_classes(self) -> list:
        """Get product categories from directory structure"""
        if not os.path.exists(self.train_dir):
            raise FileNotFoundError(f"Training directory '{self.train_dir}' not found.")
        return sorted([d for d in os.listdir(self.train_dir) if os.path.isdir(os.path.join(self.train_dir, d))])

    def create_model(self):
        """Transfer learning with EfficientNet"""
        base_model = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(*self.input_size, 3)
        )
        
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x)
        predictions = Dense(len(self.classes), activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        
        for layer in base_model.layers:
            layer.trainable = False
            
        model.compile(
            optimizer=Adam(0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model

    def train(self):
        """Train with data augmentation and MLflow logging"""
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            validation_split=0.2
        )
        
        train_generator = train_datagen.flow_from_directory(
            self.train_dir,
            target_size=self.input_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='training'
        )
        
        val_generator = train_datagen.flow_from_directory(
            self.train_dir,
            target_size=self.input_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='validation'
        )
        
        model = self.create_model()
        
        # MLflow tracking
        mlflow.set_experiment("Product Recognition")
        with mlflow.start_run():
            history = model.fit(
                train_generator,
                steps_per_epoch=max(1, train_generator.samples // self.batch_size),
                validation_data=val_generator,
                validation_steps=max(1, val_generator.samples // self.batch_size),
                epochs=self.epochs,
                callbacks=[
                    tf.keras.callbacks.ModelCheckpoint(
                        self.model_path,
                        save_best_only=True
                    )
                ]
            )
            
            # Log metrics
            mlflow.log_metrics({
                'train_accuracy': float(history.history['accuracy'][-1]),
                'val_accuracy': float(history.history['val_accuracy'][-1])
            })
            mlflow.keras.log_model(model, "model")
            mlflow.log_artifact(self.model_path)
        
        return history

if __name__ == "__main__":
    trainer = ProductRecognizerTrainer()
    print(f"Training on {len(trainer.classes)} product categories")
    history = trainer.train()
    print(f"Training completed. Model saved to {trainer.model_path}")