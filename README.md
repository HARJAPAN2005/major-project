## Overview
Anemia is a severe global public health crisis. Traditional diagnosis relies on invasive, painful, and costly blood draws that require specialized clinical infrastructure and generate biohazardous waste. 

This project proposes a **non-invasive, point-of-care anemia screening system** designed for deployment via smartphone cameras. By leveraging deep learning and computer vision, the system extracts precise color features from specific anatomical regions—the eye conjunctiva, palms, and nail beds—to estimate hemoglobin levels rapidly and painlessly.

## Key Features
* **Multi-Modal Analysis:** Combines data from three distinct anatomical regions (eyes, palms, nails) to improve diagnostic robustness and overcome single-modality limitations.
* **Advanced Image Segmentation:** Utilizes state-of-the-art Convolutional Neural Network (CNN) architectures to isolate regions of interest (ROI) with high pixel-level accuracy.
* **Edge-Optimized:** Balances diagnostic accuracy with computational efficiency, incorporating lightweight models (e.g., MobileNetV2) suitable for mobile deployment.
* **Continuous Hemoglobin Estimation:** Designed to process extracted feature vectors (e.g., RGB intensities) through regression models to predict continuous hemoglobin concentrations, moving beyond simple binary classification.

## System Architecture

The pipeline is divided into three parallel segmentation tracks, each tailored to a specific body part using specialized deep learning architectures:

1. **Eye Conjunctiva Segmentation**
   * **Model:** `MobileNetV2-U-Net` Hybrid
   * **Rationale:** Utilizes MobileNetV2 as an efficient encoder to extract deep features with minimal computational overhead, ideal for isolating the delicate structures of the conjunctiva.
2. **Palm Segmentation**
   * **Model:** `U²-Net` (Nested U-Structure)
   * **Rationale:** Employs a nested structure to capture both global context and high-resolution details, providing state-of-the-art boundary precision for complex salient objects like human hands.
3. **Nail Bed Segmentation**
   * **Model:** `Attention U-Net`
   * **Rationale:** Integrates attention gates into the standard U-Net architecture to suppress irrelevant background regions while highlighting salient features, perfectly suited for the small spatial footprint of fingernails.

## Data Pipeline

1. **Image Acquisition:** Capture images of the patient's eyes, palms, and nails using a standard smartphone camera.
2. **Preprocessing:** Normalize images and correct for environmental lighting and varying skin tones.
3. **Segmentation:** Pass images through their respective deep learning models to generate precise binary masks of the ROIs.
4. **Feature Extraction:** Calculate average pixel intensities (Red, Green, Blue channels) and other color space metrics from the masked regions to generate a unified mathematical feature vector ($x$).
5. **Prediction:** Multiply the feature vector by a trained weight matrix ($w$) and add a bias term ($b$) in a regression model to output the estimated hemoglobin level ($y$).

## Datasets
Training the segmentation models relies on a mix of open-source and clinical datasets, including:
* **Human Palm Images Dataset** (Kaggle - feyiamujo)
* **Hands and Palm Images Dataset** (Kaggle - shyambhu)
* Custom proprietary datasets featuring eye conjunctiva and nail beds paired with ground-truth clinical hemoglobin readings.

## Getting Started

### Prerequisites
* Python 3.8+
* PyTorch or TensorFlow (depending on the environment)
* OpenCV, NumPy, scikit-learn, Matplotlib

### Installation
```bash
# Clone the repository
git clone [https://github.com/yourusername/anemia-detection-system.git](https://github.com/yourusername/anemia-detection-system.git)
cd anemia-detection-system

# Install dependencies
pip install -r requirements.txt
```

### Usage
```bash
# Run the segmentation and extraction pipeline on a sample image
python main.py --image_path ./samples/sample_palm.jpg --modality palm

# Run the full multi-modal pipeline
python multi_modal_predict.py --eye ./samples/eye.jpg --palm ./samples/palm.jpg --nail ./samples/nail.jpg
```

## Future Work
* **Dataset Expansion:** Collecting larger, paired datasets containing multi-modal images and corresponding clinical hemoglobin levels to train the final regression model.
* **Environmental Robustness:** Improving color correction algorithms to handle extreme variations in ambient lighting and camera sensor quality across different smartphone tiers.
* **Mobile App Integration:** Packaging the trained models into a lightweight mobile application for real-time edge inference.

## Key References
1. **Jain, P., Bauskar, S., & Gyanchandani, M. (2021).** "Neural Network Based Non-Invasive Method to Detect Anemia from Images of Eye Conjunctiva." *Proceedings of ISCON*.
2. **Qin, X., et al. (2020).** "U²-Net: Going Deeper with Nested U-Structure for Salient Object Detection." *Pattern Recognition*.
3. **Luo, S., Wang, L., & Kern, T. J. (2021).** "Non-Invasive Hemoglobin Level Measurement Using Conjunctiva Images and Deep Learning." *Biomedical Signal Processing and Control*.
4. **Ronneberger, O., Fischer, P., & Brox, T. (2015).** "U-Net: Convolutional Networks for Biomedical Image Segmentation." *MICCAI*
