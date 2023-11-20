# Makefile for binding bpe C code program to Python
# The linker flags: -Wl,-ld_classic -undefined dynamic_lookup  
# 	are for pybind11 usage with Mac M1+ OS. Please comment out as needed.
# There are also CXX flags to ignore certain warnings stemming from the source
# 	code that may be commented out.

# select compiler for C and C++
CXX = g++

PYLIB_SRC = .

BPE_SRC = source

LINK_TARGET = bpe.so

INC_DIRS = \
		   -I$(PYLIB_SRC) \
		   -I$(BPE_SRC)

BUILD_DIR = build

PYLIB_SOURCES = $(PYLIB_SRC)/bpe.cpp \
				$(PYLIB_SRC)/main_pybind.cpp

BPE_SOURCES = \
			  $(BPE_SRC)/AC_BitPlaneCoding.c \
			  $(BPE_SRC)/StagesCodingGaggles.c \
			  $(BPE_SRC)/header.c \
			  $(BPE_SRC)/AdjustOutput.c \
			  $(BPE_SRC)/bitsIO.c \
			  $(BPE_SRC)/lifting_97M.c \
			  $(BPE_SRC)/BPEBlockCoding.c \
			  $(BPE_SRC)/bpe_decoder.c \
			  $(BPE_SRC)/lifting_97f.c \
			  $(BPE_SRC)/CoeffGroup.c \
			  $(BPE_SRC)/bpe_encoder.c \
			  $(BPE_SRC)/DC_EnDeCoding.c \
			  $(BPE_SRC)/errorhandle.c \
			  $(BPE_SRC)/ricecoding.c \
			  $(BPE_SRC)/PatternCoding.c \
			  $(BPE_SRC)/waveletbpe.c \

CXXFLAGS = \
		   -std=c++11 -g -Wall $(INC_DIRS) -fPIC \
		   $(shell python3-config --includes --cflags) \
		   $(shell python3 -m pybind11 --includes) \
		   -Wno-deprecated -Wno-unused-but-set-variable \
		   -Wno-unused-parameter -Wno-sign-compare
# above -Wno flags are to ignore certain warnings during testing

LDFLAGS = -lm $(shell python3-config --ldflags)
#-Wl,-ld_classic -undefined dynamic_lookup
# above line is for succesful compilation on Mac M1+ architecture as of: 9/23/23

OBJS = $(PYLIB_SOURCES:%.cpp=$(BUILD_DIR)/%.o) $(BPE_SOURCES:%.c=$(BUILD_DIR)/%.o)

.PHONY: all clean

$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(BUILD_DIR)/$(BPE_SRC)
	$(CXX) -c $< -o $@ $(CXXFLAGS)

$(BUILD_DIR)/%.o: %.cpp
	@mkdir -p $(BUILD_DIR)/$(BPE_SRC)
	$(CXX) -c $< -o $@ $(CXXFLAGS)

$(LINK_TARGET): $(OBJS)
	@mkdir -p $(BUILD_DIR)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

all: $(LINK_TARGET)

clean:
	rm -rf $(BUILD_DIR) $(LINK_TARGET)
