from flask import Flask, request, jsonify
from ultrabot import ultraChatBot
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    """Route principale pour recevoir les webhooks UltraMsg"""
    
    if request.method == 'GET':
        return "🤖 Chatbot SamAbonnement actif - Webhook prêt"
    
    if request.method == 'POST':
        try:
            # Logger les données reçues
            print(f"Webhook reçu: {request.json}")
            
            # Vérifier que les données sont valides
            if request.json and 'data' in request.json:
                bot = ultraChatBot(request.json)
                response = bot.Processingـincomingـmessages()
                print(f"Réponse bot: {response}")
                return jsonify({'status': 'success', 'response': response})
            else:
                print("Données webhook invalides")
                return jsonify({'status': 'error', 'message': 'Invalid webhook data'})
                
        except Exception as e:
            print(f"Erreur webhook: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)})

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Route alternative webhook (au cas où)"""
    return home()

@app.route('/test')
def test():
    """Page de test"""
    return jsonify({
        'status': 'Chatbot actif',
        'webhook_url': '/',
        'alternative_webhook': '/webhook'
    })

if __name__ == '__main__':
    app.run(debug=True)