import os
import shutil
import streamlit as st
from pydub import AudioSegment
import zipfile
import librosa
import numpy as np
import soundfile as sf
import tempfile

# Streamlit App Title
st.title("🎵 IDRAK Audio Converter (Fixed)")

# Sidebar File Uploader
st.sidebar.header("📂 Upload Your Audio Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload .mp3 or .wav files", type=["mp3", "wav"], accept_multiple_files=True
)

# Set up directories
converted_folder = os.path.join(os.getcwd(), "converted_sounds")
zip_output_path = os.path.join(os.getcwd(), "converted_audios.zip")
os.makedirs(converted_folder, exist_ok=True)

def convert_audio(input_file, output_directory, file_name):
    try:
        file_base, file_ext = os.path.splitext(file_name)
        file_base = file_base.replace(" ", "_")  # Replace spaces with underscores
        output_file = os.path.join(output_directory, f"{file_base}.wav")

        # Load audio using librosa for high-quality resampling
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_file.write(input_file.read())
            temp_file_path = temp_file.name

        # Load audio with librosa
        audio, sr = librosa.load(temp_file_path, sr=None, mono=True)
        os.unlink(temp_file_path)  # Clean up temporary file

        # Resample to 8000 Hz using librosa's high-quality resampler
        target_sr = 8000
        audio_resampled = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)

        # Normalize audio to prevent clipping
        audio_normalized = audio_resampled / np.max(np.abs(audio_resampled)) * 0.9

        # Convert to 16-bit PCM
        audio_16bit = (audio_normalized * 32767).astype(np.int16)

        # Save as WAV using soundfile (pydub for final export)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            sf.write(temp_wav.name, audio_16bit, target_sr, subtype='PCM_16')
            temp_wav_path = temp_wav.name

        # Load with pydub to ensure proper WAV formatting
        audio_segment = AudioSegment.from_file(temp_wav_path, format="wav")
        audio_segment = audio_segment.set_channels(1).set_frame_rate(8000).set_sample_width(2)
        audio_segment.export(output_file, format="wav")

        os.unlink(temp_wav_path)  # Clean up temporary WAV
        return output_file

    except Exception as e:
        st.error(f"Error processing {file_name}: {str(e)}")
        return None

def zip_directory(folder_path, zip_path):
    """Creates a zip file from a folder."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

converted_files = []

if st.button("🚀 Convert All Uploaded Files"):
    if uploaded_files:
        st.write("### Processing Files... ✅")

        # Clear previous converted files and ZIP file
        if os.path.exists(converted_folder):
            shutil.rmtree(converted_folder)
        os.makedirs(converted_folder, exist_ok=True)

        if os.path.exists(zip_output_path):
            os.remove(zip_output_path)

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            output_file_path = convert_audio(uploaded_file, converted_folder, file_name)

            if output_file_path:
                converted_files.append(output_file_path)
                st.success(f"✅ Converted: {file_name}")
            else:
                st.error(f"❌ Failed to convert: {file_name}")

        # Create ZIP after processing
        if converted_files:
            zip_directory(converted_folder, zip_output_path)
            st.success(f"🎉 Conversion complete! {len(converted_files)} files processed.")
        else:
            st.warning("⚠ No files were converted. Check your uploaded files!")

    else:
        st.error("❌ No files uploaded. Please upload .mp3 or .wav files.")

# Download ZIP button
if os.path.exists(zip_output_path):
    with open(zip_output_path, "rb") as f:
        st.download_button(
            label="⬇ Download All Converted Files (ZIP)",
            data=f,
            file_name="converted_audios.zip",
            mime="application/zip",
        )
