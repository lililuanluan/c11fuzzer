CCDIR=/home/vagrant/c11tester-benchmarks
INCLUDE=/home/vagrant/c11tester-benchmarks/cdschecker_modified_benchmarks/include
CC=$(CCDIR)/clang
CXX=$(CCDIR)/clang++
OBJ=./obj

CXXFLAGS=-std=c++17 -pthread -Wall $(SANITIZE) -g -I$(INCLUDE)

UNAME = $(shell uname)

TESTNAME = demo demo2 demo3 long-race ring_buf bipartite_buf mp bipartite_buf_hard left_right reorder_10 P1#  LB test 
all: $(TESTNAME)

CDSLIB="/home/vagrant/c11tester"

$(TESTNAME): % : %.cc
	mkdir -p $(OBJ)
	$(CXX) -o $(OBJ)/$@ $< $(CXXFLAGS) $(LDFLAGS) 

clean:
	rm -f $(OBJ)/* $(OBJ)/*.o