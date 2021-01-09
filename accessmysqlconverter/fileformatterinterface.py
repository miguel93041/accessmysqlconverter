"""
This class handles the writing of the SQL File
"""


class Fileformatterinterface:
    """Interface for sql file formatters"""
    def write_header(self, database_name):
        """Writes the HEADER(SQL_Mode, time_zone, database name, CREATE and USE)"""
        pass

    def write_table(self, table_name, formatted_columns):
        """Writes table structure"""
        pass

    def _get_primary_keys(self, formatted_columns):
        """Get columns that are primary key"""
        pass

    def _get_index_keys(self, formatted_columns):
        """Get columns that are index key"""
        pass

    def _get_origin_table(self, referenced_table_name, column_name):
        """Gets the origin table of the 1:N relation"""
        pass

    def write_table_data(self, table_name, columns, data):
        """Write data of table"""
        pass

    def _write_table_insert_header(self, columns, table_name):
        """Write insert table statement"""
        pass

    def _write_table_insert_values(self, columns, data):
        """Write insert table values"""
        pass

    def _get_table_insert_value(self, columns, row):
        """Get insert table row value"""
        pass
