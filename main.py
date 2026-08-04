from yacc import *

def run():

    # specifying test
    tests_dir = "robot_scripts"
    test_name = "test_arrays.txt"

    with open(f"{tests_dir}/{test_name}", "r", encoding="utf-8") as file:
        text = file.read()

    prog = parser.parse(text + '\n')

    map_file = open('maps/map.txt')
    try:
        prog.find_exit(map_file)
    except Exception as e:
        prog.set_exception(e)
        return prog.exception
    return 'Interpreter finished script executing. Robot didnt found exit.'

def test_run(text):
    prog = parser.parse(text + '\n')
    map_file = open('map.txt')
    prog.find_exit(map_file)
    print()

print(run())
