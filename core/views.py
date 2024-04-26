from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django import forms
from .models import Reviewer
from django.core.mail import send_mail
from django.conf import settings

from .models import Submission
from .forms import SubmissionForm, AssignReviewerForm

def index(request):
    return render(request, 'index.html')

#### REGISTRATION AND ACCOUNTS FLOW ####

@login_required
@user_passes_test(lambda u: u.groups.filter(name = 'editor').exists())
def view_submissions(request):
    submissions = Submission.objects.all()
    return render(request, 'submissions.html', {'submissions': submissions})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

#### SUBMISSIONS WORKFLOW ####

@login_required
def submit(request):
    if request.method == "GET":
        form = SubmissionForm()
    elif request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.author = request.user
            submission.save()
            messages.success(request, 'Your submission was successful!')
            return redirect('submissions')
    else:
        form = SubmissionForm()

    return render(request, 'submit.html', {'form': form})

#### SUBMISSION REVIEW FLOW ####

def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return render(request, 'submission_detail.html', {'submission': submission})


@login_required
@user_passes_test(lambda u: u.groups.filter(name = 'editor').exists())
def assign_reviewer(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == "POST":
        form = AssignReviewerForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not User.objects.filter(email=email).exists():
                # Create a new User
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=User.objects.make_random_password(),
                )
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                # Add the user to the 'reviewer' group
                group = Group.objects.get(name='reviewer')
                user.groups.add(group)

                # Assign the user as a reviewer to the submission
                Reviewer.objects.create(user=user, submission=submission)

                # Send an email to the new user
                send_mail(
                    'You have been assigned as a reviewer',
                    'You have been asked to review a submission. Please create an account to start reviewing.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'Reviewer was successfully assigned!')
            else:
                messages.info(request, 'User with this email already exists. No new user was created.')
                
            return redirect('index')
    else:
        form = AssignReviewerForm()

    return render(request, 'assign_reviewer.html', {'form': form})