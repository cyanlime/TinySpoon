#!/usr/bin/env Python
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import datetime
from django.utils.timezone import UTC
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from childrenrecipe.serializers import *
from .models import *
from . import config
import time
from .serializers import *
from django.db.models import Q
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import(
	AllowAny,
	IsAuthenticated
)
from rest_framework.decorators import(
	api_view,
	permission_classes,
	parser_classes,
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.core.handlers.wsgi import WSGIRequest
#from .exceptions import *
from .datatime import EPOCH

# Create your views here.

class JSONResponse(HttpResponse):
        """
        An HttpResponse that renders its content into JSON.
        """
	def __init__(self, data, **kwargs):
        	content = JSONRenderer().render(data)
        	kwargs['content_type'] = 'application/json'
        	super(JSONResponse, self).__init__(content, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
        queryset = Group.objects.all()
        serializer_class = GroupSerializer

class APIRootView(APIView):
    def get(self, request):
#        year = now().year
	year = datetime.now().year
        data = {
            'year-summary-url': reverse('year-summary', args=[year], request=request)
        }
        return Response(data)

class RecipeViewSet(viewsets.ModelViewSet):
	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer
	ordering =('-create_time')

class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer

class MaterialViewSet(viewsets.ModelViewSet):
	queryset = Material.objects.all()
	serializer_class = MaterialSerializer

class ProcedureViewSet(viewsets.ModelViewSet):
	queryset = Procedure.objects.all()
	serializer_class = ProcedureSerializer
	
class TagViewSet(viewsets.ModelViewSet):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def tags(request):
	data = []
	categorys = {}
	tags = Tag.objects.exclude(category__is_tag=1)
	if tags:
                for tag in tags:
                        tag_id = tag.id
                        tag_name = tag.name
                        category_name = tag.category.name
                        category_seq = tag.category.seq
                        categroy = None
                        if category_name in categorys:
                                category = categorys[category_name]
                        else:
                                category = {'seq': category_seq, 'category': category_name, 'tags': []}
                                categorys[category_name] = category
                                data.append(category)
                        category['tags'].append({
                                'id': tag_id,
                                'tag': tag_name,                                                            
                        })

                if len(data)>1:
                        for item in range(0, len(data)-1):
                                #category_seq = data[item].get('seq')
                                min = item
                                for item2 in range(item+1, len(data)):
                                        if data[item2].get('seq') < data[min].get('seq'):
                                                min = item2
                                tmp = data[item]
                                data[item] = data[min]
                                data[min] = tmp
                        return Response(data, status=status.HTTP_200_OK)
                else:
                        return Response(data, status=status.HTTP_200_OK)                       
        else:
                return Response(data, status=status.HTTP_200_OK) 

def serialize_recipe(recipe, request):

        now = datetime.datetime.now()
        epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)

        recipe_create_time = recipe.create_time
        recipe_id = recipe.id
        recipe_name = recipe.name
        recipe_user = recipe.user
        recipe_exihibitpic = recipe.exihibitpic.url
        recipe_introduce = recipe.introduce
        recipe_tips = recipe.tips
        
        #import pdb
        #pdb.set_trace()
        recipe_tags = recipe.tag.filter(category__is_tag=3)
        
        td = recipe_create_time - epoch
        timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)
  
        age_recipe = {'url': request.build_absolute_uri(reverse("recipes", kwargs={}))+str(recipe.id)+'/',
                'id': recipe_id ,'create_time': timestamp_recipe_createtime, 'name': recipe_name, 'user': recipe_user, 
                'exihibitpic': request.build_absolute_uri(recipe_exihibitpic), 'introduce': recipe_introduce,
                'tips': recipe_tips, 'tags':[]}
                
        for tag in recipe_tags:
                therapeutic_tag = {'id': tag.id, 'name': tag.name, 'category_id': tag.category_id,
                        'category_name': tag.category.name}
                age_recipe['tags'].append(therapeutic_tag)

        return age_recipe
        

@api_view(['POST'])
@permission_classes([AllowAny])
def recipes(request):
        #import pdb
        #pdb.set_trace()

        data = []
        
        search = request.data.get('search', None)
        createtime = request.data.get('create_time', None)
        select_tags = request.data.get('tag_id', None)

        pdb.set_trace()
        age_tags = []
        other_tags = []

        stage_tags = Tag.objects.filter(category__is_tag=1)
        for select_tag in select_tags: 
                if stage_tags:
                        for tag in stage_tags:
                                if select_tag==int(tag.id):
                                        age_tags.append(int(tag.id))
     
        #pdb.set_trace()
        
        for tag in select_tags: 
                if tag not in age_tags:
                        other_tags.append(tag)

        if createtime:
                datetime_createtime = datetime.datetime.fromtimestamp(createtime)

        if Recipe.objects.exists():
                if search is None:
                        if select_tags is not None and len(select_tags)>0:
                                if createtime is not None:
                                        screen_recipes = Recipe.objects.filter(tag__in=select_tags).filter(create_time__lt=datetime_createtime).order_by('-create_time')
                                else:
                                        screen_recipes = Recipe.objects.filter(tag__in=select_tags).order_by('-create_time')         
                        else:
                                if createtime is not None:
                                        screen_recipes = Recipe.objects.filter(create_time__lt=datetime_createtime).order_by('-create_time') 
                                else:
                                        screen_recipes = Recipe.objects.order_by('-create_time') 
                else:   
                        if createtime is not None:    
                                screen_recipes = Recipe.objects.filter(name__contains=search).filter(create_time__lt=datetime_createtime).order_by('-create_time') 
                        else:
                                screen_recipes = Recipe.objects.filter(name__contains=search).order_by('-create_time') 
                
                #pdb.set_trace()
                category_recipes_index = {}
                distinct_screen_recipes = []
                for raw_recipe in screen_recipes.all():
                        if raw_recipe not in distinct_screen_recipes:
                                distinct_screen_recipes.append(raw_recipe)
                        
                for recipe in distinct_screen_recipes:
                        stages = recipe.tag.filter(category__is_tag=1).all()
                        if stages is None or stages.count()==0:
                                continue
                        for stage in stages:
                                recipes_with_stage = category_recipes_index.get(stage.name, None)                       
                                if (recipes_with_stage is None):
                                        recipes_with_stage = []
                                        category_recipes = {'recipes': recipes_with_stage, 'age': stage.name, 'tag_id': stage.id, 'tag_seq': stage.seq}
                                        category_recipes_index[stage.name] = recipes_with_stage
                                        data.append(category_recipes)
                                        
                                if len(recipes_with_stage)<10:
                                        recipes_with_stage.append(serialize_recipe(recipe, request))
                                else:
                                        recipes_with_stage = recipes_with_stage[:9]
                                        recipes_with_stage.append(serialize_recipe(recipe, request))
                                
                data.sort(key=lambda category_recipes: category_recipes.get('tag_seq'))
                return Response(data, status=status.HTTP_200_OK)  
        
        else:        
                return Response(data, status=status.HTTP_200_OK)
        
@api_view(['GET'])
@permission_classes([AllowAny])
def recipe(request, recipe_id):

        #import pdb
        #pdb.set_trace()
       
        raw_recipes = Recipe.objects.filter(id = recipe_id)
        #raw_recipes = get_list_or_404(Recipe, pk=recipe_id)
        if len(raw_recipes)==1:
                now = datetime.datetime.now()
                epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)

                for recipe in raw_recipes:
                        recipe_create_time = recipe.create_time
                        recipe_id = recipe.id
                        recipe_name = recipe.name
                        recipe_user = recipe.user
                        recipe_exihibitpic = recipe.exihibitpic.url
                        recipe_introduce = recipe.introduce
                        recipe_tips = recipe.tips
                        recipe_tags = recipe.tag.all()
                        recipe_materials = recipe.material_set.all()
                        recipe_procedures = recipe.procedure_set.all() 

                        td = recipe_create_time - epoch
                        timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)

                        separate_recipe = {'url': request.build_absolute_uri(reverse("recipes", kwargs={}))+str(recipe.id)+'/',
                                'create_time': timestamp_recipe_createtime, 'id': recipe_id , 'name': recipe_name, 'user': recipe_user, 
                                'exihibitpic': request.build_absolute_uri(recipe_exihibitpic), 'introduce': recipe_introduce,
                                'tips': recipe_tips, 'tags':[], 'materials': [], 'procedures':[], 'width': recipe.exihibitpic.width, 
                                'height': recipe.exihibitpic.height, 'share_url': config.SHARE_URL % recipe.id}

                        #pdb.set_trace()
                        for tag in recipe_tags:
                                recipe_tag = {'id': tag.id, 'name': tag.name, 'category_id': tag.category_id, 'category_name': tag.category.name}
                                separate_recipe['tags'].append(recipe_tag)

                        #pdb.set_trace()
                        for material in recipe_materials:
                                recipe_material = {'recipe_name': material.recipe.name, 'id': material.id, 'name': material.name,
                                        'portion': material.portion}

                                separate_recipe['materials'].append(recipe_material)

                        #pdb.set_trace()
                        for procedure in recipe_procedures:

                                td1 = procedure.create_time - epoch
                                timestamp_procedure_createtime = int(td1.microseconds + (td1.seconds + td1.days * 24 * 3600) * 10**6)

                                procedure_image = procedure.image
                                
                                if hasattr(procedure_image, 'url'):
                                        procedure_image = request.build_absolute_uri(procedure_image.url)
                                        procedure_image_width = procedure.image.width
                                        procedure_image_height = procedure.image.height
                                else:
                                        procedure_image = None
                                        procedure_image_width = 0
                                        procedure_image_height = 0

                                recipe_procedure = {'recipe_name': procedure.recipe.name, 'create_time': timestamp_procedure_createtime, 
                                        'id': procedure.id, 'seq': procedure.seq, 'describe': procedure.describe, 'image': procedure_image, 
                                        'width': procedure_image_width, 'height': procedure_image_height}

                                separate_recipe['procedures'].append(recipe_procedure)

                return Response(separate_recipe, status=status.HTTP_200_OK)

        else:
                separate_recipe = {}
                return Response(separate_recipe, status=status.HTTP_200_OK)


        # raw_data = Recipe.objects
        # if search <> None and len(search) > 0:
        #         raw_data = raw_data.filter(name__contains=search)
        # if select_tag <> None and len(select_tag) > 0:
        #         raw_data = raw_data.filter(tag__in=select_tag)
        # # TODO order by create_time
        # desktop = {}
        # for recipe in raw_data.all():
        #         stages = recipe.tag.filter(category__is_tag=1).all()
        #         if stages is None or stages.count() == 0:
        #                 continue
        #         for stage in stages:
        #                 recipes_with_stage = desktop.get(stage.name, None)
        #                 if(recipes_with_stage is None):
        #                         recipes_with_stage = []
        #                         desktop[stage.name] = recipes_with_stage
        #                 # TODO limit max 5
        #                 recipes_with_stage.append(serialize_recipe(recipe))
        # # TODO order desktop by stage
        # return Response(desktop, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def recommend(request):
  
        now = datetime.datetime.now()
        epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)

	if Recommend.objects.filter(pubdate__lte=now): 
                recommend = Recommend.objects.filter(pubdate__lte=now).order_by('-pubdate').first()
                
                if recommend.name:
                        recommend_name = recommend.name
                else:
                        recommend_name = recommend.recipe.name

                if recommend.introduce:
                        recommend_introduce = recommend.introduce
                else:
                        recommend_introduce = recommend.recipe.introduce

                recommend_image = recommend.image.url
                recommend_pubdate = recommend.pubdate
                recommend_create_time = recommend.create_time
                recommend_recipe_id = recommend.recipe.id
                recommend_recipe_create_time = recommend.recipe.create_time
                recommend_recipe_name = recommend.recipe.name
                recommend_recipe_user = recommend.recipe.user
                recommend_recipe_introduce = recommend.recipe.introduce

		td = recommend_recipe_create_time - epoch
                td1 = recommend_create_time - epoch
                td2 = recommend_pubdate - epoch
		timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)
                timestamp_createtime = int(td1.microseconds + (td1.seconds + td1.days * 24 * 3600) * 10**6)
                timestamp_pubdate = int(td2.microseconds + (td2.seconds + td2.days * 24 * 3600) * 10**6)
                
                recommend = {'recommend_recipe': 'Today\'s Specials', 'create_time': timestamp_createtime,
                        'pubdate': timestamp_pubdate, 'image': request.build_absolute_uri(recommend_image), 
                        'name': recommend_name, 'introduce': recommend_introduce, 'recipe': {}}
                
                recommend['recipe'] = {
                        'id': recommend_recipe_id,
                        'create_time': timestamp_recipe_createtime,
                        'name': recommend_recipe_name,
                        'user': recommend_recipe_user,
                        'introduce': recommend_recipe_introduce,
                        'url': request.build_absolute_uri(reverse("recipes", kwargs={}))+str(recommend_recipe_id)+'/'
                }
                return Response(recommend, status=status.HTTP_200_OK)
        
        else:
                recommend = {}
                return Response(recommend, status=status.HTTP_200_OK)
