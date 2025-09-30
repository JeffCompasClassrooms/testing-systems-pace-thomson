from mydb import MyDB
import os


os.remove('test_data.dat')
exists = os.path.isfile('test_data.dat') 
assert not exists
a_db = MyDB("test_data.dat")

a_list = ["Gummy", 'idk', 'mandmds']
a_db.saveStrings(a_list)

exists = os.path.isfile('test_data.dat') 
assert exists
b_list = a_db.loadStrings()

assert a_list == b_list