from django.test import TestCase
import json
from django.urls import reverse
from django.urls import reverse_lazy
from rest_framework.test import APIRequestFactory,APIClient
from rest_framework.test import APITestCase
from django.forms.models import model_to_dict
from .api import * 
from .models import *
from .modelFactories import *
from .serializers import *

# Create your tests here.
# My code begins here
class ModelsDbTests(TestCase):
    def setUp(self):
        self.org = OrganismFactory.create(id=1) 
        self.prot = ProteinFactory.create(id=1) #
        self.pfam= PfamFactory.create(id=1)
        self.dom = DomainFactory.create(pk=1)
        self.prot.organism_id= self.org
        self.prot.domains.add(self.dom)
        
        self.prot.save()
        
    def tearDown(self):
        Organism.objects.all().delete()
        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)
        

    def testOrganismExists(self):
        """organism model exists"""
        self.assertIsNotNone(self.org)

    def testOrganismGenusBlank(self):
        """Changing organism genus to blank raises validation error"""
        self.org.genus = ""  # Set the genus field to a blank value
        with self.assertRaises(ValidationError):
            self.org.save()
    
    def testOrganismCladeBlank(self):
        """Changing organism genus to blank raises validation error"""
        self.org.clade = ""  # Set the genus field to a blank value
        with self.assertRaises(ValidationError):
            self.org.save()
        
    def testOrganismGetPfams(self):
        
        pfams = self.org.get_pfams()
        self.assertEqual(pfams[0].domain_id,self.prot.domains.all()[0].pfam_id.domain_id)
        
        
    def testProteinExists(self):
        """Protein model exists"""
        self.assertIsNotNone(self.prot)
    
    def testProteinIdNotBlank(self):
        self.prot.protein_id = ' '
        with self.assertRaises(ValidationError):
            self.prot.save()
    
    def testProteinLengthNotZero(self):
        self.prot.length = 0 
        with self.assertRaises(ValidationError):
            self.prot.save()
    
    def testProteinSequenceNotBlank(self):
        self.prot.sequence = " " 
        with self.assertRaises(ValidationError):
            self.prot.save()
    
    
    def testDomainExists(self):
        """domain model exists"""
        self.assertIsNotNone(self.dom)
    
    def testDomainStartGTStop(self):
        self.dom.stop = self.dom.start
        with self.assertRaises(ValidationError):
            self.dom.save()
    
    def testPfamsExists(self):
        """pfam model exists"""
        self.assertIsNotNone(self.pfam)    
    
    def testPfamBlankValues(self):
        self.pfam.domain_id =' '
        self.pfam.domain_description = " "
        with self.assertRaises(ValidationError):
            self.pfam.save()
        
    
class CallerAPIListTests(APITestCase):
    def setUp(self):
        self.c = APIClient()
        self.batchSize = 2 
        self.doms = DomainFactory.create_batch(self.batchSize)
        self.prots = ProteinFactory.create_batch(self.batchSize)
        for prot in self.prots:
            for dom in self.doms:
                prot.domains.add(dom)
            
    def tearDown(self):
        Organism.objects.all().delete();
        OrganismFactory.reset_sequence(0)
        Protein.objects.all().delete()
        ProteinFactory.reset_sequence(0)
        
    
    def testGetOrganismList(self):
   
        goodUrl = reverse('organism_api_list')
        res = self.c.get(goodUrl,format='json')
        self.assertEqual(res.status_code,200) 
        data = json.loads(res.content)
        # print(data)
        self.assertTrue('taxa_id' in data['results'][0])
        self.assertEqual(len(data['results']),self.batchSize)  
      
    def testGetProteinList(self):
  
        goodUrl = reverse('protein_api_list')
        res = self.c.get(goodUrl,format='json')
        res.render() 
        self.assertEqual(res.status_code,200) 
        data = json.loads(res.content)
        # print(data)
        self.assertTrue('protein_id' in data['results'][0])
        self.assertEqual(len(data['results']),self.batchSize)
       
    
    def testProteinListIncludesDomains(self):
        goodUrl = reverse('protein_api_list')
        res = self.c.get(goodUrl,format='json')
        res.render() 
        self.assertEqual(res.status_code,200) 
        data = json.loads(res.content)
        # print(data)
        self.assertTrue('domains' in data['results'][0])
        
        
    def testGetDomainList(self):
        
        goodUrl = reverse('domain_list')
        res = self.c.get(goodUrl,format='json')
        res.render()
        self.assertEqual(res.status_code,200)
        data = json.loads(res.content)
        self.assertTrue('pfam_id' in data['results'][0])
        self.assertEqual(len(data['results']),self.batchSize)
       
        
    def testGetPfamList(self):
       
        goodUrl = reverse('pfamlist')
        res = self.c.get(goodUrl,format='json')
        res.render()
        self.assertEqual(res.status_code,200)
        data = json.loads(res.content)
        self.assertTrue('domain_id' in data['results'][0])
        self.assertEqual(len(data['results']),self.batchSize)
      
class OrganismTests(APITestCase):
    
    def setUp(self):
        self.c = APIClient()
        self.batchSize = 2 
        self.dom = DomainFactory.create(pk=1)
        self.doms = DomainFactory.create_batch(self.batchSize)
        self.prots = ProteinFactory.create_batch(self.batchSize)
        self.prots[1].organism_id= self.prots[0].organism_id
        self.prots[1].save()
        # print(Organism.objects.all())
        for prot in self.prots:
            for dom in self.doms:
                prot.domains.add(dom)
    
    def tearDown(self):
        Organism.objects.all().delete()
        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)  
        
    def testGetOrganismProteins(self):
        goodUrl = reverse('organism_proteins',kwargs={"taxa_id":1})
        commonProteinsInOrganism = 2 
        res = self.c.get(goodUrl,format='json')
        res.render()
        self.assertEqual(res.status_code,200)
        data = json.loads(res.content)
        
        self.assertTrue('protein_id' in data['results'][0])
        self.assertEqual("protein0" ,data['results'][0]['protein_id'])
        self.assertEqual(commonProteinsInOrganism,len(data["results"][0]))

class ProteinTests(APITestCase):
        
    def setUp(self):
        self.c = APIClient()
        
        self.prot1 = ProteinFactory.create(id=1)
        self.prot2 = ProteinFactory.create(id=2)
        
        self.dom1 = DomainFactory.create(id=1)
        self.dom2 = DomainFactory.create(id=2)
        self.dom3 = DomainFactory.create(id=3)
        self.protDoms= []
        self.protDoms.append(ProteinDomains(protein=self.prot1,domain=self.dom1))
        self.protDoms.append(ProteinDomains(protein=self.prot1,domain=self.dom2))
        self.protDoms.append(ProteinDomains(protein=self.prot2,domain=self.dom3))
        
        ProteinDomains.objects.bulk_create(self.protDoms)
        
    def tearDown(self):
       
        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        ProteinDomains.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)  
        
    def testGetProteinDetailSingleDomain(self):
        proteinId = 'protein0'
        goodUrl = reverse('protein_api', kwargs={'protein_id':proteinId})    
        res = self.c.get(goodUrl)
        res.render() # is this required??? 
        self.assertEqual(res.status_code,200)
        data = json.loads(res.content )
        # print(data)
        self.assertTrue('protein_id' in data)
        self.assertTrue('domains' in data)
        self.assertEqual(data['protein_id'], proteinId)
        self.assertEqual(len(self.prot1.domains.all()),len(data['domains']))
        
    def testGetProteinDetailManyDomains(self):
        proteinId = 'protein1'
        goodUrl = reverse('protein_api', kwargs={'protein_id':proteinId})    
        res = self.c.get(goodUrl)
        res.render() # is this required??? 
        self.assertEqual(res.status_code,200)
        data = json.loads(res.content )
        self.assertTrue('protein_id' in data)
        self.assertTrue('domains' in data)
        self.assertEqual(data['protein_id'], proteinId)
        self.assertEqual(len(self.prot2.domains.all()),len(data['domains']))
        
    def testGetPfamDetail(self):
        pfamid = 'pfam0'
        goodUrl = reverse('pfam_api', kwargs={'pfam_id':pfamid})    
        res = self.c.get(goodUrl)
        res.render() # is this required??? 
        self.assertEqual(res.status_code,200)
        data = json.loads(res.content )
   
        self.assertTrue(data['domain_id'],pfamid)
        
    def testGetOrganismPfams(self):
        """Test whether all the pfams for a given organism are returned"""
        goodUrl = reverse('organism_api', kwargs={'taxa_id':self.prot1.organism_id.taxa_id})    
        res = self.c.get(goodUrl)
        res.render() 
        self.assertEqual(res.status_code,200)
        data = json.loads(res.content)
        self.assertEqual(len(self.prot1.domains.all()),data['count'])
        
    def testCoverage(self):
        """tests the coverage end point"""
        expectedCoverage =0
        sum =0 
        for dom in self.prot1.domains.all():
            sum += dom.stop - dom.start  
        expectedCoverage = sum / self.prot1.length 
        proteinId = 'protein0'
        goodUrl=reverse('coverage_api',kwargs={'protein_id':proteinId})
        res = self.c.get(goodUrl)
        
        self.assertEqual(res.status_code,200)
        data =json.loads(res.content)
        self.assertEqual(data['coverage'],expectedCoverage)
    
    def testPostProteinOnNewValues(self):
        """tests whether a protein can be posted without any existing data in the DB"""
        goodUrl = reverse("new_protein")
        organism_data = {'genus':'testGenus','species':'testSpecies','clade':'testClade','taxa_id':100} 
        pfam_data = {"domain_id":"PF00000","domain_description":"domaindescription"}
        domain_data = [{'pfam_id':pfam_data,'description':'domain description','start':100,"stop":200}] 
        protein_data = {'protein_id':'testProtein','organism_id':organism_data,'sequence':'testSequence',"length":100,'domains':domain_data}
        
        data={**protein_data}
        res = self.c.post(goodUrl,data,format='json')
        res.render()  
        # print(res.data)
        self.assertEqual(res.status_code,201)
        testUrl = reverse('protein_api',kwargs={'protein_id':data['protein_id']})
        res = self.c.get(testUrl)
        res.render() 
        
        returnedData = json.loads(res.content)
        
        self.assertIn(returnedData['protein_id'],data['protein_id'])
    
    
    def testPostProteinExisting(self):
        """tests whether a protein can be posted with existing related values"""
        goodUrl = reverse("new_protein")
        organism_data = OrganismSerializer(self.prot1.organism_id).data
        
        pfam_data = PfamSerializer(self.prot1.domains.all()[0].pfam_id).data
        domain_data = [ DomainSerializer(self.prot1.domains.all()[0]).data]
        
        protein_data = {'protein_id':'testProtein','organism_id':organism_data,'sequence':'testSequence',"length":100,'domains':domain_data}
        # data=json.dumps(protein_data)
        # print(data)
        data={**protein_data}
        res = self.c.post(goodUrl,data,format='json')
        self.assertEqual(res.status_code,201)
        
        
        testUrl = reverse('protein_api',kwargs={'protein_id':data['protein_id']})
        res = self.c.get(testUrl)
        self.assertEqual(res.status_code,200)
        res.render() 
        returnedData = json.loads(res.content)
        self.assertIn(data['protein_id'],returnedData['protein_id'])
        
from io import StringIO
from django.core.management import call_command

class LoaderTest(TestCase):
    
    def setUp(self):
        OrganismFactory.create(id=1)
        
    def tearDown(self):
        Organism.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        
    def testCmdOut(self):
        out = StringIO()
        arg1 = 'test'
        call_command("loader",test=arg1, stdout=out)
        self.assertIn("test", out.getvalue())
    
    def testFilePathInput(self):
        out = StringIO()
        pfam_fp = 'pfam_descriptions.csv'
        proteins_fp = 'proteinTest.csv'
        sequences_fp = 'sequences.csv'

        # Call the management command with the file paths
        call_command('loader', pfams=pfam_fp, proteins=proteins_fp, sequences=sequences_fp, stdout=out)

        # print(out.getvalue())
        self.assertIn(f'{pfam_fp}', out.getvalue())
        self.assertIn(f'{proteins_fp}', out.getvalue())
        self.assertIn(f'{sequences_fp}', out.getvalue())
    
    def testFilePathInputErrors(self):
        out = StringIO()
        pfam_fp = 'pfam_descriptions.csv'
        proteins_fp = 'proteinTest.csv'
        sequences_fp = 'sequences.csv'

        # Call the management command with the file paths
        call_command('loader', pfams=pfam_fp, proteins=proteins_fp, sequences=sequences_fp, stdout=out)

        # print(out.getvalue())
        self.assertIn(f'filepath does not exist', out.getvalue())

    def testFilePathDefaultValues(self):
        out = StringIO()
        
        pfam_fp = 'pfam_descriptions.csv'
        proteins_fp = 'assignment_data_set.csv'
        sequences_fp = 'assignment_data_sequences.csv'

        # Call the management command with the file paths
        call_command('loader', stdout=out)

        # print(out.getvalue())
        self.assertIn(f'{pfam_fp}', out.getvalue())
        self.assertIn(f'{proteins_fp}', out.getvalue())
        self.assertIn(f'{sequences_fp}', out.getvalue())
    
    def testDBFlushedTrue(self):
        out = StringIO()
        self.assertEqual(1,len(Organism.objects.all()))
        call_command('loader', stdout=out)
        self.assertIn('DB flushed',out.getvalue())
    
    def testDBPopulated(self):
        out = StringIO()
        self.assertEqual(1,len(Organism.objects.all()))
        call_command('loader', stdout=out)
        self.assertTrue(1995,out.getvalue())
        
        
        
class DomainSerialiserTest(APITestCase):
    
    
    def setUp(self):
        self.dom1 = DomainFactory.create(id=1)
        # print(self.dom1)
        self.domSerial = DomainSerializer(instance = self.dom1)
        # self.domSerial.is_valid(raise_exception=True) 
        self.domFields =  ['id','pfam_id','description','start','stop']
        
        
    def tearDown(self):

        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        ProteinDomains.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)  
        
    def testDomainSerializer(self):
        data = self.domSerial.data
        self.assertEqual(set(data.keys()),set(self.domFields))
        
    def testDomainSerializerDataValid(self):
        domainData = model_to_dict(self.dom1)
        pfamData = model_to_dict(self.dom1.pfam_id)
        domainData['pfam_id'] = pfamData
        self.domSerial= DomainSerializer(data=domainData)
        self.assertTrue(self.domSerial.is_valid(raise_exception=True))
        
    def testDomainStartGTStopData(self):
        domainData = model_to_dict(self.dom1)
        domainData['stop'] = domainData['start'] -1
        pfamData = model_to_dict(self.dom1.pfam_id)
        domainData['pfam_id'] = pfamData
        self.domSerial= DomainSerializer(data=domainData)
        with self.assertRaises(Exception):
            self.domSerial.is_valid(raise_exception=True)
    
    def testDomainStartStopZero(self):
        domainData = model_to_dict(self.dom1)
        domainData['stop'] =0
        pfamData = model_to_dict(self.dom1.pfam_id)
        domainData['pfam_id'] = pfamData
        self.domSerial= DomainSerializer(data=domainData)
        with self.assertRaises(Exception):
            self.domSerial.is_valid(raise_exception=True)
        domainData['stop'] = 100
        domainData['start'] =0
        with self.assertRaises(Exception):
            self.domSerial.is_valid(raise_exception=True)
        
    def testDomainPfam(self):
        domainData = model_to_dict(self.dom1)
        pfamData = model_to_dict(self.dom1.pfam_id)
        # domainData['pfam_id'] = pfamData
        self.domSerial= DomainSerializer(data=domainData)
        with self.assertRaises(Exception):
            self.domSerial.is_valid(raise_exception=True)
        

from rest_framework.exceptions import ValidationError as DRFVE
class OrganismSerializerTest(APITestCase):
    def setUp(self):
        self.org = OrganismFactory.create(id=1)        
        self.orgSerial = OrganismSerializer(instance = self.org)
        self.orgFields =  ['id','taxa_id','clade','genus','species']
        
        
    def tearDown(self):

        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        ProteinDomains.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)  
        
    def testOrganismSerializer(self):
        
        data = self.orgSerial.data
        self.assertEqual(set(data.keys()),set(self.orgFields))
        
    def testOrganismSerializerDataValid(self):
        
        orgData= model_to_dict(self.org)
        self.orgSerial =OrganismSerializer(data=orgData)
        self.assertTrue(self.orgSerial.is_valid(raise_exception=True))
        
    #handled by the rest framework exceptions
    def testOrganismSerializerBlankGenus(self):
        orgData= model_to_dict(self.org)
        orgData['genus'] = ' '
        self.orgSerial =OrganismSerializer(data=orgData)
        with self.assertRaises(DRFVE):
            self.orgSerial.is_valid(raise_exception=True)
    
    #handled by the rest framework exceptions
    def testOrganismSerializerBlankSpecies(self):
        orgData= model_to_dict(self.org)
        orgData['species'] = ' '
        self.orgSerial =OrganismSerializer(data=orgData)
        with self.assertRaises(DRFVE):
            self.orgSerial.is_valid(raise_exception=True)
    
    def testOrganismSerializerTaxaId(self):
        orgData= model_to_dict(self.org)
        orgData['taxa_id'] = 0
        self.orgSerial =OrganismSerializer(data=orgData)
        with self.assertRaises(DRFVE):
            self.orgSerial.is_valid(raise_exception=True)
    
class PfamSerializerTest(APITestCase):
    def setUp(self):
        self.pfam = PfamFactory.create(id=1)        
        self.pfamSerial = PfamSerializer(instance = self.pfam)
        
        self.pfamFields =  ['id','domain_id','domain_description']
        
        
    def tearDown(self):

        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        ProteinDomains.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)  
        
    def testPfamSerializer(self):        
        data = self.pfamSerial.data
        self.assertEqual(set(data.keys()),set(self.pfamFields))
        
    def testPfamSerializerValidData(self):
        
        pfamData= model_to_dict(self.pfam)
        self.pfamSerial = PfamSerializer(data=pfamData)
        self.assertTrue(self.pfamSerial.is_valid(raise_exception=True))
        
    #handled by the rest framework exceptions
    def testPfamSerializerBlankDomainId(self):
        pfamData= model_to_dict(self.pfam)
        pfamData['domain_id']= ' '
        self.pfamSerial = PfamSerializer(data=pfamData)
        with self.assertRaises(DRFVE):
            self.pfamSerial.is_valid(raise_exception=True)
    
    def testPfamSerializerBlankDomainDescription(self):
    
        pfamData= model_to_dict(self.pfam)
        pfamData['domain_description']= ' '
        self.pfamSerial = PfamSerializer(data=pfamData)
        with self.assertRaises(DRFVE):
            self.pfamSerial.is_valid(raise_exception=True)
    
class ProteinSerialiazerTest(APITestCase):
    
    def setUp(self):
        self.prot =ProteinFactory.create(id=1)        
        self.protSerial= ProteinSerializer(instance = self.prot)
        self.protFields = ['protein_id','sequence','taxonomy','length','domains']            
        self.org = self.prot.organism_id
        
    
    def tearDown(self):

        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        ProteinDomains.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)  
        
    def testProteinSerializer(self):        
        data = self.protSerial.data
        self.assertEqual(set(data.keys()),set(self.protFields))
        
    def testProteinSerializerValidData(self):
        
        protData= model_to_dict(self.prot)
        protData['taxonomy'] = model_to_dict(self.org)
        protData.pop('organism_id')
        protData.pop('id')
        self.protSerial = ProteinSerializer(data=protData)
        self.assertTrue(self.protSerial.is_valid(raise_exception=True))
        
    def testProteinSerializerLength(self):
        
        protData= model_to_dict(self.prot)
        protData['taxonomy'] = model_to_dict(self.org)
        protData.pop('organism_id')
        protData.pop('id')
        protData['length']= -1
        self.protSerial = ProteinSerializer(data=protData)
        with self.assertRaises(ValueError):
            self.protSerial.is_valid(raise_exception=True)
        
    
class ProteinDomainSerializerTest(APITestCase):
    
    def setUp(self):
        self.prot =ProteinFactory.create(id=1)        
        self.dom = DomainFactory.create(id=1)
        self.protDom = ProteinDomains.objects.create(protein=self.prot,domain= self.dom)
        self.protDomSerial = ProteinDomainSerializer(instance=self.protDom)
        self.protDomFields = {}
        self.protDomFields['protein'] = model_to_dict(self.prot)
        self.protDomFields['domain'] = model_to_dict(self.dom)
    def tearDown(self):

        Protein.objects.all().delete()
        Pfam.objects.all().delete()
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        ProteinDomains.objects.all().delete()
        OrganismFactory.reset_sequence(0)
        ProteinFactory.reset_sequence(0)
        DomainFactory.reset_sequence(0)
        PfamFactory.reset_sequence(0)     
    
    def testProteinDomainValid(self):
        data = self.protDomSerial.data
        self.assertEqual(set(data.keys()),set(self.protDomFields))

    def testProteinDomainData(self):
        proteinDomainData = model_to_dict(self.protDom)
        self.protDomSerial = ProteinDomainSerializer(data=proteinDomainData)
        self.assertTrue(self.protDomSerial.is_valid(raise_exception=True))
    
    
#my code ends here 