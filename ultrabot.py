import json
import requests
import datetime
import time
import random

class ultraChatBot():    
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = 'https://api.ultramsg.com/instance122729/'
        self.token = 'rjasbdgk5ff8aoal'
        
        # Gestion des sessions utilisateurs (états)
        self.user_sessions = {}
        
        # Messages anti-spam
        self.anti_spam_messages = [
            "Merci de patienter 🙏 Votre demande est en cours de traitement.",
            "Plus vous envoyez de messages, plus le temps de traitement est rallongé.",
            "Pas d'inquiétude, vous êtes bien pris en charge.",
            "Nous traitons les demandes par ordre d'arrivée.",
            "Veuillez patienter, nous analysons votre demande.",
            "Merci pour votre patience, nous vous répondons au plus vite.",
            "Votre demande est importante pour nous, merci de patienter.",
            "Nous prenons en compte votre message, merci de ne pas spammer.",
            "Patience svp, notre équipe traite votre demande.",
            "Merci d'éviter les messages répétés, nous vous traitons."
        ]

    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatID, text):
        data = {"to": chatID, "body": text}  
        answer = self.send_requests('messages/chat', data)
        return answer

    def send_to_sav(self, client_info, problem_type="general"):
        """Envoie les infos au SAV WhatsApp +221770184531"""
        sav_number = "+221770184531@c.us"
        
        if problem_type == "no_access":
            message = f"🚨 CLIENT SANS ACCÈS:\n\nClient: {client_info['phone']}\nNom: {client_info.get('name', 'Non fourni')}\nCapture paiement: {client_info.get('payment_proof', 'À recevoir')}\n\nÀ traiter rapidement !"
        elif problem_type == "technical":
            message = f"🔧 PROBLÈME TECHNIQUE:\n\nClient: {client_info['phone']}\nDescription: {client_info.get('problem', 'Capture à recevoir')}\n\nÀ résoudre !"
        else:
            message = f"📞 DEMANDE CLIENT:\n\nClient: {client_info['phone']}\nType: {problem_type}\n\nÀ traiter"
            
        return self.send_message(sav_number, message)

    def get_main_menu(self):
        return """Bienvenue chez irabonnement.com 👋

Je suis l'assistant automatique conçu par DakarDev 🤖

Je suis encore en phase d'apprentissage, merci de votre compréhension 🙏

Voici ce que je peux faire pour vous 👇 :

1️⃣ Comment ça fonctionne ?
2️⃣ J'ai passé commande, je n'ai rien reçu
3️⃣ J'ai un problème avec mon compte
4️⃣ Je veux me réabonner
5️⃣ Je veux acheter un abonnement
6️⃣ Contacter un conseiller humain"""

    def get_services_selection(self):
        return """Parfait 😊

Quel produit souhaitez-vous comprendre ? Répondez simplement avec le nom du produit parmi cette liste :

- Netflix
- Prime Video
- Disney+
- Crunchyroll
- IPTV
- Surfshark VPN
- NordVPN
- Carte Xbox
- Carte PSN
- HBO Max"""

    def get_service_info(self, service):
        service_info = {
            "netflix": """🟥 **Netflix :**

🎬 Netflix : À partir de 2500F, vous cotisez pour un profil personnel, utilisable sur un seul appareil.

Une fois votre commande passée, vous recevez automatiquement vos accès par mail et WhatsApp.""",

            "prime video": """🟦 **Prime Video :**

🎥 Prime Video : Service de streaming Amazon avec films et séries exclusives.

Accès direct après commande, compatible tous appareils.""",

            "disney+": """🟦 **Disney+ :**

🎥 Disney+ : Disponible uniquement via VPN.

Nous vous fournissons un compte Disney+ + un compte VPN.

1️⃣ Connectez d'abord le VPN aux 🇺🇸 USA (serveur Chicago)
2️⃣ Ensuite, ouvrez l'application Disney+""",

            "crunchyroll": """🟠 **Crunchyroll :**

🎌 Crunchyroll : La plateforme #1 pour les animés et mangas.

Accès premium à tous les contenus, sous-titres français disponibles.""",

            "iptv": """🟩 **IPTV :**

📺 IPTV : Nécessite un VPN ou une configuration DNS.

Voici les étapes :
1️⃣ Téléchargez une app OTT (ex : Smarters Player, Televizo, 9Xtream, Hot IPTV)
2️⃣ Connectez un VPN (comme Surfshark) ou utilisez les DNS fournis après l'achat.""",

            "surfshark vpn": """🔒 **Surfshark VPN :**

🛡️ VPN premium pour sécuriser votre connexion et accéder aux contenus géo-bloqués.

Compatible tous appareils, configuration simple.""",

            "nordvpn": """🔵 **NordVPN :**

🛡️ VPN haut de gamme pour protection et accès mondial.

Serveurs ultra-rapides, sécurité maximale.""",

            "carte xbox": """🟢 **Carte Xbox :**

🎮 Cartes cadeaux Xbox pour acheter jeux et contenus.

Livraison immédiate du code de la carte.""",

            "carte psn": """🔵 **Carte PSN :**

🎮 Cartes PlayStation Network pour le PlayStation Store.

Codes livrés instantanément après achat.""",

            "hbo max": """🟣 **HBO Max :**

🎭 HBO Max : Séries et films premium, contenu exclusif.

Accès complet à la bibliothèque HBO."""
        }
        
        return service_info.get(service.lower(), "Service non trouvé. Tapez un nom exact de la liste.")

    def handle_no_access_request(self, chatID):
        return """D'accord, nous allons vous aider ✅

Veuillez nous envoyer :
- Votre **nom et prénom** utilisés lors de la commande
- Une **capture d'écran de votre paiement**

Dès réception, nous transmettrons au service technique."""

    def handle_technical_problem(self, chatID):
        return """Désolé pour le désagrément 😥

Pour mieux comprendre votre problème, merci de nous envoyer une **capture d'écran** du message ou de l'erreur rencontrée.

Une fois reçu, nous le transmettrons au service technique."""

    def handle_bug_solutions(self, chatID):
        return """Désolé pour cela 😥

Voici quelques vérifications de base :

1️⃣ Désinstallez puis réinstallez l'application
2️⃣ Redémarrez votre appareil  
3️⃣ Assurez-vous d'avoir activé le VPN si nécessaire

👉 Si cela ne fonctionne toujours pas, merci de nous envoyer une **capture d'écran** de l'erreur.

Nous transmettrons à notre service technique."""

    def handle_resubscription(self, chatID):
        return """Merci de vous rendre sur notre site : https://irabonnement.com

👉 Si votre abonnement est expiré, vous devrez commander un **nouveau compte**."""

    def handle_new_purchase(self, chatID):
        return """Parfait ✅

Vous pouvez commander directement sur : https://irabonnement.com

La livraison est automatique 📩"""

    def handle_human_advisor(self, chatID):
        # Transmettre au SAV
        self.send_to_sav({"phone": chatID}, "conseiller_humain")
        
        return """Votre demande a été transmise à notre service client.

⏳ Un conseiller va vous répondre dans un délai estimé de **moins de 40 minutes** (entre 10h et 22h).

Merci pour votre patience."""

    def check_spam(self, chatID):
        """Vérifie si l'utilisateur spam (3+ messages en peu de temps)"""
        current_time = time.time()
        
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"messages": [], "state": "menu"}
        
        # Nettoyer les anciens messages (plus de 60 secondes)
        self.user_sessions[chatID]["messages"] = [
            msg_time for msg_time in self.user_sessions[chatID]["messages"] 
            if current_time - msg_time < 60
        ]
        
        # Ajouter le message actuel
        self.user_sessions[chatID]["messages"].append(current_time)
        
        # Vérifier le spam (3+ messages en 60 secondes)
        return len(self.user_sessions[chatID]["messages"]) >= 3

    def get_user_state(self, chatID):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"state": "menu", "messages": []}
        return self.user_sessions[chatID]["state"]

    def set_user_state(self, chatID, state):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"messages": []}
        self.user_sessions[chatID]["state"] = state

    def Processingـincomingـmessages(self):
        if self.dict_messages != []:
            message = self.dict_messages
            
            # Vérification sécurisée du message
            if not message.get('body'):
                print("Message vide reçu")
                return 'EmptyMessage'
            
            # Vérifier que ce n'est pas un message envoyé par nous
            if message['fromMe']:
                print("Message envoyé par nous, ignoré")
                return 'FromMe'
                
            chatID = message['from']
            message_body = message['body'].strip().lower()
            
            print(f"Message reçu de {chatID}: {message['body']}")
            
            # Vérifier le spam
            if self.check_spam(chatID):
                spam_response = random.choice(self.anti_spam_messages)
                return self.send_message(chatID, spam_response)
            
            # Récupérer l'état actuel de l'utilisateur
            current_state = self.get_user_state(chatID)
            
            # === GESTION DES SALUTATIONS ET RETOUR AU MENU ===
            if any(word in message_body for word in ['bonjour', 'bonsoir', 'salut', 'hello', 'hi', 'menu', 'accueil']):
                self.set_user_state(chatID, "menu")
                return self.send_message(chatID, self.get_main_menu())
            
            # === MESSAGES SPÉCIFIQUES ===
            if "je vous contacte depuis le site irabonnement" in message_body:
                self.set_user_state(chatID, "menu")
                return self.send_message(chatID, self.get_main_menu())
                
            if "j'ai une question" in message_body:
                self.set_user_state(chatID, "menu")
                return self.send_message(chatID, self.get_main_menu())
            
            # === POLITESSE ===
            if message_body in ['merci', 'thank you', 'thanks']:
                return self.send_message(chatID, "Je vous en prie 😊")
            
            # === GESTION DES BUGS ===
            if any(word in message_body for word in ['ça marche pas', 'marche pas', 'bug', 'ne fonctionne pas', 'problème connexion', 'je n\'arrive pas', 'pas connecter']):
                return self.send_message(chatID, self.handle_bug_solutions(chatID))
            
            # === NAVIGATION SELON L'ÉTAT ===
            if current_state == "menu":
                # Choix du menu principal
                if message_body == "1" or "comment ça fonctionne" in message_body:
                    self.set_user_state(chatID, "services_selection")
                    return self.send_message(chatID, self.get_services_selection())
                    
                elif message_body == "2" or "j'ai passé commande" in message_body or "rien reçu" in message_body:
                    self.set_user_state(chatID, "waiting_user_info")
                    return self.send_message(chatID, self.handle_no_access_request(chatID))
                    
                elif message_body == "3" or "problème avec mon compte" in message_body:
                    self.set_user_state(chatID, "waiting_screenshot")
                    return self.send_message(chatID, self.handle_technical_problem(chatID))
                    
                elif message_body == "4" or "réabonner" in message_body or "reabonner" in message_body:
                    return self.send_message(chatID, self.handle_resubscription(chatID))
                    
                elif message_body == "5" or "acheter un abonnement" in message_body or "nouvelle commande" in message_body:
                    return self.send_message(chatID, self.handle_new_purchase(chatID))
                    
                elif message_body == "6" or "conseiller humain" in message_body or "agent" in message_body:
                    self.set_user_state(chatID, "transferred_to_human")
                    return self.send_message(chatID, self.handle_human_advisor(chatID))
                    
            elif current_state == "services_selection":
                # L'utilisateur a choisi un service
                service_info = self.get_service_info(message_body)
                self.set_user_state(chatID, "menu")  # Retour au menu après info
                return self.send_message(chatID, service_info + "\n\nTapez 'menu' pour retourner au menu principal.")
                
            elif current_state == "waiting_user_info":
                # L'utilisateur envoie ses infos (nom + capture)
                self.send_to_sav({
                    "phone": chatID,
                    "name": message['body'],
                    "type": "no_access"
                }, "no_access")
                
                self.set_user_state(chatID, "transferred_to_sav")
                response = """Vos informations ont bien été transmises au service technique.

⏳ Un agent va vous répondre dans un délai estimé de **moins de 40 minutes** (entre 10h et 22h)."""
                return self.send_message(chatID, response)
                
            elif current_state == "waiting_screenshot":
                # L'utilisateur envoie une capture du problème
                self.send_to_sav({
                    "phone": chatID,
                    "problem": "Capture d'écran reçue",
                    "type": "technical"
                }, "technical")
                
                self.set_user_state(chatID, "transferred_to_sav")
                response = """Merci, nous avons transmis votre problème à notre service technique.

Un agent vous répondra sous peu (délai moyen : - de 40 minutes, entre 10h et 22h)."""
                return self.send_message(chatID, response)
                
            elif current_state == "transferred_to_sav" or current_state == "transferred_to_human":
                # L'utilisateur est déjà transféré, on ne répond plus
                return "UserTransferred"
            
            # === MESSAGE NON RECONNU ===
            return self.send_message(chatID, self.get_main_menu())
        
        return 'NoData'