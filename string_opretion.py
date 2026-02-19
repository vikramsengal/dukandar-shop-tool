# string = "helloworld"
# lenofstr =  len(string)
# print(lenofstr)
# s = string[0],string[1],string[2]
# print(s)
# strslicing = string[0:5],string[3:],string[7:],string[7:8]
# z = list(strslicing)
# y = set(strslicing)
# print(y)
# print(z)
# print(type(strslicing))
# print(strslicing)

# print("second string :::")
# a = "   hello   "
# b = "WORLD"
# print(a + b)
# print(a + " " + b)
# print(a + "ha" + b)
# print(a + "ha" * 3 +  b)
# print("ell" in "hello")

# print("all method : \n")

# print(b.lower())
# print(a.upper())
# print(a.title())
# print(a.capitalize())
# print(a.swapcase())
# print(a.endswith("lo"))

# print("serch method :: \n")

# print(a.find("l"))
# print(a.rfind("lo"))
# print(a.index("o"))
# print(a.count("l"))
# print(a.replace("l","L"))

# print("strip and split addition ::: \n")

# print(a.strip())
# print(a.rstrip())
# print(a.lstrip())

# f = "hello world"
# print(set(f.split()))
# print(tuple(f.split()))
# # print(dict(f.split())) # kisi bhi string ko split karte vakt isko dictnary me convert nahi ho sakti
# print(",".join(["hello","vikram"]))
# print(f.startswith("he"))
# print(f.endswith("ld"))

# name = "ravi"
# age = 22
# print(f"name:{name},age:{age}")
# print("name:{},age:{}".format(name,age))
# print("name{n},age{a}".format(n = name,a = age))
# print(f"my name is {name} and i am {age} old")
# print("name %s,age %d" % (name,age))

# print("numbar alinment :::")

# print(f"{3.140000:.2f}")
# print(f"{1000:,}")

#qs1
#एक string दी है "hello world" — उसमें से पहला character निकालो।
string = "hello world"
firstcherter = string[0]
print(firstcherter)

#qs 2
#"python" में आखिरी character निकालो (negative indexing से)।
string = "python"
negetivindex_find_cher = string[-1]
print(negetivindex_find_cher)

#qs3
#"programming" का length बताओ।
ver = "programing"
print(len(ver))

#qs4
#"hello" से "he" substring निकालो।
ver = "hello"
print(ver[0:2])

#qs5
#"hello world" में "world" मौजूद है या नहीं — in operator का उपयोग करके check करो।
string = "hello world"
print("world" in string)

#qs6
#"computer" से "put" substring slice करो।
verebal = "computer"
print(verebal[3:6])

#qs7
#"abcdefg" को reverse बताओ (सिर्फ slicing से)।
verebal = "abcdefg"
print("abcdefg"[::-1])

#QS8
#"Hello World" को lowercase करो।
VER = "Hello World"
print(ver.lower())

#qs9
#"hello world" को uppercase करो।
ver = "hello world"
print(ver.upper())

#qs9
#"hello" में "l" कितनी बार है — count method से बताओ।
ver = "hello"
print(ver.count("l"))

#10
#"hello world" में "world" को "python" से replace करो।
ver = "hello world"
print(ver.replace("world","python"))

#11
#" hello " का whitespace दोनों तरफ से हटाओ।
ver = " hello "
print(ver.strip())

#12
#"apple,banana,mango" को comma के आधार पर split करो।
ver = "apple","banana","mango"
print(",".join([ver[0],ver[1],ver[2]]))

#13
#['a', 'b', 'c'] को " - " से join करके "a - b - c" बनाओ (बस join का use करना है)।
print("-".join(['a','b','c']))

#14
#"Python Programming" check करो कि क्या यह "Python" से शुरू होता है।
ver = "python programing"
print(ver.startswith("python"))

#15
#f-string का उपयोग करके "My name is Rahul and I am 20 years old" print करो (variables से)।
name = "rahul"
age = 20
print(f"my name is {name} and i am {age} years old")

#16
#किसी number जैसे 3.14159 को दो decimal में format करो।
print(f"{3.149576:.2f}")
print(format(3.147685,".2f"))

#17
#"Hi" को 10 spaces width में center में align करो f-string formatting से।
print("\thi\t")
#origanal method
ver = "Hi"
print(f"'     '{ver}'     '")

#18
#किसी number को comma format में print करो (जैसे 10000 → 10,000)
a = 10000
print(f"{a:,}")

#19
#"hello" को "HELLO" में convert करो — लेकिन सिर्फ string methods use करके, कोई logic नहीं।
ver = "hello"
print(ver.upper())

#20
#"abracadabra" में "bra" substring का पहला index find करो।
ver = "abracadabra"
print(ver.find("bra"))

#21
#"abracadabra" में "ra" substring का आखिरी index find करो।
ver = "abracadabra"
print(ver.rfind("ra"))

#22
#"Python Is Fun" में सारे spaces को "_" से replace करो।
ver = "Python Is Fun"
print(ver.replace(" ", "_"))

#23
#"helloHELLO" में case बदल दो — uppercase lowercase swap।
ver = "helloHELLO"
print(ver.swapcase())

#24
#"123hello456" से सिर्फ "hello" निकालो slicing से (index manually find करके)।
ver = "123hello456"
print(ver[3:8])

#25
#"abcdefghijklmnop" से हर तीसरा character निकालो (सिर्फ slicing से)।
ver = "abcdefghijklmnop"
print(ver[3:4])

#26
#"reverseonlymiddle" में से सिर्फ middle के 5 characters को reverse करके दो (लेकिन पूरे string को नहीं)।
ver = "reverseonlymiddle"
result = ver[:11] + ver[11:17][::-1] + ver[17:]
print(result)

#27
#"unpredictable" के पहला, आखिरी और बीच वाला character एक ही slicing expression के ज़रिए निकालो।
ver = "unpredictable"
# len = len(ver) / 2
# print(len)
result =ver[:1] + ver[6:7] + ver[12:]
print(result)