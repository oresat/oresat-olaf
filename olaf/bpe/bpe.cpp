#include <Python.h>
#include <pybind11/pybind11.h>
//#include <pybind11/numpy.h>
#include "source/main_pybind.h" 

namespace py = pybind11;


PYBIND11_MODULE(bpe, m)
{
    //docstring
    m.doc() = "pybind11 bpe plugin";    
        
        py::class_<BITSTREAM>(m, "Bitstream")
            .def(py::init<>())
            .def_readonly("SegBitCounter", &BITSTREAM::SegBitCounter) //
            .def_readonly("TotalBitCounter", &BITSTREAM::TotalBitCounter)
            .def_readonly("ByteBitBuffer", &BITSTREAM::ByteBuffer_4Bytes) //
            .def_readonly("CodeWordAlignmentBits", &BITSTREAM::CodeWordAlighmentBits)
            .def_readonly("CodeWord_Length", &BITSTREAM::CodeWord_Length); //

        py::class_<HEADER_STRUCTURE_PART1>(m, "Header_pt1")
            .def(py::init<>())
            .def_readonly("StartImgFlag", &HEADER_STRUCTURE_PART1::StartImgFlag) //
            .def_readonly("EngImgFlg", &HEADER_STRUCTURE_PART1::EngImgFlg)
            .def_readonly("SegmentCount_8Bits", &HEADER_STRUCTURE_PART1::SegmentCount_8Bits)
            .def_readonly("BitDepthDC_5Bits", &HEADER_STRUCTURE_PART1::BitDepthDC_5Bits)
            .def_readonly("BitDepthAC_5Bits", &HEADER_STRUCTURE_PART1::BitDepthAC_5Bits)
            .def_readonly("Reserved", &HEADER_STRUCTURE_PART1::Reserved)
            .def_readonly("Part2Flag", &HEADER_STRUCTURE_PART1::Part2Flag)
            .def_readonly("Part3Flag", &HEADER_STRUCTURE_PART1::Part3Flag)
            .def_readonly("Part4Flag", &HEADER_STRUCTURE_PART1::Part4Flag)
            .def_readonly("PadRows_3Bits", &HEADER_STRUCTURE_PART1::PadRows_3Bits)
            .def_readonly("Reserved_5Bits", &HEADER_STRUCTURE_PART1::Reserved_5Bits);


        py::class_<HEADER_STRUCTURE_PART2>(m, "Header_pt2")
            .def(py::init<>())
            .def_readonly("SegByteLimit_27Bits", &HEADER_STRUCTURE_PART2::SegByteLimit_27Bits) //
            .def_readonly("DCstop", &HEADER_STRUCTURE_PART2::DCstop) //
            .def_readonly("BitPlaneStop_5Bits", &HEADER_STRUCTURE_PART2::BitPlaneStop_5Bits)
            .def_readonly("StageStop_2Bits", &HEADER_STRUCTURE_PART2::StageStop_2Bits)
            .def_readonly("UseFill", &HEADER_STRUCTURE_PART2::UseFill)
            .def_readonly("Reserved_4Bits", &HEADER_STRUCTURE_PART2::Reserved_4Bits);

        py::class_<HEADER_STRUCTURE_PART3>(m, "Header_pt3")
            .def_readonly("S_20Bits", &HEADER_STRUCTURE_PART3::S_20Bits) //
            .def_readonly("OptDCSelect", &HEADER_STRUCTURE_PART3::OptDCSelect) //
            .def_readonly("OptACSelect", &HEADER_STRUCTURE_PART3::OptACSelect)
            .def_readonly("Reserved_2Bits", &HEADER_STRUCTURE_PART3::Reserved_2Bits);

        py::class_<HEADER_STRUCTURE_PART4>(m, "Header_pt4")
            .def(py::init<>())
            .def_readonly("DWTType", &HEADER_STRUCTURE_PART4::DWTType) //
            .def_readonly("Reserved_2Bits", &HEADER_STRUCTURE_PART4::Reserved_2Bits) 
            .def_readonly("SignedPixels", &HEADER_STRUCTURE_PART4::SignedPixels)
            .def_readonly("PixelBitDepth_4Bits", &HEADER_STRUCTURE_PART4::PixelBitDepth_4Bits)
            .def_readonly("ImageWidth_20Bits", &HEADER_STRUCTURE_PART4::ImageWidth_20Bits) //
            .def_readonly("TransposeImg", &HEADER_STRUCTURE_PART4::TransposeImg)
            .def_readonly("CodewordLength_2Bits", &HEADER_STRUCTURE_PART4::CodewordLength_2Bits)
            .def_readonly("Reserved", &HEADER_STRUCTURE_PART4::Reserved)
            .def_readonly("CustomWtFlag", &HEADER_STRUCTURE_PART4::CustomWtFlag)
            .def_readonly("CustomWtHH1_2bits", &HEADER_STRUCTURE_PART4::CustomWtHH1_2bits)
            .def_readonly("CustomWtHL1_2bits", &HEADER_STRUCTURE_PART4::CustomWtHL1_2bits)
            .def_readonly("CustomWtLH1_2bits", &HEADER_STRUCTURE_PART4::CustomWtLH1_2bits)
            .def_readonly("CustomWtHH2_2bits", &HEADER_STRUCTURE_PART4::CustomWtHH2_2bits)
            .def_readonly("CustomWtHL2_2bits", &HEADER_STRUCTURE_PART4::CustomWtHL2_2bits)
            .def_readonly("CustomWtLH2_2bits", &HEADER_STRUCTURE_PART4::CustomWtLH2_2bits)
            .def_readonly("CustomWtHH3_2bits", &HEADER_STRUCTURE_PART4::CustomWtHH3_2bits)
            .def_readonly("CustomWtHL3_2bits", &HEADER_STRUCTURE_PART4::CustomWtHL3_2bits)
            .def_readonly("CustomWtLH3_2bits", &HEADER_STRUCTURE_PART4::CustomWtLH3_2bits)
            .def_readonly("CustomWtLL3_2bits", &HEADER_STRUCTURE_PART4::CustomWtLL3_2bits)
            .def_readonly("Reserved_11Bits", &HEADER_STRUCTURE_PART4::Reserved_11Bits); //

        py::class_<HEADER>(m, "Header")
            .def(py::init<>())
            .def_readonly("Part1", &HEADER::Part1) //
            .def_readonly("Part2", &HEADER::Part2) //
            .def_readonly("Part3", &HEADER::Part3) //
            .def_readonly("Part4", &HEADER::Part4); //
            
        py::class_<HEADERUNION>(m, "Header_union")
            .def(py::init<>())
            .def_readonly("Header", &HEADERUNION::Header) // 
            .def_readonly("Field", &HEADERUNION::Field); //

        py::class_<STR_STOPLOCATION>(m, "STR_STOPLOCATION")
            .def(py::init<>())
            .def_readonly("BitPlaneStopDecoding", &STR_STOPLOCATION::BitPlaneStopDecoding) //
            .def_readonly("BlockNoStopDecoding", &STR_STOPLOCATION::BlockNoStopDecoding) //
            .def_readonly("TotalBitsReadThisTime", &STR_STOPLOCATION::TotalBitsReadThisTime) //
            .def_readonly("LocationFind", &STR_STOPLOCATION::LocationFind) //
            .def_readonly("X_LocationStopDecoding", &STR_STOPLOCATION::X_LocationStopDecoding)
            .def_readonly("Y_LocationStopDecoding", &STR_STOPLOCATION::Y_LocationStopDecoding)
            .def_readonly("stoppedstage", &STR_STOPLOCATION::stoppedstage);

        py::class_<CODINGPARAMETERS>(m, "Coding_params")
            .def(py::init<>())
            .def_readonly("bits", &CODINGPARAMETERS::Bits) //
            .def_readonly("bit_plane", &CODINGPARAMETERS::BitPlane)
            .def_readonly("bits_per_pixel", &CODINGPARAMETERS::BitsPerPixel)
            .def_readonly("DecodingAllowedBitsSizeInSegment", &CODINGPARAMETERS::DecodingAllowedBitsSizeInSegment)
            .def_readonly("rate_reached", &CODINGPARAMETERS::RateReached)
            .def_readonly("decod_stop_locations", &CODINGPARAMETERS::DecodingStopLocations)
            .def_readonly("quant_factor", &CODINGPARAMETERS::QuantizationFactorQ)
            .def_readonly("block_counter", &CODINGPARAMETERS::BlockCounter)
            .def_readonly("block_index", &CODINGPARAMETERS::block_index)
            .def_readonly("N", &CODINGPARAMETERS::N)
            .def_readonly("segment_full", &CODINGPARAMETERS::SegmentFull)
            .def_readonly("PtrHeader", &CODINGPARAMETERS::PtrHeader)
            .def_readonly("ImageRows", &CODINGPARAMETERS::ImageRows)
            .def_readonly("ImageWidth", &CODINGPARAMETERS::ImageWidth)
            .def_readonly("PadCols_3Bits", &CODINGPARAMETERS::PadCols_3Bits)
            .def_readonly("PixelByteOrder", &CODINGPARAMETERS::PixelByteOrder)
            .def_readonly("InputFile", &CODINGPARAMETERS::InputFile)
            .def_readonly("CodingOutputFile", &CODINGPARAMETERS::CodingOutputFile);

        m.def("EncoderEngine", &EncoderEngine);  
        m.def("DecoderEngine", &DecoderEngine);           
        m.def("HeaderInitialization", &HeaderInilization); 
        m.def("Usage", &Usage);
        m.def("ParameterValidCheck", &ParameterValidCheck);
        m.def("command_flag_menu", &command_flag_menu);         

        //m.def("main_encode", &main_encode);             
        //m.def("main_decode", &main_decode);
}
