from rest_framework import viewsets
from rest_framework import permissions
from .serializers import *
from .models import * 
from django.urls import reverse,reverse_lazy
from django.http import JsonResponse,HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.shortcuts import redirect

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import mixins

#my code starts here 
class CoverageDetail(generics.GenericAPIView, mixins.RetrieveModelMixin):
    """
    Retrieve the domain coverage for a given protein. That is the sum of the protein domain lengths (start-stop) divided by the length of the protein.

    [ref]: http://127.0.0.1:8000/api/coverage/[PROTEIN ID]
    """

    serializer_class = CoverageSerializer
    lookup_field = 'protein_id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        queryset = self.get_queryset()

        protein = queryset[0] if len(queryset) == 1 else None

        if protein is not None:
            domains = protein.domains.all()
            summary = 0

            for domain in domains:
                summary += (domain.stop - domain.start)

            coverage = summary / protein.length
            context['coverage'] = coverage
        return context

    def get_queryset(self):
        queryset = Protein.objects.all()
        try:
            if self.kwargs['protein_id'] is not None:
                queryset = queryset.filter(protein_id=self.kwargs['protein_id'])
        except KeyError:
            return None

        return queryset

    def get(self, request, *args, **kwargs):
        try:
            if self.kwargs['protein_id'] is not None:
                return self.retrieve(request, *args, **kwargs)
            else:
                return redirect('index')
        except Protein.DoesNotExist:
            return HttpResponseNotFound('No such protein')


class OrganismList(generics.ListAPIView):
    """
    List all organisms.
    """

    serializer_class = OrganismSerializer
    queryset = Organism.objects.all()


class OrganismPfamList(generics.ListAPIView):
    """
    List all domains in all the proteins for a given organism.

    [ref]: http://127.0.0.1:8000/api/pfams/[TAXA ID]
    """

    serializer_class = OrganismDomainSerializer
    lookup_field = 'taxa_id'

    def get_queryset(self):
        try:
            if self.kwargs['taxa_id'] is not None:
                organism = Organism.objects.get(taxa_id=self.kwargs['taxa_id'])
                organismPfams = organism.get_pfams()
            return organismPfams
        except KeyError:
            return HttpResponseNotFound

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProteinDetail(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    """
    Retrieve the protein sequence and all information about it.

    [ref]: http://127.0.0.1:8000/api/protein/[PROTEIN ID]

    Add a new record.

    [ref]: http://127.0.0.1:8000/api/protein/{PROTEIN DATA}
    """

    serializer_class = ProteinSerializer
    lookup_field = 'protein_id'
    queryset = Protein.objects.all()

    def get_object(self):
        protein = super().get_object()
        return protein

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def get(self, request, *args, **kwargs):
        try:
            if self.kwargs['protein_id'] is not None:
                return self.retrieve(request, *args, **kwargs)
        except KeyError:
            return redirect('protein_create')

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            proteinDomains = []
            domainData = [domain for domain in request.data['domains']]
            organismData = request.data['organism_id']
            request.data.pop('organism_id')
            organismSerial = OrganismSerializer(data=organismData)
            if organismSerial.is_valid(raise_exception=True):
                organismSerial.save()
                organism = organismSerial.data

            proteinData = request.data
            proteinData['taxonomy'] = organism
            proteinSerializer = ProteinSerializer(data=proteinData)
            if proteinSerializer.is_valid(raise_exception=True):
                proteinObj = proteinSerializer.save()

                for domain in domainData:
                    pfam = domain['pfam_id']
                    pfamSerial = PfamSerializer(data=pfam)

                    if pfamSerial.is_valid(raise_exception=True):
                        pfamSerial.save()

                    domain['pfam_id'] = pfam
                    domain['protein_id'] = proteinObj
                    domainSerial = DomainSerializer(data=domain)
                    if domainSerial.is_valid(raise_exception=True):
                        domainObj = domainSerial.save()

                    proteinDomains.append(ProteinDomains(protein=proteinObj, domain=domainObj))

                ProteinDomains.objects.bulk_create(proteinDomains)

                return Response(proteinSerializer.data, status=status.HTTP_201_CREATED)

            else:
                return Response(proteinSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            error = {}
            error['exception'] = Exception("error in creating protein")
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class ProteinCreate(generics.CreateAPIView):
    """
    Add a new record.

    [ref]: http://127.0.0.1:8000/api/protein/{protein_id:<protein_id>,sequence:<sequence>,taxonomy:{}}
    """

    serializer_class = ProteinSerializer


class ProteinList(generics.ListAPIView):
    """
    List all proteins.
    """

    serializer_class = ProteinSerializer
    queryset = Protein.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrganismProteinList(generics.ListAPIView):
    """
    List all proteins for a given organism.

    [ref]: http://127.0.0.1:8000/api/proteins/[TAXA ID]
    """

    serializer_class = OrganismProteinSerializer
    lookup_field = 'taxa_id'

    def get_queryset(self):
        queryset = Protein.objects.all()
        try:
            if self.kwargs['taxa_id'] is not None:
                org = Organism.objects.get(taxa_id=self.kwargs['taxa_id'])
                queryset = queryset.filter(organism_id=org)
        except KeyError:
            pass  # need to throw a 404 error here

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            context["taxa_id"] = self.kwargs['taxa_id']
            return context
        except KeyError:
            return HttpResponseNotFound("error")

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class DomainList(generics.ListAPIView):
    """
    List all domains.
    """

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class PfamList(generics.GenericAPIView, mixins.ListModelMixin):
    """
    List all Pfams.

    [ref]: http://127.0.0.1:8000/api/pfams/
    """

    serializer_class = PfamSerializer
    queryset = Pfam.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except KeyError:
            return self.retrieve(request, *args, **kwargs)


class PfamDetail(generics.GenericAPIView, mixins.RetrieveModelMixin):
    """
    Retrieve the domain and its description.

    [ref]: http://127.0.0.1:8000/api/pfam/[PFAM ID]
    """

    serializer_class = PfamSerializer
    lookup_field = 'domain_id'
    lookup_url_kwarg = 'pfam_id'

    def get_queryset(self):
        queryset = Pfam.objects.all()
        try:
            queryset.filter(domain_id=self.kwargs['pfam_id'])
        except KeyError:
            raise Exception

        return queryset

    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)

               
        
# my code ends here