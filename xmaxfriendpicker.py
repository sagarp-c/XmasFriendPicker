import random
import os
from cryptography.fernet import Fernet

print("🎄 Xmas Friend Picker (Encrypted) 🎄\n")

# Step 1: Enter participants
while True:
    try:
        n = int(input("Enter number of friends (min 2): "))
        if n >= 2:
            break
        print("You need at least 2 participants.")
    except ValueError:
        print("Enter a valid number.")

names = []
for i in range(n):
    while True:
        name = input(f"Enter name of person {i+1}: ").upper()
        if name in names:
            print("Name already exists! Choose a unique name.")
        else:
            names.append(name)
            break

# Step 2: Generate encryption key & cipher
key = Fernet.generate_key()
cipher = Fernet(key)
print(key,cipher)
# Encrypt names
encrypted_names = [cipher.encrypt(name.encode()).decode() for name in names]

# Fully random, fair secret-santa assignment
# Keep generating until no one gets themselves
while True:
    shuffled = encrypted_names[:]
    random.shuffle(shuffled)

    decrypted = [cipher.decrypt(x.encode()).decode() for x in shuffled]
    if all(decrypted[i] != names[i] for i in range(n)):
        break  # Valid assignment

# Convert to a working list
remaining = shuffled[:]

input("\nPress ENTER to hide the screen for the first participant...")
os.system('cls' if os.name == 'nt' else 'clear')

print("\nAll names are ready! Each participant will pick a number privately.\n")

# Step 3: Picking phase
for i in range(n):

    # Validate participant identity
    while True:
        participant = input("Enter your name: ").upper()
        if participant in names:
            break
        print("Sorry, you are not in the participant list. Try again.")

    # Identify who is left in the remaining encrypted picks
    available_indices = []
    for idx, encrypted_person in enumerate(remaining):
        if cipher.decrypt(encrypted_person.encode()).decode() != participant:
            available_indices.append(idx)

    print(f"\nChoose a number from these remaining folded papers:")
    print(f"Available numbers: {[i+1 for i in available_indices]}")

    # Validate choice
    while True:
        try:
            choice = int(input("Your choice: ")) - 1
            if choice in available_indices:
                break
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")

    picked = cipher.decrypt(remaining.pop(choice).encode()).decode()
    print(f"\n🎁 Your Xmas friend is: {picked}")

    input("\nPress ENTER to hide the screen for the next participant...")
    os.system('cls' if os.name == 'nt' else 'clear')

print("All participants have picked their Xmas friend! 🎉")
print(f"\nNote: Encryption key (to decrypt manually if needed): {key.decode()}")
