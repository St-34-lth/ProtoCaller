from django.urls import path,include
from rest_framework import routers 
from .api import * 
from .views import *
# my code starts here 
urlpatterns=[
    #assignment requests
    path('api/protein/<str:protein_id>',ProteinDetail.as_view(),name='protein_api'),
    path('api/protein/',ProteinDetail.as_view(),name='new_protein'),
    path('api/protein',ProteinCreate.as_view(),name='protein_create'),
    
    path('api/proteins/<int:taxa_id>',OrganismProteinList.as_view(),name='organism_proteins'),
    path('api/pfams/<int:taxa_id>',OrganismPfamList.as_view(),name='organism_api'),
    path('api/pfam/<str:pfam_id>',PfamDetail.as_view(),name='pfam_api'),
    path('api/coverage/<str:protein_id>',CoverageDetail.as_view(),name='coverage_api'),
    #additional
    path('',index.as_view(),name='index'),
    path('api/proteins', ProteinList.as_view(),name='protein_api_list'),
    path('api/organisms',OrganismList.as_view(),name='organism_api_list'),
    path('api/domains',DomainList.as_view(),name='domain_list'),
    path('api/pfams',PfamList.as_view(),name='pfamlist'),
    
]

# my code ends here 