#!/usr/bin/env Python
# coding=utf-8
from __future__ import unicode_literals
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
import datatime

from django.db import models
# Create your models here.

class Recipe(models.Model):
	create_time = models.DateTimeField(auto_now_add=True)
	name = models.CharField(max_length=200)
	user = models.CharField(max_length=40, blank=True)
	exihibitpic = models.ImageField(upload_to='exhibited_picture/%Y/%m/%d', blank=False)
	introduce = models.TextField(blank=False)
	tips = models.TextField(blank=True)
	tags = models.ManyToManyField('Tag')
	pageviews = models.IntegerField()
	collect_quantity = models.IntegerField()
	time_weight = models.IntegerField()
	def __unicode__(self):
		return self.name

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		import datetime
		epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)
		instance_create_time = instance.create_time
		td = instance_create_time - epoch
		timestamp_recipe_createtime = int(td.seconds + td.days * 24 * 3600)
		instance.time_weight = timestamp_recipe_createtime+int(instance.pageviews)*3600*24
pre_save.connect(Recipe.pre_save, Recipe, dispatch_uid="TinySpoon.childrenrecipe.models.Recipe")

class Material(models.Model):
	recipe = models.ForeignKey('Recipe')
	name = models.CharField(max_length=200)
	portion = models.CharField(max_length=20)
	def __unicode__(self):
		return '%s %s' % (self.recipe.name, self.name)

class Procedure(models.Model):
	recipe = models.ForeignKey('Recipe')
	seq = models.IntegerField()
	describe = models.TextField(blank=False)
	image = models.ImageField(upload_to='exhibited_picture/%Y/%m/%d', blank=True)
	create_time = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.recipe.name

class Tag(models.Model):
	name = models.CharField(max_length=100)
	category = models.ForeignKey('Category')
	seq = models.IntegerField()
	def __unicode__(self):
		return self.name

class Category(models.Model):
	name = models.CharField(max_length=100)
	is_tag =models.IntegerField(blank=False)
	seq = models.IntegerField()
	def __unicode__(self):
		return self.name

class Recommend(models.Model):
	create_time = models.DateTimeField(auto_now=True)
	recipe = models.ForeignKey('Recipe')
	name = models.CharField(max_length=200, blank=True)
	introduce = models.TextField(blank=True)
	image = models.ImageField(upload_to='exhibited_picture/%Y/%m/%d', blank=False)
	pubdate = models.DateTimeField()
	def __unicode__(self):
		return self.recipe.name
