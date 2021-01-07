"""
Class that gets column strucutre, vartypes, etc... intermediary between access file and sql file
"""


from os import path
from tkinter import messagebox
from accessmysqlconverter.fileformatter import Fileformatter


class Accesshandler:
    def __init__(self, cur):
        self._cur = cur

    def make_file(self, output_dir, database_name, is_db_other):
        """Makes sql file"""
        table_names = self._get_table_names()
        suffix = ".sql"
        file = open("{}".format(path.join(output_dir, database_name + suffix)), "w+", encoding='utf-8')
        fileformatter = Fileformatter(file)
        fileformatter.write_header(database_name, is_db_other)
        for name in table_names:
            fileformatter.write_table(name, self._get_columns(name), is_db_other)

        MsgBox = messagebox.askquestion('Import data', 'Do you want to import the data?', icon='warning')
        if MsgBox == "yes":
            for name in table_names:
                fileformatter.write_table_data(name, self._get_table_columns(name), self._get_table_data(name), is_db_other)

        file.close()

    def _get_table_names(self):
        """Retrieves a list with the names of the tables"""
        tables = list()
        for table in self._cur.tables(tableType="TABLE"):
            name = table[2]
            if name[0] != "~":        # Sometimes you get strange tables like ~TR324XZ0 so we need to filter them
                tables.append(name)
        return tables

    def _get_columns(self, table_name):
        """Gets from a table it's columns with it's var names, types..."""
        formatted_columns = list()
        table_columns = self._get_table_columns(table_name)
        table_columns_statistics = self._get_table_columns_statistics(table_name)

        for column in table_columns:
            column_name = column[3]
            column_var_type = column[5]
            column_var_size = column[6]
            column_var_sql_type = self._get_type_SQL(column_var_type)        # Transform ACCESS VARTYPE to SQL VARTYPE
            column_is_primary_key = self._is_primary_key(table_columns_statistics, column_name)
            column_is_auto_increment = column_var_type == "COUNTER"

            formatted_columns.append((column_name, column_var_sql_type, column_var_size, column_is_primary_key, column_is_auto_increment))
        return formatted_columns

    def _get_table_columns(self, table_name):
        """Retrieves a list with the columns of the given table"""
        columns = list()
        cur_columns = self._cur.columns(table=table_name)
        for column in cur_columns:
            columns.append(column)

        return columns

    def _get_table_columns_statistics(self, table_name):
        """Retrieves a list with the columns statistics of the given table (useful for keys)"""
        columns_statistics = list()
        for column in self._cur.statistics(table_name):
            columns_statistics.append(column)
        return columns_statistics

    @staticmethod
    def _get_type_SQL(access_type):
        """Access vartypes to SQL vartypes"""
        switcher = {
            "LONGBINARY": "varbinary",
            "BIT": "bit",
            "COUNTER": "int",
            "CURRENCY": "float",
            "GUID": "int",
            "DOUBLE": "double",
            "INTEGER": "int",
            "BYTE": "int",
            "SMALLINT": "int",
            "DECIMAL": "float",
            "REAL": "int",
            "DATETIME": "datetime",
            "VARCHAR": "varchar",
            "LONGCHAR": "longtext"
        }
        return switcher.get(access_type, "varchar")

    @staticmethod
    def _is_primary_key(table_columns, pColumn_name):
        """Check if column is primary key"""
        for column in table_columns:
            column_name = column[8]
            column_primary_Key = column[5]
            if column_name == pColumn_name and column_primary_Key == "PrimaryKey":
                return True
        return False

    def _get_table_data(self, table_name):
        """Simple query to fetch all data inside a table"""
        self._cur.execute("SELECT * FROM `{}`".format(table_name))
        return self._cur.fetchall()
