# app.py
import streamlit as st
import tempfile
import os
from langchain_core.runnables import RunnableConfig
from your_workflow_module import app  # Import your compiled LangGraph workflow
from IPython.display import Audio
import base64

# Set page configuration
st.set_page_config(
    page_title="AI Music Composer",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .composer-container {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #1668a4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎵 AI Music Composer</h1>', unsafe_allow_html=True)
st.markdown("Create beautiful music with AI using LangGraph and Generative AI")

# Main container
with st.container():
    st.markdown('<div class="composer-container">', unsafe_allow_html=True)

    # Input section
    col1, col2 = st.columns(2)

    with col1:
        musician_input = st.text_area(
            "Describe your music:",
            placeholder="e.g., Write a sorrowful string quartet in C minor",
            height=100
        )

    with col2:
        style = st.selectbox(
            "Select music style:",
            ("Classical", "Romantic", "Baroque", "Jazz", "Modern", "Cinematic", "Electronic")
        )

    # Generate button
    generate_button = st.button("Compose Music")

    st.markdown('</div>', unsafe_allow_html=True)


# Function to process the music generation
def generate_music(input_text, style_selection):
    inputs = {
        "musician_input": input_text,
        "style": style_selection
    }

    # Invoke the LangGraph workflow
    with st.spinner("Composing your music... This may take a moment."):
        result = app.invoke(inputs)

    return result


# Function to create a download link for the MIDI file
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href


# Function to convert MIDI to WAV (simplified version)
def convert_midi_to_wav(midi_file_path):
    # This is a simplified version - in production, you'd use proper MIDI to audio conversion
    try:
        # For demonstration, we'll just return the MIDI file path
        # In a real implementation, you would use fluidsynth or similar
        return midi_file_path
    except Exception as e:
        st.error(f"Error converting MIDI to audio: {e}")
        return None


# Process generation when button is clicked
if generate_button:
    if musician_input:
        # Generate music
        result = generate_music(musician_input, style)

        # Display success message
        st.success("Your composition is ready!")

        # Display download link for MIDI file
        midi_file = result['midi_file']
        st.markdown(get_binary_file_downloader_html(midi_file, 'MIDI File'), unsafe_allow_html=True)

        # Try to convert and play audio
        try:
            # Convert MIDI to WAV (simplified)
            audio_file = convert_midi_to_wav(midi_file)

            if audio_file and os.path.exists(audio_file):
                # Display audio player
                st.audio(audio_file, format='audio/wav')
            else:
                st.info("Audio preview is not available. Download the MIDI file to listen to your composition.")
        except:
            st.info("Audio preview is not available. Download the MIDI file to listen to your composition.")

        # Display composition details
        with st.expander("Composition Details"):
            st.write("**Melody:**", result.get('melody', 'N/A'))
            st.write("**Harmony:**", result.get('harmony', 'N/A'))
            st.write("**Rhythm:**", result.get('rhythm', 'N/A'))
            st.write("**Final Composition:**", result.get('composition', 'N/A'))
    else:
        st.warning("Please describe the music you want to create.")

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.write(
        "This AI Music Composer uses LangGraph to orchestrate multiple AI agents that work together to create original music compositions.")

    st.header("How to Use")
    st.write("1. Describe the music you want to create")
    st.write("2. Select a music style")
    st.write("3. Click 'Compose Music'")
    st.write("4. Download your MIDI file or listen to the preview")

    st.header("Features")
    st.write("• Melody Generation")
    st.write("• Harmony Creation")
    st.write("• Rhythm Analysis")
    st.write("• Style Adaptation")
    st.write("• MIDI Export")

# Footer
st.markdown("---")
st.markdown("Built with LangGraph, Generative AI, and Music21")