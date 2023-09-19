//The purpose of this file is to bind the BPE C-code via python.

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
            .def(py::init<>())
            .def_property("SegBitCounter", &BITSTREAM::SegBitCounter) //
            .def_property("TotalBitCounter", &BITSTREAM::TotalBitCounter)
            .def_property("ByteBuffer_4Bytes", &BITSTREAM::ByteBuffer_4Bytes) //
            .def_property("CodeWordAlighmentBits", &BITSTREAM::CodeWordAlighmentBits)
            .def_property("CodeWord_Length", &BITSTREAM::CodeWord_Length); //
        
        py::class_<HEADER_STRUCTURE_PART1>(m, "Header_pt1")
            .def(py::init<>())
            .def_property("StartImgFlag", &HEADER_STRUCTURE_PART1::StartImgFlag) //
            .def_property("EngImgFlg", &HEADER_STRUCTURE_PART1::EngImgFlg)
            .def_property("SegmentCount_8Bits", &HEADER_STRUCTURE_PART1::SegmentCount_8Bits)
            .def_property("BitDepthDC_5Bits", &HEADER_STRUCTURE_PART1::BitDepthDC_5Bits)
            .def_property("BitDepthAC_5Bits", &HEADER_STRUCTURE_PART1::BitDepthAC_5Bits)
            .def_property("Reserved", &HEADER_STRUCTURE_PART1::Reserved)
            .def_property("Part2Flag", &HEADER_STRUCTURE_PART1::Part2Flag)
            .def_property("Part3Flag", &HEADER_STRUCTURE_PART1::Part3Flag)
            .def_property("Part4Flag", &HEADER_STRUCTURE_PART1::Part4Flag)
            .def_property("PadRows_3Bits", &HEADER_STRUCTURE_PART1::PadRows_3Bits)
            .def_property("Reserved_5Bits", &HEADER_STRUCTURE_PART1::Reserved_5Bits);

        py::class_<HEADER_STRUCTURE_PART2>(m, "Header_pt2")
            .def(py::init<>())
            .def_property("SegByteLimit_27Bits", &HEADER_STRUCTURE_PART2::SegByteLimit_27Bits) //
            .def_property("DCstop", &HEADER_STRUCTURE_PART2::DCstop) //
            .def_property("BitPlaneStop_5Bits", &HEADER_STRUCTURE_PART2::BitPlaneStop_5Bits)
            .def_property("StageStop_2Bits", &HEADER_STRUCTURE_PART2::StageStop_2Bits)
            .def_property("UseFill", &HEADER_STRUCTURE_PART2::UseFill)
            .def_property("Reserved_4Bits", &HEADER_STRUCTURE_PART2::Reserved_4Bits);
            
        py::class_<HEADER_STRUCTURE_PART3>(m, "Header_pt3")
            .def(py::init<>())
            .def_property("S_20Bits", &HEADER_STRUCTURE_PART3::S_20Bits) //
            .def_property("OptDCSelect", &HEADER_STRUCTURE_PART3::OptDCSelect) //
            .def_property("OptACSelect", &HEADER_STRUCTURE_PART3::OptACSelect)
            .def_property("Reserved_2Bits", &HEADER_STRUCTURE_PART3::Reserved_2Bits);
        
        py::class_<HEADER_STRUCTURE_PART4>(m, "Header_pt4")
            .def(py::init<>())
            .def_property("DWTType", &HEADER_STRUCTURE_PART4::DWTType) //
            .def_property("Reserved_2Bits", &HEADER_STRUCTURE_PART4::Reserved_2Bits) 
            .def_property("SignedPixels", &HEADER_STRUCTURE_PART4::SignedPixels)
            .def_property("PixelBitDepth_4Bits", &HEADER_STRUCTURE_PART4::PixelBitDepth_4Bits)
            .def_property("ImageWidth_20Bits", &HEADER_STRUCTURE_PART4::ImageWidth_20Bits) //
            .def_property("TransposeImg", &HEADER_STRUCTURE_PART4::TransposeImg)
            .def_property("CodewordLength_2Bits", &HEADER_STRUCTURE_PART4::CodewordLength_2Bits)
            .def_proper("Reserved", &HEADER_STRUCTURE_PART4::Reserved)
            .def_property("CustomWtFlag", &HEADER_STRUCTURE_PART4::CustomWtFlag)
            .def_property("CustomWtHH1_2bits", &HEADER_STRUCTURE_PART4::CustomWtHH1_2bits)
            .def_property("CustomWtHL1_2bits", &HEADER_STRUCTURE_PART4::CustomWtHL1_2bits)
            .def_property("CustomWtLH1_2bits", &HEADER_STRUCTURE_PART4::CustomWtLH1_2bits)
            .def_property("CustomWtHH2_2bits", &HEADER_STRUCTURE_PART4::CustomWtHH2_2bits)
            .def_property("CustomWtHL2_2bits", &HEADER_STRUCTURE_PART4::CustomWtHL2_2bits)
            .def_property("CustomWtLH2_2bits", &HEADER_STRUCTURE_PART4::CustomWtLH2_2bits)
            .def_property("CustomWtHH3_2bits", &HEADER_STRUCTURE_PART4::CustomWtHH3_2bits)
            .def_property("CustomWtHL3_2bits", &HEADER_STRUCTURE_PART4::CustomWtHL3_2bits)
            .def_property("CustomWtLH3_2bits", &HEADER_STRUCTURE_PART4::CustomWtLH3_2bits)
            .def_property("CustomWtLL3_2bits", &HEADER_STRUCTURE_PART4::CustomWtLL3_2bits)
            .def_property("Reserved_11Bits", &HEADER_STRUCTURE_PART4::Reserved_11Bits); //
                                                                     
        py::class_<HEADER>(m, "Header")
            .def(py::init<>())
            .def_property("Part1", &HEADER::Part1) //
            .def_property("Part2", &HEADER::Part2) //
            .def_property("Part3", &HEADER::Part3) //
            .def_property("Part4", &HEADER::Part4); //
        
        py::class_<HEADERUNION>(m, "Header_union")
            .def_property(py::init<>())
            .def_property("Header", &HEADERUNION::Header) // 
            .def_property("Field", &HEADERUNION::Field); //

        py::class_<STR_STOPLOCATION>(m, "STR_STOPLOCATION")
            .def(py::init<>())
            .def_property("BitPlaneStopDecoding", &STR_STOPLOCATION::BitPlaneStopDecoding) //
            .def_property("BlockNoStopDecoding", &STR_STOPLOCATION::BlockNoStopDecoding) //
            .def_property("TotalBitsReadThisTime", &STR_STOPLOCATION::TotalBitsReadThisTime) //
            .def_property("LocationFind", &STR_STOPLOCATION::LocationFind) //
            .def_property("X_LocationStopDecoding", &STR_STOPLOCATION::X_LocationStopDecoding)
            .def_property("Y_LocationStopDecoding", &STR_STOPLOCATION::Y_LocationStopDecoding)
            .def_property("stoppedstage", &STR_STOPLOCATION::stoppedstage);
        
        py::class_<CODINGPARAMETERS>(m, "Coding_params")
            .def(py::init<>())
            .def_property("bits", &CODINGPARAMETERS::Bits) //
            .def_property("bit_plane", &CODINGPARAMETERS::BitPlane)
            .def_property("bits_per_pixel", &CODINGPARAMETERS::BitsPerPixel)
            .def_property("DABSiS", &CODINGPARAMETERS::DecodingAllowedBitsSizeInSegment)
            .def_property("rate_reached", &CODINGPARAMETERS::RateReached)
            .def_property("dec_stop_locations", &CODINGPARAMETERS::DecodingStopLocations)
            .def_property("quant_factor", &CODINGPARAMETERS::QuantizationFactorQ)
            .def_property("block_counter", &CODINGPARAMETERS::BlockCounter)
            .def_property("block", &CODINGPARAMETERS::block_index)
            .def_property("N", &CODINGPARAMETERS::N)
            .def_property("segment_full", &CODINGPARAMETERS::SegmentFull)
            .def_property("PtrHeader", &CODINGPARAMETERS::PtrHeader)
            .def_property("ImageRows", &CODINGPARAMETERS::ImageRows)
            .def_property("ImageWidth", &CODINGPARAMETERS::ImageWidth)
            .def_property("PadCols_3Bits", &CODINGPARAMETERS::PadCols_3Bits)
            .def_property("PixelByteOrder", &CODINGPARAMETERS::PixelByteOrder)
            .def_property("InputFile", &CODINGPARAMETERS::InputFile)
            .def_property("CodingOutputFile", &CODINGPARAMETERS::CodingOutputFile);
        
        m.def("EncoderEngine", &EncoderEngine);  
        m.def("DecoderEngine", &DecoderEngine);           
        m.def("HeaderInitialization", &HeaderInilization); 
        m.def("Usage", &Usage);
        m.def("ParameterValidCheck", &ParameterValidCheck);
        m.def("command_flag_menu", &command_flag_menu);         

        //m.def("main_encode", &main_encode);             
        //m.def("main_decode", &main_decode);
}
