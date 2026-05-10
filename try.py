import sys
from utils.exception import CustomException

def main():
    try:
        a = 10
        b = 0
        c = a / b
    except Exception as e:
        raise CustomException(e, sys)
    

if __name__ == "__main__":
    main()
