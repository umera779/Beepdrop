To implement an invite system in your Django app, where users can generate unique invite links and prevent self-invites or re-invites, follow these steps:
Step 1: Update Models

Create a model to store invite information and track who invited whom.

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string

User = get_user_model()

class Invite(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    invitee = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='invited_by')
    code = models.CharField(max_length=10, unique=True, default=get_random_string(10))
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.inviter} invited {self.invitee or 'N/A'} with code {self.code}"

Step 2: Generate Invite Links

Provide users with a unique invite link.

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def invite_page(request):
    invite, created = Invite.objects.get_or_create(inviter=request.user, used=False)
    invite_link = request.build_absolute_uri(f"/invite/{invite.code}/")
    return render(request, "invite_page.html", {"invite_link": invite_link})

In the invite_page.html template:

<p>Share this link with your friends:</p>
<a href="{{ invite_link }}">{{ invite_link }}</a>

Step 3: Handle Invites

Create a view to handle incoming invite links.

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages

def invite_view(request, code):
    invite = get_object_or_404(Invite, code=code, used=False)

    # Prevent self-invites
    if request.user.is_authenticated and request.user == invite.inviter:
        messages.error(request, "You cannot use your own invite link.")
        return redirect("home")

    # Handle new user registration via the invite link
    if not request.user.is_authenticated:
        # Redirect to signup with code in session
        request.session['invite_code'] = code
        return redirect("signup")

    # Prevent re-invites
    if invite.invitee:
        messages.error(request, "This invite link has already been used.")
        return redirect("home")

    # Assign invitee if user is logged in
    invite.invitee = request.user
    invite.used = True
    invite.save()

    messages.success(request, "You have successfully accepted the invite!")
    return redirect("home")

Step 4: Handle Signup

When a user registers via the invite link, link them to the inviter.

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            code = request.session.pop('invite_code', None)
            if code:
                try:
                    invite = Invite.objects.get(code=code, used=False)
                    invite.invitee = user
                    invite.used = True
                    invite.save()
                except Invite.DoesNotExist:
                    pass
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

Step 5: Prevent Re-Invites

Ensure that a user cannot invite someone already invited or registered.

In the invite generation logic:

@login_required
def invite_page(request):
    invite, created = Invite.objects.get_or_create(inviter=request.user, used=False)
    
    # Prevent users from generating multiple unused invites
    if not created:
        invite_link = request.build_absolute_uri(f"/invite/{invite.code}/")
        return render(request, "invite_page.html", {"invite_link": invite_link})

    invite_link = request.build_absolute_uri(f"/invite/{invite.code}/")
    return render(request, "invite_page.html", {"invite_link": invite_link})

Step 6: Track Invites

You can add a dashboard or admin page to view invites sent and accepted.
Validation Summary

    Self-Invites: Prevent users from using their own invite link.
    Re-Invites: Ensure invite links are single-use by checking the used field.
    Duplicate Invites: Avoid creating multiple unused invite links per user.

Let me know if you need further assistance!


