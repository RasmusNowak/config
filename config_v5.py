import psycopg2
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import configurator_layout as layout
from collections import defaultdict

# Connection parameters. What elephantSQL gave me.
DATABASE = 'lytihzus'
USER = 'lytihzus'
PASSWORD = '7fXi38ffXgDuG0koLg7ZfD5FkvwQQHGE'
HOST = 'cornelius.db.elephantsql.com'
PORT = '5432'  

# Connection string. What I need to connect to elephantsql.
conn_string = f"host={HOST} port={PORT} dbname={DATABASE} user={USER} password={PASSWORD}"

# Connect to elephantsql database. This is the connection object.
conn = psycopg2.connect(conn_string)

# Select everything from elephantsql. 
query = "SELECT * FROM public.maindata"

# Load data into a pandas dataframe. 
df = pd.read_sql_query(query, conn)

# Close the connection to elephantsql.
conn.close()

# Extract columns for different categories for the drop down menus. list of unique values in each column. set() removes duplicates. dropna() removes NaN values. str.strip() removes whitespace. tolist() converts to list.
body_drawings = list(set(df["Body drawings"].dropna().str.strip().tolist()))
nrv_drawings = list(set(df["NRV drawings"].dropna().str.strip().tolist()))
piston_drawings = list(set(df["Piston drawings"].dropna().str.strip().tolist()))
fitting_drawings = list(set(df["Fitting drawings"].dropna().str.strip().tolist()))
systems = list(set(df["System"].dropna().str.strip().tolist()))

# categories is a dictionary of lists. Each list contains the unique values for each category. that I just created above.
categories = {
    'Body drawings': body_drawings,
    'NRV drawings': nrv_drawings,
    'Piston drawings': piston_drawings,
    'Fitting drawings': fitting_drawings,
    'System': systems
}

# Filter out rows with NaN in either 'Body drawings' or 'Body description' before creating the mapping
filtered_body_df = df.dropna(subset=['Body drawings', 'Body description'])
body_mapping = dict(zip(filtered_body_df['Body drawings'].str.strip(), filtered_body_df['Body description'].str.strip()))

# Filter out rows with NaN in either 'Piston drawings' or 'Piston description' before creating the mapping
filtered_piston_df = df.dropna(subset=['Piston drawings', 'Piston description'])
piston_mapping = dict(zip(filtered_piston_df['Piston drawings'].str.strip(), filtered_piston_df['Piston description'].str.strip()))

# Filter out rows with NaN in either 'NRV drawings' or 'NRV description' before creating the mapping
filtered_nrv_df = df.dropna(subset=['NRV drawings', 'NRV description'])
nrv_mapping = dict(zip(filtered_nrv_df['NRV drawings'].str.strip(), filtered_nrv_df['NRV description'].str.strip()))

print(nrv_mapping)

# Combine all mappings into one. ** unpacks the dictionaries into one. why? because I need to combine them into one dictionary. why is that i
descriptions_mapping = {**body_mapping, **piston_mapping, **nrv_mapping}

print((len(descriptions_mapping)))

number_to_description = {v: k for k, v in descriptions_mapping.items()}

print(len(number_to_description))

# Initialize the state variable at the top of your script
showing_descriptions = False

def toggle_description():
    global showing_descriptions  # Access the global variable to update it

    for category, combo in combos.items():
        current_value = combo.get()
        current_values = combo['values']

        new_values = []
        if showing_descriptions:
            # Switching from descriptions to numbers
            new_current_value = number_to_description.get(current_value, current_value)
            for val in current_values:
                new_values.append(number_to_description.get(val, val))
        else:
            # Switching from numbers to descriptions
            new_current_value = descriptions_mapping.get(current_value, current_value)
            for val in current_values:
                new_values.append(descriptions_mapping.get(val, val))

        combo['values'] = new_values
        combo.set(new_current_value)

    showing_descriptions = not showing_descriptions
    description_button.config(text="Show Numbers" if showing_descriptions else "Show Descriptions")

# This functions purpose is to sort the drawing numbers based on the selected system. 
def sort_by_system(selected_system, df, combos, categories):
    print(f"Selected system: {selected_system}")  # Debug print to ensure the correct system is selected.

    # Go through each combobox and update its values
    for category, combo in combos.items():
        if category in ['Body drawings', 'NRV drawings', 'Piston drawings', 'Fitting drawings']:
            # Get all unique drawing numbers for the category
            drawing_numbers = categories[category]
            
            # Create a filtered list based on the selected system
            filtered_numbers = []
            for number in drawing_numbers:
                # Check if the number is in the selected system
                if selected_system == "All" or df[df[category] == number]['System'].str.contains(selected_system).any():
                    filtered_numbers.append(number)
            
            # Update the combobox values for the category
            combo['values'] = filtered_numbers

def get_compatible_for_part(part, df):
    global number_to_description, showing_descriptions

    def find_compatible_parts(single_part):
        print(f"Finding compatible parts for: {single_part}")

        # Use regex to match the exact part number, to avoid partial matches.
        regex_pattern = f"\\b{single_part}\\b"
        rows_with_part = df[df['Complete drawing list'].str.contains(regex_pattern, na=False, regex=True)]
        print(f"Rows with part '{single_part}':\n{rows_with_part}")

        all_parts = set()
        for parts_list in rows_with_part['Complete drawing list']:
            # Assuming parts are separated by commas in the 'Complete drawing list'
            parts = [p.strip() for p in parts_list.split(',')]
            all_parts.update(parts)
        all_parts.discard(single_part)

        print(f"Compatible parts for '{single_part}': {all_parts}")
        return all_parts

    # Normalize the part number for consistency.
    part = part.strip()

    # Check if the part is a description and convert it to its corresponding drawing number
    if showing_descriptions and part in number_to_description:
        part = number_to_description[part]

    # Now, find compatible parts using the drawing number.
    return list(find_compatible_parts(part))

def update_combos(combos, df, categories):
    global number_to_description, showing_descriptions, descriptions_mapping
    print("Updating comboboxes based on selections...")

    selected_parts_numbers = {}
    for category, combo in combos.items():
        selected_part = combo.get()
        print(f"Selected part before conversion in category '{category}': {selected_part}")

        # Convert descriptions to numbers if showing descriptions
        if showing_descriptions:
            selected_part = number_to_description.get(selected_part, selected_part)
            print(f"Converted to number: {selected_part}")

        # Store the drawing numbers, not descriptions, for compatibility checks
        if selected_part:
            selected_parts_numbers[category] = selected_part

    # Exit if no parts are selected
    if not selected_parts_numbers:
        print("No parts are selected, resetting combos...")
        reset_combos()
        return

    # Perform compatibility checks using drawing numbers
    for category, combo in combos.items():
        if category in selected_parts_numbers:
            continue  # Skip the category if it's already selected

        all_values = categories[category]
        filtered_values = []
        for value in all_values:
            is_compatible = True
            for selected_category, selected_number in selected_parts_numbers.items():
                if selected_category != category:
                    # Convert to numbers for compatibility check
                    value_number = value if not showing_descriptions else number_to_description.get(value, value)
                    selected_number = selected_number if not showing_descriptions else number_to_description.get(selected_number, selected_number)

                    # Check compatibility using numbers
                    if not df[df[selected_category].str.contains(selected_number, na=False)][category].str.contains(value_number, na=False).any():
                        is_compatible = False
                        break

            if is_compatible:
                filtered_values.append(value)

        # Debugging: Print the filtered values to be set
        print(f"Filtered values for '{category}': {filtered_values}")

        # Convert numbers to descriptions for display if needed
        if showing_descriptions:
            filtered_values = [descriptions_mapping.get(num, num) for num in filtered_values]

        # Set the combobox values to the filtered values
        combo['values'] = filtered_values
        # Print the actual values set in the combobox
        print(f"Values set in combobox '{category}': {combo['values']}")

    print("Finished updating comboboxes.")


def show_code_number(combos, df):
    # Get the selected parts as drawing numbers or descriptions based on the toggle state
    selected_parts = [combo.get() for category, combo in combos.items() if combo.get() and category != 'System']

    if not selected_parts or len(selected_parts) < 2:
        messagebox.showwarning("Warning", "Please select at least two parts before proceeding!")
        return

    # If descriptions are shown, translate them to drawing numbers
    if showing_descriptions:
        selected_parts = [number_to_description.get(part, part) for part in selected_parts]

    # Debug prints
    print("Selected Parts:", selected_parts)

    matched_rows = df[df['Complete drawing list'].apply(lambda x: all(part in str(x) for part in selected_parts))]

    if matched_rows.empty:
        messagebox.showwarning("Warning", "No code number found for the selected combination!")
    else:
        code_number = matched_rows.iloc[0]['Code number']
        messagebox.showinfo("Code Number", f"The code number for the selected combination is: {code_number}")

def reset_combos():
    """Reset all combobox selections and show all available parts."""
    global combos, categories  # Access the global variables

    for category, combo in combos.items():
        combo.set('')  # Clear the current selection
        combo['values'] = categories[category]  # Reset the values to the original list

root = layout.setup_root()
combos, combo_frame, description_button = layout.setup_combobox_frame(root, categories, update_combos, reset_combos, show_code_number, toggle_description, sort_by_system, df)
layout.setup_header(root, combo_frame)

root.mainloop()