CFLAGS=-Wall -Wextra --pedantic -g0 -O3 -std=c++0x
OPENCV=`pkg-config opencv --cflags --libs`

all: method

method:
	g++ -o method main.cpp VideoFolder.cpp Method.cpp YourMethod.cpp $(OPENCV) $(CFLAGS)

comparator:
	g++ -o comparator mainComparator.cpp VideoFolder.cpp Comparator.cpp $(OPENCV) $(CFLAGS)

clean:
	rm -rf *o comparator method