import copy
import pandas as pd
from .partition import Partition
from .hierarchies import build_hierarchies


class MondrianAnonymizer:
    def __init__(self, df, quasi_identifiers, sensitive_attributes, k=10):
        self.raw_data = df
        self.qis = quasi_identifiers
        self.sensitive = sensitive_attributes
        self.k = k
        self.trees = build_hierarchies()
        self.result_partitions = []

        # Determine global ranges (min-max) for numerical attributes
        # This is needed for normalized width calculations
        self.global_ranges = {}
        for col in self.qis:
            if col in self.trees:
                self.global_ranges[col] = self.trees[col]
            else:
                self.global_ranges[col] = f"{self.raw_data[col].min()}-{self.raw_data[col].max() + 1}"

    def run(self):
        """Initializes the whole partition and starts the recursion."""
        print(f"Starting Anonymization with K={self.k}...")

        # Initial allowability: All QIs are cuttable
        allowable = {k: True for k in self.qis}
        for s in self.sensitive:
            allowable[s] = False

        whole_partition = Partition(
            dimensions=self.qis,
            ranges=self.global_ranges,
            allowable_dims=allowable,
            members=self.raw_data,
            iteration=0
        )

        self._anonymise_recursive(whole_partition)
        return self._build_anonymized_df()

    def _anonymise_recursive(self, partition):
        """Core recursive logic."""

        # 1. Base Case: partition is too small to split further
        if len(partition) < 2 * self.k:
            self.result_partitions.append(partition)
            return

        # 2. Calculate widths and filter un-cuttable dimensions
        partition.widths = self._get_dimension_width(partition)

        # If width is 0, we can't cut it anymore
        for dim, width in partition.widths.items():
            if width == 0:
                partition.allowable_dims[dim] = False

        # 3. Sort dimensions by width (Greedy approach)
        # Sort descending by width
        dimension_ranking = sorted(partition.widths.items(), key=lambda item: item[1], reverse=True)
        possible_cuts = [dim for dim, w in dimension_ranking if partition.allowable_dims[dim]]

        # 4. Try to cut
        valid_split_found = False
        for dim in possible_cuts:
            sub_partitions = self._split_partition(partition, dim)

            # Check K-anonymity for sub-partitions
            # Criteria: All groups must be >= K, or we reject the split.
            # (Strictly speaking, Mondrian checks if strict K-anonymity is preserved)

            valid_counts = [len(sp) >= self.k for sp in sub_partitions]

            if all(valid_counts):
                valid_split_found = True
                for sp in sub_partitions:
                    self._anonymise_recursive(sp)
                break
            else:
                # This dimension didn't work, mark as allowable=False for this specific path
                partition.allowable_dims[dim] = False

        if not valid_split_found:
            self.result_partitions.append(partition)

    def _get_dimension_width(self, partition):
        widths = {}
        for dim in self.qis:
            if dim in self.trees:
                # Categorical width
                node = partition.ranges[dim]
                root = self.trees[dim]
                widths[dim] = len(node.leaves) / len(root.leaves) if len(root.leaves) > 0 else 0
            else:
                # Numerical width
                curr_low, curr_high = map(int, partition.ranges[dim].split('-'))

                # Global range for normalization
                glob_low, glob_high = map(int, self.global_ranges[dim].split('-'))

                curr_w = curr_high - curr_low
                glob_w = glob_high - glob_low
                widths[dim] = curr_w / glob_w if glob_w > 0 else 0
        return widths

    def _split_partition(self, partition, dim):
        sub_partitions = []

        if dim in self.trees:
            # Categorical Split
            current_node = partition.ranges[dim]
            for child in current_node.children:
                new_ranges = copy.deepcopy(partition.ranges)
                new_ranges[dim] = child

                # Filter members
                descendant_leaves = [n.name for n in child.leaves]
                # If child is a leaf itself
                if not descendant_leaves:
                    descendant_leaves = [child.name]

                # Filter dataframe
                sub_members = partition.members[partition.members[dim].isin(descendant_leaves)]

                sub_p = Partition(partition.dimensions, new_ranges, copy.deepcopy(partition.allowable_dims),
                                  sub_members, partition.iteration + 1)
                sub_partitions.append(sub_p)
        else:
            # Numerical Split (Median)
            median = int(partition.members[dim].median())
            curr_low, curr_high = map(int, partition.ranges[dim].split('-'))

            # Range 1: [low, median)
            # Range 2: [median, high)
            split_ranges = [f"{curr_low}-{median}", f"{median}-{curr_high}"]

            for r_str in split_ranges:
                r_low, r_high = map(int, r_str.split('-'))
                new_ranges = copy.deepcopy(partition.ranges)
                new_ranges[dim] = r_str

                # Filter members
                sub_members = partition.members[(partition.members[dim] >= r_low) & (partition.members[dim] < r_high)]

                sub_p = Partition(partition.dimensions, new_ranges, copy.deepcopy(partition.allowable_dims),
                                  sub_members, partition.iteration + 1)
                sub_partitions.append(sub_p)

        return sub_partitions

    def _build_anonymized_df(self):
        anon_df = pd.DataFrame()

        # Enumerate gives us a unique integer (0, 1, 2...) for each partition
        for partition_id, p in enumerate(self.result_partitions):
            p_df = pd.DataFrame()

            # 1. Fill QIs
            for col in self.qis:
                val = p.ranges[col]
                val_str = val.name if hasattr(val, 'name') else val
                p_df[col] = [val_str] * len(p)

            # 2. Fill Sensitive/Other Attributes
            for col in self.raw_data.columns:
                if col not in self.qis:
                    p_df[col] = p.members[col].values

            # 3. ADD PARTITION ID (This enables coloring)
            p_df['partition_id'] = partition_id

            # 4. Restore Index
            p_df.index = p.members.index
            anon_df = pd.concat([anon_df, p_df])

        return anon_df.sort_index()