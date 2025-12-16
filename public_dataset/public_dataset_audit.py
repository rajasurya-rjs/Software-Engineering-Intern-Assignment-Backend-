import pandas as pd

print("\n========== TASK 2 : PUBLIC DATASET AUDIT ==========\n")

# Load public dataset
df = pd.read_csv("titanic (1).csv")

# ------------------------------
# 1. Basic Dataset Information
# ------------------------------
print("1. DATASET OVERVIEW")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}\n")

print("Column Names:")
print(list(df.columns), "\n")

# ------------------------------
# 2. Entity Identification
# ------------------------------
print("2. ENTITY IDENTIFICATION")
print("- Primary Entity Identified: Passenger")
print("- Dataset is passenger-centric with embedded attributes\n")

# ------------------------------
# 3. Attribute Analysis
# ------------------------------
print("3. ATTRIBUTE ANALYSIS")
print(df.dtypes, "\n")

# ------------------------------
# 4. Missing Values
# ------------------------------
print("4. MISSING VALUES (per column)")
missing = df.isnull().sum()
print(missing, "\n")

# ------------------------------
# 5. Duplicate Records
# ------------------------------
print("5. DUPLICATE RECORD CHECK")
print(f"Total duplicate rows: {df.duplicated().sum()}\n")

# ------------------------------
# 6. Categorical Inconsistencies
# ------------------------------
print("6. CATEGORICAL INCONSISTENCIES")
for col in df.select_dtypes(include="object").columns:
    unique_vals = df[col].dropna().unique()
    lower_vals = [str(v).lower() for v in unique_vals]
    if len(set(lower_vals)) != len(unique_vals):
        print(f"- Inconsistent casing found in column: {col}")
    else:
        print(f"- {col}: No casing inconsistency detected")

print()

# ------------------------------
# 7. Data Quality Observations
# ------------------------------
print("7. DATA QUALITY OBSERVATIONS")
print("- Dataset contains missing values (Age, Cabin, Embarked)")
print("- Categorical columns rely on free-text values")
print("- No enforced primary or foreign key constraints")
print("- Dataset is denormalized\n")

# ------------------------------
# 8. Normalization & Schema Insight
# ------------------------------
print("8. NORMALIZATION INSIGHTS")
print("- Passenger data, ticket data, and embarkation data are mixed")
print("- Would require splitting into multiple relational tables:")
print("  * passengers")
print("  * tickets")
print("  * embarkation_ports\n")

# ------------------------------
# 9. SOURCE → TARGET MAPPING
# ------------------------------
print("9. SOURCE → TARGET SCHEMA MAPPING (PostgreSQL)")

print("\nPASSENGERS TABLE")
print("PassengerId → passengers.id (PK)")
print("Name        → passengers.name")
print("Sex         → passengers.gender")
print("Age         → passengers.age")
print("Pclass      → passengers.travel_class")

print("\nTICKETS TABLE")
print("Ticket      → tickets.ticket_number")
print("Fare        → tickets.fare")
print("Cabin       → tickets.cabin (nullable)")

print("\nEMBARKATION_PORTS TABLE")
print("Embarked    → ports.port_code")

print("\n========== PUBLIC DATASET AUDIT COMPLETE ==========\n")
