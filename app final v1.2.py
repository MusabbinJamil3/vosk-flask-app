from flask import Flask, render_template, jsonify, request
import vosk
import os, json
import pyaudio

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
text_file_path = os.path.join(current_directory, 'conversation.txt')

with open(text_file_path) as text_file:
    default_text_to_send = text_file.read()
    print(default_text_to_send)

app = Flask(__name__)

model = vosk.Model(r"E:\Musab\Task 14 Speech to text\vosk-model-small-en-us-0.15")
recognizer = vosk.KaldiRecognizer(model, 16000)
recognized_text = ""
recognition_running = False

def callback(in_data, frame_count, time_info, status):
    global recognized_text, recognition_running
    
    if not recognition_running:
        return (in_data, pyaudio.paComplete)
    
    if status:
        print(status)
    else:
        recognizer.AcceptWaveform(in_data)
        result = recognizer.PartialResult()
        recognized_text = str(result)[17:-3]
        print(recognized_text, end='', flush=True)

    return (in_data, pyaudio.paContinue)

def speech_to_text():
    global recognition_running

    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=4000,
                        stream_callback=callback)
    except IOError as e:
        print(f'Error opening stream: {e}')
    except Exception as e:
        print(f'Error: {e}')

    print('Mic: On')
    
    stream.start_stream()
    print("Say something:")

    while recognition_running==True:
        pass  # Continue streaming until recognition_running is False
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    result = recognizer.FinalResult()
    print(result)
    with open('conversation.txt', 'w') as file:
        file.write(str(result))

@app.route('/')
def index():
    return render_template('index v1.1.html')

@app.route('/stop_recognition', methods=['GET'])
def stop_recognition():
    global recognition_running

    recognition_running = False

    return jsonify({'status': 'Recognition stopped', 'text': recognized_text})

@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    global recognized_text, recognition_running

    recognized_text = ""  # Clear previous recognized text
    recognition_running = True
    speech_to_text()

    return jsonify({'status': 'Recognition started'})

@app.route('/get_text', methods=['GET'])
def get_text():
    global recognized_text
    return jsonify({'text': recognized_text})

@app.route('/audio_send_text', methods=['POST'])
def send_recognized_text():
    global recognized_text
    return jsonify({'processed_text': recognized_text})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
