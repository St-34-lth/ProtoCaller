import os
import sys
import django
import csv
import pandas as pd 
from collections import defaultdict
import copy
from django.db import transaction
from django.utils import timezone 
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings 
#my code starts here

#paths are all relative


from caller.models import *

class Command(BaseCommand):
    help = 'A loader script for the populating the ProtoCaller database'
        
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE','ProtoCaller.settings')
        django.setup()
        self.parentdir = os.path.join(settings.BASE_DIR,'ProtoCaller','data') 

        self.data_fp = os.path.join(settings.BASE_DIR,'data/')

    def add_arguments(self, parser):
        parser.add_argument('--test',type=str,help="testing mode")
        parser.add_argument('--pfams', type=str, help='File path for PFAM descriptions')
        parser.add_argument('--proteins', type=str, help='File path for proteins')
        parser.add_argument('--sequences', type=str, help='File path for sequences')
    
    def get_fps(self,*args,**options):
        self.stdout.write('fps')
        
        default_pfams_fp = 'pfam_descriptions.csv'
        default_seq_fp = 'assignment_data_sequences.csv'
        default_prot_fp ='assignment_data_set.csv'
        
        default_pfams_fp = os.path.join(self.data_fp,default_pfams_fp)
        default_seq_fp = os.path.join(self.data_fp,default_seq_fp)
        default_prot_fp = os.path.join(self.data_fp,default_prot_fp)
        
        default_folders = {"pfams_fp":default_pfams_fp,"prot_fp":default_prot_fp,"seq_fp":default_seq_fp}
        
        
       
        try: 
            pfams_fp = ""
            prot_fp =""
            seq_fp =""
            if options['pfams']:
                pfams_fp = options['pfams']
                self.stdout.write(f' Processing PFAM descriptions file: {pfams_fp}')
                pfams_fp = os.path.join(self.data_fp,pfams_fp)
                
            if options['proteins']:
                prot_fp = options['proteins']
                self.stdout.write(f' Processing proteins file: {prot_fp}')
                prot_fp = os.path.join(self.data_fp,prot_fp)
                
            if options['sequences']:
                seq_fp = options['sequences']
                self.stdout.write(f' Processing sequences file: {seq_fp}')
                seq_fp = os.path.join(self.data_fp,seq_fp)
            
            folders = {"pfams_fp":pfams_fp,"prot_fp":prot_fp,"seq_fp":seq_fp}
            
            for fp in folders.keys():
                if not (os.path.exists(folders[fp])):
                    self.stdout.write(' filepath does not exist make sure it is added under the project"s data/ directory')
                    self.stdout.write(folders[fp])
                    raise FileNotFoundError 
                
            return folders 
        except FileNotFoundError:
            self.stdout.write(f'using default values for filepaths...: {default_folders["pfams_fp"]}, {default_folders["prot_fp"]}, {default_folders["seq_fp"]}')
            return default_folders
        except KeyError:
            self.stdout.write(f'using default values for filepaths...: {default_folders["pfams_fp"]}, {default_folders["prot_fp"]}, {default_folders["seq_fp"]}')
            return default_folders
        
    def handle(self,*args,**options):
        
        try: 
                if options['test'] =='test':
                    self.stdout.write('test')
                    return
                dataFolders = self.get_fps(*args,**options) 
                                            
                self.stdout.write('loading script')
                self.stdout.write('loading data from: ') 
                self.stdout.write(self.data_fp)
                self.stdout.write('ensuring database is flushed....')
            
                
                flag =  self.resetDb()
                if flag:
                    self.stdout.write('DB flushed successfully')
                    
                dataLists = self.loadDb(dataFolders)
                for name,data in dataLists.items():
                    if len(data) == 0:
                        self.stdout.write(name)
                        self.stdout.write('dataList is empty.')
                        

                self.stdout.write('creating databases:')
                self.createDb(dataLists['organisms'],dataLists['pfams'],dataLists['proteins'],dataLists['domains'],dataLists['proteinDomains'])
                self.stdout.write('Organism, Protein, Domain, Pfam, ProteinDomain tables populated successfully with:')
                print(len(Organism.objects.all()),' ',len(Protein.objects.all()),' ', len(Domain.objects.all()),' ',len(Pfam.objects.all()),' ', len(ProteinDomains.objects.all()))
        except Exception:
            raise CommandError("Something went wrong during populating the database")
        
    def loadDb(self,folders):
        
        org_ids= {}
        pfam_ids = {}
        prot_ids={}
        proteinDomains = []
        domains = [] 
        dataLists = {}
        for folder in folders.keys():
            
            with open(folders[folder]) as csv_file:
                
                csv_reader = csv.reader(csv_file, delimiter=',')
                
                header = csv_reader.__next__() 
                
                print("running on: "+ folder)
                    
                for row in csv_reader:
                    if row.count(',') > 0:
                        row.remove(',')
                        
                    rowNo = csv_reader.line_num
                    
                    if folder == "pfams_fp":
                        pfam_id = row[0]
                        domain_description = row[1]
                        pfam_ids[pfam_id] = Pfam(domain_id=pfam_id,domain_description=domain_description,id=rowNo)

                    if folder == "prot_fp":
                        
                        protein_id = row[0]
                        taxa_id = row[1]
                        clade = row[2]
                        genusSpecies = row[3]
                        description = row[4]
                        pfam_id = row[5]
                        start = row[6]
                        stop = row[7]
                        length = row[8] 
                                                        
                        if taxa_id not in org_ids.keys():
                            
                            genusSpecies = genusSpecies.split(' ')     
                            org_ids[taxa_id]= Organism(taxa_id=taxa_id,
                                                    genus=genusSpecies[0],
                                                    species=genusSpecies[1],
                                                    clade=clade,id=rowNo)
                        
                        domain = Domain(id=rowNo,pfam_id_id =int(pfam_ids[pfam_id].id),start=start,stop=stop,description=description)
                    
                        if protein_id not in prot_ids.keys():
                            protein = Protein(protein_id=protein_id,
                                        sequence ='',
                                        length=length,         
                                        organism_id_id=org_ids[taxa_id].id,
                                        id=rowNo)

                            prot_ids[protein_id] = protein 
                            proteinDomains.append(ProteinDomains(protein = protein,domain=domain))
                            
                        else: 
                            
                            proteinDomains.append(ProteinDomains(protein = prot_ids[protein_id],domain=domain))
                            
                            # print('same protein',protein_id,pfam_id)
                        domains.append(domain)   

                    if folder == "seq_fp":
                        protein_id = row[0]
                        sequence = row[1]
                        prot_ids[protein_id].sequence = sequence 

        dataLists['domains'] = domains 
        dataLists['organisms'] = [*org_ids.values() ] 
        dataLists['pfams'] = [*pfam_ids.values()] 
        dataLists['proteins'] =[*prot_ids.values()] 
        dataLists['proteinDomains'] = proteinDomains
        
        return dataLists 

    def resetDb(self):
        Protein.objects.all().delete()
        Protein.objects.raw("delete from sqlite_sequence where name='caller_protein';")
        Domain.objects.all().delete()
        Domain.objects.raw("delete from sqlite_sequence where name='caller_domain';")
        Organism.objects.all().delete()
        Organism.objects.raw("delete from sqlite_sequence where name='caller_organism';")
        Pfam.objects.all().delete();
        Pfam.objects.raw("delete from sqlite_sequence where name='caller_pfam';")
        ProteinDomains.objects.all().delete()
        ProteinDomains.objects.raw("delete from sqlite_sequence where name='caller_ProteinDomains';")

        if len(Pfam.objects.all()) > 0:
            return False 
        if len(Protein.objects.all()) > 0:
            return False 
        if len(Domain.objects.all()) > 0:
            return False 
        if len (Organism.objects.all()) > 0:
            return False 
        if len(ProteinDomains.objects.all()) >0:
            return False
        return True
     
    def createDb(self,organisms,pfams,proteins,domains,proteinDomains):
        Pfam.objects.bulk_create(pfams)
        Organism.objects.bulk_create(organisms)
        Protein.objects.bulk_create(proteins)
        Domain.objects.bulk_create(domains)
        ProteinDomains.objects.bulk_create(proteinDomains)

#my code ends here