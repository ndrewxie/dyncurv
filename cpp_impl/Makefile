CXX = g++
CXXFLAGS = -std=c++17 -Wall -g
CXXDEBUGFLAGS = -O0 -fsanitize=address -fsanitize=undefined
CXXRELEASEFLAGS = -O3 -fassociative-math

dyncurv: src/*
	$(CXX) $(CXXFLAGS) $(CXXDEBUGFLAGS) src/main.cpp

release: src/*
	$(CXX) $(CXXFLAGS) $(CXXRELEASEFLAGS) src/main.cpp -o dyncurv

clean:
	rm -f dyncurv

.PHONY: clean