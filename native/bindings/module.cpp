#include <Raptor/Raptor.hpp>
#include <pybind11/pybind11.h>
namespace py = pybind11;


PYBIND11_MODULE(raptor_native, m)
{
    m.doc() = "Raptor native extension";
    m.def("hello_world", Raptor::HelloWorld);
}
