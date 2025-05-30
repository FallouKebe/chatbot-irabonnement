from flask import Flask, request, jsonify
from ultrabot import ultraChatBot
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    """Route principale pour webhooks UltraMsg - irabonnement.com"""
    
    if request.method == 'GET':
        return """
        <div style="font-family: Arial; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
            <div style="max-width: 600px; margin: 0 auto; text-align: center;">
                <h1>🤖 Chatbot irabonnement.com</h1>
                <p style="font-size: 18px;">✅ Assistant automatique conçu par DakarDev</p>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>📱 Status: <span style="color: #4CAF50;">EN LIGNE</span></h3>
                    <p>🔗 Webhook configuré et actif</p>
                    <p>⚡ Prêt à recevoir les messages WhatsApp</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <h4>🎯 Fonctionnalités du bot:</h4>
                    <p>• Menu interactif 6 options</p>
                    <p>• Descriptions produits détaillées</p>
                    <p>• Gestion SAV automatique</p>
                    <p>• Anti-spam intelligent</p>
                    <p>• Transfert vers conseillers humains</p>
                </div>
                <p style="margin-top: 30px; opacity: 0.8;">Powered by UltraMsg API</p>
            </div>
        </div>
        """
    
    if request.method == 'POST':
        try:
            print(f"📨 Webhook irabonnement reçu: {request.json}")
            
            # Vérifier les données
            if request.json and 'data' in request.json:
                bot = ultraChatBot(request.json)
                response = bot.Processingـincomingـmessages()
                print(f"🤖 Bot irabonnement - Réponse: {response}")
                return jsonify({'status': 'success', 'response': response, 'bot': 'irabonnement'})
            else:
                print("❌ Données webhook invalides")
                return jsonify({'status': 'error', 'message': 'Invalid webhook data'})
                
        except Exception as e:
            print(f"❌ Erreur webhook irabonnement: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Route webhook alternative pour irabonnement.com"""
    if request.method == 'GET':
        return jsonify({
            'status': 'webhook_active',
            'bot': 'irabonnement.com',
            'developer': 'DakarDev',
            'features': [
                'Menu interactif 6 options',
                'Descriptions produits détaillées', 
                'Gestion SAV automatique',
                'Anti-spam intelligent',
                'Transfert conseillers humains'
            ],
            'timestamp': '2025-05-29',
            'ready': True
        })
    
    return home()

@app.route('/test')
def test():
    """Page de test et debug pour irabonnement.com"""
    return jsonify({
        'chatbot': 'irabonnement.com',
        'developer': 'DakarDev',
        'status': 'ACTIF',
        'webhook_routes': ['/', '/webhook'],
        'ultramsg_configured': True,
        'instance': '122729',
        'sav_number': '+221770184531',
        'features': {
            'menu_options': 6,
            'products': ['Netflix', 'Disney+', 'IPTV', 'VPN', 'Gaming'],
            'anti_spam': True,
            'sav_integration': True,
            'human_transfer': True
        },
        'ready': True
    })

@app.route('/status')
def status():
    """Status détaillé du bot irabonnement"""
    return jsonify({
        'bot_name': 'Assistant irabonnement.com',
        'version': '1.0',
        'developer': 'DakarDev',
        'last_update': '2025-05-29',
        'services_supported': [
            'Netflix', 'Prime Video', 'Disney+', 'Crunchyroll',
            'IPTV', 'Surfshark VPN', 'NordVPN', 
            'Carte Xbox', 'Carte PSN', 'HBO Max'
        ],
        'menu_structure': {
            '1': 'Comment ça fonctionne ?',
            '2': 'J\'ai passé commande, je n\'ai rien reçu',
            '3': 'J\'ai un problème avec mon compte', 
            '4': 'Je veux me réabonner',
            '5': 'Je veux acheter un abonnement',
            '6': 'Contacter un conseiller humain'
        },
        'sav_integration': {
            'number': '+221770184531',
            'response_time': '< 40 minutes',
            'hours': '10h-22h'
        }
    })

if __name__ == '__main__':
    app.run(debug=True)