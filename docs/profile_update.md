Bulk Profile Update with CSV
=======
Update profiles from a local CSV file (for example, in staging):
```
eatool --env stage indico profileeditcsv 'testprofileupdateIndico.csv'
```

Update profiles from Google Sheet:
```
eatool gsuite sheetcsv https://docs.google.com/spreadsheets/.../edit | eatool indico profileeditcsv -
```

CSV Format
=======
The CSV file should follow a certain format. To ensure a smooth import, please adhere strictly to the naming conventions and data types described below.

### The Identifier Field
The command requires a unique identifier to locate the correct record. By default, the command expects a column titled **email**. If you use the `--id-field` option in the command (e.g., `--id-field employee_id`), the CSV must instead include a column matching that specific field name to serve as the unique ID.

### Header Naming & Types
Column titles in your CSV must match the field names listed below **exactly**. Differences in capitalization or spacing (e.g., using "First Name" instead of `first_name`) will result in the field being ignored by the script:

- `address`         : Text
- `affiliation`     : Text
- `cap_details`     : Text
- `country`         : Two-letter ISO country code
- `dietary_details` : Text
- `dietary_options` : A JSON-formatted array of UUIDs enclosed in quotes. See [here](https://github.com/canonical/indico-custom-profile-fields/blob/fa29efb961edbc2953832f658731415b9e9b16c8/indico_custom_profile_fields/custom_fields.json#L93) for valid values.
- `employee_id`     : Text
- `first_name`      : Text
- `group`           : Text
- `last_name`       : Text
- `legal_first`     : Text
- `legal_last`      : Text
- `nickname`        : Text
- `phone`           : Text
- `product`         : Text
- `pronouns`        : Text
- `shirt_size`      : A single unique UUID string. See [here](https://github.com/canonical/indico-custom-profile-fields/blob/fa29efb961edbc2953832f658731415b9e9b16c8/indico_custom_profile_fields/custom_fields.json#L67) for valid values.
- `title`           : Any value from `['mr', 'ms', 'mrs', 'dr', 'prof', 'mx']`

You are **not required** to include every field listed above in your CSV. The script supports partial updates. Only the identifier column (e.g., `email`) is mandatory. You may include only the identifier and the specific columns you wish to update. Any fields omitted from the CSV will remain unchanged in the system.

By default, the script skips blank cells. If you want to delete existing data, type `<CLEAR>` in the cell, and the script will clear the data.

Two example sheets that demonstrate everything mentioned can be found [here](https://docs.google.com/spreadsheets/d/1RE4aWge6-U2qBOxgptIjV7D5YinT_QiSrCv_BrJstHM/edit?usp=sharing).

