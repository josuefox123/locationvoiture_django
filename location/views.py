from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Vehicule, Client, Louer
from .forms import VehiculeForm, ClientForm, LouerForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.shortcuts import redirect

from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
import random
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash





# ===========================
# ACCUEIL
# ===========================
def accueil(request):
    today = now().date()
    vehicules = Vehicule.objects.exclude(
        louer__statut="valide",
        louer__date_debut__lte=today,
        louer__date_finlocation__gte=today
    )
    return render(request, "location/accueil.html", {"vehicules": vehicules})

# ===========================
# AUTHENTIFICATION AVEC CONFIRMATION PAR EMAIL
# ===========================


User = get_user_model()

# ----------- LOGIN -----------
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier') 
        password = request.POST.get('password')

        user = None
        try:
            # Tentative avec email
            user_obj = User.objects.get(email=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            # Tentative avec username
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            client = Client.objects.filter(user=user).first()

            # Vérifie confirmation email via Client
            if client and not client.email_confirmed:
                messages.error(request, "Vous devez confirmer votre adresse email avant de vous connecter.")
                return redirect("confirm_email", user_id=user.id)

            # OK -> login
            login(request, user)

            # Redirection selon rôle
            if user.is_superuser:
                return redirect('/monadmin/')
            elif user.is_staff:
                return redirect('monadmin')
            else:
                return redirect('accueil')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")

    return render(request, 'location/login.html')

# ----------- REGISTER -----------
def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('prenom')
        last_name = request.POST.get('nom')
        email = request.POST.get('email')
        phone = request.POST.get('telephone')
        profession = request.POST.get('profession')
        address = request.POST.get('address')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'location/register.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Un compte avec cet email existe déjà.')
            return render(request, 'location/register.html')

        # Création utilisateur inactif
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            is_active=False, 
        )

        # Génération du code
        code = str(random.randint(100000, 999999))

        # Création client lié avec confirmation en attente
        client = Client.objects.create(
            user=user,
            nom=last_name,
            prenom=first_name,
            email=email,
            telephone=phone,
            profession=profession,
            adresse=address,
            email_confirmed=False,
            confirmation_code=code,
            confirmation_code_expires_at=timezone.now() + timedelta(minutes=10),
        )

        # Envoi du mail
        send_mail(
            subject="Confirmation de votre compte",
            message=f"Bonjour {first_name},\n\nVotre code de confirmation est : {code}\nIl est valable 10 minutes.",
            from_email="noreply@tonsite.com",
            recipient_list=[email],
        )

        messages.info(request, "Un code de confirmation a été envoyé à votre email (valide 10 minutes).")
        return redirect("confirm_email", user_id=user.id)

    return render(request, 'location/register.html')


# ----------- CONFIRMER LE EMAIL -----------
def confirm_email(request, user_id):
    user = get_object_or_404(User, id=user_id)
    client = get_object_or_404(Client, user=user)

    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        if (
            client.confirmation_code == code
            and client.confirmation_code_expires_at
            and timezone.now() <= client.confirmation_code_expires_at
        ):
            user.is_active = True
            user.save()

            client.email_confirmed = True
            client.confirmation_code = None
            client.confirmation_code_expires_at = None
            client.save()

            messages.success(request, "Votre compte a été confirmé, Vous pouvez vous connecter.")
            return redirect("login")
        else:
            messages.error(request, "Code invalide ou expiré.")

    return render(request, "location/confirm_email.html", {"user": user})


# ----------- RENVOYER LE CODE -----------
def resend_code(request, user_id):
    user = get_object_or_404(User, id=user_id)
    client = get_object_or_404(Client, user=user)

    code = str(random.randint(100000, 999999))
    client.confirmation_code = code
    client.confirmation_code_expires_at = timezone.now() + timedelta(minutes=10)
    client.save()

    send_mail(
        subject="Nouveau code de confirmation",
        message=f"Votre nouveau code est : {code}\nIl est valable 10 minutes.",
        from_email="noreply@tonsite.com",
        recipient_list=[user.email],
    )

    messages.info(request, "Un nouveau code a été envoyé à votre email.")
    return redirect("confirm_email", user_id=user.id)


# ----------- DECONNECTION -----------
def logout_view(request):
    logout(request)
    return redirect('accueil')


# ===========================
# CRUD VEHICULES
# ===========================
def liste_vehicules(request):
    vehicules = Vehicule.objects.all()
    return render(request, "location/liste_vehicules.html", {"vehicules": vehicules})


def ajouter_vehicule(request):
    form = VehiculeForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect("vehicules")  
    return render(request, "location/formulaire.html", {"form": form})

def liste_vehicules(request):
    vehicules = Vehicule.objects.all()
    return render(request, "location/monadmin/vehicules.html", {"vehicules": vehicules})


def modifier_vehicule(request, id):
    vehicule = get_object_or_404(Vehicule, pk=id)
    form = VehiculeForm(request.POST or None, request.FILES or None, instance=vehicule)
    if form.is_valid():
        form.save()
        return redirect("vehicules")
    return render(request, "location/formulaire.html", {"form": form})


def supprimer_vehicule(request, id):
    vehicule = get_object_or_404(Vehicule, pk=id)
    vehicule.delete()
    return redirect("vehicules")


# ===========================
# CRUD CLIENTS
# ===========================
def liste_clients(request):
    clients = Client.objects.all()
    return render(request, "location/monadmin/clients.html", {"clients": clients})


def ajouter_client(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("clients")
    return render(request, "location/formulaire.html", {"form": form})


def modifier_client(request, id):
    client = get_object_or_404(Client, pk=id)
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        return redirect("clients")
    return render(request, "location/formulaire.html", {"form": form})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import Client
from .forms import ClientForm


@login_required
def modifier_mon_profil(request):
    client = get_object_or_404(Client, user=request.user)

    # Formulaire profil (on exclut les champs sensibles manuellement)
    form = ClientForm(request.POST or None, instance=client)
    for field in ["email_confirmed", "confirmation_code", "confirmation_code_expires_at"]:
        if field in form.fields:
            form.fields.pop(field)

    # Formulaire mot de passe
    password_form = PasswordChangeForm(user=request.user, data=request.POST or None)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # Formulaire de profil
        if form_type == "profile":
            if form.is_valid():
                client = form.save(commit=False)

                # Mise à jour aussi du User lié (prénom, nom, email)
                request.user.first_name = client.prenom
                request.user.last_name = client.nom
                request.user.email = client.email
                request.user.save()

                client.save()
                messages.success(request, "Profil mis à jour avec succès ✅")
                return redirect("modifier_mon_profil")
            else:
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

        # Formulaire de mot de passe
        elif form_type == "password":
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # évite la déconnexion
                messages.success(request, "Mot de passe modifié avec succès 🔑")
                return redirect("modifier_mon_profil")
            else:
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire de mot de passe.")

    return render(
        request,
        "location/modifier_mon_profil.html",
        {"form": form, "password_form": password_form},
    )




def supprimer_client(request, id):
    client = get_object_or_404(Client, id_client=id) 
    client.delete()
    return redirect('clients')


# ===========================
# CRUD LOCATIONS
# ===========================
def liste_locations(request):
    # Récupération des paramètres GET
    statut = request.GET.get("statut")
    recherche = request.GET.get("q")

    # Tri par défaut : les plus récents en premier
    locations = Louer.objects.all().order_by("-created_at")

    # Filtrer par statut si fourni
    if statut and statut != "ALL":
        locations = locations.filter(statut=statut)

    # Recherche par client (nom, prénom) ou véhicule (marque, modèle, immatriculation)
    if recherche:
        locations = locations.filter(
            Q(id_client__nom__icontains=recherche) |
            Q(id_client__prenom__icontains=recherche) |
            Q(id_vehicule__marque__icontains=recherche) |
            Q(id_vehicule__model__icontains=recherche) |
            Q(id_vehicule__immatriculation__icontains=recherche)
        )
        

    context = {
        "locations": locations,
        "statut_actuel": statut,
        "recherche": recherche,
    }
    return render(request, "location/monadmin/locations.html", context)


def ajouter_location(request):
    form = LouerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("locations")
    return render(request, "location/formulaire.html", {"form": form})


def modifier_location(request, id):
    location = get_object_or_404(Louer, pk=id)
    form = LouerForm(request.POST or None, instance=location)
    if form.is_valid():
        form.save()
        return redirect("locations")
    return render(request, "location/formulaire.html", {"form": form})
def supprimer_location(request, id):
    # request is required for Django views even if not used directly
    location = get_object_or_404(Louer, pk=id)
    location.delete()
    return redirect("locations")
    


# ===========================
# DEMANDE DE LOCATION (Client)
# ===========================
@login_required
def demande_location(request, id):
    vehicule = get_object_or_404(Vehicule, pk=id)

    # Vérification que l'utilisateur a bien un profil client
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, "Vous devez avoir un profil client pour faire une demande de location.")
        return redirect("accueil")

    if request.method == "POST":
        form = LouerForm(request.POST)

        if form.is_valid():
            location = form.save(commit=False)
            location.id_vehicule = vehicule
            location.id_client = client
            location.statut = "en_attente" 

            # Vérification de chevauchement avec des locations déjà validées
            conflits = Louer.objects.filter(
                id_vehicule=vehicule,
                statut="valide"
            ).filter(
                Q(date_debut__lte=location.date_finlocation) &
                Q(date_finlocation__gte=location.date_debut)
            )

            if conflits.exists():
                conflit = conflits.first()
                messages.error(
                    request,
                    f"⚠️ Ce véhicule n’est pas disponible : déjà loué du "
                    f"{conflit.date_debut} au {conflit.date_finlocation} "
                    f"par {conflit.id_client.prenom} {conflit.id_client.nom}."
                )
            else:
                location.statut = "en_attente"
                location.save()
                messages.success(
                    request,
                    "Votre demande de location a été enregistrée et est en attente de validation."
                )
                return redirect("mes_locations")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Erreur dans le champ {field}: {error}")

    else:
        # Pré-remplir certains champs
        form = LouerForm(initial={
            "id_vehicule": vehicule.pk,
            "id_client": client.pk,
            "kilometrageapreslocation": vehicule.kilometrageinitiale,
            "date_debut": datetime.now().date(),
            
        })


         # Envoyer un mail à l’admin
        subject = "Nouvelle demande de location"
        message = (
            f"Un client a fait une demande de location.\n\n"
            f"Client : {request.user.get_full_name()} ({request.user.email})\n"
            f"Véhicule : {vehicule.marque} {vehicule.model} - {vehicule.immatriculation}\n"
            # f"Statut : {location.statut}"
        )
        send_mail(
            subject,
            message,
            None,  # from email (par défaut DEFAULT_FROM_EMAIL)
            ["admin@autolocation.com"],  # mail de l’admin
            fail_silently=False,
        )

        send_mail(
            "Confirmation de votre demande",
            f"Bonjour {request.user.first_name},\n\n"
            f"Votre demande de location du véhicule {vehicule.marque} {vehicule.model} "
            f"a bien été enregistrée. Nous vous contacterons rapidement.\n\n"
            f"Merci,\nAutoLocation",
            None,
            [request.user.email],  # destinataire = client connecté
            fail_silently=False,
        )




    return render(request, "location/demande_location.html", {
        "form": form,
        "vehicule": vehicule,
    })

@login_required
def mes_locations(request):
    # Vérifier si l'utilisateur a un profil client associé
    try:
        # Récupérer le client associé à l'utilisateur
        client = Client.objects.get(user=request.user)
        # Filtrer les locations par le client (utilisation de id_client, pas client)
        locations = Louer.objects.filter(id_client=client)
        return render(request, 'location/mes_locations.html', {'locations': locations})
    except Client.DoesNotExist:
        messages.error(request, 'Vous devez avoir un profil client pour accéder à vos locations.')
        return redirect('accueil')
    



    # ===========================
# ADMIN PERSONNALISÉ
# ===========================



def admin_required(view_func):
    """Décorateur personnalisé pour les vues admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('accueil')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def monadmin(request):
   
    stats = {
        'total_vehicules': Vehicule.objects.count(),
        'total_clients': Client.objects.count(),
        'total_locations': Louer.objects.count(),
        'locations_actives': Louer.objects.filter(
            date_debut__lte=datetime.now(),
            date_finlocation__gte=datetime.now()
        ).count(),
    }
    
    locations_recentes = Louer.objects.filter(
        date_debut__gte=datetime.now() - timedelta(days=7)
    ).select_related('id_vehicule', 'id_client').order_by('-date_debut')[:5]
    
    vehicules_populaires = Vehicule.objects.annotate(
        nb_locations=Count('louer')
    ).order_by('-nb_locations')[:5]
    
    context = {
        'stats': stats,
        'locations_recentes': locations_recentes,
        'vehicules_populaires': vehicules_populaires,
    }
    
    return render(request, 'location/monadmin/dashboard.html', context)


@admin_required
def monadmin_vehicules(request):
    vehicules = Vehicule.objects.all().order_by('-created_at')
    return render(request, 'location/monadmin/vehicules.html', {'vehicules': vehicules})

@admin_required
def monadmin_clients(request):
    clients = Client.objects.all().select_related('user').order_by('-created_at')
    return render(request, 'location/monadmin/clients.html', {'clients': clients})

@admin_required
def monadmin_locations(request):
    locations = Louer.objects.all().select_related('id_vehicule', 'id_client').order_by('-created_at')
    return render(request, 'location/monadmin/locations.html', {'locations': locations})






# ===========================
# GESTION DES LOCATIONS (Admin)
# ===========================



def _conflits_valide(location: Louer):
    """Retourne les locations VALIDÉES du même véhicule qui chevauchent 'location' (exclut elle-même)."""
    return Louer.objects.filter(
        id_vehicule=location.id_vehicule,
        statut="VALIDE",
    ).exclude(pk=location.pk).filter(
        Q(date_debut__lte=location.date_finlocation) &
        Q(date_finlocation__gte=location.date_debut)
    )


def _envoyer_mail_changement_statut(loc: Louer):
    """Envoie un mail au client selon le statut de la location."""
    client = loc.id_client
    vehicule = loc.id_vehicule

    if loc.statut == "VALIDE":
        sujet = "Votre location a été validée "
        message = (
            f"Bonjour {client.prenom},\n\n"
            f"Votre demande de location du véhicule {vehicule.marque} {vehicule.model} "
            f"({vehicule.immatriculation}) du {loc.date_debut} au {loc.date_finlocation} "
            f"a été VALIDÉE.\n\n"
            f"Merci de votre confiance,\nAutoLocation"
        )

    elif loc.statut == "REFUSE":
        sujet = "Votre demande de location a été refusée "
        message = (
            f"Bonjour {client.prenom},\n\n"
            f"Nous sommes désolés, mais votre demande de location du véhicule "
            f"{vehicule.marque} {vehicule.model} ({vehicule.immatriculation}) "
            f"du {loc.date_debut} au {loc.date_finlocation} a été REFUSÉE.\n\n"
            f"Motif : {loc.motif if loc.motif else 'Non précisé'}\n\n"
            f"Merci de votre compréhension,\nAutoLocation"
        )
    else:
        return  

    send_mail(
        sujet,
        message,
        "noreply@autolocation.com",  # expéditeur
        [client.email],             # destinataire = client
        fail_silently=False,
    )


@staff_member_required
@require_POST
def valider_location(request, id):
    loc = get_object_or_404(Louer, pk=id)
    motif = (request.POST.get("motif") or "").strip()

    # blocage si chevauchement
    conflits = _conflits_valide(loc)
    if conflits.exists():
        c = conflits.first()
        messages.error(
            request,
            f"Impossible de valider : véhicule déjà loué du {c.date_debut} au {c.date_finlocation} "
            f"par {c.id_client.prenom} {c.id_client.nom}."
        )
        return redirect("locations") 

    loc.statut = "VALIDE"
    loc.motif = motif
    loc.save()

    _envoyer_mail_changement_statut(loc)

    messages.success(request, "La demande a été validée.")
    return redirect("locations")  


@staff_member_required
@require_POST
def refuser_location(request, id):
    loc = get_object_or_404(Louer, pk=id)
    motif = request.POST.get("motif", "").strip()

    loc.statut = "REFUSE"
    loc.motif = motif
    loc.save()

    _envoyer_mail_changement_statut(loc)

    messages.success(request, "La demande a été refusée.")
    return redirect("locations")  


@staff_member_required
@require_POST
def changer_statut_location(request, id):
    loc = get_object_or_404(Louer, pk=id)
    nouveau_statut = request.POST.get("statut")
    motif = (request.POST.get("motif") or "").strip()

    # validation du statut soumis
    valeurs_statuts = {choice[0] for choice in Louer.STATUT_CHOICES}
    if nouveau_statut not in valeurs_statuts:
        messages.error(request, "Statut invalide.")
        return redirect("locations")  

    # si on passe à VALIDE -> vérifier chevauchements
    if nouveau_statut == "VALIDE":
        conflits = _conflits_valide(loc)
        if conflits.exists():
            c = conflits.first()
            messages.error(
                request,
                f"Impossible de valider : véhicule déjà loué du {c.date_debut} au {c.date_finlocation} "
                f"par {c.id_client.prenom} {c.id_client.nom}."
            )
            return redirect("locations")   

    modification = (loc.statut != nouveau_statut) or (loc.motif or "") != motif
    loc.statut = nouveau_statut
    loc.motif = motif
    loc.save()

    if modification:
        _envoyer_mail_changement_statut(loc)
        messages.success(request, "Statut mis à jour.")
    else:
        messages.info(request, "Aucun changement à enregistrer.")

    return redirect("locations")   



# ===========================
# MESSAGERIE INTERNE


# @login_required
# def messages_view(request, user_id=None):
#     users = User.objects.exclude(id=request.user.id)

#     # Si admin → il voit tous les utilisateurs
#     if request.user.is_staff:
#         users = User.objects.exclude(id=request.user.id)
#     else:
#         # Si client → il voit seulement l’admin
#         users = User.objects.filter(is_staff=True)

#     selected_user = None
#     conversation = []

#     if user_id:
#         selected_user = User.objects.get(id=user_id)
#         conversation = Message.objects.filter(
#             sender__in=[request.user, selected_user],
#             receiver__in=[request.user, selected_user]
#         ).order_by("timestamp")

#         # marquer comme lus
#         Message.objects.filter(receiver=request.user, sender=selected_user).update(is_read=True)

#     if request.method == "POST":
#         content = request.POST.get("message")
#         if content and selected_user:
#             Message.objects.create(sender=request.user, receiver=selected_user, content=content)
#             return redirect("messages_view", user_id=selected_user.id)

#     return render(request, "location/messaging.html", {
#         "users": users,
#         "selected_user": selected_user,
#         "conversation": conversation,
#     })

# def chatbot_response(message):
#     message = message.lower()
#     if "prix" in message:
#         return "Nos prix dépendent du véhicule choisi, consultez la page Véhicules."
#     elif "disponible" in message:
#         return "Les véhicules disponibles sont affichés sur la page d'accueil."
#     elif "bonjour" in message:
#         return "Bonjour 👋, comment puis-je vous aider ?"
#     else:
#         return "Merci pour votre message, un administrateur va vous répondre."

