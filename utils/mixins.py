class EagerLoaderMixin(object):
    """
    这个mixin包含一个通用的方法，可以通过select_related和prefetch_related提前告知Django
    需要加载的外键信息，任何需要跨表查询的serializer都应该绑定这个mixin，并且在使用的场景里
    （通常都是view）使用这个方法加入查询的外键名
    """
    @staticmethod
    def setup_eager_loading(queryset, select_related=None, prefetch_related=None):
        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        return queryset
