import streamlit as st
import speech_recognition as sr
from io import BytesIO
import tempfile
import os

def transcribe_audio(audio_file):
    """Transcribe audio file to text using Google Speech Recognition"""
    # Initialize recognizer
    r = sr.Recognizer()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file.write(audio_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Load audio file
        with sr.AudioFile(tmp_file_path) as source:
            # Record audio
            audio = r.record(source)
            
            # Recognize speech using Google Speech Recognition
            text = r.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Speech Recognition service; {e}"
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

def main():
    st.title("Speech to Text Converter")
    st.write("""
    Convert your speech to text using Google's Speech Recognition.
    Upload an audio file (WAV format) or record directly from your microphone.
    """)
    
    # File uploader for audio files
    audio_file = st.file_uploader("Upload an audio file", type=['wav'])
    
    if audio_file is not None:
        st.audio(audio_file)
        
        if st.button("Transcribe Audio"):
            with st.spinner("Transcribing..."):
                transcription = transcribe_audio(audio_file)
                
            st.subheader("Transcription:")
            st.write(transcription)
            
            # Option to copy transcription
            st.text_area("Copy transcription:", transcription)
    
    st.markdown("---")
    st.markdown("""
    ### Instructions:
    1. Upload a WAV audio file using the file uploader above
    2. Click the "Transcribe Audio" button
    3. Wait for the transcription to complete
    4. Copy the transcribed text from the text area
    
    ### Note:
    - Make sure your audio is clear and has minimal background noise
    - The audio file must be in WAV format
    - Internet connection is required for transcription
    """)

if __name__ == "__main__":
    main() 