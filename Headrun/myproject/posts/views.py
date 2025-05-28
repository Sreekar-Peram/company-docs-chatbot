from django.shortcuts import render, redirect
from .models import Post
from django.contrib.auth.decorators import login_required
from . import forms
# Create your views here.

"""
user is authorised
render create_post
"""
@login_required
def posts_list_view(request):
    user_posts = Post.objects.filter(author=request.user)
    return render(request, 'posts/posts_list.html', {'posts': user_posts})

def posts_view(request, slug):
    post = Post.objects.get(slug=slug)
    return render(request, 'posts/posts_view.html', {'post': post})

def posts_create_view(request):
    if request.method == 'POST': 
        form = forms.CreatePost(request.POST, request.FILES) 
        if form.is_valid():
            newpost = form.save(commit=False) 
            newpost.author = request.user 
            newpost.save()
            return redirect('posts:list')
    else:
        form = forms.CreatePost()
    return render(request, 'posts/posts_create.html', { 'form': form })



