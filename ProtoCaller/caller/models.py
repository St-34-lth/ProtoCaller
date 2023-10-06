from django.db import models
from django.core.exceptions import *
# Create your models here.
#my code starts here 
# Organism model represents an organism in the database
class Organism(models.Model):
    id = models.AutoField(primary_key=True)
    genus = models.CharField(max_length=127, null=False, blank=False)
    species = models.CharField(max_length=255, null=False, blank=False)
    clade = models.CharField(max_length=10, null=False, blank=False)
    taxa_id = models.IntegerField(blank=False, null=False)
    
    def clean(self):
        # Validate that the genus field is not empty or only whitespace
        if self.genus.isspace():
            raise ValidationError('genus cannot be empty')

        # Validate that the species field is not empty or only whitespace
        if self.species.isspace():
            raise ValidationError('species cannot be empty')
       
        # Validate that the clade field is not empty or only whitespace
        if self.clade.isspace():
            raise ValidationError('clade cannot be empty')
        
    def save(self, *args, **kwargs):
        # Run the clean() method to perform data validation before saving
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_pfams(self):
        try: 
            # Get the proteins associated with this organism
            proteins = Protein.objects.filter(organism_id=self)
            
            # Get the domains associated with the proteins
            domains = proteins.values('domains').all()
            
            # Get the Pfam objects associated with the domains
            pfam_objects = Pfam.objects.filter(domain__in=domains)
            
            return pfam_objects
        except Exception:
            raise Exception("error looking for pfams")
            
    def __str__(self):
        return f'taxa_id: {self.taxa_id} clade: {self.clade}, genus: {self.genus}, species: {self.species}'  

# Protein model represents a protein in the database
class Protein(models.Model):
    id = models.AutoField(primary_key=True)
    protein_id = models.CharField(blank=False, null=False, max_length=255)
    organism_id = models.ForeignKey(Organism, on_delete=models.CASCADE, null=True)  
    sequence = models.CharField(max_length=1024)
    length = models.IntegerField()
    domains = models.ManyToManyField('Domain', through='proteinDomains', related_name='domains')

    def save(self, *args, **kwargs):
        # Run the clean() method to perform data validation before saving
        self.full_clean()
        super().save(*args, **kwargs)
    
    def clean(self):
        # Validate that the protein_id field is not empty or only whitespace
        if not len(self.protein_id) > 0:  # Could perhaps check for a fixed number if the protein_id is a fixed sequence  
            raise ValidationError('protein_id cannot be empty')
        if self.protein_id.isspace():
            raise ValidationError('protein_id cannot be empty')
        
        # Validate that the length field is greater than 0
        if self.length <= 0:
            raise ValidationError('protein length cannot be less than or equal to 0')
        
        # Validate that the sequence field is not empty or only whitespace
        if self.sequence.isspace():
            raise ValidationError('protein sequence cannot be blank')
        if len(self.sequence) <= 0:
            raise ValidationError('protein sequence cannot be of size 0')
        
# Pfam model represents a Pfam entry in the database
class Pfam(models.Model):
    id = models.AutoField(primary_key=True)
    domain_id = models.CharField(max_length=255, blank=False, null=False)
    domain_description = models.CharField(max_length=255, null=False, blank=False)

    def save(self, *args, **kwargs):
        # Run the clean() method to perform data validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        # Validate that the domain_id field is not empty or only whitespace
        if self.domain_id.isspace():
            raise ValidationError("domain id empty")
  
        # Validate that the domain_description field is not empty or only whitespace
        if self.domain_description.isspace():
            raise ValidationError("domain description empty")

# Domain model represents a domain in the database
class Domain(models.Model):
    id = models.AutoField(primary_key=True)
    protein_id = models.ManyToManyField('Protein', through='proteinDomains', related_name='protein')
    pfam_id = models.ForeignKey(Pfam, on_delete=models.CASCADE, null=True)
    start = models.IntegerField(blank=False, null=False)
    stop = models.IntegerField(blank=False, null=False)
    description = models.CharField(max_length=255, blank=False, null=False, default=None)

    def save(self, *args, **kwargs):
        # Run the clean() method to perform data validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        # Validate that both start and stop values are greater than 0
        if not (self.start > 0 and self.stop > 0):
            raise ValidationError("start and stop values cannot be 0 or less than 0")
        
        # Validate that start value is less than stop value
        if not (self.start < self.stop):
            raise ValidationError("start cannot be greater than stop")

# ProteinDomains model represents the relationship between Protein and Domain models
class ProteinDomains(models.Model):
    protein = models.ForeignKey(Protein, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    
    
#my code ends here 