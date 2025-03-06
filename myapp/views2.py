import boto3
from django.conf import settings
from django.shortcuts import render
from .forms import VideoUploadForm

def upload_videos(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY
            )

            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # Handle multiple uploads for input1
            input1_files = request.FILES.getlist('input1')
            for file in input1_files:
                s3.upload_fileobj(file, bucket_name, f"uploads/input1/{file.name}")

            # Handle multiple uploads for input2
            input2_files = request.FILES.getlist('input2')
            for file in input2_files:
                s3.upload_fileobj(file, bucket_name, f"uploads/input2/{file.name}")

            # Handle single file upload for input3
            input3_file = request.FILES['input3']
            s3.upload_fileobj(input3_file, bucket_name, f"uploads/input3/{input3_file.name}")

            return render(request, "upload_success.html")  # Redirect to success page

    else:
        form = VideoUploadForm()

    return render(request, "upload.html", {"form": form})