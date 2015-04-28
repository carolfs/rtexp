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

#ifndef NN_HPP
#define NN_HPP

#include <Python.h>
#include <vector>

namespace iznn {

class Neuron {
public:
	Neuron() {
	}
	Neuron(double bias, double tau, double vrest = -65,
		   double vreset = -65, double vt = -40);
	void advance();
	void reset();
	inline double potential() const {
		return _v;
	}
	inline double bias() const {
		return _bias;
	}
	inline bool has_fired() const {
		return _has_fired;
	}
	inline void add_current(double current) {
		_current += current;
	}
	inline double current() const {
		return _current;
	}
private:
	double _expinvtau;
	double _vrest;
	double _vreset;
	double _vt;
	double _bias;
	double _v;
	bool _has_fired;
	double _current;
};

class Synapse {
public:
	Synapse() {
	}
	Synapse(Neuron* source, Neuron* dest, double weight) :
		_weight(weight), _source(source), _dest(dest) {
	}
	inline double advance() {
		if (_source->has_fired()) {
			_dest->add_current(_weight);
			return _weight;
		}
		else {
			return 0;
		}
	}
private:
	double _weight;
	Neuron* _source;
	Neuron* _dest;
};

class Network {
public:
	Network(Py_ssize_t input_neurons, Py_ssize_t output_neurons,
			Py_ssize_t hidden_neurons, PyObject* parameters, double tau);
	struct BadParameters {
		BadParameters(const char* m = "") {
			msg = m;
		}
		const char* msg;
	};
	PyObject* advance(PyObject* input);
	PyObject* advance_with_current(PyObject* input, double total_current = 0);
	PyObject* advance_with_current_and_noise(PyObject* input, PyObject* noise);
	PyObject* advance_with_noise(PyObject* input, PyObject* noise);
	PyObject* get_potentials() const;
	PyObject* get_spikes() const;
	void reset();
	Py_ssize_t get_num_input_neurons() const { return _input_neurons; }
	Py_ssize_t get_num_output_neurons() const { return _output_neurons; }
	Py_ssize_t get_num_neurons() const { return _neurons.size(); }
private:
	class PythonError {};
	void add_input(PyObject* input);
	PyObject* advance_neurons();
	static const double ACTION_POTENTIAL_CURRENT = 80;
	std::vector<Neuron> _neurons;
	Py_ssize_t _input_neurons;
	Py_ssize_t _output_neurons;
	std::vector<Synapse> _synapses;
};

}

#endif
