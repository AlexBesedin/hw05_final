from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

NUMBER_POSTS: int = 10


def paginator_func(posts, request):
    paginator = Paginator(posts, NUMBER_POSTS)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.all()
    page_obj = paginator_func(posts, request)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_func(posts, request)
    context = {
        "group": group,
        "page_obj": page_obj,
        "posts": posts,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_func(posts, request)
    following = Follow.objects.filter(author__username=username).count()
    context = {
        "author": author,
        "page_obj": page_obj,
        "posts_count": author.posts.count(),
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        "post": post,
        "author": post.author,
        "posts_count": post.author.posts.count(),
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request,
            "posts/create_post.html",
            {"form": form},
        )
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect("posts:profile", request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None, files=request.FILES or None, instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post = form.save()
            return redirect("posts:post_detail", post.id)
        context = {
            "form": form,
            "is_edit": True,
            "post": post,
        }
        return render(request, "posts/create_post.html", context)
    else:
        return redirect("posts:post_detail", post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_func(post_list, request)
    context = {
        "page_obj": page_obj
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.get_or_create(user=user, author=author)
    return redirect(reverse("posts:profile", args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    is_follower.delete()
    return redirect("posts:profile", username=author)
