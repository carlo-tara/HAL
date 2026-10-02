from router import handle_choice

def decide_dinner():
    prompt = "stasera mangio pasta o riso?"
    options = ["pasta", "riso"]
    scelta = handle_choice(prompt, options)
    print(f"Domanda: {prompt}")
    print(f"Scelta di Laya: {scelta}")

if __name__ == "__main__":
    decide_dinner()
