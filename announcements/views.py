from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Announcement

@login_required
def announcement_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Announcement.objects.create(title=title, content=content)
        return redirect('admin_dashboard')
    return render(request, 'announcements/announcement_create.html', {})

@login_required
def announcement_update(request, id):
    announcement = get_object_or_404(Announcement, id=id)
    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.content = request.POST.get('content')
        announcement.save()
        return redirect('admin_dashboard')
    return render(request, 'announcements/announcement_update.html', {'announcement': announcement})

@login_required
def announcement_delete(request, id):
    announcement = get_object_or_404(Announcement, id=id)
    announcement.delete()
    return redirect('admin_dashboard')