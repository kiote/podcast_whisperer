import whisper

if __name__ == "__main__":
    # Load the Whisper model
    model = whisper.load_model("medium")  # You can choose "tiny", "small", "medium", etc.

    # Transcribe the audio file
    result = model.transcribe("last.mp3", language='et', verbose=True)

    # Print or save the transcription text
    print(result["text"])

    # Access and print timecodes for each segment
    for segment in result["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        print(f"[{start:.2f} --> {end:.2f}] {text}")

