import json
from django.http import HttpResponse, HttpResponseNotAllowed
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

        note = post_body_json["request_note"]
        if note["type"] == "home":
            all_i_follow = Following.objects.filter(follower=request.user.id).filter(isapproved="yes")
            all_i_follow_and_me = User.objects.filter(Q(id__in = all_i_follow) | Q(id=request.user.id))

            older_posts = Post.objects.filter(post_time__lt=oldest_datetime_object).filter(poster__in = all_i_follow_and_me).order_by('-id')[:20]
        elif note["type"] == "user":
            username = note["arg"]
            poster = User.objects.get(username=username)
            older_posts = Post.objects.filter(post_time__lt=oldest_datetime_object).filter(poster=poster).order_by('-id')[:20]
        else:
            pass
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
    else:
        return HttpResponseNotAllowed('POST')



def api_get_latest_posts(request):
    if request.method == 'POST':
        post_body_orig = request.body.decode('utf-8')
        post_body_json = json.loads(post_body_orig)
        latest_time = post_body_json["latest_time"]
        latest_datetime_object = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S.%f%z')

        note = post_body_json["request_note"]
        if note["type"] == "home":
            all_i_follow = Following.objects.filter(follower=request.user.id).filter(isapproved="yes")
            all_i_follow_and_me = User.objects.filter(Q(id__in = all_i_follow) | Q(id=request.user.id))

            newer_posts = Post.objects.filter(post_time__gt=latest_datetime_object).filter(poster__in = all_i_follow_and_me).order_by('-id')[:20]
        elif note["type"] == "user":
            username = note["arg"]
            poster = User.objects.get(username=username)
            newer_posts = Post.objects.filter(post_time__gt=latest_datetime_object).filter(poster=poster).order_by('-id')[:20]

        newer_posts_list = [{"id" : o.pk, 
                            "post_time" :  datetime.strftime(o.post_time, "%Y-%m-%d %H:%M:%S.%f%z"),
                            "poster_username" : o.poster.username,
                            "poster_shown_name":o.poster.shown_name ,
                            "text": o.text}
                            for o in newer_posts]
        return JsonResponse({'newer_posts':newer_posts_list})
    else:
        return HttpResponseNotAllowed('POST')

def api_get_recent_posts_counter(request):
    if request.method == 'POST':
        post_body_orig = request.body.decode('utf-8')
        post_body_json = json.loads(post_body_orig)
        latest_time = post_body_json["latest_time"]
        latest_datetime_object = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S.%f%z')

        note = post_body_json["request_note"]
        if note["type"] == "home":
            all_i_follow = Following.objects.filter(follower=request.user.id).filter(isapproved="yes")
            all_i_follow_and_me = User.objects.filter(Q(id__in = all_i_follow) | Q(id=request.user.id))

            newer_posts_len = Post.objects.filter(post_time__gte=latest_datetime_object) \
                                        .filter(poster__in = all_i_follow_and_me) \
                                        .exclude(Q(poster=request.user) & Q(post_time=latest_datetime_object)) \
                                        .__len__()
        elif note["type"] == "user":
            username = note["arg"]
            poster = User.objects.get(username=username)
            newer_posts_len = Post.objects.filter(post_time__gte=latest_datetime_object) \
                                        .filter(poster=poster) \
                                        .exclude(Q(post_time=latest_datetime_object)) \
                                        .__len__()

        
        return JsonResponse({'newer_posts_num':newer_posts_len})
    else:
        return HttpResponseNotAllowed('POST')



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
    else:
        return HttpResponseNotAllowed('POST')

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
            fields = ('shown_name', 'desc', 'avatar',  'email')
            
        avatar = forms.ImageField(required = False)


    if request.user == AnonymousUser():
        return redirect('/account/login')  #redirect to login



    if request.method == "POST":
        current_user = User.objects.get(id=request.user.id)
        old_image_path = os.path.abspath(f"./media/{current_user.avatar.name}")
        form = UserConfigForm(request.POST,request.FILES, instance=current_user)
        

        if form.is_valid():
            image_path = os.path.abspath(f"./media/{current_user.avatar.name}") 
            try:
                avatar_path_in_form = form.cleaned_data['avatar'].path
            except AttributeError:
                avatar_path_in_form = form.cleaned_data['avatar']
            
            if avatar_path_in_form != old_image_path and is_custom_avatar_path(old_image_path):
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
    form = UserConfigForm(initial={'shown_name': current_user.shown_name,
                                    'desc' : current_user.desc,
                                    'url' : current_user.url,
                                    'email' : current_user.email})
    template = loader.get_template('user_config.html')
    return HttpResponse(template.render({'form': form, 'avatar': current_user.avatar}, request))

def is_custom_avatar_path(old_image_path):
    return os.path.exists(old_image_path) and (old_image_path != os.path.abspath("./media/static/default_avatar.png"))

def follow_request(request, request_value, dest_username):
    if request.method != "POST":
        return HttpResponseNotAllowed('POST')
    else:
        current_user = User.objects.get(id=request.user.id)
        dest_user = User.objects.get(username=dest_username)
        
        if request_value == "send-following-request":
            following_status = Following(follower=current_user, followee= dest_user, isapproved="undecided")
            following_status.save()
            return JsonResponse({'status': "request sent"})
        elif request_value == "cancel-following-request":
            following_status = Following.objects.get(follower=current_user.id, followee= dest_user.id)
            following_status.delete()
            return JsonResponse({'status': "request cancelled"})
        elif request_value == "unfollow":
            following_status = Following.objects.get(follower=current_user.id, followee= dest_user.id)
            following_status.delete()
            return JsonResponse({'status': "unfollowed"})
        else:
            return JsonResponse({'status': "other"})



def user_timeline(request, username):
    user_id = User.objects.get(username=username).id

    user_following_number = Following.objects.filter(follower=user_id).filter(isapproved="yes").__len__()
    user_follower_number = Following.objects.filter(followee=user_id).filter(isapproved="yes").__len__()


    following_relationship  = Following.objects.filter(follower=request.user.id).filter(followee=user_id)
    following_status = ""
    if following_relationship.__len__() == 0:
        following_status = "unfollowed"
    else:
        following_status = following_relationship[0].isapproved
    

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
        'following_status': following_status,
        'user_following_number' : user_following_number,
        'user_follower_number': user_follower_number,
        'latest_received_time' : latest_received_time,
        'oldest_received_time' : oldest_received_time,
        'viewed_timeline_list': viewed_timeline_list,
    }
    return HttpResponse(template.render(context, request))

def home(request):

    if request.user == AnonymousUser():
        return redirect('/account/login')   # redirect to main page

    all_i_follow = Following.objects.filter(follower=request.user.id).filter(isapproved="yes")
    all_i_follow_and_me = User.objects.filter(Q(id__in = all_i_follow) | Q(id=request.user.id))
    public_timeline_list = Post.objects.filter(poster__in = all_i_follow_and_me).order_by('-id')[:20]
        
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