# Lyrics Generator

This project is a Flask-based web application that processes audio files to generate subtitles and separate vocals from background music using machine learning models.

## Features

With this application, you can:
- **Generate Lyrics**: Automatically transcribe the lyrics from an audio file.
- **Separate Vocals**: Extract the vocal track from an audio file.
- **Separate Background Music**: Extract the background music from an audio file.
## Installation

### Prerequisites

- Python 3.6+
- pip (Python package installer)
- Virtual environment (optional but recommended)

### Setup

1. **Clone the repository**:
   ```sh
   git clone https://github.com/varun0310t/subtitle_generator.git
   cd subtitle_generator

2. Create and activate a virtual environment:
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On macOS/Linux

3. Install dependencies:
   pip install -r requirements.txt    

# Usage

1. Run the Flask server:
   python main.py
   
2. Send a POST request to the /process endpoint:

   URL: http://127.0.0.1:5000/process
   Method: POST
   Form Data:
   file: The audio file to be processed.
   query: A comma-separated string indicating the type of processing (lyrics, vocals, background).
   accuracy: An optional parameter to specify the accuracy level (0 to 4), which determines the Whisper model size. Defaults to 1 (base model).  

# Example Request
Using curl:curl -X POST http://127.0.0.1:5000/process \
          -F "file=@path/to/your/song.mp3" \
          -F "query=lyrics,vocals" \
          -F "accuracy=2"

# Endpoints

1. /process