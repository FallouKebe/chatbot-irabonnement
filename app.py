from flask import Flask, request, jsonify
from ultrabot import ultraChatBot
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    """Route principale - GET pour navigateur, POST pour webhooks"""
    
    if request.method == 'GET':
        return """
        <h1>🤖 Chatbot SamAbonnement</h1>
        <p>✅ Serveur actif et prêt</p>
        <p>🔗 Webhook: <code>/</code> ou <code>/webhook</code></p>
        <p>📱 Status: En attente des messages WhatsApp</p>
        """
    
    if request.method == 'POST':
        try:
            print(f"📨 Webhook reçu: {request.json}")
            
            if request.json and 'data' in request.json:
                bot = ultraChatBot(request.json)
                response = bot.Processingـincomingـmessages()
                print(f"🤖 Réponse bot: {response}")
                return jsonify({'status': 'success', 'response': response})
            else:
                print("❌ Données webhook invalides")
                return jsonify({'status': 'error', 'message': 'Invalid data'})
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)})

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Route webhook alternative (pour UltraMsg)"""
    
    if request.method == 'GET':
        return jsonify({
            'status': 'webhook_active',
            'message': 'Webhook SamAbonnement prêt pour UltraMsg'
        })
    
    # Pour POST, utilise la même logique que home()
    return home()

@app.route('/test')
def test():
    """Page de test"""
    return jsonify({
        'chatbot': 'SamAbonnement',
        'status': 'active',
        'webhook_urls': ['/', '/webhook'],
        'ultramsg_ready': True
    })

if __name__ == '__main__':
    app.run(debug=True)