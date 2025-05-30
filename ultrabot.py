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
        
        # SOLUTION PERSISTANCE : Fichier pour sauvegarder les sessions
        self.sessions_file = 'user_sessions.json'
        self.user_sessions = self.load_sessions()
        
        # NOUVEAU : Système de déduplication des messages
        self.processed_messages_file = 'processed_messages.json'
        self.processed_messages = self.load_processed_messages()
        
        # Messages anti-spam pour utilisateurs normaux
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
        
        # Messages anti-spam pour utilisateurs transférés (après 5+ messages)
        self.transferred_spam_messages = [
            "Plus vous envoyez de messages, plus le délai de traitement sera rallongé. ⏳ Merci de patienter.",
            "Votre demande est prise en charge, merci de patienter sans insister. 🙏 Nous allons régler votre problème.",
            "Chaque message supplémentaire retarde le traitement de votre dossier. Patience svp.",
            "Notre équipe vous contactera, inutile d'envoyer plus de messages. Nous réglons votre problème.",
            "Patience svp, votre insistance rallonge les délais de réponse. Nous vous aiderons."
        ]

    def load_processed_messages(self):
        """Charge la liste des messages déjà traités"""
        try:
            if os.path.exists(self.processed_messages_file):
                with open(self.processed_messages_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    # Nettoyer les anciens messages (plus de 24h)
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
        """Sauvegarde la liste des messages traités"""
        try:
            if messages is None:
                messages = self.processed_messages
            with open(self.processed_messages_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f)
        except Exception as e:
            print(f"❌ Erreur sauvegarde messages traités: {e}")

    def is_message_already_processed(self, message):
        """Vérifie si ce message a déjà été traité"""
        message_id = message.get('id', '')
        if message_id and message_id in self.processed_messages:
            print(f"🔄 Message déjà traité: {message_id}")
            return True
        return False

    def mark_message_as_processed(self, message):
        """Marque un message comme traité"""
        message_id = message.get('id', '')
        if message_id:
            self.processed_messages[message_id] = time.time()
            self.save_processed_messages()
            print(f"✅ Message marqué comme traité: {message_id}")

    def load_sessions(self):
        """Charge les sessions depuis le fichier JSON"""
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
        """Charge les sessions depuis le fichier JSON"""
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
        """Sauvegarde les sessions dans le fichier JSON"""
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
        """NOUVEAU: Formate le numéro WhatsApp pour le SAV"""
        # Supprimer @c.us et ajouter +
        if "@c.us" in whatsapp_id:
            clean_number = whatsapp_id.replace("@c.us", "")
            formatted_number = f"+{clean_number}"
            print(f"📱 Numéro formaté: {whatsapp_id} → {formatted_number}")
            return formatted_number
        return whatsapp_id

    def send_to_sav(self, client_info, problem_type="general"):
        """Envoie une alerte au SAV WhatsApp (individuel ou groupe)"""
        # # OPTION 1: Envoyer à un numéro individuel
        # sav_destination = "+221770184531@c.us"
        
        # OPTION 2: Envoyer à un groupe WhatsApp (recommandé)
        # Remplacez par l'ID de votre groupe SAV
        sav_destination = "120363366576958989@g.us"  # Format: 1234567890-1234567890@g.us
        
        # OPTION 3: Envoyer aux deux (groupe + responsable)
        # sav_destination = ["+221770184531@c.us", "VOTRE_GROUPE_SAV_ID@g.us"]
        client_phone_raw = client_info.get('phone', 'Inconnu')
        
        # NOUVEAU: Formater le numéro pour le SAV
        client_phone_formatted = self.format_phone_number(client_phone_raw)
        
        # Messages clairs pour le SAV
        if problem_type == "no_access":
            client_name = client_info.get('name', 'Non fourni')
            message = f"🚨 CLIENT SANS ACCES\n\nNumero: {client_phone_formatted}\nNom: {client_name}\nProbleme: Commande payee mais acces non recu\nCapture: Reçue\n\n⚡ A traiter rapidement SVP"
            
        elif problem_type == "technical":
            message = f"🔧 PROBLEME TECHNIQUE\n\nNumero: {client_phone_formatted}\nProbleme: Dysfonctionnement signale\nCapture: Reçue\n\n⚡ A resoudre rapidement SVP"
            
        elif problem_type == "conseiller_humain":
            message = f"📞 DEMANDE CONSEILLER\n\nNumero: {client_phone_formatted}\nDemande: Contact conseiller humain\n\n⚡ A traiter rapidement SVP"
            
        else:
            message = f"❓ DEMANDE CLIENT\n\nNumero: {client_phone_formatted}\nType: {problem_type}\n\n⚡ A traiter SVP"
        
        # NOUVEAU: Envoyer à une ou plusieurs destinations
        if isinstance(sav_destination, list):
            # Envoyer à plusieurs destinations
            results = []
            for destination in sav_destination:
                print(f"📤 Envoi alerte SAV vers {destination}: {message}")
                result = self.send_message(destination, message)
                results.append(result)
            return results
        else:
            # Envoyer à une seule destination
            print(f"📤 Envoi alerte SAV vers {sav_destination}: {message}")
            return self.send_message(sav_destination, message)

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
        """Reconnaissance des noms de services"""
        service_lower = service.lower().strip()
        
        # Dictionnaire avec toutes les variantes possibles
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
        
        # Recherche exacte d'abord
        if service_lower in service_info:
            return service_info[service_lower]
        
        # Recherche partielle si pas trouvé
        for key, value in service_info.items():
            if service_lower in key or key in service_lower:
                return value
        
        return "❌ Service non trouvé. Veuillez taper exactement un nom de la liste."

    def handle_no_access_request(self, chatID):
        return """D'accord, nous allons vous aider ✅

Veuillez d'abord nous envoyer votre **nom et prénom** utilisés lors de la commande.

Ensuite, nous vous demanderons la capture d'écran de votre paiement."""

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

    def is_in_active_flow(self, chatID):
        """NOUVEAU: Vérifie si l'utilisateur est dans un flux actif (pour éviter le spam)"""
        state = self.get_user_state(chatID)
        active_states = ["waiting_name", "waiting_payment_screenshot", "waiting_screenshot", "services_selection"]
        return state in active_states

    def check_spam(self, chatID):
        """CORRECTION FINALE: Spam check qui fonctionne vraiment"""
        current_time = time.time()
        
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"messages": [], "state": "menu", "data": {}}
        
        current_state = self.get_user_state(chatID)
        
        # IMPORTANT: Si utilisateur dans un flux actif, PAS de spam check
        if self.is_in_active_flow(chatID):
            print(f"🔄 Utilisateur {chatID} dans flux actif - pas de spam check")
            return False
        
        # CORRECTION: Toujours ajouter le message actuel AVANT le nettoyage
        self.user_sessions[chatID]["messages"].append(current_time)
        
        # Si utilisateur transféré : spam après 3+ messages en 2 minutes
        if current_state in ["transferred_to_sav", "transferred_to_human"]:
            # Nettoyer les anciens messages (plus de 120 secondes = 2 minutes)
            self.user_sessions[chatID]["messages"] = [
                msg_time for msg_time in self.user_sessions[chatID]["messages"] 
                if current_time - msg_time < 120
            ]
            
            message_count = len(self.user_sessions[chatID]["messages"])
            print(f"🔍 Spam check transféré - Messages: {message_count}")
            
            # CORRECTION: Sauvegarder après modification
            self.save_sessions()
            
            if message_count >= 6:
                return "transferred_total_silence"  # Silence total après 6+ messages
            elif message_count >= 3:
                return "transferred_spam"  # Message anti-spam après 3+ messages
            else:
                return "transferred_silent"  # Silence simple < 3 messages
        
        # Utilisateur normal : spam = 3+ messages en 90 secondes
        else:
            # Nettoyer les anciens messages (plus de 90 secondes)
            self.user_sessions[chatID]["messages"] = [
                msg_time for msg_time in self.user_sessions[chatID]["messages"] 
                if current_time - msg_time < 90
            ]
            
            message_count = len(self.user_sessions[chatID]["messages"])
            print(f"🔍 Spam check normal - Messages: {message_count}")
            
            # CORRECTION: Sauvegarder après modification
            self.save_sessions()
            
            if message_count >= 3:
                return "normal_spam"
        
        return False

    def get_user_state(self, chatID):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"state": "menu", "messages": [], "data": {}}
        return self.user_sessions[chatID]["state"]

    def set_user_state(self, chatID, state):
        if chatID not in self.user_sessions:
            self.user_sessions[chatID] = {"messages": [], "data": {}}
        self.user_sessions[chatID]["state"] = state
        print(f"🔄 État changé pour {chatID}: {state}")
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

    def is_image_message(self, message):
        """Détecte si le message est une image"""
        return message.get('type') == 'image'

    def Processingـincomingـmessages(self):
        if self.dict_messages != []:
            message = self.dict_messages
            
            # NOUVEAU : Vérification de déduplication
            if self.is_message_already_processed(message):
                return 'AlreadyProcessed'
            
            # Marquer le message comme traité immédiatement
            self.mark_message_as_processed(message)
            
            # Vérifier les images au lieu de "message vide"
            if self.is_image_message(message):
                print(f"📸 Image reçue de {message['from']}")
                chatID = message['from']
                message_body = "[IMAGE]"
                message_lower = "image"
            elif not message.get('body'):
                print("Message vide reçu (pas une image)")
                return 'EmptyMessage'
            else:
                chatID = message['from']
                message_body = message['body'].strip()
                message_lower = message_body.lower()
            
            # Vérifier que ce n'est pas un message envoyé par nous
            if message['fromMe']:
                print("Message envoyé par nous, ignoré")
                return 'FromMe'
                
            print(f"📱 Message reçu de {chatID}: {message_body}")
            print(f"🔄 État actuel: {self.get_user_state(chatID)}")
            
            # === PRIORITÉ ABSOLUE #1 : COMMANDES DE RETOUR AU MENU ===
            if message_lower in ['menu', 'accueil', 'retour', 'retourner au menu']:
                print(f"🔄 RETOUR AU MENU FORCÉ")
                self.set_user_state(chatID, "menu")
                # Nettoyer les messages pour éviter le spam check
                if chatID in self.user_sessions:
                    self.user_sessions[chatID]["messages"] = []
                return self.send_message(chatID, self.get_main_menu())
            
            # === PRIORITÉ #2 : GESTION DU SPAM (après menu) ===
            current_state = self.get_user_state(chatID)
            spam_status = self.check_spam(chatID)
            
            if spam_status == "transferred_total_silence":
                print(f"🔇 Utilisateur {chatID} transféré - silence total (8+ messages)")
                return "TransferredTotalSilence"
                
            elif spam_status == "transferred_spam":
                response = random.choice(self.transferred_spam_messages)
                print(f"⚠️ Utilisateur {chatID} transféré - message anti-spam")
                return self.send_message(chatID, response)
                
            elif spam_status == "transferred_silent":
                print(f"🔇 Utilisateur {chatID} transféré - silence simple")
                return "TransferredSilent"
                
            elif spam_status == "normal_spam":
                spam_response = random.choice(self.anti_spam_messages)
                print(f"⚠️ Utilisateur {chatID} normal - anti-spam")
                return self.send_message(chatID, spam_response)
            
            # === PRIORITÉ #3 : SALUTATIONS ET MESSAGES SPÉCIAUX ===
            if current_state == "menu":
                # Gestion des salutations
                if any(word in message_lower for word in ['bonjour', 'bonsoir', 'salut', 'hello', 'hi']):
                    print(f"👋 Salutation détectée: {message_lower}")
                    return self.send_message(chatID, self.get_main_menu())
                
                # Messages spécifiques du site
                if "je vous contacte depuis le site irabonnement" in message_lower:
                    print(f"🌐 Message site détecté")
                    return self.send_message(chatID, self.get_main_menu())
                    
                if "j'ai une question" in message_lower:
                    print(f"❓ Question générique détectée")
                    return self.send_message(chatID, self.get_main_menu())
            
            # === PRIORITÉ #4 : POLITESSE (sauf si transféré) ===
            if current_state not in ["transferred_to_sav", "transferred_to_human"]:
                if message_lower in ['merci', 'thank you', 'thanks']:
                    return self.send_message(chatID, "Je vous en prie 😊")
            
            # === PRIORITÉ #5 : GESTION DES BUGS (sauf si transféré) ===
            if current_state not in ["transferred_to_sav", "transferred_to_human"]:
                if any(word in message_lower for word in ['ça marche pas', 'marche pas', 'bug', 'ne fonctionne pas', 'problème connexion', 'je n\'arrive pas', 'pas connecter']):
                    self.set_user_state(chatID, "menu")
                    return self.send_message(chatID, self.handle_bug_solutions(chatID))
            
            # === NAVIGATION SELON L'ÉTAT ===
            if current_state == "menu":
                print(f"🏠 Traitement menu pour: {message_lower}")
                
                # CORRECTION: Gestion des images non sollicitées en état menu
                if message_lower == "image":
                    return self.send_message(chatID, "Je n'ai pas besoin d'image pour le moment. 😊\n\nVeuillez choisir une option du menu en tapant le numéro (1, 2, 3, 4, 5 ou 6).")
                
                if message_lower == "1" or "comment ça fonctionne" in message_lower:
                    self.set_user_state(chatID, "services_selection")
                    return self.send_message(chatID, self.get_services_selection())
                    
                elif message_lower == "2" or "j'ai passé commande" in message_lower or "rien reçu" in message_lower:
                    self.set_user_state(chatID, "waiting_name")
                    return self.send_message(chatID, self.handle_no_access_request(chatID))
                    
                elif message_lower == "3" or "problème avec mon compte" in message_lower:
                    self.set_user_state(chatID, "waiting_screenshot")
                    return self.send_message(chatID, self.handle_technical_problem(chatID))
                    
                elif message_lower == "4" or "réabonner" in message_lower or "reabonner" in message_lower:
                    # CORRECTION: L'option 4 reste en état menu et ne demande jamais d'image
                    return self.send_message(chatID, self.handle_resubscription(chatID))
                    
                elif message_lower == "5" or "acheter un abonnement" in message_lower or "nouvelle commande" in message_lower:
                    return self.send_message(chatID, self.handle_new_purchase(chatID))
                    
                elif message_lower == "6" or "conseiller humain" in message_lower or "agent" in message_lower:
                    self.set_user_state(chatID, "transferred_to_human")
                    return self.send_message(chatID, self.handle_human_advisor(chatID))
                    
            elif current_state == "services_selection":
                # L'utilisateur a choisi un service
                print(f"🎯 Recherche service pour: '{message_lower}'")
                service_info = self.get_service_info(message_lower)
                
                if "❌ Service non trouvé" not in service_info:
                    print(f"✅ Service trouvé, envoi info")
                    self.set_user_state(chatID, "menu")
                    return self.send_message(chatID, service_info + "\n\nTapez 'menu' pour retourner au menu principal.")
                else:
                    print(f"❌ Service non trouvé")
                    return self.send_message(chatID, "❌ Service non trouvé. " + self.get_services_selection())
                
            elif current_state == "waiting_name":
                # CORRECTION MAJEURE OPTION 2 : L'utilisateur envoie son nom
                if message_lower == "image":
                    return self.send_message(chatID, "Merci pour l'image, mais nous avons d'abord besoin de votre **nom et prénom** en texte.")
                
                print(f"👤 Nom reçu: {message_body}")
                self.set_user_data(chatID, "customer_name", message_body)
                self.set_user_state(chatID, "waiting_payment_screenshot")
                
                return self.send_message(chatID, f"""Merci {message_body} ✅

Maintenant, veuillez envoyer la **capture d'écran de votre paiement**.

Dès réception, nous transmettrons le tout au service technique.""")
                
            elif current_state == "waiting_payment_screenshot":
                # CORRECTION MAJEURE OPTION 2 : L'utilisateur envoie la capture de paiement
                if message_lower != "image":
                    return self.send_message(chatID, "Nous attendons la **capture d'écran de votre paiement**. Veuillez envoyer l'image.")
                
                print(f"💳 Capture paiement reçue de: {chatID}")
                customer_name = self.get_user_data(chatID, "customer_name", "Non fourni")
                
                # Envoyer au SAV
                self.send_to_sav({
                    "phone": chatID,
                    "name": customer_name,
                    "payment_proof": "Capture de paiement reçue",
                    "type": "no_access"
                }, "no_access")
                
                self.set_user_state(chatID, "transferred_to_sav")
                response = f"""✅ Parfait ! Nous avons bien reçu vos informations :

👤 Nom : {customer_name}
💳 Capture de paiement : Reçue

📤 Votre dossier a été transmis à notre service technique.

⏳ Un agent va vous répondre dans un délai estimé de moins de 40 minutes (entre 10h et 22h).

Merci pour votre patience."""
                return self.send_message(chatID, response)
                
            elif current_state == "waiting_screenshot":
                # CORRECTION OPTION 3 : L'utilisateur envoie une capture du problème
                if message_lower != "image":
                    return self.send_message(chatID, "Nous attendons une **capture d'écran** de votre problème. Veuillez envoyer l'image.")
                
                print(f"📸 Capture technique reçue de: {chatID}")
                
                # Envoyer au SAV avec numéro du client
                self.send_to_sav({
                    "phone": chatID,
                    "problem": "Capture d'écran du problème reçue",
                    "type": "technical"
                }, "technical")
                
                self.set_user_state(chatID, "transferred_to_sav")
                response = """✅ Merci ! Nous avons bien reçu votre capture d'écran.

📤 Votre problème a été transmis à notre service technique.

⏳ Un agent vous répondra sous peu (délai moyen : moins de 40 minutes, entre 10h et 22h).

Nous allons régler votre problème rapidement."""
                return self.send_message(chatID, response)
                
            elif current_state == "transferred_to_sav" or current_state == "transferred_to_human":
                # L'utilisateur est déjà transféré : silence (géré par le spam ci-dessus)
                print(f"🔇 Utilisateur {chatID} transféré - traité par la gestion du spam")
                return "TransferredHandledBySpam"
            
            # === MESSAGE NON RECONNU (sauf si transféré) ===
            if current_state not in ["transferred_to_sav", "transferred_to_human"]:
                print(f"❓ Message non reconnu, retour au menu")
                self.set_user_state(chatID, "menu")
                return self.send_message(chatID, self.get_main_menu())
            
            # Si transféré et message non reconnu : déjà géré par le spam
            return "TransferredSilent"
        
        return 'NoData'