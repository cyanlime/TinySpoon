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

class LargeViewsModeRecipeInline(admin.TabularInline):
	model = LargeViewsModeRecipe
	raw_id_fields = ('recipe',)

class LargeViewsModeAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	inlines = [
		LargeViewsModeRecipeInline,
	]

class DetailsListModeWebPageInline(admin.TabularInline):
	model = DetailsListModeWebPage
	raw_id_fields = ('webpage',)

class DetailsListModeAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	inlines = [
		DetailsListModeWebPageInline,
	]

class WebPageAdmin(admin.ModelAdmin):
	list_display = ('id', 'title',)
	search_fields = ['title']

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