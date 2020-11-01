from encoder.params_model import model_embedding_size as speaker_embedding_size
from utils.argutils import print_args
from utils.modelutils import check_model_paths
from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
import argparse
import torch
import sys
from audioread.exceptions import NoBackendError
import os
import re
from timeit import default_timer as timer

import sys
import contextlib
import io

import sounddevice as sd

class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stdout = DummyFile()
    sys.stderr = DummyFile()
    yield
    sys.stdout = save_stdout
    sys.stderr = save_stderr

from voices_dict import voices_dict
Lorem_Ipsum="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

encoder_path=Path("/Users/glw001/Documents/Development/voice_clone/Real-Time-Voice-Cloning/encoder/saved_models/pretrained.pt")
synthesizer_path=Path("/Users/glw001/Documents/Development/voice_clone/Real-Time-Voice-Cloning/synthesizer/saved_models/logs-pretrained/")
vocoder_path=Path("/Users/glw001/Documents/Development/voice_clone/Real-Time-Voice-Cloning/vocoder/saved_models/pretrained/pretrained.pt")

check_model_paths(encoder_path=encoder_path, synthesizer_path=synthesizer_path,
                      vocoder_path=vocoder_path)
    
    
global in_fpath, filenum, preprocessed_wav, embed, torch, vocoder
filenum = 0

data_path = '/Users/glw001/Documents/Development/voice_clone/LibriSpeech/train-clean-100'
in_fpath = Path(f'{data_path}/F1088-Christabel/134315/1088-134315-0002.flac')

seed = 694201312

word_substitutions={
    'do':'doo',
    'Do':'Doo',
    'NPC':'En Pee See'
    }

## Load the models one by one.
print("Preparing the encoder, the synthesizer and the vocoder...")
encoder.load_model(encoder_path)
synthesizer = Synthesizer(synthesizer_path.joinpath("taco_pretrained"), seed=seed)
vocoder.load_model(vocoder_path)

preprocessed_wav = encoder.preprocess_wav(in_fpath)
original_wav, sampling_rate = librosa.load(str(in_fpath))
preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)

embed = encoder.embed_utterance(preprocessed_wav)
torch.manual_seed(seed)
vocoder.load_model(vocoder_path)

def word_replace(text:str):
    text = " " + text + " "
    for word in word_substitutions:
        regex=f'\s({word})[\.|\s|\!|\?]'
        word_match = re.findall(regex,text)
        for i in word_match:
            text = text.replace(i,word_substitutions[word],1)
    return text

def text_to_speech(text:str,play_sound:bool=True):
    start = timer()
    texts = [text]
    embeds = [embed]
    print("Creating the MEL spectrogram")
    with nostdout():
        specs = synthesizer.synthesize_spectrograms(texts, embeds)
        spec = specs[0]

    print("Generating audio")

    with nostdout():
        generated_wav = vocoder.infer_waveform(spec)
        generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate))
        
        # Trim excess silences to compensate for gaps in spectrograms (issue #53)
        generated_wav = encoder.preprocess_wav(generated_wav)
        
    filename = f'tts_generated{filenum}.wav'
    sf.write(filename, generated_wav.astype(np.float32), synthesizer.sample_rate)

    print(text)
    if play_sound:
        os.system(f'afplay {filename} &')
    elapsed_time = timer() - start
    print(f'Generated in {elapsed_time}')
    
def char_tts(text:str=Lorem_Ipsum,character:str=None,tone:str=None):
    
    global filenum
    
    training_dir = voices_dict[character]['ID']
    tone_file = voices_dict[character]['tone'][tone] + '.flac'
    tone_dir = tone_file.split("-")[1]
    local_infpath = Path(f'{data_path}/{training_dir}/{tone_dir}/{tone_file}')
    
    sentences = word_replace(text).replace(",","\n").replace(". ",'.\n|\n ').replace("?",'?\n|\n').replace("!",'!\n|\n').replace(";",';|\n').split("|")

    i=0
    for loop in range(0,len(sentences)):
        while i < len(sentences)-1 and len(sentences[i]) < 60 and ';' not in sentences[i]:
            sentences[i] = sentences[i] + sentences[i+1]
            sentences.remove(sentences[i+1])
        i += 1
    if len(sentences[-1].strip()) == 0:
        sentences.remove(sentences[-1])
    
    change_mode(character=character,tone=tone)
    
    for i in sentences:
        text_to_speech(i)
        filenum = (filenum + 1) % 10
        
def change_mode(character:str="Human_Man",tone:str="neutral"):
    
    training_dir = voices_dict[character]['ID']
    tone_file = voices_dict[character]['tone'][tone] + '.flac'
    tone_dir = tone_file.split("-")[1]
    local_infpath = Path(f'{data_path}/{training_dir}/{tone_dir}/{tone_file}')
    
    global in_fpath, filenum, preprocessed_wav, embed, torch, vocoder
    if local_infpath != in_fpath and character is not None:
        if tone is None:
            tone = "neutral"
        
        print(f'Reference sound has changed; now loading {character}:{tone}...')
        with nostdout():
            in_fpath = local_infpath
        
            preprocessed_wav = encoder.preprocess_wav(in_fpath)
            original_wav, sampling_rate = librosa.load(str(in_fpath))
            preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)

            embed = encoder.embed_utterance(preprocessed_wav)
            torch.manual_seed(seed)
            vocoder.load_model(vocoder_path)
            text_to_speech('Tea.',play_sound=False)
    else:
        print('Mode is already correct. No need to change.')