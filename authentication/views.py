from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import  EmailAuthenticationForm

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
# Create your views here.
  
class EmailLoginView(View):
    template_name = 'registration/login.html'

    def get(self, request):
        form = EmailAuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # or any success URL
        return render(request, self.template_name, {'form': form})

def logout_view(request):
    request.session.flush()
    return redirect('home')    

