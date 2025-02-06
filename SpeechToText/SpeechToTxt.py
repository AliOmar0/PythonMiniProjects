import streamlit as st
import speech_recognition as sr
from io import BytesIO
import tempfile
import os
import time

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
        
        .record-button {
            width: 100%;
            height: 120px;
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin: 1rem 0;
        }
        
        .record-button:hover {
            background-color: #c82333;
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
        
        .transcription-box {
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

def record_from_mic(duration=5):
    """Record audio from microphone and transcribe"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Display recording status
        st.markdown('<div class="status-box info-box">🎤 Adjusting for ambient noise...</div>', unsafe_allow_html=True)
        r.adjust_for_ambient_noise(source, duration=1)
        
        st.markdown('<div class="status-box info-box">🎙️ Recording... Speak now!</div>', unsafe_allow_html=True)
        try:
            # Show recording progress
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(duration/100)
                progress_bar.progress(i + 1)
            
            audio = r.listen(source, timeout=duration, phrase_time_limit=duration)
            st.markdown('<div class="status-box info-box">🔍 Processing speech...</div>', unsafe_allow_html=True)
            
            # Try multiple recognition services
            text = None
            error_message = ""
            
            try:
                text = r.recognize_google(audio)
            except sr.RequestError as e:
                error_message += f"Google Speech Recognition error; {str(e)}\n"
            
            if not text:
                try:
                    text = r.recognize_sphinx(audio)
                except:
                    error_message += "Sphinx Recognition error\n"
            
            if text:
                return True, text
            else:
                return False, "Could not recognize speech. " + error_message
                
        except sr.WaitTimeoutError:
            return False, "No speech detected within timeout"
        except sr.UnknownValueError:
            return False, "Speech Recognition could not understand the audio"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

def transcribe_audio(audio_file):
    """Transcribe audio file to text"""
    r = sr.Recognizer()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file.write(audio_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        with sr.AudioFile(tmp_file_path) as source:
            # Show processing status
            st.markdown('<div class="status-box info-box">🔍 Processing audio file...</div>', unsafe_allow_html=True)
            
            # Record audio
            audio = r.record(source)
            
            # Try multiple recognition services
            text = None
            error_message = ""
            
            try:
                text = r.recognize_google(audio)
            except sr.RequestError as e:
                error_message += f"Google Speech Recognition error; {str(e)}\n"
            
            if not text:
                try:
                    text = r.recognize_sphinx(audio)
                except:
                    error_message += "Sphinx Recognition error\n"
            
            if text:
                return True, text
            else:
                return False, "Could not recognize speech. " + error_message
                
    except sr.UnknownValueError:
        return False, "Speech Recognition could not understand the audio"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass

def main():
    # Only set page config if running directly
    if __name__ == "__main__":
        st.set_page_config(page_title="Speech to Text Converter", layout="centered")
    
    init_styles()
    
    st.markdown('<h1 class="app-title">Speech to Text Converter</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="tab-content">
        Convert your speech to text using advanced speech recognition.
        Choose between recording directly from your microphone or uploading an audio file.
        </div>
    """, unsafe_allow_html=True)
    
    # Add tabs for different input methods
    tab1, tab2 = st.tabs(["🎤 Microphone", "📁 File Upload"])
    
    with tab1:
        st.write("Use your microphone to record speech directly")
        
        # Add recording duration selector
        duration = st.slider("Recording Duration (seconds)", 
                           min_value=3, 
                           max_value=30, 
                           value=5,
                           help="Select how long you want to record")
        
        if st.button("Start Recording", key="record_btn", use_container_width=True):
            success, transcription = record_from_mic(duration)
            
            if success:
                st.markdown('<div class="status-box success-box">✅ Transcription successful!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-box error-box">❌ {transcription}</div>', unsafe_allow_html=True)
                transcription = ""
            
            st.markdown('<div class="transcription-box">', unsafe_allow_html=True)
            st.write("Transcription:")
            st.write(transcription)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Copy button
            if transcription.strip():
                st.text_area("Copy transcription:", transcription, key="mic_transcription")
    
    with tab2:
        st.write("Upload an audio file (WAV format)")
        
        # File uploader for audio files
        audio_file = st.file_uploader("Upload an audio file", 
                                    type=['wav'],
                                    help="Only WAV files are supported")
        
        if audio_file is not None:
            st.audio(audio_file)
            
            if st.button("Transcribe Audio", key="transcribe_btn", use_container_width=True):
                success, transcription = transcribe_audio(audio_file)
                
                if success:
                    st.markdown('<div class="status-box success-box">✅ Transcription successful!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="status-box error-box">❌ {transcription}</div>', unsafe_allow_html=True)
                    transcription = ""
                
                st.markdown('<div class="transcription-box">', unsafe_allow_html=True)
                st.write("Transcription:")
                st.write(transcription)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Copy button
                if transcription.strip():
                    st.text_area("Copy transcription:", transcription, key="file_transcription")
    
    st.markdown("""
        <div class="instructions">
        <h3>Instructions:</h3>
        
        <h4>Using Microphone:</h4>
        1. Select recording duration using the slider
        2. Click the "Start Recording" button
        3. Speak clearly into your microphone
        4. Wait for the transcription to complete
        
        <h4>Using File Upload:</h4>
        1. Upload a WAV audio file using the file uploader
        2. Click the "Transcribe Audio" button
        3. Wait for the transcription to complete
        
        <h4>Notes:</h4>
        • When using microphone, speak clearly and minimize background noise
        • For file upload, audio must be in WAV format
        • Internet connection is required for optimal transcription
        • If one recognition service fails, another will be attempted automatically
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 