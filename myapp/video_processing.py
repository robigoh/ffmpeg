import os
import ffmpeg
import tempfile
from itertools import product
from .upload_handlers import upload_to_s3

def get_video_resolution(video_path):
    """Retrieve the resolution (width, height) of a video."""
    try:
        probe = ffmpeg.probe(video_path)
        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
        if video_streams:
            width = video_streams[0]["width"]
            height = video_streams[0]["height"]
            return width, height
    except ffmpeg.Error as e:
        print(f"❌ ERROR reading resolution of {video_path}: {e}")
        return None

def merge_videos(video_list, reference_resolution):
    """Merge multiple videos using FFmpeg and upload to S3."""
    
    if len(video_list) < 2:
        raise ValueError("At least two videos are required to merge.")

    # Use a temporary file for merged output
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_output_path = temp_file.name

    # Build FFmpeg input parameters
    input_files = " ".join(f'-i "{video}"' for video in video_list)

    # Construct FFmpeg command
    ffmpeg_cmd = (
        f'ffmpeg -y {input_files} '
        f'-filter_complex "'
        + "".join(
            f'[{i}:v]scale={reference_resolution[0]}:{reference_resolution[1]}:force_original_aspect_ratio=decrease:eval=frame,'
            f'pad={reference_resolution[0]}:{reference_resolution[1]}:-1:-1:color=black[v{i}]; ' for i in range(len(video_list))
        )
        + "".join(f'[v{i}][{i}:a]' for i in range(len(video_list)))
        + f' concat=n={len(video_list)}:v=1:a=1 [v] [a]" '
        f'-map [v] -map [a] -crf 30 -preset veryfast -vcodec libx264 '
        f'-b:v 800k -maxrate 1200k -bufsize 2M -c:a aac -b:a 96k '
        f'"{temp_output_path}"'
    )
    
    # Execute FFmpeg command
    os.system(ffmpeg_cmd)

    return temp_output_path  # Return temp file path

def process_uploaded_videos(hook_videos, lead_videos, body_videos, user_id):
    """
    Generate all valid video combinations and merge them.
    Ensure all videos have the same resolution.
    """

    output_videos = []
    all_videos = (hook_videos or []) + (lead_videos or []) + body_videos

    # Get reference resolution
    if not all_videos:
        return []
    
    reference_resolution = get_video_resolution(all_videos[0])
    print(reference_resolution)
    if not reference_resolution:
        raise ValueError("Could not determine the resolution of uploaded videos.")

    # # Ensure all videos match the resolution
    # for video in all_videos:
        # print (get_video_resolution(video))
        # if get_video_resolution(video) != reference_resolution:
            # raise ValueError(f"Error: {video} has a different resolution. Please upload videos with the same resolution.")

    # Ensure at least one body video exists
    if not body_videos:
        raise ValueError("At least one body video is required.")

    # Generate valid video combinations
    video_combinations = []

    if hook_videos and lead_videos:
        video_combinations = [[h, l, body] for h in hook_videos for l in lead_videos for body in body_videos]
    elif hook_videos:
        video_combinations = [[h, body] for h in hook_videos for body in body_videos]
    elif lead_videos:
        video_combinations = [[l, body] for l in lead_videos for body in body_videos]
    else:
        video_combinations = [[body] for body in body_videos]

    print("Generated Combinations:", video_combinations)  # Debugging output

    for combination in video_combinations:
        # Determine filename format dynamically
        filename_parts = []
        h_index = l_index = None

        for part in combination:
            if part in hook_videos:
                h_index = hook_videos.index(part) + 1
                filename_parts.append(f"hook-{h_index}_")
            if part in lead_videos:
                l_index = lead_videos.index(part) + 1
                filename_parts.append(f"lead-{l_index}_")
        
        # Always append body index
        filename_parts.append("body-1")

        output_filename = "".join(filename_parts) + ".mp4"
        
        # Ensure user-specific merged folder
        user_folder = f"uploads/{user_id}/merged/"
        s3_output_path = f"{user_folder}{output_filename}"

        # Merge videos
        temp_output_path = merge_videos(combination, reference_resolution)

        # Upload to S3
        s3_url = upload_to_s3(temp_output_path, s3_output_path)
        output_videos.append(s3_url)

        # Delete temp file after upload
        os.remove(temp_output_path)

    return output_videos