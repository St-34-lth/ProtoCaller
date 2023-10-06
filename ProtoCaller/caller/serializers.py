from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
import json 

#my code starts here

# Serializer for the Coverage view 
class CoverageSerializer(serializers.ModelSerializer):
    coverage = serializers.SerializerMethodField()
    
    def get_coverage(self, obj):
        return self.context['coverage']
        
    class Meta:
        model = Protein    
        fields = ['coverage']
        
# Serializer for the Organism model
class OrganismSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Organism
        fields = ['id', 'taxa_id', 'clade', 'genus', 'species']
    
    def validate(self, data):
        # Validate that the taxa_id is greater than 0
        if int(data['taxa_id']) <= 0:
            raise ValidationError('taxa id cannot be 0')
      
        return data
    
    def create(self, validated_data):
        try: 
            # Get or create an Organism instance with the validated data
            organism = Organism.objects.get_or_create(**validated_data)
            return organism[0]
        except Exception:
            raise ValidationError("organism object could not be fetched/created")
        
# Serializer for the Pfam model
class PfamSerializer(serializers.ModelSerializer):
    
    class Meta: 
        model = Pfam
        fields = ['id', 'domain_id', 'domain_description']
    
    def create(self, validated_data):
        # Get or create a Pfam instance with the validated data
        pfam = Pfam.objects.get_or_create(**validated_data)[0]
        return pfam
    
# Serializer for the Domain model
class DomainSerializer(serializers.ModelSerializer):
        
    pfam_id = PfamSerializer()
    
    class Meta:
        model = Domain 
        fields = ['id', 'pfam_id', 'description', 'start', 'stop']
    
    def validate(self, data):  
        # Validate that the start value is less than the stop value
        if data['start'] > data['stop']:
            raise Exception("start greater than stop")
            
        # Validate that the start value is greater than 0
        if not data['start'] > 0: 
            raise Exception("start invalid")
        
        # Validate that the stop value is greater than 0
        if not data['stop'] > 0: 
            raise Exception("Stop invalid")
        
        return data     
    
    def create(self, validated_data):
        try:
            # Get the corresponding Pfam instance based on the domain_id
            pfam = Pfam.objects.get(domain_id=validated_data['pfam_id']['domain_id'])
            
            # Remove the 'pfam_id' field from the validated_data
            validated_data.pop('pfam_id')
            
            # Get or create a Domain instance with the Pfam and validated_data
            domain = Domain.objects.get_or_create(pfam_id=pfam, **validated_data)[0]
         
            return domain 
         
        except Pfam.DoesNotExist:
            raise Exception('Pfam does not exist')
         
# Serializer for the Protein model
class ProteinSerializer(serializers.ModelSerializer):
    taxonomy = OrganismSerializer(source='organism_id')
    domains = DomainSerializer(many=True)
    
    class Meta:
        model = Protein           
        fields = ['protein_id', 'sequence', 'taxonomy', 'length', 'domains']            
        read_only = ['id']
        
    def validate(self, data):
        # Validate that the length value is greater than or equal to 0
        if int(data['length']) < 0:
            raise ValueError("inappropriate length")
        
        return data 
    
    def get_domains(self, obj):
        # Get all domains associated with the Protein instance
        domains = obj.domains.all()
        
        # Serialize the domains using DomainSerializer
        serialized_domains = DomainSerializer(domains, many=True).data
       
        return serialized_domains 
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        
        # Remove the 'id' field from the 'taxonomy' object
        repr['taxonomy'].pop('id', None)

        # Remove the 'id' field from each 'pfam_id' object in the 'domains' list
        for domain in repr['domains']:
            domain.pop('id', None)
            domain['pfam_id'].pop('id', None)
        
        return repr
    
    def create(self, validated_data):
        # Create a new Protein instance using the validated data
        protein = Protein.objects.create(
            protein_id=validated_data['protein_id'],
            organism_id=Organism.objects.get(taxa_id=validated_data['organism_id']['taxa_id']),
            sequence=validated_data['sequence'],
            length=validated_data['length']
        )
                
        return protein 

# Serializer for the Organism and Protein models
class OrganismProteinSerializer(serializers.ModelSerializer):
                
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        
        try: 
            if self.context['taxa_id'] is not None: 
                repr['id'] = instance.id
                repr['protein_id'] = instance.protein_id
                return repr
              
        except KeyError:
            return Exception("inappropriate taxa_id") 

    class Meta:
        model = Protein    
        fields = ['protein_id', 'id']

# Serializer for the Organism and Domain models
class OrganismDomainSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Pfam
        fields = ['id', 'domain_id', 'domain_description']

# Serializer for the ProteinDomains model
class ProteinDomainSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProteinDomains
        exclude = ['id']
#my code ends here

