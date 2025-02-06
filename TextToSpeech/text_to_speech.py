import streamlit as st
from gtts import gTTS
import tempfile
import os
from io import BytesIO

def init_styles():
    """Initialize custom CSS styles"""
    st.markdown("""
        <style>
        .main {
            padding: 2rem 1rem;
        }
        
        .app-title {
            text-align: center;
            color: #ffffff;
            font-size: 48px;
            margin: 2rem 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .tab-content {
            background-color: #2c3338;
            border: 2px solid #1a1d20;
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        .convert-button {
            width: 100%;
            height: 60px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin: 1rem 0;
        }
        
        .convert-button:hover {
            background-color: #218838;
            transform: translateY(-2px);
        }
        
        .status-box {
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-size: 18px;
            font-weight: bold;
        }
        
        .success-box {
            background-color: #28a745;
            color: white;
        }
        
        .error-box {
            background-color: #dc3545;
            color: white;
        }
        
        .info-box {
            background-color: #17a2b8;
            color: white;
        }
        
        .audio-box {
            background-color: #343a40;
            border: 2px solid #1a1d20;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            color: white;
            min-height: 100px;
        }
        
        .instructions {
            background-color: #343a40;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            color: #a0a0a0;
        }
        
        .stMarkdown {
            color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

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
    # Only set page config if running directly
    if __name__ == "__main__":
        st.set_page_config(page_title="Text to Speech Converter", layout="centered")
    
    init_styles()
    
    st.markdown('<h1 class="app-title">Text to Speech Converter</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="tab-content">
        Convert your text into natural-sounding speech with support for multiple languages and accents.
        Enter your text below and customize the voice settings in the sidebar.
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar settings
    st.sidebar.header("Voice Settings")
    
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
    
    # Text input
    text_input = st.text_area(
        "Enter the text you want to convert to speech:",
        height=150,
        help="Type or paste your text here"
    )
    
    if st.button("Convert to Speech", use_container_width=True):
        if text_input.strip():
            with st.spinner("Converting text to speech..."):
                st.markdown('<div class="status-box info-box">🔊 Converting text to speech...</div>', unsafe_allow_html=True)
                audio_buffer = text_to_speech(
                    text_input,
                    language=languages[selected_language],
                    accent=selected_accent
                )
                
                if audio_buffer:
                    st.markdown('<div class="status-box success-box">✅ Conversion successful!</div>', unsafe_allow_html=True)
                    st.markdown('<div class="audio-box">', unsafe_allow_html=True)
                    st.audio(audio_buffer)
                    
                    # Download button
                    st.download_button(
                        label="Download Audio",
                        data=audio_buffer,
                        file_name="text_to_speech.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box error-box">❌ Please enter some text to convert.</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="instructions">
        <h3>Instructions:</h3>
        
        <h4>Converting Text to Speech:</h4>
        1. Enter your text in the text area above
        2. Select the desired language from the sidebar
        3. For English, you can also select different accents
        4. Click "Convert to Speech" to generate the audio
        5. Use the play button to preview the audio
        6. Click "Download Audio" to save the MP3 file
        
        <h4>Notes:</h4>
        • For best results, keep sentences clear and well-punctuated
        • Internet connection is required for conversion
        • The generated speech will sound more natural with proper punctuation
        • Different languages and accents are available for customization
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 