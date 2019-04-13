from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.contrib.postgres.search import SearchVector

from taggit.models import Tag

from .models import Post, Comment
from .forms import (
    EmailPostForm, 
    CommentForm, 
    SearchForm,
)

PAGINATE_BY = 5

def post_list(request, tag_slug=None):
    object_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, PAGINATE_BY)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        #If page is out of range deliver last page of resuts
        posts = paginator.page(paginator.num_pages)
    return render(
        request,
        'blog/post/list.html',
        {
            'page': page,
            'posts': posts,
            'tag': tag,
        },
    )

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name= 'posts'
    paginate_by = PAGINATE_BY
    template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    #We can be sure, that we'll get a single post, because we set
    #'unique_for_date' parameter in slug field definition to use
    #'publish' date
    post = get_object_or_404(
        Post, slug=post, status='published', publish__year=year,
        publish__month=month, publish__day=day
    )

    #List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment=None

    if request.method == "POST":
        #A comment was posted
        
        comment_form = CommentForm(initial={'post': post.id}, data=request.POST)
        if comment_form.is_valid():
            #Create Comment object, but don't save to the database yet
            new_comment = comment_form.save()
            #Assign current post to the comment
            # new_comment.post = post
            #Save the comment
            # new_comment.save()
    else:
        comment_form = CommentForm(initial={'post': post.id})

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags','-publish')[:4]

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'new_comment': new_comment,
            'comment_form': comment_form,
            'similar_posts': similar_posts,
        }
    )

def post_share(request, post_id):
    # Get post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == "POST":
        #Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recomments you reading"
            message = f"Read '{post.title}' at {post_url}\n\n"\
                      f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True

    else:
        form = EmailPostForm()

    return render(
        request, 
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent,
        })

def index_redirect(request):
    return redirect('blog:post_list')


def post_search(request):
    form = SearchForm()

    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.filter(
                Q(title__icontains=query) | Q(body__icontains=query))
    
    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results,
        }
    )