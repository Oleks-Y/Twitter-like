import random

from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Tweet
from .forms import TweetForm
from .serializers import TweetSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS
# Create your views here.
def home_view(request, *args, **kwargs):
    print(request.user or None)
    return render(request, "pages/home.html", context={}, status=200)

@api_view(["POST"])
def tweet_create_view(request, *args, **kwargs):
   
    serializer = TweetSerializer(data=request.POST or None)
    if (serializer.is_valid(raise_exception=True)):
        serializer.save(user = request.user)
        return Response(serializer.data, status=201)       
    return Response({}, status=400) 
@api_view(["GET"])
def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs, many = True)  
    return Response(serializer.data)

def tweet_create_view_pure_django(request, *args, **kwargs):
    
    '''
    REST  API Crud
    '''
    user = request.user
    if not request.user.is_authenticated:
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next") or None
    print("next_url: ", next)
    if form.is_valid(): 
        obj = form.save(commit=False)
        # do other form related logic 
        obj.user = user # Annon User
        obj.save()
        if request.is_ajax():
            return JsonResponse({}, status=201)
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=400)
    return render(request, 'components/forms.html', context={"form": form})


def tweet_list_view_pure_django(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweets_list = [x.serialize() for x in qs]
    data= {
        'response': tweets_list,

    }
    return JsonResponse(data)

def tweet_detail_view(request, tweet_id, *args,**kwargs):
    """
    REST  API VIEW
    Consume by JavaScript 
    return json data
    """
    data={
        "id" : tweet_id,
     }
    status = 200
    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
    except :
        data["message"] = "Not found"
        status=404   
    return  JsonResponse(data) # json dumps content_type = 'applicayion/json' 