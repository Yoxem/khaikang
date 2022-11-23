import json
from django.http import HttpResponse
from django.template import loader
from .models import User, Post, Following
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Q
import string
import random
from django import forms
from django.utils.safestring import mark_safe
from string import Template
from django.forms import ImageField
import os

def api_get_previous_posts(request):
    if request.method == 'POST':
        post_body_orig = request.body.decode('utf-8')
        post_body_json = json.loads(post_body_orig)
        oldest_time = post_body_json["oldest_time"]
        oldest_datetime_object = datetime.strptime(oldest_time, '%Y-%m-%d %H:%M:%S.%f%z')
        older_posts = Post.objects.filter(post_time__lt=oldest_datetime_object).order_by('-id')[:20]
        older_posts_list = [{"id" : o.pk, 
                    "post_time" :  datetime.strftime(o.post_time, "%Y-%m-%d %H:%M:%S.%f%z"),
                    "poster_username" : o.poster.username,
                    "poster_shown_name":o.poster.shown_name ,
                    "text": o.text}
                    for o in older_posts]
        if len(list(older_posts)) > 0:
            oldest_time = datetime.strftime(list(older_posts)[-1].post_time, "%Y-%m-%d %H:%M:%S.%f%z")
        else:
            oldest_time = oldest_time
        return JsonResponse({'older_posts':older_posts_list,      
                            'oldest_time': oldest_time})



def api_get_latest_posts(request):
    if request.method == 'POST':
        post_body_orig = request.body.decode('utf-8')
        post_body_json = json.loads(post_body_orig)
        latest_time = post_body_json["latest_time"]
        latest_datetime_object = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S.%f%z')
        newer_posts = Post.objects.filter(post_time__gte=latest_datetime_object)
        newer_posts_list = [{"id" : o.pk, 
                            "post_time" :  datetime.strftime(o.post_time, "%Y-%m-%d %H:%M:%S.%f%z"),
                            "poster_username" : o.poster.username,
                            "poster_shown_name":o.poster.shown_name ,
                            "text": o.text}
                            for o in newer_posts]
        return JsonResponse({'newer_posts':newer_posts_list})

def api_get_recent_posts_counter(request):
    if request.method == 'POST':
        post_body_orig = request.body.decode('utf-8')
        post_body_json = json.loads(post_body_orig)
        latest_time = post_body_json["latest_time"]
        latest_datetime_object = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S.%f%z')
        newer_posts_len = Post.objects.filter(post_time__gte=latest_datetime_object).exclude(Q(poster=request.user) & Q(post_time=latest_datetime_object)).__len__()
        return JsonResponse({'newer_posts_num':newer_posts_len})



def api_post(request):
    if request.method == 'POST':
        post_body_orig = request.body.decode('utf-8')
        post_body_json = json.loads(post_body_orig)
        post_text = post_body_json["text"]
        post_privilage = post_body_json["privilage"]
        print(f"結果：{post_privilage}, {post_text}")
        current_user = request.user
        print(current_user.id)

        current_user_object = User.objects.get(id=int(current_user.id))

        a_post = Post(privilage = post_privilage, text = post_text, poster = current_user_object,
        post_time = timezone.now())
        a_post.save()
        return HttpResponse(200, str(post_text))

def signup(request):
    small_letters_a_to_z = string.ascii_letters
    honeypot_name_length = random.choice(range(14,18))
    honeypot_name = ("").join([random.choice(small_letters_a_to_z) for letter in range(honeypot_name_length)])
    
    try:
        request.session['hnyp_name'] = request.session['hnyp_name']
    except KeyError:
        request.session['hnyp_name'] = honeypot_name

    class KhaikangUserCreationForm(UserCreationForm):
        def save(self, commit=True):
            user = super(KhaikangUserCreationForm, self).save(commit=False)
            user.shown_name = self.cleaned_data["username"]
            user.avatar = "static/default_avatar.png"
            if commit:
                user.save()
            return user

        class Meta(UserCreationForm.Meta):
            model = User

            fields = UserCreationForm.Meta.fields + ('email', )

    form = KhaikangUserCreationForm()
    honeypot_name = request.session['hnyp_name']

    if request.method == "POST":
        form = KhaikangUserCreationForm(request.POST)

        if request.POST.get(honeypot_name) != "":
            return HttpResponse(200, "")

        if form.is_valid():
            form.fields['shown_name'] = form.fields['username']
            form.save()
            return redirect('/account/login')  #redirect to login
    
    if request.user != AnonymousUser():
        return redirect('/home')   # redirect to main page

    form = KhaikangUserCreationForm()
    
    template = loader.get_template('signup.html')
    return HttpResponse(template.render({'form': form, 'honeypot_name': honeypot_name}, request))




def user_config(request):
    from PIL import Image
    def erase_exif(image_url):
        original_image = Image.open(image_url)

        image_data = list(original_image.getdata())
        image_without_exif = Image.new(original_image.mode, original_image.size)
        image_without_exif.putdata(image_data)

        image_without_exif.save(image_url)

    """crop image to square"""
    def crop_image(image_path):
        img = Image.open(image_path)
        width, height = img.size  
        left = 0
        top  = 0
        right = img.width
        bottom = img.height
        if width > height:
            left = (width - height) / 2
            right = (width + height) / 2
        elif width < height:
            top = (height - width) / 2
            bottom = (width + height) / 2
        else:
            pass

        img = img.crop((left, top, right, bottom))
        img.save(image_path)




    class UserConfigForm(forms.ModelForm):
        class Meta:
            
            model = User
            fields = ('shown_name', 'avatar', 'desc',   'email')
        


    if request.user == AnonymousUser():
        return redirect('/account/login')  #redirect to login



    if request.method == "POST":
        current_user = User.objects.get(id=request.user.id)
        old_image_path = os.path.abspath(f"./media/{current_user.avatar.name}")
        form = UserConfigForm(request.POST,request.FILES, instance=current_user)
        

        if form.is_valid():
            print(old_image_path)
            
            if os.path.exists(old_image_path) and (old_image_path != os.path.abspath("./media/static/default_avatar.png")):
                a = os.remove(old_image_path)
                print(a)
            
            form.save()

            image_path = os.path.abspath(f"./media/{current_user.avatar.name}")
            erase_exif(image_path)
            crop_image(image_path)


                #
            #current_user_avatar = request.user.avatar
            #print(current_user_avatar)
            #erase_exif(current_user_avatar)


        else:
            pass

    current_user = User.objects.get(id=request.user.id)
    form = UserConfigForm(initial={'shown_name': request.user.shown_name,
                                    'desc' : request.user.desc,
                                    'url' : request.user.url,
                                    'email' : request.user.email})
    template = loader.get_template('user_config.html')
    return HttpResponse(template.render({'form': form, 'avatar': current_user.avatar}, request))

def user_timeline(request, username):

    viewed_user = User.objects.get(username=username)
    if Following.objects.filter(follower = request.user.id).filter(followee=viewed_user.id) or request.user.id == viewed_user.id:
        viewed_timeline_list = Post.objects.filter(poster = viewed_user.id).order_by('-id')[:20]
    else:
        viewed_timeline_list = Post.objects.filter(poster = viewed_user.id).filter(privilage = 'public').order_by('-id')[:20]
    
    latest_received_time = timezone.now()
    if len(viewed_timeline_list) > 0:
        oldest_received_time = list(viewed_timeline_list)[-1].post_time
    else:
        oldest_received_time = datetime.strptime("1970/01/01 00:00", "%Y/%m/%d %H:%M")
    
    template = loader.get_template('user_timeline.html')

    context = {
        'username' : username,
        'user_shown_name' : viewed_user.shown_name,
        'latest_received_time' : latest_received_time,
        'oldest_received_time' : oldest_received_time,
        'viewed_timeline_list': viewed_timeline_list,
    }
    return HttpResponse(template.render(context, request))

def home(request):

    if request.user == AnonymousUser():
        return redirect('/account/login')   # redirect to main page
    
    public_timeline_list = Post.objects.filter(privilage = 'public').order_by('-id')[:20]
    
    latest_received_time = timezone.now()

    if len(public_timeline_list) > 0:
        oldest_received_time = list(public_timeline_list)[-1].post_time
    else:
        oldest_received_time = datetime.strptime("1970/01/01 00:00", "%Y/%m/%d %H:%M")
    
    template = loader.get_template('index.html')

    context = {
        'latest_received_time' : latest_received_time,
        'oldest_received_time' : oldest_received_time,
        'public_timeline_list': public_timeline_list,
    }
    return HttpResponse(template.render(context, request))