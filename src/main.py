import os
import json

from crawler import QuoteCrawler
from indexer import InvertedIndex
from search import SearchIndex, load_index_from_file

datafile = "data/index.json"

def parse_find_command(input_line):
    """
    Parse and validate a CLI command of the form:
        find <arg1> <arg2> ...

    Returns:
        list[str]  -- arguments after 'find'

    Raises:
        ValueError -- if input is malformed
    """

    # Enforce single spaces only (no tabs, no double spaces)
    if "  " in input_line or "\t" in input_line:
        raise ValueError("Arguments must be separated by a single space")

    # Exactly 'find' is not allowed
    if input_line == "find":
        raise ValueError("Empty arguments are not allowed")

    # Must be 'find ' followed by arguments
    if input_line[4] != " ":
        raise ValueError("Command must be 'find <args>'")

    parts = input_line.split(" ")

    # parts[0] is 'find'
    args = parts[1:]

    # Defensive check: no empty arguments
    if any(arg == "" for arg in args):
        raise ValueError("Empty arguments are not allowed")

    return args

def parse_print_command(input_line):
    """
    Parse and validate a CLI command of the form:
        print <argument>

    Returns:
        str  -- the single argument

    Raises:
        ValueError -- if input is malformed
    """

    # Enforce single spaces only
    if "  " in input_line or "\t" in input_line:
        raise ValueError("Arguments must be separated by a single space")

    # Exactly 'print' is not allowed
    if input_line == "print":
        raise ValueError("Empty arguments are not allowed")
    
    # Must be followed by a space
    if input_line[5] != " ":
        raise ValueError("Command must be 'print <argument>'")

    parts = input_line.split(" ")

    if len(parts) != 2:
        raise ValueError("The 'print' command requires exactly one argument")

    # parts[0] is 'print'
    argument = parts[1]

    if argument == "":
        raise ValueError("Argument may not be empty")

    return argument


def handle_build_command():
    
    crawler = QuoteCrawler()
    indexer = InvertedIndex()
    # Crawl website
    crawler.crawl(indexer)            
    # Build index file 
    path = indexer.build()
    print(f"Index written to {path}")

    return

def handle_load_command():
    # Check the index has been built first
    if not os.path.exists(datafile):
        print("Index could not be found to load. Run the build command to create the index")
        return

    # Load file
    searcher = load_index_from_file(datafile)
    print(f"Index data loaded from {datafile}")

    # Return the searcher
    return searcher

def handle_print_command(args, searcher):

    # Check the index is loaded
    if searcher is None:
        print("No index found, please load an index first")
        return

    # Parse the arguments
    try:
        arg = parse_print_command(input_line)
    except ValueError as v:
        print(v)
        return

    # Get raw inverted index
    results = searcher.print_raw(arg)
    # Display results
    if len(results) == 0:
        print(f"No results found for '{arg}'")
        return
    print(f"Inverted index for '{arg}'")
    for k, v in results.items():
        print(f"{k}: {v}")

    return

def handle_find_command(input_line, searcher):
    
    # Check the index is loaded
    if searcher is None:
        print("No index found, please load an index first")
        return

    # Parse the arguments
    try:
        args = parse_find_command(input_line)
    except ValueError as v:
        print(v)
        return
    
    # Get the matching page(s)
    results = searcher.search_all(args)
    if len(results) == 0:
        print(f"No results found")
        return
    
    # Only care about web pages (r[0]), not the frequency (r[1])
    for r in results:
        print(r[0])

    return

if __name__ == "__main__":

    searcher = None

    # Loop shell until quits
    while True:

        input_line = input("\n> ").lower().strip()

        if input_line == "build":
            handle_build_command()

        elif input_line == "load":
            searcher = handle_load_command()

        elif input_line[:5] == "print":
            handle_print_command(input_line, searcher)
            
        elif input_line[:4] == "find":
            handle_find_command(input_line, searcher)

        elif input_line == "quit" or input_line == "exit":
            break
        
        elif input_line == "help" or input_line == "h":
            print("""Available commands:
    build       - builds the website's index and saves to a file
    load        - loads the index from a file (requires the file to exist)
    print <arg> - displays the raw inverted index for the given argument (reqires an index to be loaded)
    find <args> - displays the webpages containing all arguments (requires an index to be loaded)
    help/h    - displays this help message
    quit/exit - quits the program             
                """)

        else:
            print("Command not recognised. Valid commands are 'build', 'load', 'print', 'find', 'help' and 'quit'")