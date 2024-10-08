from flask import Flask, request, send_file, jsonify, Response
from datetime import timedelta
import torch
import whisper
import srt
from spleeter.separator import Separator
import os
import tensorflow as tf

app = Flask(__name__)

# Enable TensorFlow logging to see device placement
tf.debugging.set_log_device_placement(True)

# Map accuracy levels to Whisper model sizes
accuracy_models = {
    '0': 'tiny',
    '1': 'base',
    '2': 'small',
    '3': 'medium',
    '4': 'large'
}

def separate_audio(input_audio_path, output_dir="separated_audio"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_audio_path, output_dir)
    del separator
    return os.path.join(output_dir, os.path.splitext(os.path.basename(input_audio_path))[0], 'vocals.wav')

def transcribe_to_srt(audio_path, model_size="base", srt_filename="output.srt"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(model_size, device=device)
    result = model.transcribe(audio_path)
    subtitles = srt.compose([srt.Subtitle(index=i, start=timedelta(seconds=seg['start']), end=timedelta(seconds=seg['end']), content=seg['text']) for i, seg in enumerate(result['segments'])])
    with open(srt_filename, 'w') as f:
        f.write(subtitles)
    return srt_filename

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    query = request.form.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    accuracy = request.form.get('accuracy', '1')  # Default to '1' (base model) if not provided
    model_size = accuracy_models.get(accuracy, 'base')

    input_audio_path = os.path.join("uploads", file.filename)
    file.save(input_audio_path)

    response_files = []

    if 'subtitles' in query:
        srt_path = transcribe_to_srt(input_audio_path, model_size=model_size)
        response_files.append(srt_path)

    if 'vocals' in query or 'background' in query:
        vocals_path = separate_audio(input_audio_path)
        if 'vocals' in query:
            response_files.append(vocals_path)
        if 'background' in query:
            background_path = vocals_path.replace('vocals.wav', 'accompaniment.wav')
            response_files.append(background_path)

    # Send files individually
    def generate():
        for file_path in response_files:
            yield from open(file_path, 'rb')
            yield b'\n--fileboundary\n'

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=fileboundary')

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)