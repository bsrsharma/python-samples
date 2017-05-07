import hashlib
import random

def md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.digest()


print("Hash for 'Hello'")

hashS16 = md5("Hello")

niceStr = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def makeNiceStr(str):

   LoC = list(' '*len(str))
   
   for i in range(len(str)):
      myInt = ord(str[i])
      myInt = myInt & 31
      c = niceStr[myInt]
      LoC[i] = c
   return(''.join(LoC))


print(makeNiceStr(hashS16))
   
# hash a bunch of names

print("Delaware Pennsylvania California Texas...")
print(makeNiceStr(md5("Delaware Pennsylvania California Texas...")))

print("Ecuador Japan Bhutan Paraguay")
print(makeNiceStr(md5("Ecuador Japan Bhutan Paraguay")))

print("Russia Romania")
print(makeNiceStr(md5("Russia Romania")))

print("Turkmenistan Denmark")
print(makeNiceStr(md5("Turkmenistan Denmark")))

print("Tajikistan Jamaica")
print(makeNiceStr(md5("Tajikistan Jamaica")))

print("Panama Djibouti Nepal")
print(makeNiceStr(md5("Panama Djibouti Nepal")))

print("Bolivia Srilanka Singapore")
print(makeNiceStr(md5("Bolivia Srilanka Singapore")))


# Generate an array of random Bytes

fileHandle = open('arrs.dat', 'w')

rb = ' '*30
rbL = list(rb)
rblen = 0  # length of the random string


for i in range(10000):

    for j in range(2):
  
        for k in range (30):
            rbL[k] = chr(random.randint(0, 255))
        rblen = random.randint(1, 20) + 10
        rb = ''.join(rbL)
        rb = rb[:rblen]
        fileHandle.write(makeNiceStr(rb))
        fileHandle.write(" , ")
  
    for k in range (30):
       rbL[k] = chr(random.randint(0, 255))
    rblen = random.randint(1, 20) + 10
    rb = ''.join(rbL)
    rb = rb[:rblen]
    fileHandle.write(makeNiceStr(rb))
    fileHandle.write("\n")
	

fileHandle.close()

print("wrote arrs.dat")
