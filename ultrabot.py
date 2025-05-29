import json
import requests
import datetime

class ultraChatBot():    
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = 'https://api.ultramsg.com/instance122729/'
        self.token = 'rjasbdgk5ff8aoal'

   
    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatID, text):
        data = {"to" : chatID,
                "body" : text}  
        answer = self.send_requests('messages/chat', data)
        return answer

    def send_image(self, chatID):
        data = {"to" : chatID,
                "image" : "https://file-example.s3-accelerate.amazonaws.com/images/test.jpeg"}  
        answer = self.send_requests('messages/image', data)
        return answer

    def send_video(self, chatID):
        data = {"to" : chatID,
                "video" : "https://file-example.s3-accelerate.amazonaws.com/video/test.mp4"}  
        answer = self.send_requests('messages/video', data)
        return answer

    def send_audio(self, chatID):
        data = {"to" : chatID,
                "audio" : "https://file-example.s3-accelerate.amazonaws.com/audio/2.mp3"}  
        answer = self.send_requests('messages/audio', data)
        return answer

    def send_voice(self, chatID):
        data = {"to" : chatID,
                "audio" : "https://file-example.s3-accelerate.amazonaws.com/voice/oog_example.ogg"}  
        answer = self.send_requests('messages/voice', data)
        return answer

    def send_contact(self, chatID):
        data = {"to" : chatID,
                "contact" : "14000000001@c.us"}  
        answer = self.send_requests('messages/contact', data)
        return answer

    def time(self, chatID):
        t = datetime.datetime.now()
        time = t.strftime('%Y-%m-%d %H:%M:%S')
        return self.send_message(chatID, time)

    def welcome(self, chatID, noWelcome = False):
        welcome_string = ''
        if (noWelcome == False):
            welcome_string = """🎬 *Bienvenue chez SamAbonnement !*

Votre partenaire pour les abonnements premium 🌟

Choisissez une option :
1️⃣ Nos Services  
2️⃣ Tarifs & Formules
3️⃣ Aide & Support
4️⃣ Parler à un conseiller

Tapez le numéro de votre choix ou 'menu' 👆"""
        else:
            welcome_string = """❓ Commande non reconnue

Tapez une de ces commandes :
*hi* ou *menu* : Menu principal
*time* : Heure du serveur
*image* : Recevoir une image
*video* : Recevoir une vidéo
*audio* : Recevoir un audio
*voice* : Recevoir un message vocal
*contact* : Recevoir un contact

Ou tapez *menu* pour le menu complet"""
        return self.send_message(chatID, welcome_string)

    def Processingـincomingـmessages(self):
        if self.dict_messages != []:
            message = self.dict_messages
            
            # Vérification sécurisée du message
            if not message.get('body'):
                print("Message vide reçu")
                return 'EmptyMessage'
            
            # Nettoyer et séparer le message
            message_body = message['body'].strip()
            text = message_body.split()
            
            # Vérifier que le message n'est pas vide après nettoyage
            if not text:
                print("Message vide après nettoyage")
                return 'EmptyMessage'
            
            # Vérifier que ce n'est pas un message envoyé par nous
            if not message['fromMe']:
                chatID = message['from']
                command = text[0].lower()
                
                print(f"Message reçu de {chatID}: {message_body}")
                print(f"Commande: {command}")
                
                # Menu principal / Salutations
                if command in ['hi', 'salut', 'hello', 'bonjour', 'menu']:
                    return self.welcome(chatID)
                    
                # Commandes spécifiques
                elif command == 'time':
                    return self.time(chatID)
                elif command == 'image':
                    return self.send_image(chatID)
                elif command == 'video':
                    return self.send_video(chatID)
                elif command == 'audio':
                    return self.send_audio(chatID)
                elif command == 'voice':
                    return self.send_voice(chatID)
                elif command == 'contact':
                    return self.send_contact(chatID)
                    
                # Navigation par numéros
                elif command == '1':
                    services_msg = """📺 *Nos Services Premium :*

🔴 *Netflix* - Tous contenus HD/4K
🎬 *Amazon Prime Video* - Films & séries  
🏰 *Disney+* - Marvel, Star Wars, Pixar
📡 *IPTV* - +5000 chaînes mondiales

✅ Qualité garantie
✅ Plusieurs écrans simultanés  
✅ Support technique inclus

Tapez *2* pour les tarifs ou *menu* pour retourner"""
                    return self.send_message(chatID, services_msg)
                    
                elif command == '2':
                    tarifs_msg = """💰 *Nos Tarifs Compétitifs :*

📺 *Netflix Premium*
├ 1 mois : 5.000 CFA
├ 3 mois : 12.000 CFA
└ 6 mois : 20.000 CFA

🎬 *Prime Video*  
├ 1 mois : 3.000 CFA
└ 3 mois : 8.000 CFA

🏰 *Disney+*
├ 1 mois : 4.000 CFA
└ 3 mois : 10.000 CFA

📡 *IPTV Premium*
├ 1 mois : 6.000 CFA
└ 3 mois : 15.000 CFA

💳 *Paiement : Orange Money, Wave*

Tapez *4* pour commander ou *menu*"""
                    return self.send_message(chatID, tarifs_msg)
                    
                elif command == '3':
                    aide_msg = """🆘 *Centre d'Aide SamAbonnement*

Pour toute assistance :
📧 Email : support@samabonnement.com
📱 WhatsApp : +221 XX XXX XX XX
⏰ Horaires : Lun-Dim 9h-21h

Problèmes fréquents :
• Vérifiez votre connexion internet
• Redémarrez l'application  
• Vérifiez la date d'expiration

Tapez *4* pour parler à un conseiller
Tapez *menu* pour retourner"""
                    return self.send_message(chatID, aide_msg)
                    
                elif command == '4':
                    conseiller_msg = """👨‍💼 *Contact Conseiller*

Votre demande a été transmise !

⏰ *Délai de réponse :*
• Lun-Ven : 9h-18h (< 2h)  
• Sam-Dim : 10h-16h (< 4h)

📧 Contact direct :
support@samabonnement.com

Un conseiller vous contactera rapidement.

Tapez *menu* pour retourner"""
                    return self.send_message(chatID, conseiller_msg)
                    
                # Commande non reconnue
                else:
                    return self.welcome(chatID, True)
            else: 
                print("Message envoyé par nous, ignoré")
                return 'FromMe'
        else:
            print("Aucune donnée de message")
            return 'NoData'