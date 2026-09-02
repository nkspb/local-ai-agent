"""
Main module for CLI interaction
"""


from .agent import run_agent

def main() -> None:
    user_input = input("You: ")
    answer = run_agent(user_input)
    print(f"Assistant: {answer}")
    

if __name__ == "__main__":
    main()