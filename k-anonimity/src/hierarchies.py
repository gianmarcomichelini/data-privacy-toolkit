from anytree import Node


def build_hierarchies():
    """
    Constructs the generalization hierarchies for categorical attributes.
    Returns a dictionary {attribute_name: root_node}.
    """
    # --- Country ---
    country_root = Node("World")
    n_america = Node("North-America", parent=country_root)
    cs_america = Node("Centre-South-America", parent=country_root)
    asia = Node("Asia", parent=country_root)
    europe = Node("Europe", parent=country_root)

    for country in ['Canada', 'Mexico', 'United-States']:
        Node(country, parent=n_america)
    for country in ["Columbia", "Cuba", "Dominican Republic", "Ecuador", "El-Salvador",
                    "Guatemala", "Haiti", "Honduras", "Jamaica", "Nicaragua",
                    "Outlying-US(Guam-USVI-etc)", "Peru", "Puerto-Rico", "Trinidad&Tobago"]:
        Node(country, parent=cs_america)
    for country in ["Cambodia", "China", "Hong", "India", "Iran", "Japan", "Laos",
                    "Philippines", "South", "Taiwan", "Thailand", "Vietnam"]:
        Node(country, parent=asia)
    for country in ['England', 'France', 'Germany', 'Greece', 'Holand-Netherlands',
                    'Hungary', 'Ireland', 'Italy', 'Poland', 'Portugal', 'Scotland',
                    'Yugoslavia']:
        Node(country, parent=europe)

    # --- Gender ---
    gender_root = Node('Gender')
    Node('Male', parent=gender_root)
    Node('Female', parent=gender_root)

    # --- Marital Status ---
    marital_root = Node("Marital-Status")
    unmarried = Node("Unmarried", parent=marital_root)
    married = Node("Married", parent=marital_root)
    for status in ['Never-married', 'Divorced', 'Separated', 'Widowed']:
        Node(status, parent=unmarried)
    for status in ['Married-civ-spouse', 'Married-spouse-absent', 'Married-AF-spouse']:
        Node(status, parent=married)

    # --- Education ---
    education_root = Node("Education")
    low = Node("Low", parent=education_root)
    medium = Node("Medium", parent=education_root)
    high = Node("High", parent=education_root)
    for edu in ['Kinder', 'Preschool', '1st-4th', '5th-6th', '7th-8th', '9th', '10th', '11th', '12th']:
        Node(edu, parent=low)
    for edu in ['HS-grad', 'Some-college', 'Assoc-acdm', 'Assoc-voc', 'Prof-school']:
        Node(edu, parent=medium)
    for edu in ['Bachelors', 'Masters', 'Doctorate']:
        Node(edu, parent=high)

    # --- Occupation ---
    occupation_root = Node("Occupation")
    white_collar = Node("White-Collar", parent=occupation_root)
    blue_collar = Node("Blue-Collar", parent=occupation_root)
    service = Node("Service", parent=occupation_root)
    other = Node("Other", parent=occupation_root)
    for occ in ['Adm-clerical', 'Exec-managerial', 'Prof-specialty', 'Sales', 'Tech-support']:
        Node(occ, parent=white_collar)
    for occ in ['Craft-repair', 'Machine-op-inspct', 'Handlers-cleaners', 'Transport-moving', 'Farming-fishing']:
        Node(occ, parent=blue_collar)
    for occ in ['Other-service', 'Priv-house-serv', 'Protective-serv']:
        Node(occ, parent=service)
    for occ in ['Armed-Forces', 'Baby']:
        Node(occ, parent=other)

    return {
        'gender': gender_root,
        'country': country_root,
        'education': education_root,
        'marital_status': marital_root,
        'occupation': occupation_root
    }