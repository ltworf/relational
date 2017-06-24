p1=people
p2=p1.rename({'id':'i'})
p2=p2.rename({'i':'id'})
assert p1==p2
assert p1._readonly
assert p2._readonly
# It is VERY important to not change the original relations
# or other tests might fail randomly, since the relations are
# only loaded once

p2.update('age==20', {'age':50})
assert p2._readonly == False
assert p1!=p2
p3 = p2.selection('age!=50')
p4 = p1.selection('age!=20')
assert p3==p4
