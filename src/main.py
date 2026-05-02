



if __name__ == "__main__":

    # Loop shell until quits
    while True:

        i = input("> ").lower().strip()

        if i == "build":
            pass

        elif i == "load":
            pass

        elif i[:6] == "print ":
            words = i.split(" ")[1:]
            if len(words) > 1:
                print("Error: print command requires exactly one argument")
                continue
            elif len(words) == 0:
                print("Error: print command requires an argument")

            print(words[0])
            pass

        elif i[:5] == "find ":
            words = i.split(" ")[1:]
            if len(words) == 0:
                print("Error: find command requires one or more arguements")
                continue
            
            print(words)
            pass

        elif i == "quit":
            break
        else:
            print("Command not recognised. Valid commands are 'build', 'load', 'print' and 'find'")