#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
from ortools.sat.python import cp_model

import src.data_structures as ds


def minimize_output_size(
    layers: List[ds.Layer], segments: List[ds.Segment], verbose: bool = False
) -> List[ds.Allocation]:
    # Pre-compute some sizes, and indices.
    num_layers, num_segments = len(layers), len(segments)
    all_layers, all_segments = range(num_layers), range(num_segments)
    # Compute the maximum output size of all layers.
    max_output_size = max([layer.output_size for layer in layers])
    # Store the output size of each layer.
    output_sizes = [layer.output_size for layer in layers]

    # ==============================================
    # OPTIMIZE
    # ==============================================

    # Declare the model.
    model = cp_model.CpModel()

    # ==============================================
    # OPTIMIZE (VARIABLES)
    # ==============================================

    # Initialize the decision variable x[l, s].
    x = {}
    for l in all_layers:
        for s in all_segments:
            x[l, s] = model.NewBoolVar(f"x_{l}_{s}")

    # This decision variable will act as an index to the last layer placed in an
    # execution segment.
    i = []
    for s in all_segments:
        i.append(model.NewIntVar(lb=0, ub=num_layers, name=f"i_{s}"))

    # This decision variable will be set to the output size of the last layer
    # placed in an execution segment.
    y, _y = [], []
    for s in all_segments:
        y.append(model.NewIntVar(lb=0, ub=max_output_size, name=f"y_{s}"))
        _y.append(model.NewIntVar(lb=0, ub=max_output_size, name=f"_y_{s}"))

    # Determines if a segment is in use.
    u = []
    for s in all_segments:
        u.append(model.NewBoolVar(name=f"u_{s}"))

    # ==============================================
    # OPTIMIZE (CONSTRAINTS)
    # ==============================================

    # Each layer is assigned to exactly one execution segment.
    for l in all_layers:
        model.AddExactlyOne(x[l, s] for s in all_segments)

    # The amount of occupied memory in each execution segment cannot exceed its memory.
    for s in all_segments:
        model.Add(
            sum(x[l, s] * layers[l].memory for l in all_layers)
            <= segments[s].avail_memory
        )

    # The runtime for the layers executed in each execution segment cannot exceed its duration.
    for s in all_segments:
        model.Add(
            sum(x[l, s] * layers[l].runtime for l in all_layers)
            <= segments[s].avail_time
        )

    # The layers are placed in an ordered fashion inside the sequences.
    for s0 in all_segments:
        for l0 in all_layers:
            for s1 in range(s0 + 1, num_segments):
                for l1 in range(0, l0):
                    model.AddImplication(x[l0, s0], x[l1, s1].Not())

    # Set `u` as the maximum value between the allocations `x` of a given segment.
    for s in all_segments:
        model.AddMaxEquality(u[s], [x[l, s] for l in all_layers])

    # If a segment in position `s` is NOT used the next segment `s + 1` CANNOT be used.
    for s in range(0, num_segments - 1):
        model.AddImplication(u[s].Not(), u[s + 1].Not())

    # The index variable, will be assigned the index of the last layer placed inside
    # a segment. We use (l + 1) because the first element at index 0, is a placeholder
    # of value 0.
    for s in all_segments:
        model.AddMaxEquality(i[s], [x[l, s] * l for l in all_layers])

    # With this one, we basically implement:
    #   y[s] = output_sizes[i[s]] * u[s]
    # When writing a CP problem, we canno simply use a decision variable as index,
    # we need to do a couple of extra steps, as you might have noticed. Furthermore,
    # we conside the output size only if the segment is in use.
    for s in all_segments:
        model.AddElement(i[s], output_sizes, _y[s])
        model.AddMultiplicationEquality(y[s], [_y[s], u[s]])

    # ==============================================
    # OPTIMIZE (OBJECTIVE)
    # ==============================================

    # The following code defines the objective function for the problem. In our case
    # we want to minimize the **memory to store** in memory by the **last layer**
    # placed **inside an execution segment**.
    model.Minimize(sum(y[s] for s in all_segments))

    # ==============================================
    # OPTIMIZE (SOlVE)
    # ==============================================

    # Create the solver and run it on the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        raise Exception("The problem does not have an optimal solution.")

    # ==============================================
    # OPTIMIZE (SOLUTION)
    # ==============================================
    allocations = []
    for s in all_segments:
        layers_in_segment = [layers[l] for l in all_layers if solver.Value(x[l, s])]
        if layers_in_segment:
            allocations.append(ds.Allocation(segments[s], layers_in_segment))
    return allocations


def knapsack(
    layers: List[ds.Layer], segments: List[ds.Segment], verbose: bool = False
) -> List[ds.Allocation]:
    # Pre-compute some sizes, and indices.
    num_layers, num_segments = len(layers), len(segments)
    all_layers, all_segments = range(num_layers), range(num_segments)

    # ==============================================
    # OPTIMIZE
    # ==============================================

    # Declare the model.
    model = cp_model.CpModel()

    # ==============================================
    # OPTIMIZE (VARIABLES)
    # ==============================================

    # Initialize the decision variable x[l, s].
    x = {}
    for l in all_layers:
        for s in all_segments:
            x[l, s] = model.NewBoolVar(f"x_{l}_{s}")

    # Determines if a segment is in use.
    u = []
    for s in all_segments:
        u.append(model.NewBoolVar(name=f"u_{s}"))

    # ==============================================
    # OPTIMIZE (CONSTRAINTS)
    # ==============================================

    # Each layer is assigned to exactly one execution segment.
    for l in all_layers:
        model.AddExactlyOne(x[l, s] for s in all_segments)

    # The amount of occupied memory in each execution segment cannot exceed its memory.
    for s in all_segments:
        model.Add(
            sum(x[l, s] * layers[l].memory for l in all_layers)
            <= segments[s].avail_memory
        )

    # The runtime for the layers executed in each execution segment cannot exceed its duration.
    for s in all_segments:
        model.Add(
            sum(x[l, s] * layers[l].runtime for l in all_layers)
            <= segments[s].avail_time
        )

    # The layers are placed in an ordered fashion inside the sequences.
    for s0 in all_segments:
        for l0 in all_layers:
            for s1 in range(s0 + 1, num_segments):
                for l1 in range(0, l0):
                    model.AddImplication(x[l0, s0], x[l1, s1].Not())

    # Set `u` as the maximum value between the allocations `x` of a given segment.
    for s in all_segments:
        model.AddMaxEquality(u[s], [x[l, s] for l in all_layers])

    # If a segment in position `s` is NOT used the next segment `s + 1` CANNOT be used.
    for s in range(0, num_segments - 1):
        model.AddImplication(u[s].Not(), u[s + 1].Not())

    # ==============================================
    # OPTIMIZE (OBJECTIVE)
    # ==============================================

    # Minimize the number of used segments.
    model.Minimize(sum(u[s] for s in all_segments))

    # ==============================================
    # OPTIMIZE (SOlVE)
    # ==============================================

    # Create the solver and run it on the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        raise Exception("The problem does not have an optimal solution.")

    # ==============================================
    # OPTIMIZE (SOLUTION)
    # ==============================================
    allocations = []
    for s in all_segments:
        layers_in_segment = [layers[l] for l in all_layers if solver.Value(x[l, s])]
        if layers_in_segment:
            allocations.append(ds.Allocation(segments[s], layers_in_segment))
    return allocations
