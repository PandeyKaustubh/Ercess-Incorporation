
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# @login_required(login_url='/login')
def smartlogin(function):
    def inner(request) :
        print('checking for traces')
        if request.session.get('username') is None :
            print('im redirecting')
            return redirect('/')
        return function(request)
    return inner

