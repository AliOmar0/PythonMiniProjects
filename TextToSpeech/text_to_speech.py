import streamlit as st
from gtts import gTTS
import tempfile
import os
from io import BytesIO

def text_to_speech(text, language='en', accent='com'):
    """Convert text to speech and return the audio file"""
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=language, tld=accent)
        
        # Save to BytesIO buffer
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer
    except Exception as e:
        st.error(f"Error converting text to speech: {str(e)}")
        return None

def main():
    st.title("Text to Speech Converter")
    st.write("Convert your text into natural-sounding speech!")
    
    # Text input
    text_input = st.text_area("Enter the text you want to convert to speech:", height=150)
    
    # Sidebar settings
    st.sidebar.header("Settings")
    
    # Language selection
    languages = {
        'English': 'en',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt',
        'Hindi': 'hi',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Chinese': 'zh-CN'
    }
    
    selected_language = st.sidebar.selectbox(
        "Select Language",
        list(languages.keys())
    )
    
    # Accent selection (for English)
    accents = {
        'US': 'com',
        'UK': 'co.uk',
        'Australia': 'com.au',
        'India': 'co.in',
        'Canada': 'ca'
    }
    
    selected_accent = 'com'
    if selected_language == 'English':
        selected_accent = st.sidebar.selectbox(
            "Select Accent",
            list(accents.keys())
        )
        selected_accent = accents[selected_accent]
    
    if st.button("Convert to Speech"):
        if text_input.strip():
            with st.spinner("Converting text to speech..."):
                audio_buffer = text_to_speech(
                    text_input,
                    language=languages[selected_language],
                    accent=selected_accent
                )
                
                if audio_buffer:
                    st.audio(audio_buffer)
                    
                    # Download button
                    st.download_button(
                        label="Download Audio",
                        data=audio_buffer,
                        file_name="text_to_speech.mp3",
                        mime="audio/mp3"
                    )
        else:
            st.warning("Please enter some text to convert.")
    
    st.markdown("---")
    st.markdown("""
    ### Instructions:
    1. Enter your text in the text area above
    2. Select the desired language from the sidebar
    3. For English, you can also select different accents
    4. Click "Convert to Speech" to generate the audio
    5. Use the play button to preview the audio
    6. Click "Download Audio" to save the MP3 file
    
    ### Note:
    - For best results, keep sentences clear and well-punctuated
    - Internet connection is required for conversion
    - The generated speech will sound more natural with proper punctuation
    """)

if __name__ == "__main__":
    main() 