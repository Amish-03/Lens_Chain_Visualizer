# Lens Chain Visualizer

An interactive Python application that visualizes the effect of changing focal lengths in a series of three lenses, utilizing a live webcam feed to simulate an optical bench.

## 🚀 Features
- **Real-time Simulation**: Processes webcam feed instantly to show optical effects.
- **Three-Lens System**: Simulate a chain of 3 thin lenses in series.
- **Interactive Controls**: Adjust focal lengths (`f1`, `f2`, `f3`) dynamically via sliders.
- **Visual Feedback**:
    - **Defocus Blur**: Simulates the circle of confusion when the system is out of focus.
    - **Magnification/Zoom**: Simulates the change in effective focal length.
- **Optical Bench Overlay**: Visualizes the lenses (convex/concave) and the optical axis.

## 📦 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Amish-03/Lens_Chain_Visualizer.git
   cd Lens_Chain_Visualizer
   ```

2. **Install Dependencies**
   Ensure you have Python installed. Then install the required libraries:
   ```bash
   pip install opencv-python numpy
   ```

## 🎮 Usage

Run the main application script:
```bash
python main.py
```

- **Controls Window**:
    - Use trackbars to adjust the focal length of Lens 1, Lens 2, and Lens 3.
    - Range: -300mm to +300mm.
    - *Note*: Setting a slider to the middle (0 position) represents a "Planar" lens (infinite focal length, no power).
- **Main Window**:
    - Displays the processed video feed.
    - Bottom overlay shows current statistics and focus status.
    - Press **'q'** to exit the application.

## 💡 How It Works

This simulation uses the **Thin Lens Approximation** and **Gaussian Optics**.

### 1. Effective Focal Length
For multiple thin lenses in close contact (or treated as a combined system), the effective power $P_{eff}$ is the sum of individual powers:

```math
P_{eff} = P_1 + P_2 + P_3
```
```math
1/f_{eff} = 1/f_1 + 1/f_2 + 1/f_3
```

### 2. Image Transformation
The application treats the webcam feed as the "ideal" projected image and applies transformations based on the calculated $f_{eff}$ relative to a "Target Focal Length" ($f_{target}$):

- **Focus (Blur)**:
  - If `f_eff` is close to `f_target`, the image is sharp.
  - Deviation from `f_target` increases the blur radius, simulating defocus.
  - High deviation = Strong Gaussian Blur.

- **Magnification (Zoom)**:
  - Scale factor roughly equals `f_eff / f_target`.
  - Higher effective focal length = Higher Magnification (Zoom In).
  - Lower effective focal length = Lower Magnification (Zoom Out).

This provides an intuitive, qualitative visualization of how lens combinations affect image formation, akin to correcting refractive errors in the human eye.
