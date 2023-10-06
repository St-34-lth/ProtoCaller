from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView

from django.views.generic import ListView
from django.views.generic import DetailView

from .models import *
# my code starts here 

# Create your views here.


class index(ListView):
    
    #unless we need the get_queryset method to be run every time for some reason, this is more efficient
    
    queryset=[Organism.objects.all(),Protein.objects.all()]
        
    template_name = 'caller/base.html'
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
       
        context.update(kwargs)
        
        # print(context)
        return context 
    
# my code ends here 
