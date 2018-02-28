import markdown
from markdown.extensions.toc import TocExtension

from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import ListView, DetailView

from .models import Post


def index(request):
    post_list = Post.objects.all().order_by('-created_time')[:5]

    return render(request, 'index.html', context={'post_list': post_list})


class PostListView(ListView):
    model = Post
    template_name = 'list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return super(PostListView, self).get_queryset().order_by('-created_time')


class PostDetailView(DetailView):

    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views_num()
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        post.content = markdown.markdown(post.content,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                          TocExtension(slugify=slugify),
                                      ])
        return post

