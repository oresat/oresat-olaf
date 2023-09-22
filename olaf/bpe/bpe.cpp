#include <Python.h>
#include <structmember.h>
#include <iostream>
#include "pybind11/pybind11.h"
#include <pybind11/pytypes.h>
#include <pybind11/numpy.h>
#include <string>
#include "source/main_pybind.h" 

namespace py = pybind11;
using namespace pybind11::literals;


PYBIND11_MODULE(bpe, m)
{
    //docstring
    m.doc() = "pybind11 bpe plugin";    
        
        py::class_<BITSTREAM>(m, "Bitstream")
            .def(py::init<unsigned long, unsigned long, unsigned int, 
                                            unsigned int, unsigned char>());

        py::class_<HEADER_STRUCTURE_PART1>(m, "Header_pt1")
            .def(py::init<bool, bool, unsigned char, unsigned char, unsigned char, 
                    bool, bool, bool, bool, unsigned char, unsigned char>());

        py::class_<HEADER_STRUCTURE_PART2>(m, "Header_pt2")
            .def(py::init<unsigned long, bool, unsigned char, unsigned char, 
                                                        bool, unsigned char>());
        py::class_<HEADER_STRUCTURE_PART3>(m, "Header_pt3")
            .def(py::init<unsigned long, bool, bool, unsigned char>());

        py::class_<HEADER_STRUCTURE_PART4>(m, "Header_pt4")
            .def(py::init<bool, unsigned char, bool, unsigned char, 
                    unsigned long, bool, unsigned char, bool, bool, unsigned char, 
                    unsigned char, unsigned char, unsigned char, unsigned char, 
                    unsigned char, unsigned char, unsigned char, unsigned char, 
                    unsigned char, unsigned short>());

        py::class_<HEADER>(m, "Header")
            .def(py::init<HEADER_STRUCTURE_PART1, HEADER_STRUCTURE_PART2, 
                            HEADER_STRUCTURE_PART3, HEADER_STRUCTURE_PART4>());
            
        py::class_<HEADERUNION>(m, "HEADERUNION")
            .def(py::init<long, long>());

        py::class_<STR_STOPLOCATION>(m, "STR_STOPLOCATION")
            .def(py::init<char, long, short, bool, char, char, unsigned char>());

        py::class_<CODINGPARAMETERS>(m, "CODINGPARAMETERS")
            .def(py::init<BITSTREAM*, unsigned char, float, unsigned long, bool, 
                    STR_STOPLOCATION, unsigned char, unsigned int, unsigned int, 
                    unsigned char, bool, HEADERUNION*, unsigned int, unsigned int, 
                    unsigned char, unsigned char, char, char>());

        m.def("EncoderEngine", &EncoderEngine);  
        m.def("DecoderEngine", &DecoderEngine);           
        m.def("HeaderInitialization", &HeaderInilization); 
        m.def("Usage", &Usage);
        m.def("ParameterValidCheck", &ParameterValidCheck);
        m.def("command_flag_menu", &command_flag_menu);         

        //m.def("main_encode", &main_encode);             
        //m.def("main_decode", &main_decode);
}
