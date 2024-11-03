import moviepy.editor as mp
import os

def extract_audio(video_path, audio_output_path=None):
    # Load the video file
    video = mp.VideoFileClip(video_path)

    # Extract the audio
    audio = video.audio

    # If audio_output_path is not provided, generate it from the video file name
    if audio_output_path is None:
        video_filename = os.path.basename(video_path)
        audio_filename = os.path.splitext(video_filename)[0] + ".mp3"
        audio_output_path = os.path.join(os.path.dirname(video_path), audio_filename)

    # Write the audio to a file
    audio.write_audiofile(audio_output_path)

    # Close the video file
    video.close()

if __name__ == '__main__':
    # Example usage
    video_file = "./调料罐.mp4"
    extract_audio(video_file)