from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Group, Post, User
from .forms import CommentForm, PostForm


def paginator_object(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    page_obj = paginator_object(request, post_list)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = 'Здесь будет информация о группах проекта Yatube'
    post_list = group.posts.all()
    page_obj = paginator_object(request, post_list)
    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    page_obj = paginator_object(request, post_list)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    title = post.text[0:30]
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'posts_count': posts_count,
        'title': title,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id) 