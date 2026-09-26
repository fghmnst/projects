CC = gcc
CFLAGS = -Wall -Wextra -std=c11

main: main.o add.o
	$(CC) $(CFLAGS) main.o add.o -o main

main.o: main.c add.h
	$(CC) $(CFLAGS) -c main.c -o main.o

add.o: add.c add.h
	$(CC) $(CFLAGS) -c add.c -o add.o

.PHONY: clean

clean:
	rm -f *.o