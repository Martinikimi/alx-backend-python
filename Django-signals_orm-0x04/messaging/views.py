from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Message, Notification
from django.contrib.auth.models import User

@login_required
@cache_page(60)
def conversation_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=request.user
    )
    messages = messages.select_related('sender', 'receiver').prefetch_related('replies')
    return render(request, 'conversation.html', {'messages': messages, 'other_user': other_user})

@login_required
def delete_user_view(request):
    if request.method == 'POST':
        request.user.delete()
        return JsonResponse({'status': 'success'})
    return render(request, 'delete_account.html')
