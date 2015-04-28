//Copyright 2014, 2015 Carolina Feher da Silva
//
//This file is part of rtexp.
//
//rtexp is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//rtexp is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with rtexp.  If not, see <http://www.gnu.org/licenses/>.

#include "Python.h"
#include "nn.hpp"
#include <iostream>

namespace {

struct NetworkObject {
	PyObject_HEAD
	iznn::Network* n;
};

void Network_dealloc(NetworkObject* self) {
	delete self->n;
	Py_TYPE(self)->tp_free(reinterpret_cast<PyObject*>(self));
}

int Network_init(NetworkObject* self, PyObject* args, PyObject* kwds) {
	Py_ssize_t input_neurons;
	Py_ssize_t output_neurons;
	Py_ssize_t hidden_neurons;
	PyObject* parameters;
	double tau = 10;

	static char *kwlist[] = { "input_neurons", "output_neurons",
			"hidden_neurons", "parameters", "tau", 0 };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "nnnO|d", kwlist,
			&input_neurons, &output_neurons, &hidden_neurons, &parameters, &tau)) {
		return -1;
	}
	try {
		self->n = new iznn::Network(input_neurons, output_neurons, hidden_neurons,
				parameters, tau);
	}
	catch(iznn::Network::BadParameters n) {
		PyErr_SetString(PyExc_AttributeError, n.msg);
		return -1;
	}
	catch(...) {
		PyErr_SetString(PyExc_Exception, "Initialization error.");
		return -1;
	}
	return 0;
}

PyObject* Network_advance(NetworkObject* self, PyObject* args) {
	PyObject* inputs;
	if (!PyArg_ParseTuple(args, "O", &inputs)) {
		return 0;
	}
	return self->n->advance(inputs);
}

PyObject* Network_advance_with_current(NetworkObject* self, PyObject* args) {
	PyObject* inputs;
	if (!PyArg_ParseTuple(args, "O", &inputs)) {
		return 0;
	}
	return self->n->advance_with_current(inputs);
}

PyObject* Network_advance_with_current_and_noise(NetworkObject* self, PyObject* args) {
	PyObject* inputs;
	PyObject* noise;
	if (!PyArg_ParseTuple(args, "OO", &inputs, &noise)) {
		return 0;
	}
	return self->n->advance_with_current_and_noise(inputs, noise);
}

PyObject* Network_advance_with_noise(NetworkObject* self, PyObject* args) {
	PyObject* inputs;
	PyObject* noise;
	if (!PyArg_ParseTuple(args, "OO", &inputs, &noise)) {
		return 0;
	}
	return self->n->advance_with_noise(inputs, noise);
}

PyObject* Network_reset(NetworkObject* self) {
	self->n->reset();
	Py_RETURN_NONE;
}

PyObject* Network_num_input_neurons(NetworkObject* self) {
	return PyLong_FromSsize_t(self->n->get_num_input_neurons());
}

PyObject* Network_num_output_neurons(NetworkObject* self) {
	return PyLong_FromSsize_t(self->n->get_num_output_neurons());
}

PyObject* Network_num_neurons(NetworkObject* self) {
	return PyLong_FromSsize_t(self->n->get_num_neurons());
}

PyObject* Network_get_potentials(NetworkObject* self) {
	return self->n->get_potentials();
}

PyObject* Network_get_spikes(NetworkObject* self) {
	return self->n->get_spikes();
}

PyMethodDef network_methods[] = { { "advance",
		reinterpret_cast<PyCFunction>(Network_advance), METH_VARARGS,
		"Advances time in 1 ms, returns output." }, { "reset",
		reinterpret_cast<PyCFunction>(Network_reset), METH_NOARGS,
		"Resets all state variables." },
		{ "advance_with_current",
		reinterpret_cast<PyCFunction>(Network_advance_with_current), METH_VARARGS,
		"Advances time in 1 ms, returns (current, output)." },
		{ "advance_with_current_and_noise",
		reinterpret_cast<PyCFunction>(Network_advance_with_current_and_noise), METH_VARARGS,
		"Advances time in 1 ms, returns (current, output)." },
		{ "advance_with_noise",
		reinterpret_cast<PyCFunction>(Network_advance_with_noise), METH_VARARGS,
		"Advances time in 1 ms, returns output." }, { "num_input_neurons",
		reinterpret_cast<PyCFunction>(Network_num_input_neurons), METH_NOARGS,
		"Returns the number of input neurons." }, { "num_output_neurons",
		reinterpret_cast<PyCFunction>(Network_num_output_neurons), METH_NOARGS,
		"Returns the number of output neurons." }, { "num_neurons",
		reinterpret_cast<PyCFunction>(Network_num_neurons), METH_NOARGS,
		"Returns the number of neurons." }, { "get_potentials",
		reinterpret_cast<PyCFunction>(Network_get_potentials), METH_NOARGS,
		"Returns the current potentials of neurons." }, { "get_spikes",
		reinterpret_cast<PyCFunction>(Network_get_spikes), METH_NOARGS,
		"Returns for each neuron if it has fired." },{ 0 } };

PyTypeObject NetworkType = {
	PyVarObject_HEAD_INIT(0, 0)
	"ifnn.Network", /*tp_name*/
	sizeof(NetworkObject), /*tp_basicsize*/
	0, /*tp_itemsize*/
	reinterpret_cast<destructor>(Network_dealloc), /*tp_dealloc*/
	0, /*tp_print*/
	0, /*tp_getattr*/
	0, /*tp_setattr*/
	0, /*tp_compare*/
	0, /*tp_repr*/
	0, /*tp_as_number*/
	0, /*tp_as_sequence*/
	0, /*tp_as_mapping*/
	0, /*tp_hash */
	0, /*tp_call*/
	0, /*tp_str*/
	0, /*tp_getattro*/
	0, /*tp_setattro*/
	0, /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"Network of integrate-and-fire neurons", /* tp_doc */
	0, /* tp_traverse */
	0, /* tp_clear */
	0, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	0, /* tp_iter */
	0, /* tp_iternext */
	network_methods, /* tp_methods */
	0, /* tp_members */
	0, /* tp_getset */
	0, /* tp_base */
	0, /* tp_dict */
	0, /* tp_descr_get */
	0, /* tp_descr_set */
	0, /* tp_dictoffset */
	reinterpret_cast<initproc>(Network_init), /* tp_init */
}
;

PyModuleDef ifnn2module = {
    PyModuleDef_HEAD_INIT,
    "ifnn",
    "Integrate-and-fire neural networks.",
    -1,
    NULL, NULL, NULL, NULL, NULL
};


}

PyMODINIT_FUNC PyInit_ifnn() {
	NetworkType.tp_new = PyType_GenericNew;
	if (PyType_Ready(&NetworkType) < 0) {
		return 0;
	}
	PyObject *m = PyModule_Create(&ifnn2module);
	if (!m) {
		return 0;
	}
	Py_INCREF(&NetworkType);
	PyModule_AddObject(m, "Network", reinterpret_cast<PyObject*>(&NetworkType));
	return m;
}
