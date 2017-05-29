from urllib import quote_plus
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
from .forms import PostForm
from .models import Post

def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	
	#if not request.user.is_authenticated():
	#	raise Htto404
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()

		# message success
		messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
		"form": form,
	}
	return render(request, "post_form.html", context)


def post_detail(request, slug=None):
	instance = get_object_or_404(Post, slug=slug)
	if instance.draft or instance.publish > timezone.now():
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	share_string = quote_plus(instance.context)
	#print share_string
	context = {
		"title": instance.title,
		"instance": instance,
		"share_string" : share_string
	}
	return render(request, "post_detail.html", context)

def post_list(request):
	queryset_list = Post.objects.active()
	if request.user.is_staff or request.user.is_superuser:
		query_list= Post.objects.all()

	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
		Q(title__icontains=query)|
		Q(context__icontains=query)|
		Q(user__first_name__icontains=query)|
		Q(user__last_name__icontains=query)
		).distinct()

	paginator = Paginator(queryset_list, 3) # Show 25 contacts per page
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		queryset = paginator.page(1)
	except EmptyPage:
	    queryset = paginator.page(paginator.num_pages)

	context = { "title" : "list", 
				"object_list" : queryset,
				"page_request_var": page_request_var}
	return render(request,'post_list.html',context)

def post_update(request, slug=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"title": instance.title,
		"instance": instance,
		"form":form,
	}
	return render(request, "post_form.html", context)

def post_delete(request, slug=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("posts:list")
