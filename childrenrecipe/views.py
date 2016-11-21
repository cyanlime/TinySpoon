#!/usr/bin/env Python
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import datetime
import exceptions
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

        recipe_create_time = recipe.create_time
        recipe_id = recipe.id
        recipe_name = recipe.name
        recipe_user = recipe.user
        recipe_exihibitpic = recipe.exihibitpic.url
        recipe_introduce = recipe.introduce
        recipe_tips = recipe.tips
        recipe_pageviews = recipe.pageviews
        recipe_collect_quantity = recipe.collect_quantity
        recipe_tags = recipe.tags.filter(category__is_tag=3)

        epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)
        td = recipe_create_time - epoch
        timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)

        recipe_time_weight = timestamp_recipe_createtime+int(recipe_pageviews)*3600*24
        recipe.save()

        age_recipe = {'url': request.build_absolute_uri(reverse('recipes', kwargs={}))+str(recipe.id)+'/',
                'id': recipe_id ,'create_time': timestamp_recipe_createtime, 'name': recipe_name, 'user': recipe_user, 
                'exihibitpic': request.build_absolute_uri(recipe_exihibitpic), 'introduce': recipe_introduce,
                'tips': recipe_tips, 'pageviews': recipe_pageviews, 'collect_quantity': recipe_collect_quantity,
                'time_weight': recipe_time_weight, 'tags':[]}

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
        select_tags = request.data.get('tag_id', [])

        #pdb.set_trace()
        age_tags = []
        other_tags = []

        stage_tags = Tag.objects.filter(category__is_tag=1)
        if stage_tags and select_tags is not None:
                for select_tag in select_tags: 
                        for tag in stage_tags:
                                if select_tag==int(tag.id):
                                        age_tags.append(int(tag.id))

                for tag in select_tags:
                        if tag not in age_tags:
                                other_tags.append(tag)

        # if createtime:
        #         datetime_createtime = datetime.datetime.fromtimestamp(createtime)

        #pdb.set_trace()
        if Recipe.objects.exists():
                screen_recipes = Recipe.objects
                if search is not None:
                        screen_recipes = screen_recipes.filter(name__contains=search)
                if age_tags is not None and len(age_tags) > 0:
                        screen_recipes = screen_recipes.filter(tags__in=age_tags)
                if other_tags is not None and len(other_tags) > 0:
                        screen_recipes = screen_recipes.filter(tags__in=other_tags)
                # if createtime is not None:
                #         screen_recipes = screen_recipes.filter(create_time__lt=datetime_createtime)
                
                screen_recipes = screen_recipes.order_by('-time_weight')

                #pdb.set_trace()
                category_recipes_index = {}
                distinct_screen_recipes = []
                for raw_recipe in screen_recipes.all():
                        if raw_recipe not in distinct_screen_recipes:
                                distinct_screen_recipes.append(raw_recipe)
               
                #pdb.set_trace()    
                for recipe in distinct_screen_recipes:

                        stages = recipe.tags.filter(category__is_tag=1).all()
                     
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
    
                de_stage = []
                if age_tags is not None and len(age_tags)>0:
                        for stage_recipe in data:
                                stage_id = int(stage_recipe.get('tag_id'))
                                if stage_id in age_tags:
                                        de_stage.append(stage_recipe)
 
                        return Response(de_stage, status=status.HTTP_200_OK)           
                else:
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
                epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)

                for recipe in raw_recipes:
                        recipe_create_time = recipe.create_time
                        recipe_id = recipe.id
                        recipe_name = recipe.name
                        recipe_user = recipe.user
                        recipe_exihibitpic = recipe.exihibitpic.url
                        recipe_introduce = recipe.introduce
                        recipe_tips = recipe.tips
                        recipe_tags = recipe.tags.all()
                        recipe_materials = recipe.material_set.all()
                        recipe_procedures = recipe.procedure_set.all()                       
                        
                        #pdb.set_trace()
                        recipe_pageviews = recipe.pageviews
                        if recipe_id:
                                recipe_pageviews = recipe_pageviews+1
                                recipe.pageviews = recipe_pageviews
                                recipe.save()
                        recipe_collect_quantity = recipe.collect_quantity
                               
                        td = recipe_create_time - epoch
                        timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)

                        separate_recipe = {'url': request.build_absolute_uri(reverse("recipes", kwargs={}))+str(recipe.id)+'/',
                                'create_time': timestamp_recipe_createtime, 'id': recipe_id , 'name': recipe_name, 'user': recipe_user, 
                                'exihibitpic': request.build_absolute_uri(recipe_exihibitpic), 'introduce': recipe_introduce,
                                'tips': recipe_tips, 'tags':[], 'materials': [], 'procedures':[], 'width': recipe.exihibitpic.width, 
                                'height': recipe.exihibitpic.height, 'share_url': config.SHARE_URL % recipe.id, 'pageviews': recipe_pageviews,
                                'collect_quantity': recipe_collect_quantity}

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
                                timestamp_procedure_createtime = int(td1.seconds + td1.days * 24 * 3600)

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

@api_view(['POST'])
@permission_classes([AllowAny])
def pagination(request):
        # import pdb
        # pdb.set_trace()

        search = request.data.get('search', None)
        select_tags = request.data.get('tag_id', [])
        pagenum = request.data.get('page_number', None)
        #pagesize = request.data.get('page_size', None)

        age_tags = []
        other_tags = []

        #pdb.set_trace()
        stage_tags = Tag.objects.filter(category__is_tag=1)
        if stage_tags and select_tags is not None:
                for select_tag in select_tags:
                        for tag in stage_tags:
                                if select_tag==int(tag.id):
                                        age_id = tag.id
                                        tag_name = tag.name
                                        age_tags.append(int(tag.id))
                
                for tag in select_tags: 
                        if tag not in age_tags:
                                other_tags.append(tag)
        #pdb.set_trace()
        if len(age_tags)==1 and isinstance(pagenum, int):
                if Recipe.objects.exists():
                        screen_recipes = Recipe.objects
                        if search is not None:
                                screen_recipes = screen_recipes.filter(name__contains=search)
                        if age_tags is not None and len(age_tags) > 0:
                                screen_recipes = screen_recipes.filter(tags__in=age_tags)
                        if other_tags is not None and len(other_tags) > 0:
                                screen_recipes = screen_recipes.filter(tags__in=other_tags)

                        #pdb.set_trace()
                        # r338 = screen_recipes.filter(pk=338)[0]
                        # r438 = screen_recipes.filter(pk=438)[0]
                        # print 'r338\'s pageviews is %s and time_weight is %s' % (r338.pageviews, r338.time_weight)
                        # print 'r438\'s pageviews is %s and time_weight is %s' % (r438.pageviews, r438.time_weight)
                        
                        screen_recipes = screen_recipes.order_by('-time_weight')
                        
                        #pdb.set_trace()
                        distinct_screen_recipes = []
                        for raw_recipe in screen_recipes.all():
                                if raw_recipe not in distinct_screen_recipes:
                                        distinct_screen_recipes.append(raw_recipe)
                     
                        #pdb.set_trace()
                        if len(distinct_screen_recipes)>0:                                                   
                                result = [];
                                if pagenum>=1 and pagenum<=(len(distinct_screen_recipes)+10-1)/10:
                                        for recipe in distinct_screen_recipes[(pagenum-1)*10:(pagenum-1)*10+10]:
                                                result.append(serialize_recipe(recipe, request))
                                        
                                        stage_recipes = {'recipes': result, 'tag_id': age_id, 'age': tag_name}

                                        return Response(stage_recipes, status=status.HTTP_200_OK)
                                else:
                                        stage_recipes = {'error': 'Sorry, pageNumber value is out of range.'}
                                        return Response(stage_recipes, status=status.HTTP_200_OK)
                        else:
                                stage_recipes = {'error': 'Sorry, this stage of recipes do not exist.'}
                                return Response(stage_recipes, status=status.HTTP_200_OK)
                else:
                        stage_recipes = {'error': 'Sorry, recipe does not exist.'}
                        return Response(stage_recipes, status=status.HTTP_200_OK)      
        else:
                stage_recipes = {'errror': 'Sorry, please input an age tag_id or an integer page_number.'}
                return Response(stage_recipes, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def collect(request, recipe_id):
        #import pdb
        #pdb.set_trace()

        raw_recipes = Recipe.objects.filter(id = recipe_id)

        if len(raw_recipes)==1:
                for recipe in raw_recipes:
                        recipe_id = recipe.id
                        recipe_name = recipe.name
                        recipe_collect_quantity = recipe.collect_quantity                         
                        recipe_collect_quantity = recipe_collect_quantity+1
                        recipe.collect_quantity = recipe_collect_quantity
                        recipe.save()
        
                collection = {'collect success': 'true', 'recipe_url': request.build_absolute_uri(reverse('recipes', kwargs={}))+str(recipe.id)+'/',
                        'recipe_id': recipe_id, 'recipe_name': recipe_name, 'collect_quantity': recipe_collect_quantity}
                
                return Response(collection, status=status.HTTP_200_OK)
        
        else:
                collection = {'errror': 'Sorry, the recipe does not exist.'}
                return Response(collection, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def favoritelist(request):
        #import pdb
        #pdb.set_trace()

        collect_recipes = []
        sorted_collect_recipes = []
        recipes_id = request.data.get('recipe_id', [])

        if len(recipes_id)>0:          
                screen_recipes = Recipe.objects.filter(id__in=recipes_id)
                for recipe in screen_recipes:
                        recipe_create_time = recipe.create_time
                        recipe_id = recipe.id
                        recipe_name = recipe.name
                        recipe_user = recipe.user
                        recipe_exihibitpic = recipe.exihibitpic.url
                        recipe_introduce = recipe.introduce
                        recipe_tips = recipe.tips
                        recipe_pageviews = recipe.pageviews
                        recipe_collect_quantity = recipe.collect_quantity      
                        recipe_tags = recipe.tags.filter(category__is_tag=3)
                        
                        epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)
                        td = recipe_create_time - epoch
                        timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)
                
                        collect_recipe = {'url': request.build_absolute_uri(reverse('recipes', kwargs={}))+str(recipe.id)+'/',
                                'id': recipe_id ,'create_time': timestamp_recipe_createtime, 'name': recipe_name, 'user': recipe_user, 
                                'exihibitpic': request.build_absolute_uri(recipe_exihibitpic), 'introduce': recipe_introduce,
                                'tips': recipe_tips, 'pageviews': recipe_pageviews, 'collect_quantity': recipe_collect_quantity, 'tags':[]}
                                
                        for tag in recipe_tags:
                                therapeutic_tag = {'id': tag.id, 'name': tag.name, 'category_id': tag.category_id,
                                        'category_name': tag.category.name}
                                collect_recipe['tags'].append(therapeutic_tag)

                        collect_recipes.append(collect_recipe)

                #pdb.set_trace()
                for id in recipes_id:
                        for collect_recipe in collect_recipes:
                                if int(collect_recipe.get('id')) == id:
                                        if collect_recipe not in sorted_collect_recipes:
                                                sorted_collect_recipes.append(collect_recipe)

                return Response(sorted_collect_recipes, status=status.HTTP_200_OK)
                       
        else:
                return Response(sorted_collect_recipes, status=status.HTTP_200_OK)

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
		timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)
                timestamp_createtime = int(td1.seconds + td1.days * 24 * 3600)
                timestamp_pubdate = int(td2.seconds + td2.days * 24 * 3600)
                
                recommend = {'recommend_recipe': 'Today\'s Specials', 'create_time': timestamp_createtime,
                        'pubdate': timestamp_pubdate, 'image': request.build_absolute_uri(recommend_image), 
                        'name': recommend_name, 'introduce': recommend_introduce, 'recipe': {}}
                
                recommend['recipe'] = {
                        'id': recommend_recipe_id,
                        'create_time': timestamp_recipe_createtime,
                        'name': recommend_recipe_name,
                        'user': recommend_recipe_user,
                        'introduce': recommend_recipe_introduce,
                        'url': request.build_absolute_uri(reverse('recipes', kwargs={}))+str(recommend_recipe_id)+'/'
                }
                return Response(recommend, status=status.HTTP_200_OK)
        
        else:
                recommend = {}
                return Response(recommend, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllowAny])
def columnsrecommend(request):
        #import pdb
        #pdb.set_trace()

        now = datetime.datetime.now()
        epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)

        columnsrecommend = []
        #cards = Card.objects.filter(pubdate__lte=now)
        cards = Card.objects.all()
        for card in cards:
                card_id = card.id
                card_create_time = card.create_time
                card_exihibitpic = card.exihibitpic.url
                card_headline = card.headline
                card_subhead = card.subhead
                card_pagetype = card.pagetype
                card_reference_id = card.reference_id
                card_seq = card.seq

                td1 = card_create_time - epoch
                timestamp_card_createtime = int(td1.seconds + td1.days * 24 * 3600)
       
                #pdb.set_trace()
                if (card_pagetype==1):
                        largeviewsmodes = LargeViewsMode.objects.filter(id = card_reference_id)
        
                        if len(largeviewsmodes)==1:
                                recipes = []
                                for largeviewsmode in largeviewsmodes:
                                        largeviewsmode_id = largeviewsmode.id
                                        largeviewsmode_create_time = largeviewsmode.create_time
                                        largeviewsmode_name = largeviewsmode.name
                                        largeviewsmode_guide_language = largeviewsmode.guide_language  
                                        largeviewsmode_largeviewsmoderecipe_set = largeviewsmode.largeviewsmoderecipe_set.all()

                                        for recommend_recipe in largeviewsmode_largeviewsmoderecipe_set:
                                                recommend_recipe_id = recommend_recipe.recipe_id
                                                recommend_recipe_seq = recommend_recipe.seq
                                                recommend_recipe_create_time = recommend_recipe.recipe.create_time
                                                recommend_recipe_name = recommend_recipe.recipe.name
                                                recommend_recipe_exihibitpic = recommend_recipe.recipe.exihibitpic.url
                                                recommend_recipe_introduce = recommend_recipe.recipe.introduce
                                                
                                                td = recommend_recipe_create_time - epoch
                                                timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)
                                        
                                                recipe = {'url': request.build_absolute_uri(reverse("recipes", kwargs={}))+str(recommend_recipe_id)+'/',
                                                        'id': recommend_recipe_id, 'create_time': timestamp_recipe_createtime, 'seq': recommend_recipe_seq, 
                                                        'exihibitpic': request.build_absolute_uri(recommend_recipe_exihibitpic),
                                                        'name': recommend_recipe_name, 'introduce': recommend_recipe_introduce}
                                                
                                                recipes.append(recipe)
                                                recipes.sort(key=lambda recipe: recipe.get('seq'))

                                weekly_recommend = {'id': card_id, 'create_time': timestamp_card_createtime, 'seq': card_seq,
                                        'exihibitpic': request.build_absolute_uri(card_exihibitpic), 
                                        'headline': card_headline, 'subhead': card_subhead, 'pagetype': card_pagetype,
                                        'reference_id': card_reference_id, 'guide_language': largeviewsmode_guide_language,
                                        'recommend_recipes': 'Weekly Recipes Recommendation', 
                                        'recipes': {'id': largeviewsmode_id, 'name': largeviewsmode_name, 'recipes_list': recipes}}

                                columnsrecommend.append(weekly_recommend)
                        
                        #pdb.set_trace()
                        if (card_reference_id==0):

                                hotrecipes = []
                                now = datetime.datetime.now()
                                epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)

                                if Recipe.objects.exists(): 
                                        if len(Recipe.objects.all())>=20:
                                                recipes = Recipe.objects.order_by('-pageviews')[:20]
                                        else:
                                                recipes = Recipe.objects.order_by('-pageviews')

                                        for recipe in recipes:
                                                recommend_recipe_id = recipe.id
                                                recommend_recipe_create_time = recipe.create_time
                                                recommend_recipe_name = recipe.name
                                                recommend_recipe_exihibitpic = recipe.exihibitpic.url
                                                recommend_recipe_introduce = recipe.introduce
                                                recommend_recipe_pageviews = recipe.pageviews
                                        
                                                td = recommend_recipe_create_time - epoch    
                                                timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)
                                        
                                                separate_recipe = {'url': request.build_absolute_uri(reverse("recipes", kwargs={}))+str(recommend_recipe_id)+'/',
                                                        'id': recommend_recipe_id, 'create_time': timestamp_recipe_createtime, 'name': recommend_recipe_name,
                                                        'exihibitpic': request.build_absolute_uri(recommend_recipe_exihibitpic), 
                                                        'introduce': recommend_recipe_introduce, 'pageviews': recommend_recipe_pageviews}
                                                
                                                hotrecipes.append(separate_recipe)

                                        hot_recipes = {'id': card_id, 'create_time': timestamp_card_createtime, 'seq': card_seq,
                                                'exihibitpic': request.build_absolute_uri(card_exihibitpic), 
                                                'headline': card_headline, 'subhead': card_subhead, 'pagetype': card_pagetype,
                                                'reference_id': card_reference_id, 'recommend_recipes': 'Recent Popular Recipes', 
                                                'recipes': {'id': card_reference_id, 'name': 'hot recipes', 'recipes_list': hotrecipes}}

                                        columnsrecommend.append(hot_recipes)
               
                #pdb.set_trace()
                if (card_pagetype==2):

                        foodknowledges_addition = []
                        detailslistmodes = DetailsListMode.objects.filter(id = card_reference_id)

                        if len(detailslistmodes)==1:
                                for detailslistmode in detailslistmodes:
                                        detailslistmode_id = detailslistmode.id
                                        detailslistmode_name = detailslistmode.name
                                        detailslistmode_create_time = detailslistmode.create_time
                                        detailslistmode_detailslistmodewebpage_set = detailslistmode.detailslistmodewebpage_set.all()

                                        for foodknowledge in detailslistmode_detailslistmodewebpage_set:
                                                foodknowledge_id = foodknowledge.webpage_id
                                                foodknowledge_seq = foodknowledge.seq
                                                foodknowledge_create_time = foodknowledge.webpage.create_time
                                                foodknowledge_title = foodknowledge.webpage.title
                                                foodknowledge_subtitle = foodknowledge.webpage.subtitle
                                                foodknowledge_exihibitpic = foodknowledge.webpage.exihibitpic.url
                                                foodknowledge_url = foodknowledge.webpage.url
                                            
                                                td = foodknowledge_create_time - epoch
                                                timestamp_foodknowledge_createtime = int(td.seconds + td.days * 24 * 3600)

                                                separate_foodknowledge = {'id': foodknowledge_id, 'create_time': timestamp_foodknowledge_createtime,
                                                        'title': foodknowledge_title, 'subtitle': foodknowledge_subtitle, 'url': foodknowledge_url,
                                                        'exihibitpic': request.build_absolute_uri(foodknowledge_exihibitpic), 'seq': foodknowledge_seq}

                                                foodknowledges_addition.append(separate_foodknowledge)  
                                                foodknowledges_addition.sort(key=lambda separate_foodknowledge: separate_foodknowledge.get('seq'))

                                food_addition_knowledge = {'id': card_id, 'create_time': timestamp_card_createtime, 'seq': card_seq,
                                        'exihibitpic': request.build_absolute_uri(card_exihibitpic), 'headline': card_headline, 'subhead': card_subhead,
                                        'pagetype': card_pagetype, 'reference_id': card_reference_id, 
                                        'recommend_addition_knowledge':'Supplementary Food Addition Knowledge', 
                                        'food_knowledges': {'id': detailslistmode_id, 'name': detailslistmode_name, 'knowledges_list': foodknowledges_addition}}
        
                                columnsrecommend.append(food_addition_knowledge)  

        #pdb.set_trace()  
        for column in columnsrecommend:
                columnsrecommend.sort(key=lambda column: column.get('seq'))
        return Response(columnsrecommend, status=status.HTTP_200_OK)

   

@api_view(['GET'])
@permission_classes([AllowAny])
def tagsed(request):
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

@api_view(['GET'])
@permission_classes([AllowAny])
def recommended(request):
  
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
		timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)
                timestamp_createtime = int(td1.seconds + td1.days * 24 * 3600)
                timestamp_pubdate = int(td2.seconds + td2.days * 24 * 3600)
                
                recommend = {'recommend_recipe': 'Today\'s Specials', 'create_time': timestamp_createtime,
                        'pubdate': timestamp_pubdate, 'image': request.build_absolute_uri(recommend_image), 
                        'name': recommend_name, 'introduce': recommend_introduce, 'recipe': {}}
                
                recommend['recipe'] = {
                        'id': recommend_recipe_id,
                        'create_time': timestamp_recipe_createtime,
                        'name': recommend_recipe_name,
                        'user': recommend_recipe_user,
                        'introduce': recommend_recipe_introduce,
                        'url': "http://"+request.META['HTTP_HOST']+'/'+'api'+'/'+'recipes'+'/'+str(recommend_recipe_id)
                }
                return Response(recommend, status=status.HTTP_200_OK)
        
        else:
                recommend = {}
                return Response(recommend, status=status.HTTP_200_OK)


class RecipeResponseItem:
    def __init__(self, recipe, host, create_time,
                 tags):
        self.recipe = recipe
        self.host = host
        self.create_time = create_time
        self.tags = tags

    def to_data(self):
        recipe = self.recipe
        _id = recipe.id
        recipe_name = recipe.name
        user = recipe.user
        tips = recipe.tips
        introduce = recipe.introduce
        host = self.host
        url = 'http://%s/api/recipes/%d' % (host, _id)
        exihibitpic_url = recipe.exihibitpic
        exihibitpic = 'http://%s/images/%s' % (host, exihibitpic_url)
        exihibitpic = exihibitpic.decode('utf-8')
        data = {
            'id': _id,
            'url': url,
            'create_time': self.create_time,
            'recipe': recipe_name,
            'user': user,
            'tips': tips,
            'exihibitpic': exihibitpic,
            'introduce': introduce,
            'tag': self.tags
        }
        return data


class AgeTagManage:
    '''
    管理年龄tag
    '''
    def __init__(self):
        tag_query = Tag.objects.filter(category__is_tag=1)
        tags = tag_query.values_list('id', flat=True).all()
        self.tag_age_ids = set(tags)

    def check_age_query(self, tags):
        check_id = set(tags) & self.tag_age_ids
        return check_id

    def rest_age_tags(self, tag):
        return self.tag_age_ids - tag


class AgeQuery:
    def __init__(self, query, age_tag_id):
        self.query = query
        self.age_tag_id = age_tag_id


class RecipeDuplicationManager:
    '''
    删选结果
    '''
    def __init__(self):
        self.recipes = set()

    def add(self, recipe):
        self.recipes.add(recipe.id)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reciped(request):
   
    data = []
    search = request.data.get('search', None)
    create_time = request.data.get('create_time', None)
    tags_ = request.data.get('tag_id', [])
    host = request.META['HTTP_HOST']

    age_tag_manager = AgeTagManage()
    age_tag_id = age_tag_manager.check_age_query(tags_)

    rest_query_tags = tags_

    filter_dump_recipe = bool(tags_) 

    if age_tag_id:
        query = Recipe.objects
        assert len(age_tag_id) == 1 #only one age id
        age_tag_id_ls = list(age_tag_id)
        age_id = age_tag_id_ls[0]
        query = query.filter(tags=age_tag_id_ls[0]) #age filter
        rest_query_tags = set(tags_) - age_tag_id
        querys = [AgeQuery(query, age_id)]
    else:
        querys = []
        for _age_tag_id in age_tag_manager.tag_age_ids: #quanbu age 
            query = Recipe.objects
            query = query.filter(tags=_age_tag_id)
            querys.append(AgeQuery(query, _age_tag_id))

    # cache
    q = Q()
    for tag_id in rest_query_tags:
        q = q | Q(tags=tag_id)
    s = None
    if create_time:
        createtime = time.localtime(int(create_time))
        s = time.strftime('%Y-%m-%d %H:%M:%S', createtime)

    recipe_duplication_manager = RecipeDuplicationManager()

    for age_query in querys:
        query = age_query.query
        age_tag_id = age_query.age_tag_id
        query = query.filter(q)  # tag and query
        if search:
            query = query.filter(name__contains=search)
        if s:
            query = query.filter(create_time__lt=s)
        filter_recipes = list(recipe_duplication_manager.recipes)
        if filter_dump_recipe and filter_recipes:
            query = query.exclude(id__in=filter_recipes)

        recipes = query.order_by('-create_time').distinct()[:10]

        query_tag = Tag.objects.filter(id=age_tag_id)
        tag_first = query_tag[0]
        tag_name = tag_first.name
        tag_id = tag_first.id
        tag_seq = tag_first.seq

        tag = {'tag': tag_name, 'tag_id': tag_id, 'tag_seq': tag_seq, 'recipes': []}
        _recipes = []
        for recipe in recipes:
            recipe_duplication_manager.add(recipe)
            recipe_create_time = recipe.create_time

            td = recipe_create_time - EPOCH
            timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600))

            _tags = [{"category_name": x.category.name, 'name': x.name}
                        for x in recipe.tags.filter(category__is_tag=3)]
            recipe_item = RecipeResponseItem(recipe=recipe,
                                             host=host,
                                             create_time=timestamp_recipe_createtime,
                                             tags=_tags)
            _recipes.append(recipe_item.to_data())
        if _recipes:
            tag['recipes'] = _recipes
            data.append(tag)
    data.sort(key=lambda x: x['tag_seq'])
    return Response(data, status=status.HTTP_200_OK)
