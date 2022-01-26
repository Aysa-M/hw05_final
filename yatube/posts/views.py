from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import (get_object_or_404,
                              redirect,
                              render)
from django.conf import settings

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, Follow

COUNT_PER_PAGE = settings.COUNT_PER_PAGE
LETTERS_FOR_TITLE = 30


def index(request):
    """Information which is showing up on the start page."""
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, COUNT_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Information for displaying on the page with posts grouped by GROUPS."""
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).all()
    paginator = Paginator(post_list, COUNT_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """
    The view shows a page profile of an authorised user.
    """
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).all()
    paginator = Paginator(post_list, COUNT_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_quantity = post_list.count()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_quantity': post_quantity,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """The view shows information about a current post."""
    post = get_object_or_404(Post, pk=post_id)
    title = post.text[:LETTERS_FOR_TITLE]
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id).all()
    context = {
        'post': post,
        'title': title,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """The view creates a new post by a special form."""
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', username=new_post.author)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """
    This view edits the post by its id and saves changes in database.
    """
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    if author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    is_edit = True
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """
    The view function creates a new comment by a special form.
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Страница, куда будут выведены посты авторов, на которых подписан
    текущий пользователь.
    """
    follower = request.user
    follow = Follow.objects.filter(user=follower).exists()
    post_list = Post.objects.filter(author__following__user=follower)
    paginator = Paginator(post_list, COUNT_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_quantity = post_list.count()
    context = {
        'follow': follow,
        'post_list': post_list,
        'page_obj': page_obj,
        'post_quantity': post_quantity,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """
    Функция для подписки на интересного автора текущего пользователя.
    """
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    """
    Функция для отписки от автора текущего пользователя.
    """
    follower = request.user
    author = get_object_or_404(User, username=username)
    subscribe = Follow.objects.filter(user=follower, author=author).exists()
    if subscribe:
        following = get_object_or_404(Follow,
                                      user=follower,
                                      author=author)
        following.delete()
    return redirect('posts:profile', username=author.username)
