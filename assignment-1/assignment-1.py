#need a python program that uses a python class to manage a queue. 
def the_queue():
    line = []
    quit_questionmark = False
    print("q: quit")
    print("m: menu")
    print("a: add to queue")
    print("p: pop")
    print("l: list queue")
    while not quit_questionmark:
        actions = input("ACTION: ")
        if actions == 'q':
            quit_questionmark = True
        elif actions == 'm':
            showMenu()
        elif actions == 'a':
#            type1 = input("what type of data? number(n) string(s) float(f) ")
            added = input("data to be added: ")
#            if type1 == 'n':
#                type1 == int(added)
#            elif type1 == 'f':
#                type1 == float(added) 
            
            addToList(line, added)
        elif actions == 'p':
            print(popTheTop(line))
        else:
            print(line) 
    return None
#what does a queue even do first in first out? 
def showMenu():
    print("q: quit")
    print("m: menu")
    print("a: add to queue")
    print("p: pop")
    print("l: list queue")
    return 0

def addToList(list1, item):
    list1.append(item)
    return list1

def popTheTop(list1):
    list1.pop(0)
    return list1

the_queue()