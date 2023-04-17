import io
import os
import base64
import time
import pydub

# Import the Google Cloud client library
from google.cloud import speech_v1p1beta1 as speech

# Set up the credentials and the API client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'my-project-1477242850406-56014d1ed350.json'
client = speech.SpeechClient()

# Set up the audio folder path
audio_folder_path = 'audio-chunks'
# if the folder doesn't exist, create it, otherwise, remove all files in the folder
if not os.path.isdir(audio_folder_path):
    os.mkdir(audio_folder_path)
else:
    for filename in os.listdir(audio_folder_path):
        os.remove(os.path.join(audio_folder_path, filename))

# chunk the audio in m4a into 2 and half mins chunks wav files
original_audio = '../create_character.m4a'
sound = pydub.AudioSegment.from_file(original_audio, 'm4a')
for i, chunk in enumerate(sound[::50000]):
    chunk.export(os.path.join(audio_folder_path, 'chunk{0}.wav'.format(i)), format='wav')


# sort the os.listdir(audio_folder_path) list by filename
def get_file_number(filename):
    return int(filename.split('.')[0].split('chunk')[1])
audios = sorted(os.listdir(audio_folder_path), key=get_file_number)
print(audios)

# output file will be the original_audio filename with .txt extension
output_file = original_audio.split('/')[1].split('.')[0] + '.txt'
print(output_file)

# iterate through each audio file in the folder 
for audio_file in (audios):
    print(audio_file)
    # Read in the audio file data and encode it as Base64
    with open(os.path.join(audio_folder_path, audio_file), 'rb') as f:
        audio_content = base64.b64encode(f.read()).decode('utf-8')
    
    # Call the Google Cloud Speech-to-Text API to transcribe the audio
    response = client.recognize(
        audio = speech.RecognitionAudio(content = audio_content),
        config = speech.RecognitionConfig(
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = 16000,                      # 16khz is optional
            language_code = 'zh-CN',                        # zh-CN is Chinese, en-US is English
            enableAutomaticPunctuation = True,              # enable auto punctuation
            enableSeparateRecognitionPerChannel = True,     # enable multi-channel
            audioChannelCount = 6,                          # number of channels
            model = 'video'                                 # video model is better for long audio
        )
    )

    # write out the transcriptions into "create_character.txt" if file not exists

    with open(output_file, 'a') as f:
        for result in response.results:
            f.write(result.alternatives[0].transcript + '\n')

    # sleep 1 second to prevent timeout
    time.sleep(1)

