import json
from django.http import HttpResponse
from django.template import loader
from .models import User, Post 
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser

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

    class KhaikangUserCreationForm(UserCreationForm):
        def save(self, commit=True):
            user = super(KhaikangUserCreationForm, self).save(commit=False)
            user.shown_name = self.cleaned_data["username"]
            if commit:
                user.save()
            return user

        class Meta(UserCreationForm.Meta):
            model = User
            fields = UserCreationForm.Meta.fields + ('email',)

    form = KhaikangUserCreationForm()

    if request.method == "POST":
        form = KhaikangUserCreationForm(request.POST)
        if form.is_valid():
            form.fields['shown_name'] = form.fields['username']
            print(form.fields['shown_name'])
            form.save()
            return redirect('/account/login')  #redirect to login
    
    if request.user != AnonymousUser():
        return redirect('/home')   # redirect to main page

    form = KhaikangUserCreationForm()
    
    template = loader.get_template('signup.html')
    return HttpResponse(template.render({'form': form}, request))

def home(request):

    public_timeline_list = Post.objects.filter(privilage = 'public').order_by('-id')[:10]
    

    print(public_timeline_list)

    template = loader.get_template('index.html')

    context = {
        'public_timeline_list': public_timeline_list,
    }
    return HttpResponse(template.render(context, request))