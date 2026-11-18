from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
# Create your views here.
def register(request):
    if request.method == "POST":
        a = request.POST['fname']
        b = request.POST['lname']
        c = request.POST['email']
        d = request.POST['uname']
        e = request.POST['password']
        try:
            u = User.objects.get(username = d)
            return render(request,'register.html',{'error':"Username already exist"})
        except User.DoesNotExist:
            u = User.objects.create(
                first_name = a,
                last_name = b,
                email = c,
                username = d
            )
            u.set_password(e)
            u.save()
            return redirect('login')
    return render(request,'register.html')

def login_(request):
    if request.method=='POST':
        a=request.POST['uname']
        b=request.POST['password']
        user=authenticate(request, username=a,password=b)
        if user is not None:
           login(request,user)
           return redirect('home')
        else:
            return render(request,'login.html',{'error':'Invalid Credentials'})
    return render(request,'login.html')

@login_required(login_url='login')
def logout_(request):
    logout(request)
    return redirect('home')
@login_required(login_url='login')
def profile(req):
    return render(req,'profile.html')