
import webbrowser

user_input = input("Enter your YouTube command: ").strip().lower()
query = user_input
if "play " in user_input:
    query = query.split("play ", 1)[1]
elif "search " in user_input:
    query = query.split("search ", 1)[1]
query = query.split("on youtube")[0].strip()
if query:
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    print(f"Searched YouTube for '{query}' in your browser.")
else:
    print("No query entered.")
