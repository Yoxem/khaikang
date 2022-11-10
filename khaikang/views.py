
from django.http import HttpResponse
from django.template import loader
from .models import User, Post 

def home(request):
    public_timeline_list = Post.objects.filter(privilage = 'public')[:10]

    print(public_timeline_list)

    template = loader.get_template('index.html')

    context = {
        'latest_question_list': public_timeline_list,
    }
    return HttpResponse(template.render(context, request))