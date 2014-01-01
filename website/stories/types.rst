.. link: 
.. description: 
.. tags: 
.. date: 2014/01/01 11:04:04
.. title: Types
.. slug: types


When performing selection, implicit casting will be performed, to allow the use of operators other than == and !=.

Rules
=====

 * If the string matches this regexp: ^[\+\-]{0,1}[0-9]+$ it will be casted to python's int type
 * If the string matches this regexp: ^[\+\-]{0,1}[0-9]+(\.([0-9])+)?$ it will be casted to python's float type
 * If the string matches this regexp: ^([0-9]{1,4})(\\|-|/)([0-9]{1,2})(\\|-|/)([0-9]{1,2})$ that represents YYYY-MM-DD date, and the values correctly represent a date, it will be casted to relational's internal rdate type
 * Otherwise the string will be kept as a string type.

According to the regexp, a string like '.3' will not be casted to float. I've never liked this format and hence it is forbidden in relational.

Prevent casting
===============
Consider the following relation:

id,product
113,scanner
113a,new scanner

The id field of the 1st tuple will be casted to int, but the same field of the 2nd tuple will not be casted. To avoid anomalies in queries dealing with such fields you must prevent implicit casting.
Achieving this is simple, just cast back to string, using str()

σ (str(id).endswith('3')) (products)

Type rdate
==========

Fields
 * intdate is instance of datetime.date
 * day
 * month
 * weekday
 * year

Methods:
``
__hash__,__str__,__add__,__eq__,__ge__,__gt__,__le__,__lt__,__ne__,__sub__
``

Limits:
datetime.MAXYEAR and datetime.MINYEAR are limits to the range of the possible dates, also the regexp used must be considered.
