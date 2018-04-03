import pandas as pd
import glob
import os

def cvs_directory_to_excel(excel_writer, csv_directory, table_index_sheet='_table_index_', **kwargs):
    '''
    Read all .csv files in the csv_directory and add each as a sheet to the excel_writer.
    Sheet name is the .csv file name.
    Truncates the sheet name at a maximum length of 31 (the Excel limit).
    Adds a '_table_index_' sheet which maps the table name to the (abbreviated) sheet name.

    :param excel_writer: pandas.ExcelWriter
    :param csv_directory: path to directory with .csv files
    :param table_index_sheet: str - name of the index sheet. If None, no index sheet is generated
    :param kwargs: Additional named arguments are passed in the pd.read_csv() function
    :returns: None
    '''

    def create_truncted_post_fixed_name(long_name, max_length, index):
        '''
        Create a trunced name post-fixed with '_<index>' where the total length of the string <= max_length
        '''
        post_fix = '_' + str(index)
        return long_name[:max_length - len(post_fix)] + post_fix

    def create_unique_abbreviated_name(long_name, max_length, existing_names):
        '''
        Create a unique, abbrevated name such that it is not a member of the existing_names set.
        Name is made unique by post-fixing '_<index>' where index is an increasing integer, starting at 0
        '''
        name = long_name
        if len(name) > max_length:
            name = create_truncted_post_fixed_name(long_name, max_length, 0)
        for index in range(1, 9999):
            if name in existing_names:
                name = create_truncted_post_fixed_name(long_name, max_length, index)
            else:
                break
        return name

    # ---------------------

    table_index = []  # to hold dicts with keys 'table_name', 'sheet_name'
    sheet_names = set()

    for file_path in glob.glob(os.path.join(csv_directory, "*.csv")):  # os.path.join is safe for both Unix and Win
        # Read csv
        df = pd.read_csv(file_path, **kwargs)
        head, tail = os.path.split(file_path)
        table_name = tail[:-4]  # remove the '.csv'

        # Write in Excel
        sheet_name = create_unique_abbreviated_name(table_name, 31,
                                                    sheet_names)  # truncate table name to 31 characters due to sheet name limit in Excel
        sheet_names.add(sheet_name)
        df.to_excel(excel_writer, sheet_name, index=False)

        # Store row in table_index
        table_index.append({'table_name': table_name, 'sheet_name': sheet_name})

    # Add table_index sheet if applicable:
    if (len(table_index) > 0) & (table_index_sheet is not None):
        index_df = pd.DataFrame(table_index)
        index_df.to_excel(excel_writer, table_index_sheet, index=False)


def read_dataframes_from_excel(xl, table_index_sheet='_table_index_'):
    '''
    Create dataFrames from the sheets of the Excel file.
    Store in dictionary df_dict with table_name as key.
    The table_name is either the name of the sheet, or the table_name as defined in the table_index_sheet

    :param xl: pandas.ExcelFile - Excel file
    :param table_index_sheet: str - name of table index sheet
    :returns: Dict[str,DataFrame], one df per sheet, keyed by the table_name
    '''
    # Check for table_index sheet:
    table_index_df = None
    if (table_index_sheet is not None) and (table_index_sheet in xl.sheet_names):
        table_index_df = xl.parse(table_index_sheet)
        table_index_df.set_index('sheet_name', inplace=True)

    # Load all sheets:
    df_dict = {}
    for sheet in xl.sheet_names:
        if sheet != table_index_sheet:  # Do not load the table_index as a df_dict DataFrame
            table_name = sheet
            # Translate table_name if possible:
            if (table_index_df is not None) and (sheet in table_index_df.index.values):
                table_name = table_index_df.loc[sheet].table_name
            # Store in df_dict:
            df_dict[table_name] = xl.parse(sheet)
    return df_dict


def create_new_scenario(framework, sc_name):
    '''
    Replace any existing scenario with blank instance
    '''
    scenario = framework.get_scenario(name=sc_name)
    if (scenario != None):
        framework.delete_container(scenario)
    return framework.create_scenario(name=sc_name)

def load_scenario_from_data(scenario, data, category='input'):
    '''
    Load data into a scenario from dictionary of DataFrames

    Example usage:
    # Read data from Excel
    xl = pd.ExcelFile(excel_file_path) #Open an ExcelFile
    inputs = read_dataframes_from_excel(xl) # Read the data into a Dict of DataFrames
    # Load data into scenario
    client = Client() # Open dd_scenario Client
    fw = client.get_decision_framework(name=framework_name) # Open the framework/decision model
    scenario = create_new_scenario(fw, scenario_name) #Create a new scenario
    load_scenario_from_data(scenario, inputs) # Load data into scenario

    :param scenario: dd_scenario.Container
    :param data: Dict['str', DataFrame]
    :param category: str - category used in the scenario.add_table_data API
    :return: None
    '''
    for table in data:
        scenario.add_table_data(table, data[table], category=category)