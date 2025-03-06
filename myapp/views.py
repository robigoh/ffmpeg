import os
import boto3
import tempfile
import stripe
import json
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from .video_processing import process_uploaded_videos
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def upload_videos(request):
    # Fetch subscription data
    user_subscription = None
    if request.user.is_authenticated:
        user_subscription = Subscription.objects.filter(user=request.user).first()
        
    if request.method == "POST" and request.user.is_authenticated:
        user_id = request.user.id
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            uploaded_files = {
                'hooks': request.FILES.getlist('input1'),
                'leads': request.FILES.getlist('input2'),
                'bodies': request.FILES.getlist('input3')  # Body is required
            }

            # Function to save temp file and upload to S3
            def save_and_upload_file(uploaded_file, folder):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                    temp_path = temp_file.name
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)

                s3_key = f"uploads/{user_id}/{folder}/{uploaded_file.name}"
                s3.upload_file(temp_path, bucket_name, s3_key)

                # Generate S3 URL
                s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

                return temp_path, s3_url

            # Process each file and upload to S3
            temp_files = []
            try:
                hook_paths = [save_and_upload_file(file, "input1")[0] for file in uploaded_files['hooks']]
                lead_paths = [save_and_upload_file(file, "input2")[0] for file in uploaded_files['leads']]
                body_paths = [save_and_upload_file(file, "input3")[0] for file in uploaded_files['bodies']]
                temp_files.extend(hook_paths + lead_paths + body_paths)

                # Calculate number of output videos based on hooks and leads count
                # Defaults to 1 if no files are uploaded for hooks or leads
                num_hooks = len(hook_paths) if hook_paths else 1
                num_leads = len(lead_paths) if lead_paths else 1
                output_videos_count = num_hooks * num_leads

                # Get the current user's subscription details
                user_subscription = Subscription.objects.get(user_id=user_id)

                # Check if the user has enough unused credits
                if user_subscription.unused_credits >= output_videos_count:
                    # Deduct credits based on the number of output videos
                    user_subscription.unused_credits -= output_videos_count
                    user_subscription.save()

                    # Process the videos
                    merged_video_urls = process_uploaded_videos(hook_paths, lead_paths, body_paths, user_id)

                    # Extract only filenames from links
                    file_names = [os.path.basename(link) for link in merged_video_urls]

                    return render(request, "upload_success.html", {
                        "download_links": zip(merged_video_urls, file_names)
                    })
                else:
                    # Not enough credits
                    return render(request, "upload_error.html", {
                        "error_message": "You don't have enough unused credits to process the videos."
                    })

            except Subscription.DoesNotExist:
                # Handle case where user subscription does not exist
                return render(request, "upload_error.html", {
                    "error_message": "User subscription not found."
                })

            finally:
                # Ensure temporary files are deleted
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

    else:
        form = VideoUploadForm()

    return render(request, "upload.html", {"form": form, "user_subscription": user_subscription})

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Registration successful. Please log in.")
        return redirect("login")

    return render(request, "register.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("upload_videos")  # Redirect to upload page
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")  # Redirect to login

def create_checkout_session(request, plan_id):
    plan = Plan.objects.get(id=plan_id)
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': plan.name},
                'unit_amount': int(plan.price_per_month * 100),
            },
            'quantity': 1,
        }],
        mode='subscription',
        success_url='http://localhost:8000/success/?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:8000/cancel/',
    )

    return JsonResponse({'id': session.id})

def payment_success(request):
    return render(request, "payment_success.html")

def payment_cancel(request):
    return render(request, "payment_cancel.html")

def plans_view(request):
    plans = Plan.objects.all().order_by('price_per_month')  # Fetch all plans
    user_subscription = None

    if request.user.is_authenticated:
        user_subscription = Subscription.objects.filter(user=request.user).first()

    return render(request, "plans.html", {"plans": plans, "user_subscription": user_subscription})

def subscribe(request, plan_id):
    if not request.user.is_authenticated:
        return redirect("login")

    plan = Plan.objects.get(id=plan_id)

    # Create Stripe Checkout Session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": plan.stripe_price_id,
            "quantity": 1,
        }],
        mode="subscription",
        success_url=request.build_absolute_uri("/success/"),
        cancel_url=request.build_absolute_uri("/cancel/"),
        customer_email=request.user.email
    )

    return redirect(checkout_session.url)

def plan_list(request):
    plans = Plan.objects.all()
    return render(request, "plans/plan_list.html", {"plans": plans})
    
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = json.loads(payload)
    except json.JSONDecodeError as e:
        return HttpResponse(status=400)

    # Handle different events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_email = session['customer_email']
        plan_id = session['metadata']['plan_id']

        # Save subscription in the database
        Subscription.objects.create(user_email=user_email, plan_id=plan_id, status="active")

    return JsonResponse(status=200)
    
def stripe_webhook(request):
    # Handle Stripe webhook event here
    pass
