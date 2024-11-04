#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import pickle

from dataclasses import dataclass
from typing import List, Tuple, Any


def size_to_human(size_bytes: int) -> str:
    """Prints the given size in human-readable form.
    Args:
        size_bytes (int): The size in bytes we want to print.
    Returns:
        str: The string representing the size in human-readable form.
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%6.2f %s" % (s, size_name[i])


def bytes_to_megabytes(bytes: int) -> float:
    return (bytes / 1024) / 1024


def megabytes_to_bytes(megabytes: float) -> int:
    return int((megabytes * 1024) * 1024)


def gigabytes_to_bytes(gigabytes: float) -> int:
    return int(gigabytes * 1024 * 1024 * 1024)


class Layer:
    def __init__(self, id, memory, runtime, output_size):
        """Initialize the layer.

        Args:
            id          : The unique identifier for the layer.
            memory      : The memory usage for the layer.
            runtime     : The total execution time for the layer.
            output_size : The size of the produced output.
        """
        self.id = id
        self.memory = memory
        self.runtime = runtime
        self.output_size = output_size

    @staticmethod
    def from_dict(obj: Any) -> "Layer":
        _id = obj.get("id", "NO_ID")
        _memory = int(obj.get("memory", 0))
        _runtime = int(obj.get("runtime", 0))
        _output_size = int(obj.get("output_size", 0))
        return Layer(_id, _memory, _runtime, _output_size)

    def __str__(self):
        return f"Layer {self.id:2d}, m: {size_to_human(self.memory)}, t: {self.runtime:2d} ms, os: {size_to_human(self.output_size)}"

    def __repr__(self):
        return str(self)


class Segment:
    def __init__(self, id, avail_memory, avail_time):
        """Initialize the execution segment.

        Args:
            id           : The unique identifier for the execution segment.
            avail_memory : The available memory of the execution segment.
            avail_time   : The available time of the execution segment.
        """
        self.id = id
        self.avail_memory = avail_memory
        self.avail_time = avail_time

    @staticmethod
    def from_dict(obj: Any) -> "Segment":
        _id = obj.get("id", "NO_ID")
        _avail_memory = int(obj.get("avail_memory", 0))
        _avail_time = int(obj.get("avail_time", 0))
        return Segment(_id, _avail_memory, _avail_time)

    def __str__(self):
        return f"Segment {self.id:2d}, M: {size_to_human(self.avail_memory)}, T: {self.avail_time:2d} ms"

    def __repr__(self):
        return str(self)


@dataclass
class Allocation:
    """Allocation between segment and layers.

    Attributes
    ----------
    segment: Segment
        The segment we are allocating the layers.
    layers: List[Layer]
        The list of layers.
    """

    segment: Segment
    layers: List[Layer]

    def __init__(self, segment: Segment, layers: List[Layer]):
        """Initialize the allocations between segment and layers.

        Args:
            segment   : The segment we are allocating the layers.
            layers : The list of layers.
        """
        self.segment = segment
        self.layers = layers

    @staticmethod
    def from_dict(obj: Any) -> "Allocation":
        _segment = Segment.from_dict(obj.get("segment", {}))
        _layers = [Layer.from_dict(y) for y in obj.get("layers", [])]
        return Allocation(_segment, _layers)

    def get_used_memory(self) -> int:
        """Compute the segment used memory."""
        if self.layers:
            return sum([layer.memory for layer in self.layers])
        return 0

    def get_used_time(self) -> int:
        """Compute the segment used time."""
        if self.layers:
            return sum([layer.runtime for layer in self.layers])
        return 0

    def get_output_size(self) -> int:
        """Compute the segment output_size (using the last layer in the segment)."""
        if self.layers:
            return self.layers[-1].output_size
        return 0

    def get_split_point(self) -> Layer:
        """Returns the index of the last layer of the list."""
        if self.layers:
            return self.layers[-1]
        return None

    def __str__(self):
        s = f"Segment {self.segment.id:2d}, "
        s += f"{size_to_human(self.get_used_memory())}/{size_to_human(self.segment.avail_memory)}, "
        s += f"{self.get_used_time()}/{self.segment.avail_time:2d} ms\n"
        for layer in self.layers:
            s += f"    Layer {layer.id:2d}, "
            s += f"memory {size_to_human(layer.memory)} "
            s += f"output_size {size_to_human(layer.output_size)}\n"
        return s


class LayerData:
    def __init__(self, id, memory, n_params, runtime, output_size):
        """
        memory      : How much memory the layer occupies (bytes)
        n_params    : How many parameters it has
        runtime     : The overall runtime of the layer (ms)
        output_size : The size of its output (bytes)
        """
        self.id = id
        self.memory: int = memory
        self.n_params: int = n_params
        self.runtime: int = runtime
        self.output_size: int = output_size

    @staticmethod
    def from_dict(obj: Any) -> "LayerData":
        _id = obj.get("id", "NO_ID")
        _memory = int(obj.get("layers_mem", 0))
        _n_params = int(obj.get("layers_params", 0))
        _runtime = int(obj.get("layers_runtime", 0))
        _output_size = int(obj.get("layers_out_size", 0))
        return LayerData(_id, _memory, _n_params, _runtime, _output_size)

    def __str__(self) -> str:
        return f"LayerData {self.id:2d}, {self.n_params:12d}, {size_to_human(self.memory)}, {self.runtime:4d} ms, {size_to_human(self.output_size)}"


def get_layer_list(allocations: List[Allocation]) -> List[Layer]:
    layers = list(
        set(
            [
                layer
                for allocation in allocations
                if allocation.layers
                for layer in allocation.layers
            ]
        )
    )
    layers.sort(key=lambda l: l.id)
    return layers


def get_segment_list(allocations: List[Allocation]) -> List[Segment]:
    segments = list(set([allocation.segment for allocation in allocations]))
    segments.sort(key=lambda s: s.id)
    return segments


def get_segment_per_allocation(allocations: List[Allocation]) -> List[int]:
    return [
        allocation.segment.id
        for allocation in allocations
        if allocation.layers
        for layer in allocation.layers
    ]


def get_layer_per_allocation(allocations: List[Allocation]) -> List[int]:
    return [
        layer.id
        for allocation in allocations
        if allocation.layers
        for layer in allocation.layers
    ]


def get_splitting_points(allocations: List[Allocation]) -> List[int]:
    return [it.get_split_point() for it in allocations if it.layers]


def get_output_sizes(allocations: List[Allocation]) -> List[int]:
    return [it.get_output_size() for it in allocations if it.layers]


def get_used_memory(allocations: List[Allocation]) -> List[int]:
    return [it.get_used_memory() for it in allocations if it.layers]


def get_closest_power_of_two(value: int) -> int:
    return int(math.pow(2, math.ceil(math.log(value) / math.log(2))))


def scale_memory(allocations: List[Allocation], scale):
    for allocation in allocations:
        allocation.segment.avail_memory *= scale
        for layer in allocation.layers:
            layer.memory *= scale
            layer.output_size *= scale


def parse_layer_data(path: str) -> List[LayerData]:
    layers_data: List[LayerData] = []
    # Open the file.
    try:
        file = open(path, "rb")
    except IOError:
        input("Could not open the input file.")
        return layers_data
    # Load the file.
    unserialized = pickle.load(file)
    # Extract the lists.
    mem = unserialized["layers_mem"]
    params = unserialized["layers_params"]
    runtime = unserialized["layers_runtime"]
    out_size = unserialized["layers_out_size"]
    # Get the size.
    lengths = [len(mem), len(params), len(runtime), len(out_size)]
    # Parse the data.
    for index in range(0, min(lengths)):
        layers_data.append(
            LayerData.from_dict(
                {
                    "id": index,
                    "layers_mem": megabytes_to_bytes(mem[index]),
                    "layers_params": params[index],
                    "layers_runtime": runtime[index],
                    "layers_out_size": megabytes_to_bytes(out_size[index]),
                }
            )
        )
    return layers_data


def print_assignment_statistics(allocations: List[Allocation]) -> None:
    print("==== Layer to Segment assignment ====")
    total_memory = 0
    total_output_size = 0
    segment_output_sizes = []
    for allocation in allocations:
        # Check if there are actual layers inside this segment.
        if allocation.layers:
            # Compute the segment used memory.
            segment_memory = sum([layer.memory for layer in allocation.layers])
            # Compute the segment used time.
            segment_time = sum([layer.runtime for layer in allocation.layers])
            # Compute the segment output_size (using the last layer in the segment).
            segment_output_size = allocation.get_output_size()
            # Update the total memory.
            total_memory += segment_memory
            # Update the total output_size.
            total_output_size += segment_output_size
            # Update the list of segment latencies.
            segment_output_sizes.append(segment_output_size)
            # Print the actual info about the given execution sequence.
            print(f"Segment {allocation.segment.id}, ", end="")
            print(
                f"used memory {size_to_human(segment_memory)}/{size_to_human(allocation.segment.avail_memory)}, ",
                end="",
            )
            print(f"used time {segment_time:d}/{allocation.segment.avail_time:d} ms")
            for layer in allocation.layers:
                print(f"    Layer {layer.id}, ", end="")
                print(f"memory {size_to_human(layer.memory)} ", end="")
                print(f"output_size {size_to_human(layer.output_size)}")
            print()
    print("==== Overall statistics ====")
    print(f"Total used memory : {size_to_human(total_memory)}")
    print(f"Total output size : {size_to_human(total_output_size)}")
