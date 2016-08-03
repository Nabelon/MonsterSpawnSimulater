import struct
import json

def main():
    
    while True:
        userInput = raw_input("filename:")
        raw = json.load(open(userInput+".js"))
        output = []
        for i in raw["data"]["trackData"][0]:
            print i
            output.append([i["lat"],i["lon"],2])
        with open(userInput+".json", 'w') as f:
            json.dump(output, f, indent=2)
        print "done"  
                

if __name__ == '__main__':
    main()
