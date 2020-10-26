def load_data(data_folder):
    yield {
        "_id": "MONDO:0100096",
        "covid_phenotypes": [
            {"hp": "HP:0011899", "label": "Hyperfibrinogenemia"},
            {"hp": "HP:0025143", "label": "Chills"},
            {"hp": "HP:0025439", "label": "Pharyngitis"},
            {"hp": "HP:0002027", "label": "Abdominal pain"},
            {"hp": "HP:0032141", "label": "Precordial pain"},
            {"hp": "HP:0005403", "label": "Decrease in T cell count"},
            {"hp": "HP:0002017", "label": "Nausea and vomiting"},
            {
                "hp": "HP:0005407",
                "label": "Decreased proportion of CD4-positive T cells",
            },
            {"hp": "HP:0012649", "label": "Increased inflammatory response"},
            {"hp": "HP:0003326", "label": "Myalgia"},
            {"hp": "HP:0012735", "label": "Cough"},
            {"hp": "HP:0030783", "label": "Increased serum interleukin-6"},
            {"hp": "HP:0002098", "label": "Respiratory distress"},
            {"hp": "HP:0000224", "label": "Decreased taste sensation"},
        ],
    }