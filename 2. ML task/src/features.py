"""Feature contract shared by training, evaluation and inference."""

ID_COLUMN = "ID"
TARGET_COLUMN = "Marker"

# Marker encoding used in training data and holdout labels.
POSITIVE_CLASS = 1  # good / non-default
NEGATIVE_CLASS = 0  # bad / default
TARGET_MAP = {"good": POSITIVE_CLASS, "bad": NEGATIVE_CLASS}

FEATURES = [
    "Application creation month",
    "NUMBER CREDITS IN KBI 3",
    "NUMBER CREDITS IN KBI 6",
    "ADMINISTRATIVE VIOLATION",
    "CRIMINAL VIOLATION",
    "NUMBER CREDITS IN KBI",
    "NUMBER REQUESTS IN KBI",
    "NUMBER REQUESTS IN KBI ALL",
    "CLOSED CREDITS IN KBI",
    "CLOSED CREDITS IN KBI YEAR",
    "OVERDUES IN KBI",
    "DURATION LAST OVERDUE",
    "COUNTGUARANTEE",
    "COUNTCLOSEGUARANTEE",
    "COUNTOPENGUARANTEE",
    "DURATIONGREATESTDELAYLASTYEAR",
    "DURATIONGREATESTDELAYLASTALL",
    "LATECOUNTSUMM 1 7",
    "LATECOUNTSUMM 8 30",
    "LATECOUNTSUMM 31 90",
    "LATECOUNTSUMM 91 180",
    "LATECOUNTSUMM 181",
    "LATECOUNTPRC 1 7",
    "LATECOUNTPRC 8 30",
    "LATECOUNTPRC 31 90",
    "LATECOUNTPRC 91 180",
    "LATECOUNTPRC 181",
    "LATECOUNTPAY 1 7",
    "LATECOUNTPAY 8 30",
    "LATECOUNTPAY 31 90",
    "LATECOUNTPAY 91 180",
    "LATECOUNTPAY 181",
    "SEX",
    "BIRTH CNTR",
    "MARITAL STATUS",
    "CHILDREN",
    "MINORS",
    "HOMEPHONE",
    "WORKPHONE",
    "MOBILE 1",
    "REG TOWNTYPE",
    "HOME TOWNTYPE",
    "EMPLOYMENT",
    "EDUCATION",
    "PROFESSION",
    "REAL ESTATE",
    "VEHICLE",
    "PERSONNEL PHONE",
    "ACCOUNTING PHONE",
    "Age",
    "Length work",
    "Matching address of registration and residence",
    "Loans total",
    "Credit load",
]

CATEGORICAL = [
    "Application creation month",
    "DURATION LAST OVERDUE",
    "DURATIONGREATESTDELAYLASTALL",
    "SEX",
    "BIRTH CNTR",
    "MARITAL STATUS",
    "HOMEPHONE",
    "WORKPHONE",
    "MOBILE 1",
    "REG TOWNTYPE",
    "HOME TOWNTYPE",
    "EMPLOYMENT",
    "EDUCATION",
    "PROFESSION",
    "REAL ESTATE",
    "VEHICLE",
    "PERSONNEL PHONE",
    "ACCOUNTING PHONE",
    "Matching address of registration and residence",
]

NUMERICAL = [column for column in FEATURES if column not in CATEGORICAL]

REQUIRED_INPUT_COLUMNS = [ID_COLUMN] + FEATURES
