from flask import Flask, render_template, request, jsonify, session
import random
import secrets
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize():
    data = request.json
    names = [name.strip().upper() for name in data.get('names', [])]
    
    if len(names) < 2:
        return jsonify({'error': 'Need at least 2 participants'}), 400
    
    if len(names) != len(set(names)):
        return jsonify({'error': 'All names must be unique'}), 400
    
    # Generate encryption key
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # Encrypt names
    encrypted_names = [cipher.encrypt(name.encode()).decode() for name in names]
    
    # Generate valid assignment (no one gets themselves)
    while True:
        shuffled = encrypted_names[:]
        random.shuffle(shuffled)
        decrypted = [cipher.decrypt(x.encode()).decode() for x in shuffled]
        if all(decrypted[i] != names[i] for i in range(len(names))):
            break
    
    # Store in session
    session['key'] = key.decode()
    session['names'] = names
    session['remaining'] = shuffled
    session['picked_count'] = 0
    
    return jsonify({
        'success': True,
        'total_participants': len(names),
        'encryption_key': key.decode()
    })

@app.route('/get_available', methods=['POST'])
def get_available():
    data = request.json
    participant = data.get('participant', '').strip().upper()
    
    names = session.get('names', [])
    remaining = session.get('remaining', [])
    key = session.get('key', '')
    
    if not names or not remaining or not key:
        return jsonify({'error': 'Session expired. Please restart.'}), 400
    
    if participant not in names:
        return jsonify({'error': 'You are not in the participant list'}), 400
    
    cipher = Fernet(key.encode())
    
    # Find available indices
    available_indices = []
    for idx, encrypted_person in enumerate(remaining):
        decrypted = cipher.decrypt(encrypted_person.encode()).decode()
        if decrypted != participant:
            available_indices.append(idx + 1)  # 1-indexed for display
    
    return jsonify({
        'success': True,
        'available_numbers': available_indices,
        'participant': participant
    })

@app.route('/pick', methods=['POST'])
def pick():
    data = request.json
    participant = data.get('participant', '').strip().upper()
    choice = data.get('choice')
    
    names = session.get('names', [])
    remaining = session.get('remaining', [])
    key = session.get('key', '')
    picked_count = session.get('picked_count', 0)
    
    if not names or not remaining or not key:
        return jsonify({'error': 'Session expired. Please restart.'}), 400
    
    try:
        choice_idx = int(choice) - 1  # Convert to 0-indexed
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid choice'}), 400
    
    cipher = Fernet(key.encode())
    
    # Validate choice
    valid = False
    for idx, encrypted_person in enumerate(remaining):
        decrypted = cipher.decrypt(encrypted_person.encode()).decode()
        if idx == choice_idx and decrypted != participant:
            valid = True
            break
    
    if not valid or choice_idx < 0 or choice_idx >= len(remaining):
        return jsonify({'error': 'Invalid choice'}), 400
    
    # Pick the name
    picked_encrypted = remaining.pop(choice_idx)
    picked = cipher.decrypt(picked_encrypted.encode()).decode()
    picked_count += 1
    
    # Update session
    session['remaining'] = remaining
    session['picked_count'] = picked_count
    
    is_complete = picked_count >= len(names)
    
    return jsonify({
        'success': True,
        'picked_name': picked,
        'is_complete': is_complete,
        'picked_count': picked_count,
        'total': len(names)
    })

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)