# Mondrian K-Anonymity Anonymizer

An implementation of the Mondrian multidimensional k-anonymity algorithm for tabular data anonymization. This implementation supports mixed quasi-identifiers (both numerical and categorical) and applies generalization-based partitioning to guarantee k-anonymity.

The project is designed for educational and academic use, closely following standard formulations of the Mondrian algorithm presented in university lectures on data privacy.

## Overview

This project demonstrates how to achieve **k-anonymity** on tabular datasets containing sensitive information. K-anonymity ensures that each individual in a dataset cannot be distinguished from at least k-1 other individuals based on quasi-identifiers (QIs), protecting against re-identification attacks while preserving data utility for analysis.

### What is K-Anonymity?

K-anonymity is a privacy model where each record in a dataset is indistinguishable from at least k-1 other records with respect to certain identifying attributes (quasi-identifiers). This makes it difficult to re-identify individuals in the dataset.

**Key Concepts:**

- **Identifiers (IDs):** Direct identifiers that must be removed or encrypted (e.g., name, SSN)
- **Quasi-Identifiers (QIs):** Attributes that, when combined, could potentially identify individuals (e.g., age, gender, ZIP code)
- **Sensitive Attributes (SAs):** Private information to protect (e.g., medical diagnosis, income)
- **Generalization:** Replacing specific values with broader categories or ranges to create equivalence classes
- **Equivalence Class:** A group of k or more records that share identical quasi-identifier values after generalization

## Key Features

- **Recursive top-down partitioning** following the Mondrian algorithm
- **Support for mixed quasi-identifiers** (numerical and categorical attributes)
- **Explicit generalization hierarchies** for categorical attributes using tree structures
- **Greedy dimension selection** based on normalized width
- **Guaranteed k-anonymity** for all output equivalence classes
- **Visual grouping** via colored Excel output for easy identification of equivalence classes

## Dataset

The implementation uses the **Adult Census Income dataset**, a commonly used benchmark dataset for privacy-preserving data mining tasks.

### Sample Data

#### Original Dataset (adult.csv)

The first few rows of the original dataset:

| name | ssn | gender | age | zip | country | education | marital_status | occupation | race | income |
|---|---|---|---|---|---|---|---|---|---|---|
| Karrie Trusslove | 732-14-6110 | Male | 56 | 64152 | United-States | Bachelors | Never-married | Adm-clerical | White | <=50K |
| Brandise Tripony | 150-19-2766 | Male | 35 | 61523 | United-States | Bachelors | Married-civ-spouse | Exec-managerial | White | <=50K |
| Brenn McNeely | 725-59-9860 | Male | 32 | 95668 | United-States | HS-grad | Divorced | Handlers-cleaners | White | <=50K |
| Dorry Poter | 659-57-4974 | Male | 14 | 25503 | United-States | 11th | Married-civ-spouse | Handlers-cleaners | Black | <=50K |
| Dick Honnan | 220-93-3811 | Female | 72 | 75387 | Cuba | Bachelors | Married-civ-spouse | Prof-specialty | Black | <=50K |

#### Anonymized Output (anonymized_grouped.xlsx)

After applying k-anonymity:

| gender | age | zip | country | education | marital_status | occupation | race | income | original_id | partition_id |
|---|---|---|---|---|---|---|---|---|---|---|
| Male | 1-39 | 137-47729 | World | Education | Unmarried | Occupation | Black | <=50K | 149 | 0 |
| Male | 1-39 | 137-47729 | World | Education | Unmarried | Occupation | Black | <=50K | 165 | 0 |
| Male | 1-39 | 137-47729 | World | Education | Unmarried | Occupation | White | <=50K | 41 | 0 |
| Male | 1-39 | 137-47729 | World | Education | Unmarried | Occupation | White | <=50K | 159 | 0 |
| Male | 1-39 | 137-47729 | World | Education | Unmarried | Occupation | White | <=50K | 15 | 0 |

**Key Transformations:**

- **Direct identifiers removed:** `name` and `ssn` are completely removed from the output
- **Quasi-identifiers generalized:**
  - `age`: specific values → age ranges (e.g., "56" → "1-39")
  - `zip`: specific codes → ZIP code ranges (e.g., "64152" → "137-47729")
  - `country`: specific countries → broader geographic categories (e.g., "United-States" → "World")
  - `education`, `marital_status`, `occupation`: specific values → hierarchical generalizations
- **Sensitive attributes preserved:** `race` and `income` remain unchanged
- **Equivalence classes identified:** All records with the same `partition_id` form one k-anonymous group

### Attribute Categories

| Category                         | Attributes |
|----------------------------------|-----------|
| **Direct Identifiers** (removed) | `name`, `ssn` |
| **Quasi-Identifiers** (generalized) | `gender`, `age`, `zip`, `country`, `education`, `marital_status`, `occupation` |
| **Sensitive Attributes** (preserved) | `race`, `income` |

## Algorithm Description

The anonymization process follows the **Mondrian multidimensional k-anonymity algorithm**, which uses a greedy, recursive partitioning approach:

### Algorithm Steps

1. **Initialize:** Start with a single partition containing the entire dataset
2. **For each partition:**
   - Calculate the normalized width of each quasi-identifier dimension
   - Select the dimension with maximum width (greedy heuristic)
3. **Split the partition:**
   - **Numerical attributes:** Perform median-based split to create two intervals
   - **Categorical attributes:** Use generalization hierarchy to split into sub-categories
4. **Validate split:** Accept the split only if **all** resulting sub-partitions contain at least k records
5. **Recurse:** Repeat steps 2-4 on each sub-partition until no valid splits remain
6. **Generalize:** Apply appropriate generalization to each final partition to ensure all records within it have identical quasi-identifier values

Each final partition represents a k-anonymous equivalence class.


### What the Script Does

The script performs the following operations:

1. **Loads** the Adult Census dataset from `data/adult.csv`
2. **Removes** direct identifiers (`name`, `ssn`) to perform pseudo-anonymization
3. **Applies** the Mondrian k-anonymity algorithm with configurable k value
4. **Generates** an anonymized dataset with:
   - Generalized quasi-identifiers
   - Preserved sensitive attributes
   - Partition IDs for equivalence class identification
5. **Saves** the output to:
   - `data/anonymized_grouped.xlsx` - Excel file with color-coded k-anonymous groups

### Configuration

You can adjust the following parameters in the script:

- **`k` value:** Minimum size of each equivalence class (default: 5)
- **`n_rows`:** Number of rows to process from the dataset (default: 200)
- **Quasi-identifiers:** List of columns to use as QIs
- **Sensitive attributes:** List of columns to preserve without generalization

## Output

### Anonymized Dataset Structure

The output dataset (`anonymized_grouped.xlsx`) contains:

- **Generalized quasi-identifiers:** Replaced with broader categories or ranges
- **Preserved sensitive attributes:** Original values maintained (e.g., `race`, `income`)
- **`original_id`:** Maps back to the original row in the source dataset
- **`partition_id`:** Identifies the equivalence class for each record
- **Guaranteed k-anonymity:** Each partition contains at least k records

### Excel Visualization

The Excel output provides visual grouping features:

- Each equivalence class is highlighted with a unique background color
- Colors are deterministically assigned based on `partition_id`
- Makes it easy to visually identify which records form equivalence classes
- Helps verify that each group has at least k members

### Example Output Interpretation

```
   gender    age         zip        country     education  marital_status  ...  partition_id
0  Male    1-39    137-47729        World      Education      Unmarried    ...             0
1  Male    1-39    137-47729        World      Education      Unmarried    ...             0
2  Male    1-39    137-47729        World      Education      Unmarried    ...             0
...
5  Female  40-90   100000-999999  North-America  Education      Married    ...             1
6  Female  40-90   100000-999999  North-America  Education      Married    ...             1
...
```

Notice how:
- All records with `partition_id = 0` share identical quasi-identifier values
- All records with `partition_id = 1` share different but identical quasi-identifier values
- Each partition forms a k-anonymous equivalence class
- Sensitive attributes (`race`, `income`) may vary within each partition

## Notes and Limitations

### Current Implementation Scope

- **Privacy guarantee:** Only k-anonymity is enforced (no ℓ-diversity or t-closeness)
- **Dataset size:** Uses first 200 rows by default for demonstration purposes
- **Design focus:** Optimized for educational clarity and correctness, not production-scale performance
- **Fixed hierarchies:** Generalization trees are predefined and domain-specific

### Known Limitations

#### 1. Susceptibility to Attacks

- **Homogeneity Attack:** If all records in an equivalence class have the same sensitive value, an attacker can infer it with certainty
  - *Mitigation:* Implement ℓ-diversity to ensure diverse sensitive values
- **Background Knowledge Attack:** Attackers with additional information may still re-identify individuals
  - *Mitigation:* Combine with other privacy techniques like differential privacy

#### 3. Information Loss

- **Over-generalization:** High k values or many QIs result in significant data utility loss
- **Uneven partitioning:** Some partitions may be generalized more than others
- **No utility metric:** Current implementation doesn't measure or optimize for data utility

### Potential Improvements

- **ℓ-diversity:** Ensure at least ℓ distinct sensitive values within each equivalence class
- **t-closeness:** Maintain similar distributions of sensitive attributes across partitions
- **Differential Privacy:** Add calibrated noise for stronger privacy guarantees
