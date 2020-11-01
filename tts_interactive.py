import contextlib
import io
import sys
from instant_tts import char_tts
from instant_tts import change_mode
from voices_dict import voices_dict

class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout

chars_list = '\n\t'.join(list(voices_dict.keys()))

print("Interactive TTS mode running.")
character = input(f"Choose a character from the following options:\n\t{chars_list}\n")

tone='neutral'
print("Tone set to 'neutral'\n\n")

command = input('Enter TTS text or command.\n')

while 1==1:
    if command.startswith("tone:"):
        old_tone = tone
        tone = command.split(":")[1]
        if old_tone == tone:
            print('\tThat is the tone you were already using.\n')
        else:
            change_mode(character=character,tone=tone)
            print(f'\tVocal tone switched from {old_tone} to {tone}.\n')
    elif command.startswith("char:") or command.startswith("character:"):
        old_character = character
        character = command.split(":")[1]
        if old_character == character:
            print('\tThat is the character you were already using.\n')
        elif character not in voice_dict.keys():
            print('\tThat character is not an available voice option.\n')
        else:
            if tone not in voice_dict[character]['tone'].keys() or len(voice_dict[character]['tone'][tone]) == 0:
                tone_msg=(f"\tCurrent tone '{tone}' not available for character {character}. Switching to 'neutral'.\n")
                tone = neutral
            else:
                tone_msg=''
            change_mode(character=character,tone=tone)
            print(f'\tCharacter mode switched from {old_character} to {character}.\n{tone_msg}')
    elif command.startswith('quit()'):
        print('\tEnding session...\n')
        break
    else:
        with nostdout():
            char_tts(text=command, character=character,tone=tone)
    command = input()

