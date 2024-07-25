# util_manager.py

# lib
import json

# definition

def read_file_for_json( path_:str ):
    try:
        with open( path_, 'r' ) as file:
            return json.load(file)
    except Exception as e:
        print("error : ", e)



if __name__ == "__main__":
    result = read_file_for_json( "" )