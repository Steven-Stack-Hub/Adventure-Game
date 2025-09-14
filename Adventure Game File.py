import sys

# Simple player state
player = {
	"health": 3,
	"has_map": False,
	"has_key": False
}

def intro():
	print("""
	Welcome to the Lost Island!
	You are an explorer searching for the legendary treasure.
	Can you survive the dangers and find the prize?
	""")

def beach():
	print("\nYou stand on a sunny beach. The waves crash gently. Paths lead into the jungle, to a river, and along the shore.")
	print("Where do you want to go?")
	print("1. Enter the jungle")
	print("2. Walk along the shore")
	print("3. Go to the river")
	choice = input("> ")
	if choice == "1":
		jungle()
	elif choice == "2":
		shore()
	elif choice == "3":
		river()
	else:
		print("Invalid choice. Try again.")
		beach()

def shore():
	print("\nYou walk along the shore and meet an old fisherman.")
	print("He offers you a map for your journey. Do you accept?")
	print("1. Yes")
	print("2. No")
	choice = input("> ")
	if choice == "1":
		player["has_map"] = True
		print("You received a map! It may help you later.")
	else:
		print("You politely decline and return to the beach.")
	beach()

def river():
	print("\nAt the river, a wild crocodile blocks your path!")
	print("Do you try to cross or return to the beach?")
	print("1. Try to cross")
	print("2. Return to beach")
	choice = input("> ")
	if choice == "1":
		if player["has_map"]:
			print("You use the map to find a safe crossing. You reach the mountain.")
			mountain()
		else:
			print("The crocodile attacks! You lose 1 health.")
			player["health"] -= 1
			if player["health"] <= 0:
				game_over()
			else:
				print(f"Health remaining: {player['health']}")
				river()
	elif choice == "2":
		beach()
	else:
		print("Invalid choice. Try again.")
		river()

def mountain():
	print("\nYou climb the mountain and find a locked chest guarded by a bandit.")
	print("The bandit challenges you: 'Solve my riddle and I'll give you the key.'")
	print("What has keys but can't open locks?")
	answer = input("> ")
	if "piano" in answer.lower():
		print("Correct! The bandit gives you the key.")
		player["has_key"] = True
		print("You descend to the jungle.")
		jungle()
	else:
		print("Wrong! The bandit chases you back to the river.")
		river()

def jungle():
	print("\nYou step into the thick jungle. It's dark and mysterious. You see a cave entrance ahead.")
	if not player["has_key"]:
		print("A giant snake blocks the cave. You need a key to distract it.")
		print("Return to the beach or try another path.")
		print("1. Return to beach")
		print("2. Go to river")
		choice = input("> ")
		if choice == "1":
			beach()
		elif choice == "2":
			river()
		else:
			print("Invalid choice. Try again.")
			jungle()
	else:
		print("You use the key to distract the snake and enter the cave.")
		cave()

def cave():
	print("\nInside the cave, you find a chest glittering with gold! You found the treasure!")
	print("Congratulations, you win!")
	sys.exit()

def game_over():
	print("\nYou have lost all your health. Game over!")
	sys.exit()

def main():
	intro()
	beach()

if __name__ == "__main__":
	main()
