CCDIR=/home/vagrant/c11tester-benchmarks
INCLUDE=/home/vagrant/c11tester-benchmarks/cdschecker_modified_benchmarks/include
CC=$(CCDIR)/clang
CXX=$(CCDIR)/clang++
OBJ=./obj

CXXFLAGS=-std=c++0x -pthread -Wall $(SANITIZE) -g -I$(INCLUDE)

UNAME = $(shell uname)

TESTNAME = reorder_10 loop long-race#  LB test 
all: $(TESTNAME)

CDSLIB="/home/vagrant/c11tester"

$(TESTNAME): % : %.cc
	mkdir -p $(OBJ)
	$(CXX) -o $(OBJ)/$@ $< $(CXXFLAGS) $(LDFLAGS) 

clean:
	rm -f $(OBJ)/* $(OBJ)/*.o