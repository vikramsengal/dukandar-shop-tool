# #create on list
#
# lst = [1,2,3,4,5,6,7]
# print(lst)
# print(lst[3])
# print(lst[-1])
# print(lst[3:6])
# print(lst[:5])
# print(lst[:6])
#
# # this is append method
# lst.append(10)
# print(lst)
#
# #this is updating method update in list
# lst[0] = 50
# print(lst)
#
# #this is a insert method
# lst.insert(3,9)
# print(lst)
#
# #searching eliment using index pass on eliment this function return index
# print(lst.index(3))
#
# #this is a extend method
# lst.extend(["a",12,53])
# print(lst)
#
# #this is a pop method pass argument on index then remuve eliment
# lst.pop(3)
# print(lst)
#
# #this is a remove method pass argument on velue then remove eliment
# lst.remove("a")
# print(lst)
#
# #this is a count method
# lst.count(6)
# print(lst)
#
# #sort an eliment then assending order
# lst.sort()
# print(lst)
#
# #sort an eliment then desending order
# lst.sort(reverse=True)
# print(lst)
#
# # old list copy on new list
# new_list = lst.copy()
# print(new_list)
#
# #this method is a deffrant not for selebus but this method is inpotent
# print("this is a deffrant method......")
# squear = [x*x for x in range(10)]
# print(squear)
#
# #this is  a clear method and use for list are blenked
# lst.clear()
# print(lst)
#
#
#
# ###this is solve in list fiftin qustion
# print("this is a 50 problam qustion ......\n\n\n\n")
#
# #qs1
# list = [1,2,3,4,5]
# print(list[0],list[2],list[4])
#
# #qs2
# #list slicing any 3 eliment
# lst = [1,2,3,4,5]
# print(lst[1:4])
#
# #qs3
# lst = [1,2,3,4,5]
# print(lst[2:5])
#
# #qs4
# lst = [1,2,3,4,5]
# lst.append(10)
# print(lst)
#
# #qs5
# lst = [1,2,3,4,5]
# lst.insert(2,8)
# print(lst)
#
# #qs6
# lst = [1,2,11,4,5]
# poped_eliment = lst.pop(2)
# print(lst)
# print(poped_eliment)
#
# #qs7
# lst = [1,2,3,"a",4,5]
# lst.remove("a")
# print(lst)
#
# #qs8
# lst = [1,2,3,4,5]
# print(len(lst))
#
# #qs9
# lst = [1,2,3,4,5]
# lst.clear()
# print(lst)
#
# #qs10
# lst = [1,2,3,4,5]
# lst[4] = 50
# print(lst)
#
# #qs11
# lst = [1,2,3,4,5]
# lst2 = [1,2,3,4,5]
# lst.extend(lst2)
# print(lst)
#
# #qs12
# lst = [1,2,3,4,5]
# lst2 = [1,2,3,4,5]
# print(lst + lst2)
#
# #qs13
# lst = [5,4,3,2,1]
# lst.sort()
# print(lst)
#
# #qs14
# lst = [1,2,3,4,5]
# lst.sort(reverse=True)
# print(lst)
#
# #qs15
# lst = [1,2,3,4,5]
# lst.reverse()
# print(lst)
#
# #qs16
# lst = [1,2,3,4,5]
# print("1,2,3,4,5"[::-1])
#
# #qs17
# lst = [1,2,3,4,5]
# lst.count(7)
# print(lst)
#
# #qs18
# lst = [1,2,3,4,5]
# print(lst.index(3))
#
# #qs19
# lst = [1,2,3,4,5]
# mul_2 = [x*2 for x in range(1,len(lst) + 1)]
# new_list = mul_2
# print(new_list)
#
# #qs20
# lst = [1,2,3,4,5]
# print_using_loop = [i for i in range(1,len(lst) + 1)]
# print(print_using_loop)
#
# #qs21
# print("print odd or even numbar")
# lst = [1,2,3,4,5,6,7,8,9]
# even_numbar = []
# odd_numbar = []
# for i in lst:
#     if i % 2 == 0:
#         even_numbar.append(i)
#     else:
#         odd_numbar.append(i)
# print(even_numbar)
# print(odd_numbar)
#
# #qs22
# lst = [2,-4,5,-7,9,-1]
# positive_numbar = []
# negative_numbar = []
#
# for i in lst:
#     if i > 0:
#         positive_numbar.append(i)
#     else:
#         negative_numbar.append(i)
#
# print(positive_numbar)
# print(negative_numbar)
#
# #qs23
# lst = [1,2,3,4,5,6,7,8,9,10]
# n = 0
# for i in lst:
#     n += i
#     print(n)
#
# #qs24
# #find on meximam velue
# print("this is mex velue find method")
# lst = [1, 2, 3, 4, 5, 6, 7, 88, 99]
# max_velue = lst[0]
# for i in lst:
#     if i > max_velue:
#         max_velue = i
# print(max_velue)
#
# #qs25
# #find the minimam velue in list
# print("this is a minimam velue")
# lst = [11, 22, 33, 44, 55, 66, 7, 88, 99]
# min_velue = lst[0]
# for i in lst:
#     if i < min_velue:
#         min_velue = i
# print(min_velue)
#
# #qs26
# thisset = {1,2,3,4,5,6,7,8}
# print(thisset)
#
# thisset = {1,2,3,4,5,6,7,8}
# print(4 in thisset)
# print(5 not in thisset)
#
# thisset = {1,2,3,4,5,6,7,8}
# for i in thisset:
#     print(i)
#
# thisset = {1,2,3,4,5,6,7,8}
# thisset.add(10)
# print(thisset)
# set2 = {3,5,4,6,7,8,9,2}
# thisset.update(set2)
# print(thisset)
#
# thisset = {1,2,3,4,5,6,7,8}
# mylist = [22,43,5,4,65,76]
#
# thisset.update(mylist)
# print(thisset)
# thisset.remove(43)
# print(thisset)
# thisset.discard(65)
# print(thisset)
# x = thisset.pop()
# print(x)
# print(thisset)
# thisset.clear()
# print(thisset)
# del thisset
#
# set1 = {1,2,3,4,5,6,7,8}
# set2 = {"herry","vikram","zibra"}
# set5 = {4.5,6.4,8.0,3.2}
# boolset = {True,False}
# set3 = set1.union(set2)
# print(set3)
# set4 = set1 | set2
# print(set4)
# set6 = set1.union(set2,set5,boolset)
# print(set6)

# f = open("test.txt","r")
# print(f.read())
# f.close()

# import os
# f = open("test.txt","a")
# f.write("hello world")
# f.close()
# f = open("test.txt","r")
# os.remove("test.txt")

# f = open("hello.jpg","")
# print(f.read())
#
# filename = 'hello.jpg'
#
# with open(filename, 'rb') as f:
#     data = f.read()
#
# # Hex format में पूरा print करें
# print(data)  # हर byte के बीच space

# def myfunction(name):
#     print(name)
#
# myfunction("vikram")

# def mysum(a=8,b=9):
#     sum = a + b
#     print(sum)
# mysum()


# def my_function(*kids):
#   print("The youngest child is " + kids[0])
#
# my_function("Emil", "Tobias", "Linus")

# def mufunction(*args):
#     print("type",type(args))
#     print("args",args)
#     print("firstname",args[0])
#     print("lastname",args[1])
#     print("age",args[2])
#     print("height",args[3])
#     print("weight",args[4])
#     print("city",args[5])
#     print("phone",args[6])
#     print("email",args[7])
#     print("sername",args[8])
#
# mufunction("vikram","parbatbhai",21,164,50,"tharad",9409847728,"sengalvikram004@gmail.com","sengal")

# def my_function(getname,*names):
#     for name in names:
#         print(getname,name)
# my_function("hello","world","vikram","zibra")
#
# def my_function(greeting, *names):
#   for name in names:
#     print(greeting, name)
#
# my_function("Hello", "Emil", "Tobias", "Linus")

# import mymodule
# mymodule.mysum(55,66)
# mymodule.subtrection(12,4)
# mymodule.maltip(12,4)
# mymodule.division(12,4)
# mymodule.mysum2(12,13,14,15)
# mymodule.printlist(1,5,3,8,2,6)

# import datetime
# date = datetime.datetime(2024,3,18)
# print(date.strftime("%A"))

# import math
# x = min(1,2,3,4,5,6)
# y = max(1,2,3,4,5,6)
# print(x)
# print(y)
# z = abs(-7.25)
# print(z)
# p = pow(2,3)
# print(p)
# q = math.sqrt(64)
# print(q)
# m = math.ceil(3.14)
# n = math.floor(3.14)
# print(m)
# print(n)
# k = math.pi
# print(k)

# import json
#
# x = '{"name":"vikram","age":21,"city":"new york"}'
# y = json.loads(x)
# print(y["age"])
# print(y["name"])
# print(y["city"])
# print(type(y))

# import json
#
# x = {
#     "name": "rahul",
#     "age": 20,
#     "city":"newyork"
# }
#
# y = json.dumps(x)
# print(y)
# print(type(y))

# import json
#
# a = json.dumps({"a":1,"b":2,"c":3})
# b = json.dumps(["apple","banana","mango"])
# c = json.dumps(("apple","banana","mango"))
# d = json.dumps(("hello"))
# e = json.dumps(42)
# f = json.dumps(31.42)
# g = json.dumps(True)
# h = json.dumps(False)
# i = json.dumps(None)
#
# print(a)
# print(b)
# print(c)
# print(d)
# print(e)
# print(f)
# print(g)
# print(h)
# print(i)
#
# print(type(a))
# print(type(b))
# print(type(c))
# print(type(d))
# print(type(e))
# print(type(f))
# print(type(g))
# print(type(h))
# print(type(i))

import json

# x = {
#   "name": "John",
#   "age": 30,
#   "married": True,
#   "divorced": False,
#   "children": ("Ann","Billy"),
#   "pets": None,
#   "cars": [
#     {"model": "BMW 230", "mpg": 27.5},
#     {"model": "Ford Edge", "mpg": 24.1}
#   ]
# }
# f = dict.keys(x)
# print(f)
# g = dict.values(x)
# print(g)
#
# y = json.dumps(x)
# print(y)
# print(type(y))

# import  re
# txt = "Hello My name is VIKRAM"
# x = re.search("^Hello.*VIKRAM$",txt)
# print(x)
# sx = re.findall("me",txt)
# print(sx)

# try:
#     print(x)
# except NameError:
#     print("NameError")

# try:
#   f = open("demofile.txt")
#   try:
#     f.write("Lorum Ipsum")
#   except:
#     print("Something went wrong when writing to the file")
#   finally:
#     f.close()
# except:
#   print("Something went wrong when opening the file")

# class myclass:
#     x = 5
# print(myclass)
# print(type(myclass))

# class myclass:
#     x = 5
# m1 = myclass()
# print(m1.x)

# class Person:
#     age = 20
# p1 = Person()
# print(p1.age)
# del p1
# print(p1.age)

# class myclass:
#     x = 5
# p1 = myclass()
# p2 = myclass()
# p3 = myclass()
#
# print(p1.x)
# print(p2.x)
# print(p3.x)

# class Info:
#     def __init__(self,name,age):
#         self.name = name
#         self.age = age
# i1 = Info("rahul",20)
# print("name:",i1.name)
# print("age:",i1.age)

#defolt velue in __init__() peramitar

# class person:
#     def __init__(self, name, age=18):
#         self.name = name
#         self.age = age
#
# p1 = person("Rahul")
# p2 = person("nikesh",25)
# print(p1.name)
# print(p1.age)
# print(p2.name)
# print(p2.age)

# class person:
#     def __init__(self, name, age,city,country,district,email):
#         self.name = name
#         self.age = age
#         self.city = city
#         self.district = district
#         self.email = email
#         self.country = country
#
# p1 = person("vikram",21,"Tharad","india","vav-Tharad","sengalvikram004@gmail.com")
# print(p1.name)
# print(p1.age)
# print(p1.city)
# print(p1.country)
# print(p1.district)
# print(p1.email)

# class Person:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#
#     def getname(self):
#         print('my name is ',self.name)
#
#     def getage(self):
#         print('my age is ',self.age)
#
# p1 = Person("vikram",21)
# p2 = Person("rahul",20)
# p1.getname()
# p1.getage()
# p2.getname()
# p2.getage()

# class Car:
#     def __init__(self,name,model,color):
#         self.name = name
#         self.model = model
#         self.color = color
#
#     def greeat(self):
#         return "Hello " + self.name
#
#     def welcome(self):
#         message = self.greeat()
#         print(message,"Welcome to my showroom!")
#
# c1 = Car("vikram","toyota","white")
# c1.welcome()

# lst = []
# for i in range(1,11):
#     data = str(input("entar velue:"))
#     lst.append(data)
# print(lst.sort())
# print(lst)

print("THIS IS A INTARVIEW QUSTION SOLVE IN PYCHARM IDE")

# l = [44,85,111,99,35,47,11]
# print(111 in l)

#get missing numbar in  to 100

# def getmissing_numbar(lst):
#     return set(lst[len(lst)-1][:1])- set(l)
# l = list(range(1,100))
# l.remove(50)
# print(getmissing_numbar(l))

# lst = []
# for i in range(1,101):
#     lst.append(i)
#     if i == 50 or i == 25 or i == 75 or i == 100:
#         lst.remove(i)
#         print("missing eliment in list:::",i)
# print(lst)

#FIND duplicet numbar in intigar list

# import pyautogui
# import time
#
# pyautogui.FAILSAFE = True
#
# time.sleep(5)
# pyautogui.press('win')
# time.sleep(1)
# pyautogui.write('notepad',interval=0.1)
# time.sleep(1)
# pyautogui.press('enter')
# time.sleep(2)
# pyautogui.write('hello i am vikram sengal',interval=0.3)
# time.sleep(2)
# pyautogui.press('enter')
# pyautogui.write('autometion succsesfull',interval=0.5)

# import os
# import time
#
# # Wait for 30 minutes (30 * 60 seconds)
# time.sleep(30 * 60)
#
# # Shutdown Windows
# os.system("shutdown /s /t 0")


import pyaudio
import wave
import socket
import threading
import time
import os
from datetime import datetime
import queue
import sys

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 30  # Change as needed


class VoiceCallRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.call_active = False
        self.frames = []

        # Create recordings directory
        if not os.path.exists('call_recordings'):
            os.makedirs('call_recordings')

    def start_server(self, host='0.0.0.0', port=5000):
        """Start voice call server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)

        print(f"\n📞 Voice Call Server Started on port {port}")
        print(f"🎯 Target user should connect to: {self.get_local_ip()}:{port}")
        print("⏳ Waiting for target user to connect...\n")

        while True:
            try:
                client_socket, address = server_socket.accept()
                print(f"✅ Target connected from: {address}")

                # Start call in new thread
                call_thread = threading.Thread(
                    target=self.handle_call,
                    args=(client_socket, address)
                )
                call_thread.daemon = True
                call_thread.start()

            except KeyboardInterrupt:
                print("\n👋 Server stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        server_socket.close()

    def handle_call(self, client_socket, address):
        """Handle voice call with target"""
        self.call_active = True
        self.recording = True
        self.frames = []

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"call_recordings/call_with_{address[0]}_{timestamp}.wav"

        print(f"\n🎙️ Call started with {address}")
        print(f"⏺️ Recording to: {filename}")
        print(f"⏱️ Recording for {RECORD_SECONDS} seconds...")

        # Open recording file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        # Open audio stream for recording
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            output=True,
            frames_per_buffer=CHUNK
        )

        start_time = time.time()

        try:
            while self.call_active and (time.time() - start_time) < RECORD_SECONDS:
                # Receive audio from target
                try:
                    data = client_socket.recv(CHUNK * 2)
                    if not data:
                        break

                    # Play audio through speakers
                    stream.write(data)

                    # Record audio (both sides)
                    self.frames.append(data)

                except:
                    break

            # Save recording
            for frame in self.frames:
                wf.writeframes(frame)

            print(f"✅ Call completed! Recording saved: {filename}")
            print(f"📊 Duration: {len(self.frames) * CHUNK / RATE:.1f} seconds")

        except Exception as e:
            print(f"❌ Call error: {e}")

        finally:
            wf.close()
            stream.stop_stream()
            stream.close()
            client_socket.close()
            self.call_active = False
            self.recording = False

    def connect_to_target(self, target_ip, target_port=5000):
        """Connect to target as caller"""
        try:
            # Open audio stream
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK
            )

            # Connect to target
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))

            print(f"✅ Connected to target: {target_ip}")
            print("🎙️ Speak now... (Press Ctrl+C to stop)")

            while True:
                # Read from microphone
                data = stream.read(CHUNK, exception_on_overflow=False)

                # Send to target
                sock.sendall(data)

                # Receive from target
                try:
                    response = sock.recv(CHUNK * 2)
                    if response:
                        # Play received audio
                        stream.write(response)
                except:
                    pass

        except KeyboardInterrupt:
            print("\n👋 Call ended")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            sock.close()

    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


def main():
    print("=" * 60)
    print("🎙️ PURE PYTHON VOICE CALL RECORDER")
    print("=" * 60)
    print("\nOptions:")
    print("1. Start server (wait for target to call)")
    print("2. Call target (connect to server)")
    print("3. Exit")

    recorder = VoiceCallRecorder()

    while True:
        try:
            choice = input("\nEnter choice (1-3): ").strip()

            if choice == '1':
                port = input("Enter port (default 5000): ").strip()
                port = int(port) if port else 5000
                recorder.start_server(port=port)

            elif choice == '2':
                target_ip = input("Enter target IP address: ").strip()
                port = input("Enter target port (default 5000): ").strip()
                port = int(port) if port else 5000

                print(f"\n🔌 Connecting to {target_ip}:{port}...")
                recorder.connect_to_target(target_ip, port)

            elif choice == '3':
                print("\n👋 Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Check if pyaudio is installed
    try:
        import pyaudio
    except ImportError:
        print("❌ PyAudio not installed!")
        print("\nInstall it with:")
        print("  Windows: pip install pyaudio")
        print("  Linux: sudo apt-get install portaudio19-dev python3-pyaudio")
        print("  Mac: brew install portaudio && pip install pyaudio")
        sys.exit(1)

    main()






