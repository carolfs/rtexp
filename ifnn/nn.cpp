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

#include <cmath>
#include <iostream>
#include "nn.hpp"

using namespace iznn;

Neuron::Neuron(double bias, double tau, double vrest, double vreset, double vt) :
	_expinvtau(std::exp(-1 / tau)), _vrest(vrest), _vreset(vreset), _vt(vt), _bias(bias),
			_v(vreset), _has_fired(false), _current(bias) {
}

void Neuron::advance() {
	_v = _vrest + (_v - _vrest) * _expinvtau + _current;
	if (_v >= _vt) {
		_has_fired = true;
		_v = _vreset;
	} else {
		_has_fired = false;
	}
	_current = _bias;
}

void Neuron::reset() {
	_v = _vreset;
	_has_fired = false;
	_current = _bias;
}

Network::Network(Py_ssize_t input_neurons, Py_ssize_t output_neurons,
		Py_ssize_t hidden_neurons, PyObject* parameters, double tau) :
	_neurons(input_neurons + output_neurons + hidden_neurons),
			_input_neurons(input_neurons), _output_neurons(output_neurons),
			_synapses(0) {
	if (input_neurons <= 0) {
		throw BadParameters("Bad number of input neurons");
	}
	if (output_neurons <= 0) {
		throw BadParameters("Bad number of output neurons");
	}
	if (hidden_neurons < 0) {
		throw BadParameters("Bad number of hidden neurons");
	}
	Py_ssize_t index = 0;
	for (std::vector<Neuron>::iterator n = _neurons.begin(); n != _neurons.end(); n++) {
		PyObject* ob = PySequence_GetItem(parameters, index);
		if (!ob) {
			throw BadParameters("Bad number of parameters");
		}
		double bias = PyFloat_AsDouble(ob);
		Py_DECREF(ob);
		if (PyErr_Occurred()) {
			throw BadParameters("Bad type of parameters");
		}
		*n = Neuron(bias, tau);
		index++;
	}
	_synapses.reserve(_neurons.size() * _neurons.size());
	for (std::vector<Neuron>::iterator pre = _neurons.begin(); pre
			!= _neurons.end(); pre++) {
		for (std::vector<Neuron>::iterator post = _neurons.begin(); post
				!= _neurons.end(); post++) {
			PyObject* ob = PySequence_GetItem(parameters, index);
			if (!ob) {
				throw BadParameters("Bad number of parameters");
			}
			double weight = PyFloat_AsDouble(ob);
			Py_DECREF(ob);
			if (PyErr_Occurred()) {
				throw BadParameters("Bad type of parameters");
			}
			_synapses.push_back(Synapse(&*pre, &*post, weight));
			index++;
		}
	}
}

void Network::add_input(PyObject* input) {
	for (Py_ssize_t i = 0; i < _input_neurons; i++) {
		PyObject* ob = PySequence_GetItem(input, i);
		if (!ob) {
			throw PythonError();
		}
		double current = PyFloat_AsDouble(ob);
		Py_DECREF(ob);
		if (PyErr_Occurred()) {
			throw PythonError();
		}
		_neurons[i].add_current(current);
	}
}

PyObject* Network::advance_neurons() {
	for (std::vector<Neuron>::iterator n = _neurons.begin(); n != _neurons.end(); n++) {
		n->advance();
	}
	PyObject* output = PyList_New(_output_neurons);
	if (!output) {
		throw PythonError();
	}
	std::vector<Neuron>::const_reverse_iterator n = _neurons.rbegin();
	for (Py_ssize_t i = _output_neurons - 1; i >= 0; i--) {
		PyObject* o = n->has_fired() ? Py_True : Py_False;
		Py_INCREF(o);
		PyList_SET_ITEM(output, i, o);
		n++;
	}
	return output;
}

PyObject* Network::advance(PyObject* input)
try {
	add_input(input);
	for (std::vector<Synapse>::iterator s = _synapses.begin(); s
			!= _synapses.end(); s++) {
		s->advance();
	}
	return advance_neurons();
}
catch (PythonError) {
	return 0;
}

PyObject* Network::advance_with_current(PyObject* input, double total_current)
try {
	add_input(input);
	double current = total_current;
	for (std::vector<Synapse>::iterator s = _synapses.begin(); s
			!= _synapses.end(); s++) {
		current += std::abs(s->advance());
	}
	PyObject* output = advance_neurons();
	for (std::vector<Neuron>::iterator n = _neurons.begin(); n != _neurons.end(); n++) {
		if(n->has_fired()) {
			current += ACTION_POTENTIAL_CURRENT;
		}
		current += std::abs(n->bias());
	}
	PyObject* pycurrent = PyFloat_FromDouble(current);
	if (!pycurrent) return 0;
	PyObject* out_current = PyTuple_New(2);
	if (!out_current) {
		Py_DECREF(output);
		return 0;
	}
	PyTuple_SetItem(out_current, 0, pycurrent);
	PyTuple_SetItem(out_current, 1, output);
	return out_current;
}
catch (PythonError) {
	return 0;
}

PyObject* Network::advance_with_current_and_noise(PyObject* input, PyObject* noise)
{
    double total_current = 0;
    try {
        for (Py_ssize_t i = 0; i < _neurons.size(); i++) {
            PyObject* ob = PySequence_GetItem(noise, i);
            if (!ob) {
                throw PythonError();
            }
            double current = PyFloat_AsDouble(ob);
            Py_DECREF(ob);
            if (PyErr_Occurred()) {
                throw PythonError();
            }
            _neurons[i].add_current(current);
            total_current += current;
        }
    }
    catch (PythonError) {
            return 0;
    }
	return advance_with_current(input, total_current);
}

PyObject* Network::advance_with_noise(PyObject* input, PyObject* noise)
{
    try {
        for (Py_ssize_t i = 0; i < _neurons.size(); i++) {
            PyObject* ob = PySequence_GetItem(noise, i);
            if (!ob) {
                throw PythonError();
            }
            double current = PyFloat_AsDouble(ob);
            Py_DECREF(ob);
            if (PyErr_Occurred()) {
                throw PythonError();
            }
            _neurons[i].add_current(current);
        }
    }
    catch (PythonError) {
            return 0;
    }
	return advance(input);
}

PyObject* Network::get_potentials() const
try {
	PyObject* potentials = PyTuple_New(_neurons.size());
	Py_ssize_t i = 0;
	for (std::vector<Neuron>::const_iterator n = _neurons.begin(); n != _neurons.end(); n++) {
		PyObject* potential = PyFloat_FromDouble(n->potential());
		PyTuple_SET_ITEM(potentials, i, potential);
		i++;
	}
	return potentials;
}
catch (PythonError) {
	return 0;
}

PyObject* Network::get_spikes() const
try {
	PyObject* spikes = PyTuple_New(_neurons.size());
	Py_ssize_t i = 0;
	for (std::vector<Neuron>::const_iterator n = _neurons.begin(); n != _neurons.end(); n++) {
		PyObject* spike = (n->has_fired() ? Py_True : Py_False);
		Py_INCREF(spike);
		PyTuple_SET_ITEM(spikes, i, spike);
		i++;
	}
	return spikes;
}
catch (PythonError) {
	return 0;
}

void Network::reset() {
	for (std::vector<Neuron>::iterator n = _neurons.begin(); n != _neurons.end(); n++) {
		n->reset();
	}
}
