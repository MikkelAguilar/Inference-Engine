import sys
from inference_engine import InferenceEngine

valid_methods = ['TTC', 'FC', 'BC']

if __name__ == "__main__":
    #Exits the program if the number of arguments is not 3 and the second arguement is not a valid method
    if len(sys.argv) != 3 or sys.argv[1].upper() not in valid_methods:
        print("Incorrect Format")
        sys.exit()

    file = sys.argv[2] #Set the file to the third argument
    engine = InferenceEngine()

    #Try to read from the file, but if file is not found, end the program
    try:
        engine.read_from_file(file)
    except FileNotFoundError:
        print('File name does not exist')
        sys.exit()
    
    print(engine.search_stats(sys.argv[1])) #Print the results of the method