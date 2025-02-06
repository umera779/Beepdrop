# your_app/signals.py
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from .models import CustomUser, TaskList
from django.dispatch import receiver

@receiver(user_logged_in)
def logout_previous_sessions(sender, request, user, **kwargs):
    # Get all sessions for the user
    current_session_key = request.session.session_key
    sessions = Session.objects.filter(session_key__isnull=False)

    for session in sessions:
        # Load session data
        data = session.get_decoded()
        # If session belongs to the logged-in user and is not the current session, delete it
        if data.get('_auth_user_id') == str(user.id) and session.session_key != current_session_key:
            session.delete()


@receiver(post_save, sender=CustomUser)
def assign_existing_tasks(sender, instance, created, **kwargs):
    if created:
        # Assign all existing tasks to the newly created user
        all_tasks = TaskList.objects.all()

        for task in all_tasks:
            task.assigned_users.add(instance)
       


from django.contrib.auth.models import User
from .models import ReferralCode

@receiver(post_save, sender=User)
def create_referral_code(sender, instance, created, **kwargs):
    if created:
        ReferralCode.objects.create(user=instance)

        # all_tasks = TaskList.objects.all()

        # for task in all_tasks:
        #     task.assigned_users.add(instance)
