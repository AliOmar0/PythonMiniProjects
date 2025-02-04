from gtts import gTTS
import pygame
import os
import time

def text_to_speech():
    try:
        # Read the text from abc.txt
        with open('abc.txt', 'r') as file:
            text = file.read()

        # Create a gTTS object
        tts = gTTS(text=text, lang='en')

        # Save the audio file
        output_file = 'output.mp3'
        tts.save(output_file)
        print(f"Text has been converted to speech and saved as {output_file}")

        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Play the audio file
        print("Playing the audio...")
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Clean up
        pygame.mixer.quit()

    except FileNotFoundError:
        print("Error: abc.txt file not found!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    text_to_speech() 