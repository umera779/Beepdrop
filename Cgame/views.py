from django.shortcuts import render, redirect
from .models import Counter, TaskList, CustomUser, ButtonState, ReferralCode, Referral
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth import login, get_backends
from django.utils.timezone import now
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sessions.models import Session
from .forms import CustomUserCreationForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.mail import send_mail
from .tokens import account_activation_token
from django.core.mail import EmailMessage

from django.urls import reverse
from smtplib import SMTPException

from django.http import Http404
@login_required
def home(request):

    # Get the counter object associated with the current user

    counter = request.user.counter
    user_balance = request.user.counter.value
    level = "Learner"
    if user_balance > 15000000:
        level = "newbie"
    if user_balance >= 24000000 :
        level = "Amature"
    if user_balance >= 100000000:
        level = "Pro"
    if user_balance >= 500000000:
        level = "Elite"

    players = Counter.objects.all().order_by('-value')[:3]  # Get top 10
    
    leaderboard = []
    
    if len(players) > 0:
        leaderboard.append({
            'rank': 1,
            'username': players[0].user.username,
            'balance': players[0].value
        })
    if len(players) > 1:
        leaderboard.append({
            'rank': 2,
            'username': players[1].user.username,
            'balance': players[1].value
        })
    if len(players) > 2:
        leaderboard.append({
            'rank': 3,
            'username': players[2].user.username,
            'balance': players[2].value
        })

    return render(request, 'index.html', {'counter': counter,'level':level})

@login_required
def get_balance(request):
    """
    Return the current balance of the logged-in user.
    """
    formatted_counter_value = f"{request.user.counter.value:,}"
    return JsonResponse({'balance': formatted_counter_value})

@login_required
def get_button_state(request):
    if request.user.is_authenticated:
        button_state, created = ButtonState.objects.get_or_create(user=request.user)
        remaining_time = button_state.get_remaining_time()
        return JsonResponse({
            'state': button_state.state,
            'remaining_time': remaining_time
        })
    return JsonResponse({'state': 'unclicked', 'remaining_time': 0})

@login_required
def update_button_state(request):
    if request.method == 'POST' and request.user.is_authenticated:
        button_state, created = ButtonState.objects.get_or_create(user=request.user)
        button_state.state = 'clicked'
        button_state.last_clicked = now()
        button_state.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# @login_required
# def increment_counter(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         # Increment the counter
#         mining_speed = request.user.mining  
#         mining_goat = mining_speed.speed
#         counter = request.user.counter
#         counter.value += int(mining_goat)
#         counter.save()

#         # Update the button state
#         button_state, _ = ButtonState.objects.get_or_create(user=request.user)
#         button_state.state = "clicked"
#         button_state.last_clicked = now()
#         button_state.save()

#         formatted_counter_value = f"{counter.value:,}"
#         return JsonResponse({'counter_value': formatted_counter_value, 'button_state': button_state.state})

#     return JsonResponse({'error': 'Invalid request'}, status=400)




@login_required
def taskList(request):
    counter = request.user.counter
    user_tasks = TaskList.objects.filter(assigned_users=request.user)

    if request.method == "POST":
        task_value = request.POST.get('taskvalue')
        task_id = request.POST.get('task_id')
        redirect_url = request.POST.get('redirect_url')
        print('redirect url response:',redirect_url)
        print(redirect_url)
        if task_value and task_id:
            counter.value += int(task_value)
            counter.save()

            task = TaskList.objects.get(id=task_id)
            task.assigned_users.remove(request.user)
            return redirect(redirect_url)
            messages.success(request, f"Task '{task.Taskname}' completed successfully!")
        return redirect('/task')

    context = {"tasklist": user_tasks}
    return render(request, 'task.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()            
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def leaderboard(request):
    players = Counter.objects.all().order_by('-value')[:] 

    leaderboard = []
    current_user_position = None
    current_user_name = None

    # Sort players by their balance in descending order
    players = sorted(players, key=lambda x: x.value, reverse=True)

    for index, player in enumerate(players, start=1):
        leaderboard.append({
            'id': index,
            'username': player.user.username,
            'balance': player.value,
        })
        if player.user == request.user:
            current_user_position = index
            current_user_name = request.user.username

       
  
    return render(request, 'leaderboard.html', {'leaderboard': leaderboard,'current_user_position': current_user_position,'pname':current_user_name})



User = get_user_model()


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Create user but don't save yet
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # Prepare email
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                print(message)
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject,
                    message,
                    'emmanuelumera@yahoo.com',
                    [to_email],
                )
                email.content_subtype = 'html'

                # Try to send email
                try:
                    email.send()
                    messages.success(request, 'Please confirm your email to complete the registration.')
                    return redirect('login')
                except (SMTPException, ConnectionError) as e:
                    # If email fails, delete the inactive user and show error
                    user.delete()
                    messages.error(request, 'Failed to send verification email. Please try again later.')
                    return render(request, 'signup.html', {'form': form})

            except Exception as e:
                user.delete()
                # Handle any other unexpected errors
                messages.error(request, 'An unexpected error occurred. Please try again.')
                return render(request, 'signup.html', {'form': form})
        
        else:
            # Form is invalid, return to signup with errors
            return render(request, 'signup.html', {'form': form})
    
    # GET request - show empty form
    form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})
    
#         return HttpResponse('Activation link is invalid or has expired.')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        return HttpResponse('Activation link is invalid or has expired.')

    if user is not None and account_activation_token.check_token(user, token):
        try:
            # Activate user
            user.is_active = True
            user.save()
            
            # Create counter for new user
            Counter.objects.create(user=user, value=2000)
            
            # Set up backend for authentication
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            
            # Find and process referral if it exists
            try:
                referral = Referral.objects.get(referred_user=user, status='pending')
                # Process reward for the referrer (not the new user)
                success = process_referral_reward(referral.referrer)
                if success:
                    print(f"Successfully processed referral reward for {referral.referrer.username}")
                else:
                    print("Failed to process referral reward")
            except Referral.DoesNotExist:
                print("No pending referral found for this user")
            
            messages.success(request, 'Your account has been activated successfully!')
            return redirect('login')
            
        except Exception as e:
            print(f"Activation error: {str(e)}")
            # If anything fails during activation
            user.is_active = False
            user.save()
            
            # Mark referral as failed if it exists
            Referral.objects.filter(referred_user=user).update(status='failed')
            
            messages.error(request, 'There was an error activating your account. Please try again.')
            return redirect('login')
    else:
        return HttpResponse('Activation link is invalid or has expired.')

def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, 'This account is already active. No verification email was sent.')
            else:
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                send_mail(mail_subject, message, 'emmanuelumera@yahoo.com', [email])
                messages.success(request, 'A new verification email has been sent to your email address.')
        except User.DoesNotExist:
            messages.error(request, 'No account is associated with this email address.')

    return render(request, 'resend_verification_email.html')




@login_required
# def referral_dashboard(request):
#     try:
#         referral_code = request.user.referral_codes
#     except ReferralCode.DoesNotExist:
#         referral_code = ReferralCode.objects.create(user=request.user)

#     referrals_made = Referral.objects.filter(referrer=request.user)
    
#     # Generate the full referral URL
#     current_site = get_current_site(request)
#     referral_url = f"http://{current_site.domain}{reverse('register')}?ref={referral_code.code}"

#     context = {
#         'referral_code': referral_code,
#         'referral_url': referral_url,
#         'referrals_made': referrals_made,
#         'total_referrals': referrals_made.count(),
#         'pending_rewards': referrals_made.filter(reward_claimed=False).count()
#     }
#     return render(request, 'invite.html', context)



def referral_dashboard(request):
    try:
        # Try to get existing referral code
        referral_code = ReferralCode.objects.get(referrer=request.user)
    except ReferralCode.DoesNotExist:
        # Create new referral code if none exists
        referral_code = ReferralCode.objects.create(
            referrer=request.user,
            code=generate_unique_code()
        )

    # Get all referrals made by the user
    referrals_made = Referral.objects.filter(referrer=request.user)

    # Generate the full referral URL
    current_site = get_current_site(request)
    referral_url = f"http://{current_site.domain}{reverse('register')}?ref={referral_code.code}"

    # Prepare context for template
    context = {
        'referral_code': referral_code,
        'referral_url': referral_url,
        'referrals_made': referrals_made,
        'total_referrals': referrals_made.count(),
        'pending_rewards': referrals_made.filter(status='pending').count()  # Changed from reward_claimed to status
    }

    return render(request, 'invite.html', context)

def generate_unique_code():
    import random
    import string
    
    while True:
        # Generate a random code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Check if code already exists
        if not ReferralCode.objects.filter(code=code).exists():
            return code


def register_with_referral(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                
                # Check for referral code
                referral_code = request.session.get('referral_code')
                if referral_code:
                    try:
                        referrer_code = ReferralCode.objects.get(code=referral_code)
                        referrer = referrer_code.referrer  # Changed from .user to .referrer
                        
                        # Prevent self-referral
                        if referrer != user:
                            # Check if user hasn't been referred before
                            existing_referral = Referral.objects.filter(referred_user=user)
                            if existing_referral.exists():
                                # Clean up the user if they already have a referral
                                user.delete()
                                messages.error(request, 'This email has already been referred.')
                                return render(request, 'signup.html', {'form': form})
                            
                            # Create the referral but don't process reward yet
                            referral = Referral.objects.create(
                                referrer=referrer,
                                referred_user=user,
                                status='pending'
                            )
                            
                            # Prepare and send activation email
                            mail_subject = 'Activate your account.'
                            message = render_to_string('activation_email.html', {
                                'user': user,
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': account_activation_token.make_token(user),
                            })
                            print(message)
                            to_email = form.cleaned_data.get('email')
                            email = EmailMessage(
                                mail_subject,
                                message,
                                'emmanuelumera@yahoo.com',
                                [to_email],
                            )
                            email.content_subtype = 'html'
                            
                            try:
                                email.send()
                                messages.success(request, 'Please confirm your email to complete the registration.')
                                # Don't process reward until email is confirmed
                                return redirect('login')
                            except (SMTPException, ConnectionError) as e:
                                # If email fails, clean up everything
                                referral.delete()
                                user.delete()
                                messages.error(request, 'Failed to send verification email. Please try again later.')
                                return render(request, 'signup.html', {'form': form})
                                
                    except ReferralCode.DoesNotExist:
                        # Clean up user if referral code is invalid
                        user.delete()
                        messages.error(request, 'Your referral code was Invalid. Please try again.')
                        return render(request, 'signup.html', {'form': form})
                        
            except Exception as e:
                # Clean up any partially created records
                Referral.objects.filter(referred_user=user).delete()
                if user.pk:
                    user.delete()
                messages.error(request, 'An unexpected error occurred. Please try again.')
                print(e)
                return render(request, 'signup.html', {'form': form})
    else:
        # Store referral code in session if provided
        ref_code = request.GET.get('ref')
        if ref_code:
            request.session['referral_code'] = ref_code
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})





#######################
# Bug to fix 
# > get() returned more than one Referral -- it returned 6!
# the solution is to make sure pending referral are skipped or removed so as to allow new onces claude will fix this 

def process_referral_reward(referrer):
    """
    Process the reward for a successful referral.
    Returns True if the reward was processed, False otherwise.
    """
    try:
        # Find all pending referrals for this referrer
        pending_referrals = Referral.objects.filter(
            referrer=referrer,
            status='pending'
        )
        
        if pending_referrals.exists():
            # Get the referrer's counter
            try:
                counter = referrer.counter
                counter.value += 100000
                counter.save()
                
                # Update all pending referrals to completed
                pending_referrals.update(status='completed')
                
                print(f"Processed reward for referrer {referrer.username}: +100000")
                print(f"New counter value: {counter.value}")
                return True
                
            except Exception as e:
                print(f"Error updating counter: {str(e)}")
                return False
        else:
            print(f"No pending referrals found for {referrer.username}")
            return False
            
    except Exception as e:
        print(f"Error processing referral reward: {str(e)}")
        return False
