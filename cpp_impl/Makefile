CXX = g++
CXXFLAGS = -std=c++17 -Wall -g -fopenmp
CXXDEBUGFLAGS = -O0 -fsanitize=address -fsanitize=undefined
CXXRELEASEFLAGS = -O3 -flto

dyncurv: src/*
	$(CXX) $(CXXFLAGS) $(CXXDEBUGFLAGS) src/main.cpp src/support.cpp -o dyncurv

release: src/*
	$(CXX) $(CXXFLAGS) $(CXXRELEASEFLAGS) src/main.cpp src/support.cpp -o dyncurv

clean:
	rm -f dyncurv

.PHONY: clean
