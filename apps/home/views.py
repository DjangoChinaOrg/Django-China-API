import markdown
from markdown.extensions.toc import TocExtension

from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import ListView, DetailView
from django.db.models import Sum

from .models import Post, ProgressBar, Support


def index(request):
    post_list = Post.objects.all().order_by('-created_time')[:5]
    try:
        index_progress = ProgressBar.objects.filter(title='index')[0].progress
    except:
        index_progress = 70
    support_list = Support.objects.order_by('-id')[:5]
    dic = {'post_list': post_list, 'progress': index_progress, 'support_list': support_list}
    return render(request, 'index.html', context=dic)


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


class SupportView(ListView):
    model = Support
    template_name = 'support.html'
    context_object_name = 'support'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SupportView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['support_list'] = Support.objects.order_by('-id')
        context['sum_money'] = Support.objects.aggregate(sum=Sum('money'))['sum']
        return context
    #
    # def get_queryset(self):
    #     return super(SupportView, self).get_queryset().order_by('-id')
