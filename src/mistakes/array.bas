1 DIM a(3)
2 a(0) = 12
3 a(1) = 10
4 a(2) = 14
5 if a(0) > a(1) THEN a(1) = a(1) + 5
6 if a(2) > a(1) THEN a(2) = a(0) * 2
7 if a(0) < a(2) THEN GOSUB 9
8 GOSUB 5
9 STOP