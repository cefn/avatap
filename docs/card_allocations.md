Bank management
There are 16 sectors of 4 blocks
Blocks are indexed from 0 to 63
In each sector of 4 blocks, the fourth is reserved for authentications keys and permissions

```
MANUFACTURER-RESERVED 		: Block [0] 
AUTHENTICATE-RESERVED 		: Block [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63]
JSON-LENGTH 		  		: Block [1]: bytes 0,1,2 : length of json in each of three banks, in range 0-240
UNUSED				  		: Block [1(remaining), 2] 
Blocks [4-23 except auth]	: JSON Bank 1 [4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22]
Blocks [24-43 ]				: JSON Bank 2 [24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37, 38, 40, 41, 42]
Blocks [24-43 ]				: JSON Bank 3 [44, 45, 46, 48, 49, 50, 52, 53, 54, 56, 57, 58, 60, 61, 62]
```
