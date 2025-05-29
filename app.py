from flask import Flask, request, jsonify
from ultrabot import ultraChatBot
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    """Route principale pour webhooks UltraMsg"""
    
    if request.method == 'GET':
        return """
        <h1>🤖 Chatbot SamAbonnement</h1>
        <p>✅ Serveur actif et prêt</p>
        <p>🔗 Webhook configuré sur cette route</p>
        <p>📱 En attente des messages WhatsApp</p>
        <p>🚀 Status: <span style="color:green">ONLINE</span></p>
        """
    
    if request.method == 'POST':
        try:
            print(f"📨 Webhook reçu: {request.json}")
            
            # Vérifier les données
            if request.json and 'data' in request.json:
                bot = ultraChatBot(request.json)
                response = bot.Processingـincomingـmessages()
                print(f"🤖 Traitement terminé: {response}")
                return jsonify({'status': 'success', 'response': response})
            else:
                print("❌ Données webhook invalides")
                return jsonify({'status': 'error', 'message': 'Invalid webhook data'})
                
        except Exception as e:
            print(f"❌ Erreur webhook: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Route webhook alternative"""
    if request.method == 'GET':
        return jsonify({
            'status': 'webhook_active',
            'message': 'Webhook SamAbonnement ready',
            'timestamp': '2025-05-29'
        })
    
    return home()

@app.route('/test')
def test():
    """Page de test et debug"""
    return jsonify({
        'chatbot': 'SamAbonnement',
        'status': 'ACTIVE',
        'webhook_routes': ['/', '/webhook'],
        'ultramsg_configured': True,
        'instance': '122729',
        'ready': True
    })

if __name__ == '__main__':
    app.run(debug=True)