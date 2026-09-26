CC = gcc
CFLAGS = -Wall -Wextra -std=c17 -g

note-stats: note-stats.o
	$(CC) $(CFLAGS) note-stats.o -o note-stats

note-stats.o: note-stats.c
	$(CC) $(CFLAGS) -c note-stats.c -o note-stats.o

.PHONY: clean

clean:
	rm -f *.o note-stats