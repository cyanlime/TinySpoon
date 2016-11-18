from django.conf.urls import url, include
from rest_framework import routers
from . import views

from django.conf import settings
from django.conf.urls.static import static


router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)
#router.register(r'groups', views.GroupViewSet)
router.register(r'category',views.CategoryViewSet)
router.register(r'material',views.MaterialViewSet)
router.register(r'procedure',views.ProcedureViewSet)
router.register(r'recipes',views.RecipeViewSet)
router.register(r'tag',views.TagViewSet)
urlpatterns = [	
    url(r'^', include(router.urls)),
	url(r'^v1/tags/$', views.tags, name = 'tags'),
	url(r'^v1/recipes/$', views.recipes, name = 'recipes'),
	url(r'^v1/recipes/(?P<recipe_id>[0-9]+)/$', views.recipe, name = 'recipe'),
	url(r'^v1/pagination/$', views.pagination, name = 'pagination'),
	url(r'^v1/collect/(?P<recipe_id>[0-9]+)/$', views.collect, name = 'collect'),
	url(r'^v1/favoritelist/$', views.favoritelist, name='favoritelist'),
	url(r'^v1/recommend/$', views.recommend, name='recommend'),
	url(r'^v1/columnsrecommend/$', views.columnsrecommend, name='columnsrecommend'),


	url(r'^tags$', views.tagsed, name = 'tags'),
	url(r'^recipe$',views.reciped, name = 'recipe'),
	url(r'^recommend/$', views.recommended, name='recommend'),
]
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
