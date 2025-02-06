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

# Signup View
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            # mail_subject = 'Activate your account.'
            # message = render_to_string('activation_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': account_activation_token.make_token(user),
            # })
            # to_email = form.cleaned_data.get('email')
            # send_mail(mail_subject, message, 'emmanuelumera@yahoo.com', [to_email])
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
            email.content_subtype = 'html'  # Set the email content type to HTML
            email.send()

            messages.success(request, 'Please confirm your email to complete the registration.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


# Activation View
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        Counter.objects.create(user=user, value=2000)

        # Level.objects.create(user=user, level=1)
        backend = get_backends()[0] 
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
        ##new ##
        # process_referral_reward(referrer)

        messages.success(request, 'Your account has been activated successfully!')
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
def referral_dashboard(request):
    try:
        referral_code = request.user.referral_code
    except ReferralCode.DoesNotExist:
        referral_code = ReferralCode.objects.create(user=request.user)

    referrals_made = Referral.objects.filter(referrer=request.user)
    
    # Generate the full referral URL
    current_site = get_current_site(request)
    referral_url = f"http://{current_site.domain}{reverse('register')}?ref={referral_code.code}"

    context = {
        'referral_code': referral_code,
        'referral_url': referral_url,
        'referrals_made': referrals_made,
        'total_referrals': referrals_made.count(),
        'pending_rewards': referrals_made.filter(reward_claimed=False).count()
    }
    return render(request, 'invite.html', context)

def register_with_referral(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)   

            # Check for referral code
            referral_code = request.session.get('referral_code')
            if referral_code:
                try:
                    referrer_code = ReferralCode.objects.get(code=referral_code)
                    referrer = referrer_code.user
                    # print(referrer.counter.value)
                    
                    # Prevent self-referral
                    if referrer != user:
                        # Check if user hasn't been referred before
                        if not Referral.objects.filter(referred_user=user).exists():
                            Referral.objects.create(
                                referrer=referrer,
                                referred_user=user
                            )
                            
                            mail_subject = 'Activate your account.'
                            message = render_to_string('activation_email.html', {
                                'user': user,
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': account_activation_token.make_token(user),
                            })
                            print(message)
                            # to_email = form.cleaned_data.get('email')
                            # email = EmailMessage(
                            #     mail_subject,
                            #     message,
                            #     'emmanuelumera@yahoo.com',
                            #     [to_email],
                            # )
                            # email.content_subtype = 'html'  # Set the email content type to HTML
                            # email.send()

                            messages.success(request, 'Please confirm your email to complete the registration.')
                            process_referral_reward(referrer)
                except ReferralCode.DoesNotExist:
                    messages.error(request, 'Your referral code was Invalid. Verify your email address')
            
            return redirect('signup')
    else:
        # Store referral code in session if provided
        ref_code = request.GET.get('ref')
        if ref_code:
            request.session['referral_code'] = ref_code
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})


def process_referral_reward(user):
    """
    Process the reward for a successful referral
    You can customize this based on your reward system
    """
    # print(cofond.is_active)
    # if cofond.is_active == True

    # Example: Add points or tokens to user's account
    try:
        referral = Referral.objects.get(referrer=user, reward_claimed=False)
        # Add your reward logic here
        # For example:

        user.counter.value += 100000
        user.counter.save()

        referral.reward_claimed = True
        referral.save()
        return True
    except Referral.DoesNotExist:
        return False


