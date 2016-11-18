from django.contrib import admin
from .models import *

# Register your models here.

class MaterialInline(admin.TabularInline):
	model = Material
	extra = 1

class ProcedureInline(admin.TabularInline):
	model = Procedure
	extra = 1

class RecipeAdmin(admin.ModelAdmin):
	filter_horizontal = ('tags',)
	inlines = [
		MaterialInline,
		ProcedureInline,
	]
	list_display = ('id', 'name')
	exclude = ('pageviews', 'collect_quantity', 'time_weight', 'create_time',)
	search_fields = ['name']

class MaterialAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	search_fields = ['name']

class ProcedureAdmin(admin.ModelAdmin):
	search_fields = ['name']

class RecommendAdmin(admin.ModelAdmin):
	raw_id_fields = ('recipe',)

class CardAdmin(admin.ModelAdmin):
	list_display = ('id', 'headline', 'seq', 'pagetype', 'reference_id')

class LargeViewsModeAdmin(admin.ModelAdmin):
	filter_horizontal = ('recipes',)
	list_display = ('id', 'name')

class DetailsListModeAdmin(admin.ModelAdmin):
	filter_horizontal = ('webpages',)
	list_display = ('id', 'name')

class WebPageAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'seq')


#admin.site.register(Student)
#admin.site.register(Classes)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Recommend, RecommendAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(LargeViewsMode, LargeViewsModeAdmin)
admin.site.register(DetailsListMode, DetailsListModeAdmin)
admin.site.register(WebPage, WebPageAdmin)