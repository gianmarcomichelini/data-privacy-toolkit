import pandas as pd
import hashlib
from src.mondrian import MondrianAnonymizer


def generate_color(val):
    """
    Generates a hex color code based on the partition ID.
    Returns a CSS-like string 'background-color: #RRGGBB'
    """
    if pd.isna(val):
        return ''
    hash_object = hashlib.md5(str(val).encode())
    hex_color = hash_object.hexdigest()[:6]
    return f'background-color: #{hex_color}'


def main():
    # 1. Load Data
    print("Loading data...")
    df = pd.read_csv('data/adult.csv')
    df['original_id'] = df.index

    # Preprocessing
    quasi_identifiers = ['gender', 'age', 'zip', 'country', 'education', 'marital_status', 'occupation']
    sensitive = ['race', 'income']
    qi_and_sensitive = set(quasi_identifiers + sensitive)

    identifiers = [col for col in df.columns if col not in qi_and_sensitive and col != 'original_id']
    df = df.drop(columns=identifiers)

    # Use subset for testing
    df_subset = df.iloc[:200].copy()

    # 2. Setup Anonymizer
    anonymizer = MondrianAnonymizer(
        df=df_subset,
        quasi_identifiers=quasi_identifiers,
        sensitive_attributes=sensitive,
        k=10
    )

    # 3. Run
    anon_df = anonymizer.run()

    # --- NEW STEP: SORT BY PARTITION ID ---
    # This groups identical colors together visually
    if 'partition_id' in anon_df.columns:
        print("Sorting records by partition to group colors...")
        anon_df = anon_df.sort_values(by='partition_id')

    print("\n--- Anonymized Data (Sorted by Group) ---")
    print(anon_df.head())

    # 4. Save to Excel with Colors
    if 'partition_id' in anon_df.columns:
        print("\nGenerating colored Excel file...")
        output_file = 'data/anonymized_grouped.xlsx'

        def highlight_partitions(row):
            color = generate_color(row['partition_id'])
            return [color] * len(row)

        styled_df = anon_df.style.apply(highlight_partitions, axis=1)

        # Engine 'openpyxl' is required for writing .xlsx files
        styled_df.to_excel(output_file, engine='openpyxl', index=False)

        print(f"Saved grouped and colored dataset to '{output_file}'")
    else:
        print("\n[!] 'partition_id' not found. Cannot color rows.")
        anon_df.to_csv('data/anonymized_adult.csv')


if __name__ == "__main__":
    main()