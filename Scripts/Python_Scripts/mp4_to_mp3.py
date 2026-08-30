import os
from moviepy import VideoFileClip  # New import for version 2.0+

def convert_mp4_to_mp3(directory_path):
    # Iterate through all files in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".mp4"):
            video_path = os.path.join(directory_path, filename)
            audio_path = os.path.join(directory_path, filename.rsplit('.', 1)[0] + ".mp3")
            
            print(f"Converting: {filename} -> {os.path.basename(audio_path)}")
            
            try:
                # Load the video file
                with VideoFileClip(video_path) as video:
                    if video.audio:
                        # In v2.0+, write_audiofile is called directly on the audio attribute
                        video.audio.write_audiofile(audio_path, logger=None)
                    else:
                        print(f"No audio stream in {filename}")
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

convert_mp4_to_mp3('.')
