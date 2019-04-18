from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .forms import ImageCreateForm
from .models import Image
from common.decorators import ajax_required
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)

@login_required
def image_create(request):
    if request.method == 'POST':
        #form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Image added successfully')

            #redirect to new created item detail view
            return redirect(new_item.get_absolute_url())
        else:
            messages.error(request, 'Error saving the image')
    else:
        print(request.GET)
        form = ImageCreateForm(data=request.GET)

    return render(
        request,
        'images/image/create.html',
        {
            'section': 'images',
            'form': form,
        }
    )

@login_required
def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(
        request,
        'images/image/detail.html',
        {'section': 'images',
        'image': image}
    )

@ajax_required
@login_required
# Returns HttpResponseNotAllowed if something excep POST request is passed
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                # Won't duplicate if this user already liked
                image.users_like.add(request.user)
            else:
                # Does nothing if the user doesn't exist
                # If you want to remove all objects from many-to-many
                # relationship you can user clear() method
                image.users_like.remove(request.user)
            # Returns a HTTP response with application/json content type
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ko'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        #If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            #If the request is AJAX and the page is out of range
            #return an empyt page
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    
    if request.is_ajax():
        return render(
            request,
            'images/image/list_ajax.html',
            {'section': 'images', 'images': images},
        )
    
    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images},
    )