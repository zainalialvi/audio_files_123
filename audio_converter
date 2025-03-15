import os
import shutil
import streamlit as st
from pydub import AudioSegment
import zipfile

# Streamlit App Title
st.title("🎵 Bulk Audio Converter - WAV 8kHz PCM")

# Sidebar File Uploader
st.sidebar.header("📂 Upload Your Audio Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload .mp3 or .wav files", type=["mp3", "wav"], accept_multiple_files=True
)

# Set up directories
converted_folder = os.path.join(os.getcwd(), "converted_sounds")
zip_output_path = os.path.join(os.getcwd(), "converted_audios.zip")  # ZIP stored in working directory
os.makedirs(converted_folder, exist_ok=True)


def convert_audio(input_file, output_directory, file_name):
    """
    Convert audio files to WAV format with 16-bit PCM and 8kHz sample rate.
    Replace spaces with underscores in the output filename.

    Args:
        input_file (BytesIO): Uploaded file stream.
        output_directory (str): Directory for the output file.
        file_name (str): Name of the uploaded file.

    Returns:
        str: Path to the converted file
    """
    try:
        file_base, file_ext = os.path.splitext(file_name)

        # Replace spaces with underscores in filename
        file_base = file_base.replace(" ", "_")

        # Create output file path
        output_file = os.path.join(output_directory, f"{file_base}.wav")

        # Load audio file from memory (uploaded file)
        audio = AudioSegment.from_file(input_file, format=file_ext[1:])  # Extract format from extension

        # Convert to mono if stereo
        if audio.channels > 1:
            audio = audio.set_channels(1)

        # Set sample rate to 8kHz and bit depth to 16
        audio = audio.set_frame_rate(8000).set_sample_width(2)

        # Export the audio file
        audio.export(output_file, format="wav")

        return output_file

    except Exception as e:
        return None


def zip_directory(folder_path, zip_path):
    """Creates a zip file from a folder."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))  # Keep relative path inside ZIP


# Process files on button click
converted_files = []

if st.button("🚀 Convert All Uploaded Files"):
    if uploaded_files:
        st.write("### Processing Files... ✅")

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

# Download ZIP button at the end
if os.path.exists(zip_output_path):
    with open(zip_output_path, "rb") as f:
        st.download_button(
            label="⬇ Download All Converted Files (ZIP)",
            data=f,
            file_name="converted_audios.zip",
            mime="application/zip",
        )
