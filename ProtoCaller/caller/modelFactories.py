import factory
import faker 
from random import randint
from random import choice
from django.test import TestCase
from django.conf import settings
from django.core.files import File
from .models import *
f =  faker.Faker()
class OrganismFactory(factory.django.DjangoModelFactory):
    taxa_id = factory.Sequence(lambda n: n+1)
    id = factory.Sequence(lambda n: n+1)
    genus = factory.Faker('sentence',nb_words=1)
    species = factory.Faker('sentence',nb_words=1)
    clade = f.random_letters(1)
    
    class Meta:
        model = Organism


class PfamFactory(factory.django.DjangoModelFactory):
    domain_id = factory.Sequence(lambda n: 'pfam%d' % n ) #pfam0 pfam1 etc  
    domain_description = factory.Sequence(lambda n: 'domaindescription%d' % n) #domain description1 ... etc
    id = factory.Sequence(lambda n: n+1)
    class Meta:
        model = Pfam        
       
class ProteinFactory(factory.django.DjangoModelFactory):
    protein_id =   factory.Sequence(lambda n: 'protein%d' % n) #protein0 protein1 etc
    organism_id =  factory.SubFactory(OrganismFactory)
    id = factory.Sequence(lambda n: n+1)
    sequence = factory.Sequence(lambda n: chr((n % 26) + 97) * 1024)
    length = randint(1,100000)
    
    class Meta:
        model = Protein 
        
class DomainFactory(factory.django.DjangoModelFactory):
    
    id = factory.Sequence(lambda n: n+1) 
    pfam_id = factory.SubFactory(PfamFactory)
    start = randint(1,1000)
    stop = start + randint(1,1000)
    # protein_id = factory.SubFactory(ProteinFactory)
    description = factory.Faker('sentence',nb_words=2)#factory.Sequence(lambda n: 'domain description%d' % n)
    class Meta:
        model = Domain


    

    
