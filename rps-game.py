from tkinter import *
import random

root = Tk()
root.geometry("600x450")
root.title("Rock Paper Scissors Game")

# Set a stylish background color
root.configure(bg="#FDEBD0")  # Soft cream color

computer_value = {"0": "Rock", "1": "Paper", "2": "Scissor"}
score = 0

# Reset the game
def reset_game():
    global score
    score = 0
    b1["state"] = "active"
    b2["state"] = "active"
    b3["state"] = "active"
    l0.config(text="Score: 0", fg="black")
    l1.config(text="Player", fg="black")
    l3.config(text="Computer", fg="black")
    l4.config(text="", bg="white")

# Player chooses Rock
def isrock():
    global score
    c_v = computer_value[str(random.randint(0, 2))]
    if c_v == "Rock":
        match_result = "Match Draw"
    elif c_v == "Scissor":
        match_result = "Player Wins"
        score += 1
    else:
        match_result = "Computer Wins"
        score -= 1
    update_ui(match_result, "Rock", c_v)

# Player chooses Paper
def ispaper():
    global score
    c_v = computer_value[str(random.randint(0, 2))]
    if c_v == "Paper":
        match_result = "Match Draw"
    elif c_v == "Scissor":
        match_result = "Computer Wins"
        score -= 1
    else:
        match_result = "Player Wins"
        score += 1
    update_ui(match_result, "Paper", c_v)

# Player chooses Scissor
def isscissor():
    global score
    c_v = computer_value[str(random.randint(0, 2))]
    if c_v == "Rock":
        match_result = "Computer Wins"
        score -= 1
    elif c_v == "Scissor":
        match_result = "Match Draw"
    else:
        match_result = "Player Wins"
        score += 1
    update_ui(match_result, "Scissor", c_v)

# Update UI after each move
def update_ui(result, player_choice, computer_choice):
    l4.config(text=result, bg="#FFF3CD", fg="black")  # Yellow result box
    l1.config(text=player_choice, fg="blue")
    l3.config(text=computer_choice, fg="red")
    l0.config(text=f"Score: {score}", fg="green" if score > 0 else "red")

# Game Title
Label(root, text="Rock Paper Scissors", font="Algerian 20 bold", bg="#FDEBD0", fg="purple").pack(pady=20)

# Player vs Computer display
frame = Frame(root, bg="#FDEBD0")
frame.pack()

l0 = Label(frame, text="Score: 0", font="Algerian 14 bold", bg="#FDEBD0", fg="black")
l1 = Label(frame, text="Player", font="Algerian 14", bg="#FDEBD0")
l2 = Label(frame, text="VS", font="Algerian 12 bold", bg="#FDEBD0")
l3 = Label(frame, text="Computer", font="Algerian 14", bg="#FDEBD0")

l0.pack(side=TOP, pady=10)
l1.pack(side=LEFT, padx=20)
l2.pack(side=LEFT, padx=20)
l3.pack(side=LEFT, padx=20)

# Result display
l4 = Label(root, text="", font="Algerian 18 bold", bg="white", width=20, height=2, borderwidth=2, relief="solid")
l4.pack(pady=20)

# Buttons for Rock, Paper, and Scissors
frame1 = Frame(root, bg="#FDEBD0")
frame1.pack(pady=20)

b1 = Button(frame1, text="Rock", font="Algerian 14 bold", bg="#85C1E9", fg="white", command=isrock, width=10, height=2)
b2 = Button(frame1, text="Paper", font="Algerian 14 bold", bg="#F7DC6F", fg="black", command=ispaper, width=10, height=2)
b3 = Button(frame1, text="Scissor", font="Algerian 14 bold", bg="#F1948A", fg="white", command=isscissor, width=10, height=2)

b1.pack(side=LEFT, padx=10)
b2.pack(side=LEFT, padx=10)
b3.pack(side=LEFT, padx=10)

# Reset Button
Button(root, text="Reset Game", font="Algerian 14 bold", bg="black", fg="white", command=reset_game).pack(pady=20)

root.mainloop()