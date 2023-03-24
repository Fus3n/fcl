import os
import pyperclip

total = 0
total_wo_spaces = 0

lines = []
def countlines():
    for file in os.listdir():
        if file.endswith('.py') and file != "line-counter.py":
            with open(f"./{file}", "r") as f:
                lines = f.readlines()
                total += len(lines)
                for line in lines:
                    if line != "" and line != "\n":
                        total_wo_spaces += 1

def take_lines():
    collected = ""
    my_list = os.listdir()
    order_dict = {"l": 0, "p": 1, "i": 2, "m": 3}
    my_list.sort(key=lambda x: order_dict.get(x[0], len(order_dict)))
    for file in my_list:
        if file.endswith('.py') and file != "line-counter.py":
            print(file)
            with open(f"./{file}", "r") as f:
                collected += "#" + file + "\n\n" + f.read().strip() + "\n\n"

    return collected

# print(take_lines())
pyperclip.copy(take_lines())