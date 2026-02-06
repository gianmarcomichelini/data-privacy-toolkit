# Mondrian K-Anonymity Anonymizer

An implementation of the Mondrian multidimensional k-anonymity algorithm for tabular data anonymization. The implementation supports mixed quasi-identifiers (numerical and categorical) and applies generalization-based partitioning to guarantee k-anonymity.

The project is designed for educational and academic use, closely following standard formulations of the Mondrian algorithm presented in university lectures on data privacy.

## Overview

This project demonstrates how to achieve **k-anonymity** on tabular datasets containing sensitive information. K-anonymity ensures that each individual in a dataset cannot be distinguished from at least k-1 other individuals based on quasi-identifiers (QIs), protecting against re-identification attacks while preserving data utility for analysis.

### What is K-Anonymity?

K-anonymity is a privacy model where each record in a dataset is indistinguishable from at least k-1 other records with respect to certain identifying attributes (quasi-identifiers). This makes it difficult to re-identify individuals in the dataset.

**Key Concepts:**
- **Quasi-Identifiers (QIs):** Attributes that, when combined, could potentially identify individuals (e.g., age, gender, ZIP code)
- **Sensitive Attributes (SAs):** Private information to protect (e.g., medical diagnosis, income)
- **Identifiers:** Direct identifiers that must be removed (e.g., name)
- **Generalization:** Replacing specific values with broader categories to create equivalence classes

## Key Features

- **Recursive top-down partitioning**
- **Support for numerical and categorical quasi-identifiers**
- **Explicit generalization hierarchies** for categorical attributes
- **Greedy splitting** based on normalized dimension width
- **Guaranteed k-anonymity** for all output equivalence classes
- **Optional visualization** of equivalence classes via Excel coloring

## Dataset

The implementation uses the **Adult Census Income dataset**.


### Attribute Categories

| Category                         | Attributes |
|----------------------------------|-----------|
| **Direct Identifiers** (removed) | All columns not in QIs or sensitive |
| **Quasi-Identifiers**            | `gender`, `age`, `zip`, `country`, `education`, `marital_status`, `occupation` |
| **Sensitive Attributes**         | `race`, `income` |

## Generalization Hierarchies

Hierarchies are explicitly defined using trees (`anytree`) for categorical quasi-identifiers. Each hierarchy supports progressive generalization, from leaf values to a common ancestor.

### Supported Hierarchies

The following categorical attributes have predefined generalization hierarchies:

- **`gender`:** Gender → {Male, Female}
- **`country`:** World → Continents → Individual Countries
- **`education`:** Education → {Low, Medium, High} → Specific Degrees
- **`marital_status`:** Marital-Status → {Married, Unmarried} → Specific Statuses
- **`occupation`:** Occupation → {White-Collar, Blue-Collar, Service, Other} → Specific Jobs


## Usage

### Running the Anonymizer

1. Place the dataset in `data/adult.csv`
2. Run the script:

```bash
python main.py
```

### What the Script Does

The script performs the following steps:

1. **Loads** the Adult Census dataset
2. **Removes** direct identifiers (pseudo-anonymization)
3. **Applies** Mondrian k-anonymity algorithm
4. **Produces** an anonymized dataset with:
   - Generalized quasi-identifiers
   - Preserved sensitive attributes
5. **Saves** output files:
   - `data/anonymized_grouped.xlsx` - Excel file with colored k-anonymous groups



## Algorithm Description

The anonymization process follows the Mondrian algorithm:

1. **Initialize** a single partition containing the entire dataset.
2. **For each partition:**
   - Compute the normalized width of each quasi-identifier.
   - Select the dimension with maximum width (greedy choice).
3. **Split the partition:**
   - **Numerical attributes:** median-based interval split.
   - **Categorical attributes:** hierarchy-based generalization split.
4. **Accept a split** only if all resulting partitions contain at least k records.
5. **Recursively repeat** until no valid split exists.

Each final partition corresponds to a k-anonymous group.


### Splitting Rules

The algorithm ensures k-anonymity by enforcing:
- Each partition must have at least **2 * k members** to be splittable
- All sub-partitions after a split must have **$\ge$ k members** or be empty
- No sub-partition can have size between **1 and k-1** (non-anonymous)

## Output

### Anonymized Dataset Structure

The output dataset contains:

- **Generalized quasi-identifiers** - Replaced with broader categories or ranges
- **Preserved sensitive attributes** - Original values maintained (e.g., `race`, `income`)
- **Partition ID** - Identifies the equivalence class for each record
- **Guaranteed k-anonymity** - Each row belongs to an equivalence class of size $\ge$ k

### Excel Output

The Excel file (`anonymized_grouped.xlsx`) provides visual grouping:
- Each equivalence class is highlighted with a unique color
- Coloring is deterministic and based on `partition_id`
- Makes it easy to identify which records form equivalence classes

### Example Output

```
   gender    age         zip        country     education  marital_status  ...  partition_id
0  Gender  17-38    0-100000  North-America     Education         Married  ...             1
1  Gender  17-38    0-100000  North-America     Education         Married  ...             1
2  Gender  17-38    0-100000  North-America     Education         Married  ...             1
...
12 Gender  38-91    0-100000  North-America     Education       Unmarried  ...             2
13 Gender  38-91    0-100000  North-America     Education       Unmarried  ...             2
...
```

Notice how:
- Categorical attributes are generalized (e.g., "United-States" → "North-America")
- Numerical attributes become ranges (e.g., "25" → "17-38")
- All records with the same `partition_id` form an equivalence class

## Notes and Limitations

### Current Implementation

- **Only k-anonymity is enforced** - No ℓ-diversity or t-closeness
- **Subset processing** - Uses first 200 rows by default for performance demonstration
- **Educational focus** - Designed for clarity and correctness, not large-scale optimization
- **Fixed hierarchies** - Generalization trees are predefined and domain-specific

### Known Limitations

1. **Homogeneity Attack:** K-anonymity alone doesn't protect against diversity-based attacks (consider ℓ-diversity)
2. **Background Knowledge:** Vulnerable if attackers have additional information
3. **Scalability:** Recursive algorithm may be slow for very large datasets (>100K rows)
4. **High Dimensionality:** More quasi-identifiers increase information loss (curse of dimensionality)

### Potential Improvements

- **ℓ-diversity:** Ensure diverse sensitive values within equivalence classes
- **t-closeness:** Maintain similar distributions of sensitive attributes
- **Differential Privacy:** Add noise for stronger privacy guarantees
