# Medical Check-in System: Setup and Installation Guide

This guide will help you set up and run the automated medical check-in system on your computer.

## Prerequisites

- Python 3.7 or higher
- Webcam connected to your computer
- Git (optional, for cloning the repository)

## Installation Steps

1. **Create a project directory and set up a virtual environment**:

```bash
# Create a new directory
mkdir medical-checkin-system
cd medical-checkin-system

# Create and activate a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install required packages**:

```bash
pip install flask opencv-python numpy
```

3. **Create the application structure**:

```
medical-checkin-system/
├── app.py
├── templates/
│   └── index.html
├── patient_records.db (will be created automatically)
└── venv/
```

4. **Create the files**:
   - Copy the `app.py` code into your app.py file
   - Create a templates directory and copy the `index.html` content into templates/index.html

5. **Run the application**:

```bash
python app.py
```

6. **Access the application**:
   - Open a web browser and navigate to `http://127.0.0.1:5000/`

## Usage Guide

1. **Check-in Process**:
   - Enter your name and age in the form
   - Click "Start Measurements" to activate the camera
   - Position yourself in front of the camera so your face is visible
   - Wait a few seconds for the measurements to be taken
   - Click "Stop Measurements" when the readings appear
   - Click "Save Record" to store your information

2. **Viewing Records**:
   - Click on the "View Records" tab to see all patient entries
   - The records are displayed with the most recent entries at the top

## Troubleshooting

- **Camera not working**: Make sure your webcam is properly connected and not being used by another application.
- **Measurements not appearing**: Ensure your face is clearly visible to the camera and well-lit.
- **Application crashes**: Check that you have all the required dependencies installed.

## Notes about the Demo Implementation

This implementation is for demonstration purposes only and includes the following simulations:

- **Height Measurement**: Uses face detection to estimate height (not calibrated for accuracy)
- **Pulse Detection**: Simulates pulse reading based on facial colors (not medically accurate)
- **Temperature Reading**: Generates a random temperature within normal range (36-37.5°C)

In a production environment, you would need to:
1. Connect to actual medical devices or sensors
2. Calibrate the height estimation algorithm
3. Implement proper pulse detection using time-series analysis of facial colors
4. Use thermal cameras or external thermometers for temperature

## Security Considerations

For a production environment, you would need to add:
- User authentication
- Data encryption
- HIPAA compliance measures (for medical data)
- Regular database backups
- Input validation and sanitization