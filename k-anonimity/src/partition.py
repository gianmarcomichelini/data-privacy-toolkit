
class Partition:
    def __init__(self, dimensions, ranges, allowable_dims, members, iteration=0):
        self.dimensions = dimensions
        self.ranges = ranges
        self.allowable_dims = allowable_dims
        self.members = members  # The actual DataFrame subset
        self.iteration = iteration
        self.widths = {}
        self.medians = {}

    def __len__(self):
        return len(self.members)

    def __str__(self):
        # Determine how to print based on whether the range is a Node (categorical) or string (numerical)
        to_print = []
        for dim in self.dimensions:
            val = self.ranges[dim]
            # Check if it's an anytree Node (has a 'name' attribute)
            if hasattr(val, 'name'):
                to_print.append(val.name)
            else:
                to_print.append(val)
        return str(to_print)

    def __repr__(self):
        return self.__str__()