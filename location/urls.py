from django.urls import path
from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    # Vehicule
   path("vehicules/", views.liste_vehicules, name="vehicules"), 
    path("vehicules/ajouter/", views.ajouter_vehicule, name="ajouter_vehicule"),
    path("vehicules/modifier/<int:id>/", views.modifier_vehicule, name="modifier_vehicule"),
    path("vehicules/supprimer/<int:id>/", views.supprimer_vehicule, name="supprimer_vehicule"),

    # Client
    path("clients/", views.liste_clients, name="clients"),
    path("clients/ajouter/", views.ajouter_client, name="ajouter_client"),
    path("clients/modifier/<int:id>/", views.modifier_client, name="modifier_client"),
    path("clients/supprimer/<int:id>/", views.supprimer_client, name="supprimer_client"),

    # Louer
    path("locations/", views.liste_locations, name="locations"),
    path("locations/ajouter/", views.ajouter_location, name="ajouter_location"),
    path("locations/modifier/<int:id>/", views.modifier_location, name="modifier_location"),
    path("locations/supprimer/<int:id>/", views.supprimer_location, name="supprimer_location"),
   path("locations/<int:id>/valider/", views.valider_location, name="valider_location"),
    path("locations/<int:id>/refuser/", views.refuser_location, name="refuser_location"),
    path("locations/<int:id>/changer-statut/", views.changer_statut_location, name="changer_statut_location"),

       # Authentification
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Confirmation email
    path("confirm_email/<int:user_id>/", views.confirm_email, name="confirm_email"),
    path("resend_code/<int:user_id>/", views.resend_code, name="resend_code"),
    
    # Demandes de location 
    path("demande-location/<int:id>/", views.demande_location, name="demande_location"),
    path("mes-locations/", views.mes_locations, name="mes_locations"),

    # Admin personnalisé
path("monadmin/", views.monadmin, name="monadmin"),
path("monadmin/vehicules/", views.monadmin_vehicules, name="monadmin_vehicules"),
path("monadmin/clients/", views.monadmin_clients, name="monadmin_clients"),
path("monadmin/locations/", views.monadmin_locations, name="monadmin_locations"),

# # Messages
# # pour tout le monde
# path("messages/", views.messages_view, name="messages_view"),
# path("messages/<int:user_id>/", views.messages_view, name="messages_view"),



]