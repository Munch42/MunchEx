import munchex

while True:
    text = input("munchEx > ")
    result, error = munchex.run("<stdin>", text)

    if error: 
        print(error.as_string())
    else:
        print(result)