p1=people.rename({"id":"ido"})
people.insert((123,"lala",0,31))
assert people!=p1
people.delete("id==123")
