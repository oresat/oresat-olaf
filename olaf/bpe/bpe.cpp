#include <Python.h>
#include <pybind11/pybind11.h>
//#include <pybind11/numpy.h>

#include "source/global.h" 


namespace py = pybind11;


PYBIND11_MODULE(bpe, m)
{
    //docstring
    m.doc() = "pybind11 bpe plugin";    
        
        py::class_<BitStream>(m, "BitStream")
            .def(py::init<>())
            .def_readonly("SegBitCounter", &BitStream::SegBitCounter)
            .def_readonly("TotalBitCounter", &BitStream::TotalBitCounter)
            .def_readonly("ByteBuffer_4Bytes", &BitStream::ByteBuffer_4Bytes)
            .def_readonly("CodeWordAlighmentBits", &BitStream::CodeWordAlighmentBits)
            .def_readonly("CodeWord_Length", &BitStream::CodeWord_Length); //

        py::class_<HeaderPart1>(m, "HeaderPart1")
            .def(py::init<>())
            .def_readonly("StartImgFlag", &HeaderPart1::StartImgFlag) //
            .def_readonly("EngImgFlg", &HeaderPart1::EngImgFlg)
            .def_readonly("SegmentCount_8Bits", &HeaderPart1::SegmentCount_8Bits)
            .def_readonly("BitDepthDC_5Bits", &HeaderPart1::BitDepthDC_5Bits)
            .def_readonly("BitDepthAC_5Bits", &HeaderPart1::BitDepthAC_5Bits)
            .def_readonly("Reserved", &HeaderPart1::Reserved)
            .def_readonly("Part2Flag", &HeaderPart1::Part2Flag)
            .def_readonly("Part3Flag", &HeaderPart1::Part3Flag)
            .def_readonly("Part4Flag", &HeaderPart1::Part4Flag)
            .def_readonly("PadRows_3Bits", &HeaderPart1::PadRows_3Bits)
            .def_readonly("Reserved_5Bits", &HeaderPart1::Reserved_5Bits);


        py::class_<HeaderPart2>(m, "HeaderPart2")
            .def(py::init<>())
            .def_readonly("SegByteLimit_27Bits", &HeaderPart2::SegByteLimit_27Bits) //
            .def_readonly("DCstop", &HeaderPart2::DCstop) //
            .def_readonly("BitPlaneStop_5Bits", &HeaderPart2::BitPlaneStop_5Bits)
            .def_readonly("StageStop_2Bits", &HeaderPart2::StageStop_2Bits)
            .def_readonly("UseFill", &HeaderPart2::UseFill)
            .def_readonly("Reserved_4Bits", &HeaderPart2::Reserved_4Bits);

        py::class_<HeaderPart3>(m, "HeaderPart3")
            .def_readonly("S_20Bits", &HeaderPart3::S_20Bits) //
            .def_readonly("OptDCSelect", &HeaderPart3::OptDCSelect) //
            .def_readonly("OptACSelect", &HeaderPart3::OptACSelect)
            .def_readonly("Reserved_2Bits", &HeaderPart3::Reserved_2Bits);

        py::class_<HeaderPart4>(m, "HeaderPart4")
            .def(py::init<>())
            .def_readonly("DWTType", &HeaderPart4::DWTType) //
            .def_readonly("Reserved_2Bits", &HeaderPart4::Reserved_2Bits) 
            .def_readonly("SignedPixels", &HeaderPart4::SignedPixels)
            .def_readonly("PixelBitDepth_4Bits", &HeaderPart4::PixelBitDepth_4Bits)
            .def_readonly("ImageWidth_20Bits", &HeaderPart4::ImageWidth_20Bits) //
            .def_readonly("TransposeImg", &HeaderPart4::TransposeImg)
            .def_readonly("CodewordLength_2Bits", &HeaderPart4::CodewordLength_2Bits)
            .def_readonly("Reserved", &HeaderPart4::Reserved)
            .def_readonly("CustomWtFlag", &HeaderPart4::CustomWtFlag)
            .def_readonly("CustomWtHH1_2bits", &HeaderPart4::CustomWtHH1_2bits)
            .def_readonly("CustomWtHL1_2bits", &HeaderPart4::CustomWtHL1_2bits)
            .def_readonly("CustomWtLH1_2bits", &HeaderPart4::CustomWtLH1_2bits)
            .def_readonly("CustomWtHH2_2bits", &HeaderPart4::CustomWtHH2_2bits)
            .def_readonly("CustomWtHL2_2bits", &HeaderPart4::CustomWtHL2_2bits)
            .def_readonly("CustomWtLH2_2bits", &HeaderPart4::CustomWtLH2_2bits)
            .def_readonly("CustomWtHH3_2bits", &HeaderPart4::CustomWtHH3_2bits)
            .def_readonly("CustomWtHL3_2bits", &HeaderPart4::CustomWtHL3_2bits)
            .def_readonly("CustomWtLH3_2bits", &HeaderPart4::CustomWtLH3_2bits)
            .def_readonly("CustomWtLL3_2bits", &HeaderPart4::CustomWtLL3_2bits)
            .def_readonly("Reserved_11Bits", &HeaderPart4::Reserved_11Bits); //

        py::class_<StructHeader>(m, "StructHeader")
            .def(py::init<>())
            .def_readonly("Part1", &StructHeader::Part1) //
            .def_readonly("Part2", &StructHeader::Part2) //
            .def_readonly("Part3", &StructHeader::Part3) //
            .def_readonly("Part4", &StructHeader::Part4); //
            
        py::class_<HeaderStruct>(m, "HeaderStruct")
            .def(py::init<>())
            .def_readonly("Header", &HeaderStruct::Header) // 
            .def_readonly("Field", &HeaderStruct::Field); //

        py::class_<StrStopLocation>(m, "StrStopLocation")
            .def(py::init<>())
            .def_readonly("BitPlaneStopDecoding", &StrStopLocation::BitPlaneStopDecoding) //
            .def_readonly("BlockNoStopDecoding", &StrStopLocation::BlockNoStopDecoding) //
            .def_readonly("TotalBitsReadThisTime", &StrStopLocation::TotalBitsReadThisTime) //
            .def_readonly("LocationFind", &StrStopLocation::LocationFind) //
            .def_readonly("X_LocationStopDecoding", &StrStopLocation::X_LocationStopDecoding)
            .def_readonly("Y_LocationStopDecoding", &StrStopLocation::Y_LocationStopDecoding)
            .def_readonly("stoppedstage", &StrStopLocation::stoppedstage);

        py::class_<StructCodingPara>(m, "StructCodingPara")
            .def(py::init<>())
            .def_readonly("Bits", &StructCodingPara::Bits) //
            .def_readonly("BitPlane", &StructCodingPara::BitPlane)
            .def_readonly("BitsPerPixel", &StructCodingPara::BitsPerPixel)
            .def_readonly("DecodingAllowedBitsSizeInSegment", &StructCodingPara::DecodingAllowedBitsSizeInSegment)
            .def_readonly("RateReached", &StructCodingPara::RateReached)
            .def_readonly("DecodingStopLocations", &StructCodingPara::DecodingStopLocations)
            .def_readonly("QuantizationFactorQ", &StructCodingPara::QuantizationFactorQ)
            .def_readonly("BlockCounter", &StructCodingPara::BlockCounter)
            .def_readonly("block_index", &StructCodingPara::block_index)
            .def_readonly("N", &StructCodingPara::N)
            .def_readonly("SegmentFull", &StructCodingPara::SegmentFull)
            .def_readonly("PtrHeader", &StructCodingPara::PtrHeader)
            .def_readonly("ImageRows", &StructCodingPara::ImageRows)
            .def_readonly("ImageWidth", &StructCodingPara::ImageWidth)
            .def_readonly("PadCols_3Bits", &StructCodingPara::PadCols_3Bits)
            .def_readonly("PixelByteOrder", &StructCodingPara::PixelByteOrder)
            .def_readonly("InputFile", &StructCodingPara::InputFile)
            .def_readonly("CodingOutputFile", &StructCodingPara::CodingOutputFile);

        m.def("Usage", &Usage);
        m.def("ParameterValidCheck", &ParameterValidCheck);
        m.def("command_menu", &command_menu);    
        //m.def("command_flag_menu", &command_flag_menu, py::arg("argc"), py::arg("argv"));         

        //m.def("main_encode", &main_encode);             
        //m.def("main_decode", &main_decode);
}
