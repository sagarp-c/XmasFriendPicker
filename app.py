from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# A list to store the participants
participants = []

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get participant name from the form
        name = request.form.get("name")
        if name and name not in participants:
            participants.append(name)
        elif name in participants:
            return "This name is already in the list."
    
    return render_template("index.html", participants=participants)

@app.route("/shuffle", methods=["GET"])
def shuffle():
    # Shuffle the participants list
    if len(participants) < 2:
        return "Not enough participants to shuffle. Please add more."
    
    random.shuffle(participants)
    
    # Create secret santa assignments
    secret_santa = {}
    for i in range(len(participants)):
        secret_santa[participants[i]] = participants[(i + 1) % len(participants)]
    
    return render_template("shuffle.html", secret_santa=secret_santa)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
