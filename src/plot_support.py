#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from typing import List, Tuple

import src.data_structures as ds


markers: List[str] = ["s", "o", "x", "d", "*", "^", "d", "v", "s", "*", "^"]


def get_y_ranges(axes: List[plt.Axes]) -> Tuple[int, int]:
    return min([ax.get_ylim()[0] for ax in axes]), max(
        [ax.get_ylim()[1] for ax in axes]
    )


def plot_allocation(
    ax: plt.Axes, allocations: List[ds.Allocation], label=""
) -> plt.Line2D:
    x = ds.get_segment_per_allocation(allocations)
    y = ds.get_layer_per_allocation(allocations)
    layers = ds.get_layer_list(allocations)
    ax.set_xlabel("Segments")
    ax.set_ylabel("Layers")
    ax.set_xticks([allocation.segment.id for allocation in allocations])
    ax.set_yticks([layer.id for layer in layers])
    # Set the x-axis to integer.
    ax.get_xaxis().set_major_locator(mticker.MultipleLocator(1))
    # Plot!
    (line,) = ax.plot(x, y, label=label)
    return line


def plot_layers_memory(ax: plt.Axes, layers: List[ds.Layer], label="") -> plt.Line2D:
    x = [layer.id for layer in layers]
    y = [ds.bytes_to_megabytes(layer.memory) for layer in layers]
    # Show the major grid and style it slightly.
    ax.grid(which="major", color="#DDDDDD", linewidth=0.8)
    # Disable x-axis minor ticks.
    ax.tick_params(axis="x", which="minor", bottom=False)
    #
    ax.set_xlabel("Layers")
    ax.set_ylabel("Memory [MB]")
    # Set the x-axis to integer.
    ax.get_xaxis().set_major_locator(mticker.MultipleLocator(1))
    # Plot.
    (line,) = ax.plot(x, y, label=label)
    return line


def plot_layers_output_memory(
    ax: plt.Axes, layers: List[ds.Layer], label=""
) -> plt.Line2D:
    x = [layer.id for layer in layers]
    y = [ds.bytes_to_megabytes(layer.output_size) for layer in layers]
    # Show the major grid and style it slightly.
    ax.grid(which="major", color="#DDDDDD", linewidth=0.8)
    # Disable x-axis minor ticks.
    ax.tick_params(axis="x", which="minor", bottom=False)
    #
    ax.set_xlabel("Layers")
    ax.set_ylabel("Memory [MB]")
    # Set the x-axis to integer.
    ax.get_xaxis().set_major_locator(mticker.MultipleLocator(1))
    # Plot.
    (line,) = ax.plot(x, y, label=label)
    return line


def plot_segments_output_memory(
    ax: plt.Axes, allocations: List[ds.Allocation], label="", cumsum=False
) -> plt.Line2D:
    x = [allocation.segment.id for allocation in allocations if allocation.layers]
    y = [
        allocation.get_output_size() for allocation in allocations if allocation.layers
    ]
    if cumsum:
        y = np.cumsum(y)
    # Show the major grid and style it slightly.
    ax.grid(which="major", color="#DDDDDD", linewidth=0.8)
    # Disable x-axis minor ticks.
    ax.tick_params(axis="x", which="minor", bottom=False)
    #
    ax.set_xlabel("Segments")
    ax.set_ylabel("Output Memory [MB]")
    # Set the x-axis to integer.
    ax.get_xaxis().set_major_locator(mticker.MultipleLocator(1))
    # Plot!
    (line,) = ax.plot(x, y, label=label)
    return line


def plot_splitting_points(
    ax: plt.Axes, allocations: List[ds.Allocation], ymin: int = 0, ymax: int = 0
):
    split_layer = [it.get_split_point() for it in allocations if it.get_split_point()]
    is_first = True
    _ymin, _ymax = ax.get_ylim()
    ymin = ymin if ymin else _ymin
    ymax = ymax if ymax else _ymax
    for split in split_layer[0:-1]:
        label = "Splitting points" if is_first else ""
        ax.vlines(
            x=split.id + 0.5, ymin=ymin, ymax=ymax, ls="-.", color="purple", label=label
        )
        ax.text(split.id + 0.5, ymax, f"{split.id} ", va="top", ha="right")

        is_first = False
