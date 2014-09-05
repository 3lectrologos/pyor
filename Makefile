.PHONY: clean

CFLAGS = $(shell python-config --cflags)
LDFLAGS = $(shell python-config --ldflags)

all: demo

demo: demo.o pyor.o
	g++ $^ $(LDFLAGS) -o demo

%.o: %.cpp
	g++ -c $(CFLAGS) $<

clean:
	rm -rf demo *.o *.log *.pyc *~
