
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import os
from openai import OpenAI

app = Flask(__name__)
socketio = SocketIO(app)
client = OpenAI(api_key = '###')

def get_openai_response(research_topic, user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant knowledgeable about {research_topic}."},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
            max_tokens=150
        )
        # Extracting the latest response from the assistant
        if response.choices:
            return response.choices[0].message.content
        else:
            return "No response generated."
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"An error occurred: {e}")
        return "Sorry, I couldn't fetch a response due to an error."



@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('set_topic')
def handle_set_topic(data):
    session['research_topic'] = data['topic']
    emit('response', {'message': f"Research topic set to: {session['research_topic']}"})

@socketio.on('message')
def handle_message(data):
    user_input = data['message']
    research_topic = session.get('research_topic', 'general knowledge')
    response_text = get_openai_response(research_topic, user_input)
    emit('response', {'message': response_text})

if __name__ == '__main__':
    socketio.run(app, debug=True)