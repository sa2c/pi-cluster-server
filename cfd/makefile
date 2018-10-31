#!smake

all : elmerpostprocessserial elmerpostprocessparallel

CC    = gcc
COPT  = -std=c++11 -w -Wno-write-strings -Wno-uninitialized -Wno-deprecated  -Wno-format -fpermissive -O2 -fopenmp

OBJFILES := $(patsubst %.cpp,%.o,$(wildcard *.cpp))


LIB   = -L/usr/lib/gcc/x86_64-linux-gnu/7 -lstdc++ \
        #-L$(VTKLIB63)

CINCL = -I /usr/include/vtk-6.3


test: $(OBJFILES)
	$(CC) $(OBJFILES)  $(LIB) -o $@

%.o: %.cpp
	$(CC) -c $(COPT)  $(CINCL) $< -o $@

elmerpostprocessserial: elmerpostprocessserial.o 
	${CXX} -o elmerpostprocessserial elmerpostprocessserial.o ${LIB}
	rm  elmerpostprocessserial.o

elmerpostprocessparallel: elmerpostprocessparallel.o 
	${CXX} -o elmerpostprocessparallel elmerpostprocessparallel.o ${LIB}
	rm  elmerpostprocessparallel.o

.PHONEY: clean
clean:
	rm *.o
	rm test.*


