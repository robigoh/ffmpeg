import subprocess
from .models import UploadedFile

def process_with_ffmpeg(file_path, output_path):
    command = f'ffmpeg -i {file_path} {output_path}'
    subprocess.run(command, shell=True)

def process_files():
    for file in UploadedFile.objects.filter(processed=False):
        output_path = file.file_url.replace('.mp4', '_processed.mp4')
        process_with_ffmpeg(file.file_url, output_path)
        file.processed = True
        file.save()