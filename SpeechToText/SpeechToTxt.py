import speech_recognition as sr
import sys
import time

def listen_and_convert():
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("\nListening... Speak now!")
        
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # Listen for audio input
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=None)
            print("Processing... Please wait.")
            
            try:
                # Use Google Speech Recognition to convert audio to text
                text = recognizer.recognize_google(audio)
                print("\nYou said:", text)
                return text
                
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand what you said.")
                return None
                
            except sr.RequestError as e:
                print(f"Could not request results from speech recognition service; {e}")
                return None
                
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period.")
            return None

def main():
    print("=" * 50)
    print("Speech-to-Text Converter")
    print("=" * 50)
    print("\nThis program will convert your speech to text.")
    print("Press Ctrl+C to exit.")
    
    try:
        while True:
            result = listen_and_convert()
            if result:
                print("\nWould you like to continue? (y/n)")
                response = input().lower()
                if response != 'y':
                    print("\nThank you for using Speech-to-Text Converter!")
                    break
            else:
                print("\nWould you like to try again? (y/n)")
                response = input().lower()
                if response != 'y':
                    print("\nThank you for using Speech-to-Text Converter!")
                    break
            print("\n" + "=" * 50)
            
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main() 