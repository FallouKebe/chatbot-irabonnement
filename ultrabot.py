import json
import requests
import datetime
import time
import random
import os

class ultraChatBot():    
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = 'https://api.ultramsg.com/instance114147/'
        self.token = 'e9gigjx981vwnnzh'
        
        # Fichier pour sauvegarder les sessions
        self.sessions_file = 'user_sessions.json'
        self.user_sessions = self.load_sessions()
        
        # Système de déduplication des messages
        self.processed_messages_file = 'processed_messages.json'
        self.processed_messages = self.load_processed_messages()
        
        # Messages anti-spam
        self.anti_spam_messages = [
            "Merci de patienter 🙏 Votre demande est en cours de traitement.",
            "Plus vous envoyez de messages, plus le temps de traitement est rallongé.",
            "Pas d'inquiétude, vous êtes bien pris en charge.",
            "Nous traitons les demandes par ordre d'arrivée.",
            "Veuillez patienter, nous analysons votre demande."
        ]
        
        # Messages d'avertissement menu
        self.menu_warning_messages = {
            "first": "Veuillez répondre à partir du menu que je vous affiche. Tapez simplement le numéro de votre choix (1, 2, 3, 4, 5 ou 6).",
            "second": "Merci de répondre à partir du menu en tapant le numéro correspondant à votre demande.",
            "final": "Ok, comme vous voulez. Si vous ne souhaitez pas coopérer, je reste en silence. Vous pourrez me reparler dans 2 heures ou taper 'menu' à tout moment."
        }

    def load_processed_messages(self):
        try:
            if os.path.exists(self.processed_messages_file):
                with open(self.processed_messages_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    current_time = time.time()
                    cleaned = {k: v for k, v in messages.items() if current_time - v < 86400}
                    if len(cleaned) != len(messages):
                        self.save_processed_messages(cleaned)
                    return cleaned
            return {}
        except Exception as e:
            print(f"❌ Erreur chargement messages traités: {e}")
            return {}

    def save_processed_messages(self, messages=None):
        try:
            if messages is None:
                messages = self.processed_messages
            with open(self.processed_messages_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f)
        except Exception as e:
            print(f"❌ Erreur sauvegarde messages traités: {e}")

    def is_message_already_processed(self, message):
        message_id = message.get('id', '')
        if message_id and message_id in self.processed_messages:
            print(f"🔄 Message déjà traité: {message_id}")
            return True
        return False

    def mark_message_as_processed(self, message):
        message_id = message.get('id', '')
        if message_id:
            self.processed_messages[message_id] = time.time()
            self.save_processed_messages()

    def load_sessions(self):
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
                    print(f"✅ Sessions chargées: {len(sessions)} utilisateurs")
                    return sessions
            else:
                print("📝 Nouveau fichier de sessions créé")
                return {}
        except Exception as e:
            print(f"❌ Erreur chargement sessions: {e}")
            return {}

    def save_sessions(self):
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_sessions, f, ensure_ascii=False, indent=2)
            print(f"💾 Sessions sauvegardées: {len(self.user_sessions)} utilisateurs")
        except Exception as e:
            print(f"❌ Erreur sauvegarde sessions: {e}")

    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatID, text):
        data = {"to": chatID, "body": text}  
        answer = self.send_requests('messages/chat', data)
        return answer

    def format_phone_number(self, whatsapp_id):
        if "@c.us" in whatsapp_id:
            clean_number = whatsapp_id.replace("@c.us", "")
            formatted_number = f"+{clean_number}"
            return formatted_number
        return whatsapp_id

    def send_to_sav(self, client_info, problem_type="general"):
        sav_destination = "120363366576958989@g.us"
        client_phone_raw = client_info.get('phone', 'Inconnu')
        client_phone_formatted = self.format_phone_number(client_phone_raw)
        
        if problem_type == "no_access":
            client_name = client_info.get('name', 'Non fourni')
            message = f"🚨 CLIENT SANS ACCES\n\nNumero: {client_phone_formatted}\nNom: {client_name}\nProbleme: Commande payee mais acces non recu\nCapture: Reçue\n\n⚡ A traiter rapidement SVP"
        elif problem_type == "technical":
            message = f"🔧 PROBLEME TECHNIQUE\n\nNumero: {client_phone_formatted}\nProbleme: Dysfonctionnement signale\nCapture: Reçue\n\n⚡ A resoudre rapidement SVP"
        elif problem_type == "conseiller_humain":
            message = f"📞 DEMANDE CONSEILLER\n\nNumero: {client_phone_formatted}\nDemande: Contact conseiller humain\n\n⚡ A traiter rapidement SVP"
        else:
            message = f"❓ DEMANDE CLIENT\n\nNumero: {client_phone_formatted}\nType: {problem_type}\n\n⚡ A traiter SVP"
        
        return self.send_message(sav_destination, message)

    def get_user_state(self, chatID):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"state": "menu", "messages": [], "data": {}}
        return self.user_sessions[chatID]["state"]

    def set_user_state(self, chatID, state):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"messages": [], "data": {}}
        self.user_sessions[chatID]["state"] = state
        self.save_sessions()

    def get_user_data(self, chatID, key, default=None):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"state": "menu", "messages": [], "data": {}}
        return self.user_sessions[chatID]["data"].get(key, default)

    def set_user_data(self, chatID, key, value):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"state": "menu", "messages": [], "data": {}}
        self.user_sessions[chatID]["data"][key] = value
        self.save_sessions()

    def activate_silence_mode(self, chatID, reason="sav_active"):
        self.set_user_state(chatID, "silence_mode")
        self.set_user_data(chatID, "silence_timestamp", time.time())
        self.set_user_data(chatID, "silence_reason", reason)
        print(f"🔇 SILENCE ACTIVÉ pour {chatID} - Raison: {reason}")

    def check_sav_command(self, message):
        """Détecte les commandes SAV simples"""
        message_body = message.get('body', '').strip()
        
        # Commande /sav - Met en silence le client de cette conversation
        if message_body == '/sav':
            client_number = message.get('to', '')  # Le destinataire = client à faire taire
            if client_number:
                print(f"🎯 COMMANDE SAV: /sav pour conversation avec {client_number}")
                return ('sav_silence', client_number)
        
        # Commande /reactiver - Réactive le client de cette conversation  
        elif message_body == '/reactiver':
            client_number = message.get('to', '')
            if client_number:
                print(f"🎯 COMMANDE SAV: /reactiver pour conversation avec {client_number}")
                return ('sav_reactivate', client_number)
                
        # Aide SAV
        elif message_body == '/aide':
            return ('help', None)
        
        return None

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
        service_lower = service.lower().strip()
        
        service_info = {
            "netflix": "🟥 Netflix :\n\n🎬 Netflix : À partir de 2500F, vous cotisez pour un profil personnel, utilisable sur un seul appareil.\n\nUne fois votre commande passée, vous recevez automatiquement vos accès par mail et WhatsApp.",
            "prime video": "🟦 Prime Video :\n\n🎥 Prime Video : Service de streaming Amazon avec films et séries exclusives.\n\nAccès direct après commande, compatible tous appareils.",
            "prime": "🟦 Prime Video :\n\n🎥 Prime Video : Service de streaming Amazon avec films et séries exclusives.\n\nAccès direct après commande, compatible tous appareils.",
            "disney+": "🟦 Disney+ :\n\n🎥 Disney+ : Disponible uniquement via VPN.\n\nNous vous fournissons un compte Disney+ + un compte VPN.\n\n1️⃣ Connectez d'abord le VPN aux 🇺🇸 USA (serveur Chicago)\n2️⃣ Ensuite, ouvrez l'application Disney+",
            "disney": "🟦 Disney+ :\n\n🎥 Disney+ : Disponible uniquement via VPN.\n\nNous vous fournissons un compte Disney+ + un compte VPN.\n\n1️⃣ Connectez d'abord le VPN aux 🇺🇸 USA (serveur Chicago)\n2️⃣ Ensuite, ouvrez l'application Disney+",
            "crunchyroll": "🟠 Crunchyroll :\n\n🎌 Crunchyroll : La plateforme #1 pour les animés et mangas.\n\nAccès premium à tous les contenus, sous-titres français disponibles.",
            "iptv": "🟩 IPTV :\n\n📺 IPTV : Nécessite un VPN ou une configuration DNS.\n\nVoici les étapes :\n1️⃣ Téléchargez une app OTT (ex : Smarters Player, Televizo, 9Xtream, Hot IPTV)\n2️⃣ Connectez un VPN (comme Surfshark) ou utilisez les DNS fournis après l'achat.",
            "surfshark vpn": "🔒 Surfshark VPN :\n\n🛡️ VPN premium pour sécuriser votre connexion et accéder aux contenus géo-bloqués.\n\nCompatible tous appareils, configuration simple.",
            "surfshark": "🔒 Surfshark VPN :\n\n🛡️ VPN premium pour sécuriser votre connexion et accéder aux contenus géo-bloqués.\n\nCompatible tous appareils, configuration simple.",
            "nordvpn": "🔵 NordVPN :\n\n🛡️ VPN haut de gamme pour protection et accès mondial.\n\nServeurs ultra-rapides, sécurité maximale.",
            "nord vpn": "🔵 NordVPN :\n\n🛡️ VPN haut de gamme pour protection et accès mondial.\n\nServeurs ultra-rapides, sécurité maximale.",
            "nord": "🔵 NordVPN :\n\n🛡️ VPN haut de gamme pour protection et accès mondial.\n\nServeurs ultra-rapides, sécurité maximale.",
            "carte xbox": "🟢 Carte Xbox :\n\n🎮 Cartes cadeaux Xbox pour acheter jeux et contenus.\n\nLivraison immédiate du code de la carte.",
            "xbox": "🟢 Carte Xbox :\n\n🎮 Cartes cadeaux Xbox pour acheter jeux et contenus.\n\nLivraison immédiate du code de la carte.",
            "carte psn": "🔵 Carte PSN :\n\n🎮 Cartes PlayStation Network pour le PlayStation Store.\n\nCodes livrés instantanément après achat.",
            "psn": "🔵 Carte PSN :\n\n🎮 Cartes PlayStation Network pour le PlayStation Store.\n\nCodes livrés instantanément après achat.",
            "hbo max": "🟣 HBO Max :\n\n🎭 HBO Max : Séries et films premium, contenu exclusif.\n\nAccès complet à la bibliothèque HBO.",
            "hbo": "🟣 HBO Max :\n\n🎭 HBO Max : Séries et films premium, contenu exclusif.\n\nAccès complet à la bibliothèque HBO."
        }
        
        if service_lower in service_info:
            return service_info[service_lower]
        
        for key, value in service_info.items():
            if service_lower in key or key in service_lower:
                return value
        
        return "❌ Service non trouvé. Veuillez taper exactement un nom de la liste."

    def is_image_message(self, message):
        return message.get('type') == 'image'

    def check_spam(self, chatID):
        current_time = time.time()
        
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"messages": [], "state": "menu", "data": {}}
        
        # Ajouter le message actuel
        self.user_sessions[chatID]["messages"].append(current_time)
        
        # Garder seulement les messages des 90 dernières secondes
        self.user_sessions[chatID]["messages"] = [
            msg_time for msg_time in self.user_sessions[chatID]["messages"] 
            if current_time - msg_time < 90
        ]
        
        message_count = len(self.user_sessions[chatID]["messages"])
        self.save_sessions()
        
        # Spam si 3+ messages en 90 secondes
        if message_count >= 3:
            return True
        return False

    def Processingـincomingـmessages(self):
        if self.dict_messages != []:
            message = self.dict_messages
            
            # Vérification de déduplication
            if self.is_message_already_processed(message):
                return 'AlreadyProcessed'
            
            # Marquer le message comme traité
            self.mark_message_as_processed(message)
            
            # Ignorer les messages du groupe SAV
            sav_group_id = "120363366576958989@g.us"
            if message.get('from') == sav_group_id:
                return 'SAVGroupIgnored'
            
            # Ignorer nos propres messages automatiques
            if message.get('fromMe'):
                return 'FromMe'
            
            # PRIORITÉ #1: Détecter les commandes SAV (/sav, /reactiver, /aide)
            sav_command = self.check_sav_command(message)
            if sav_command:
                command_type, client_number = sav_command
                
                if command_type == 'help':
                    help_text = """🤖 **COMMANDES SAV**

🔇 `/sav` - Met en silence le client de cette conversation
🔊 `/reactiver` - Réactive le client de cette conversation  
📖 `/aide` - Affiche cette aide

**Utilisation:**
• Tapez `/sav` directement dans la conversation client
• Le silence se désactive automatiquement après 2h
• Utilisez `/reactiver` pour réactiver avant les 2h"""
                    return self.send_message(message.get('from'), help_text)
                
                elif command_type == 'sav_silence':
                    self.activate_silence_mode(client_number, "sav_command")
                    print(f"✅ Client {client_number} mis en SILENCE par /sav")
                    # Pas de confirmation visible pour rester discret
                    return 'SAVSilenceActivated'
                
                elif command_type == 'sav_reactivate':
                    # Réactiver le client
                    self.set_user_state(client_number, "menu")
                    self.set_user_data(client_number, "silence_timestamp", None)
                    self.set_user_data(client_number, "silence_reason", None)
                    print(f"✅ Client {client_number} RÉACTIVÉ par /reactiver")
                    # Pas de confirmation visible pour rester discret
                    return 'SAVReactivated'
            
            # Traitement des images et messages
            if self.is_image_message(message):
                chatID = message['from']
                message_body = "[IMAGE]"
                message_lower = "image"
            elif not message.get('body'):
                return 'EmptyMessage'
            else:
                chatID = message['from']
                message_body = message['body'].strip()
                message_lower = message_body.lower()
                
            print(f"📱 Message reçu de {chatID}: {message_body}")
            
            current_state = self.get_user_state(chatID)
            print(f"🔄 État actuel: {current_state}")
            
            # PRIORITÉ #2: Vérifier l'expiration du silence (2h) avant tout traitement
            if self.check_silence_expiration(chatID):
                # Client réactivé automatiquement, traiter le message normalement
                current_state = self.get_user_state(chatID)  # Recharger l'état
                print(f"⏰ Client réactivé automatiquement, nouvel état: {current_state}")
            
            # PRIORITÉ #3: Vérifier si en mode silence
            if current_state == "silence_mode":
                silence_reason = self.get_user_data(chatID, "silence_reason", "unknown")
                print(f"🔇 UTILISATEUR EN SILENCE ({silence_reason}) - AUCUNE RÉPONSE")
                return "SilenceMode"
            
            # PRIORITÉ #4: Commande "menu"
            if message_lower in ['menu', 'accueil', 'retour']:
                self.set_user_state(chatID, "menu")
                # Reset spam counter
                if chatID in self.user_sessions:
                    self.user_sessions[chatID]["messages"] = []
                return self.send_message(chatID, self.get_main_menu())
            
            # PRIORITÉ #5: Réponses simples
            if message_lower in ['merci', 'thank you', 'thanks']:
                return self.send_message(chatID, "Je vous en prie 😊")
            
            if message_lower in ['bonjour', 'bonsoir', 'salut', 'hello', 'hi']:
                return self.send_message(chatID, self.get_main_menu())
            
            # PRIORITÉ #6: Navigation selon l'état
            if current_state == "menu":
                # Gestion des images non sollicitées
                if message_lower == "image":
                    return self.send_message(chatID, "Je n'ai pas besoin d'image pour le moment. 😊\n\nVeuillez choisir une option du menu en tapant le numéro (1, 2, 3, 4, 5 ou 6).")
                
                # Options du menu
                if message_lower == "1" or "comment ça fonctionne" in message_lower:
                    self.set_user_state(chatID, "services_selection")
                    return self.send_message(chatID, self.get_services_selection())
                    
                elif message_lower == "2" or "j'ai passé commande" in message_lower or "rien reçu" in message_lower:
                    return self.send_message(chatID, """Avant tout, veuillez vérifier votre boîte mail et le numéro WhatsApp que vous avez fourni lors de l'abonnement.

Les informations de connexion sont automatiquement envoyées à ces deux endroits.

Si vous ne trouvez rien, revenez ici et tapez '2' à nouveau.""")
                    
                elif message_lower == "3" or "problème avec mon compte" in message_lower:
                    self.set_user_state(chatID, "waiting_screenshot")
                    return self.send_message(chatID, """Désolé pour le désagrément 😥

Pour mieux comprendre votre problème, merci de nous envoyer une **capture d'écran** du message ou de l'erreur rencontrée.

Une fois reçu, nous le transmettrons au service technique.""")
                    
                elif message_lower == "4" or "réabonner" in message_lower or "reabonner" in message_lower:
                    return self.send_message(chatID, """Merci de vous rendre sur notre site : https://irabonnement.com

👉 Si votre abonnement est expiré, vous devrez commander un **nouveau compte**.""")
                    
                elif message_lower == "5" or "acheter un abonnement" in message_lower:
                    return self.send_message(chatID, """Parfait ✅

Vous pouvez commander directement sur : https://irabonnement.com

La livraison est automatique 📩""")
                    
                elif message_lower == "6" or "conseiller humain" in message_lower:
                    self.send_to_sav({"phone": chatID}, "conseiller_humain")
                    self.activate_silence_mode(chatID, "waiting_sav")
                    return self.send_message(chatID, """Votre demande a été transmise à notre service client.

⏳ Un conseiller va vous répondre dans un délai estimé de **moins de 40 minutes** (entre 10h et 22h).

Merci pour votre patience.""")
                
                # Si pas une réponse valide du menu, vérifier spam puis avertissement
                else:
                    if self.check_spam(chatID):
                        spam_response = random.choice(self.anti_spam_messages)
                        return self.send_message(chatID, spam_response)
                    
                    # Avertissement menu seulement si pas de spam
                    warnings = self.get_user_data(chatID, "menu_warnings", 0)
                    if warnings == 0:
                        self.set_user_data(chatID, "menu_warnings", 1)
                        return self.send_message(chatID, f"{self.menu_warning_messages['first']}\n\n{self.get_main_menu()}")
                    elif warnings == 1:
                        self.set_user_data(chatID, "menu_warnings", 2)
                        return self.send_message(chatID, f"{self.menu_warning_messages['second']}\n\n{self.get_main_menu()}")
                    else:
                        self.activate_silence_mode(chatID, "non_cooperative")
                        return self.send_message(chatID, self.menu_warning_messages['final'])
                        
            elif current_state == "services_selection":
                service_info = self.get_service_info(message_lower)
                if "❌ Service non trouvé" not in service_info:
                    self.set_user_state(chatID, "menu")
                    return self.send_message(chatID, service_info + "\n\nTapez 'menu' pour retourner au menu principal.")
                else:
                    return self.send_message(chatID, "❌ Service non trouvé. " + self.get_services_selection())
                    
            elif current_state == "waiting_screenshot":
                if message_lower != "image":
                    return self.send_message(chatID, "Nous attendons une **capture d'écran** de votre problème. Veuillez envoyer l'image.")
                
                self.send_to_sav({"phone": chatID, "problem": "Capture d'écran reçue"}, "technical")
                self.set_user_state(chatID, "transferred_to_sav")
                return self.send_message(chatID, """✅ Merci ! Nous avons bien reçu votre capture d'écran.

📤 Votre problème a été transmis à notre service technique.

⏳ Un agent vous répondra sous peu (délai moyen : moins de 40 minutes, entre 10h et 22h).""")
            
            # Message non reconnu
            self.set_user_state(chatID, "menu")
            return self.send_message(chatID, self.get_main_menu())
        
        return 'NoData'