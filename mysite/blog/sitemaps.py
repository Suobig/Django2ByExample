from django.contrib.sitemaps import Sitemap
from blog.models import Post

class PostsSiteMap(Sitemap):
    changfeq = "weekly"
    priority = 0.9

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated