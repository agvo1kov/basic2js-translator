N%=15
B%=30
C%=35
DIM M%(N%)
SUMM% = 0
A%=B%+C%
I%=5
IF A% > A% THEN
A% = 5
B% = 1
ELSE
B% = A%
END IF
WHILE I% > 5 DO
M%(I%) = 1
SUMM% = SUMM% + M%(I%)
END WHILE
STOP