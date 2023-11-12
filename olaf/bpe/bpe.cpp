#include <Python.h>
#include <pybind11/pybind11.h>
#include "source/global.h" 

namespace py = pybind11;

PYBIND11_MODULE(bpe, m)
{
    //docstring
    m.doc() = "pybind11 bpe plugin";    

    m.def("encode_basearg", &encode_basearg);             
    m.def("encode_fullarg", &encode_fullarg);             
    m.def("decode", &decode);
}
