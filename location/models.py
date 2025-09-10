from django.db import models
from django.contrib.auth.models import User
import os
from uuid import uuid4
from django.utils import timezone
from django.urls import reverse


# Vehicule Model
def vehicule_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}" 
    return os.path.join("vehicules", filename)


class Vehicule(models.Model):
    id_vehicule = models.AutoField(primary_key=True)
    photo = models.ImageField(upload_to=vehicule_upload_path, max_length=255, null=True, blank=True)
    immatriculation = models.CharField(max_length=50, unique=True)
    marque = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    kilometrageinitiale = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)


    def __str__(self):
        return f"{self.marque} {self.model} - {self.immatriculation}"


# Client Model


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    id_client = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    profession = models.CharField(max_length=100, blank=True)
    adresse = models.TextField(blank=True)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    email_confirmed = models.BooleanField(default=False)
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    confirmation_code_expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"

# Louer Model

class Louer(models.Model):
    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("VALIDE", "Validé"),
        ("REFUSE", "Refusé"),
    ]

    id_vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, blank=True)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True)
    date_debut = models.DateField()
    date_finlocation = models.DateField()
    kilometrageapreslocation = models.IntegerField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="EN_ATTENTE")
    motif = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.id_client} loue {self.id_vehicule} [{self.get_statut_display()}]"
    
  
