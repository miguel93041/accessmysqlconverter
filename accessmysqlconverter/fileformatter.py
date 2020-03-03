"""
This class handles the writing of the SQL File
"""


class Fileformatter:

    def __init__(self, file):
        self.file = file

    def write_header(self, database_name):
        """Writes the HEADER(SQL_Mode, time_zone, database name, CREATE and USE)"""
        print("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';", file=self.file)
        print("SET time_zone = '+00:00';", file=self.file)
        print("", file=self.file)
        print("--", file=self.file)
        print("-- Database: `{}`".format(database_name), file=self.file)
        print("--", file=self.file)
        print(
            "CREATE DATABASE IF NOT EXISTS `{}` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;".format(
                database_name), file=self.file)
        print("USE `{}`;".format(database_name), file=self.file)
        print("", file=self.file)

    def write_table(self, table_name, formatted_columns):
        """Writes table structure"""
        vars_with_no_size = ("double", "datetime", "longtext")
        primary_keys = self._get_primary_keys(formatted_columns)
        index_keys = self._get_index_keys(formatted_columns)

        print("--", file=self.file)
        print("-- Table structure for table `{}`".format(table_name),
              file=self.file)
        print("--", file=self.file)
        print("CREATE TABLE IF NOT EXISTS `{}` (".format(table_name),
              file=self.file)

        counter_column = 0
        for column in formatted_columns:
            column_name, column_var_type, column_var_size, _, column_is_auto_increment = column

            line = "`{}` {}".format(column_name, column_var_type)
            if column_var_type not in vars_with_no_size:
                line += "({})".format(column_var_size)
            line += " NOT NULL"
            if column_is_auto_increment:
                line += " AUTO_INCREMENT"

            if primary_keys.__len__() > 0 or index_keys.__len__() > 0 or counter_column != (
                    formatted_columns.__len__() - 1):
                line += ","
            counter_column += 1
            print(line, file=self.file)

        if primary_keys.__len__() > 0:
            primary_line = "PRIMARY KEY ("
            counter_primary = 0
            for primary_key_name in primary_keys:
                primary_line += "`{}`".format(primary_key_name)
                if counter_primary != (primary_keys.__len__() - 1):
                    primary_line += ", "
                counter_primary += 1
            primary_line += ")"
            if index_keys.__len__() > 0:
                primary_line += ","
            print(primary_line, file=self.file)

        if index_keys.__len__() > 0:
            counter_index = 0
            for index_key_name in index_keys:
                index_line = "KEY `{0}` (`{0}`)".format(index_key_name)
                if counter_index != (index_keys.__len__() - 1):
                    index_line += ","
                counter_index += 1
                print(index_line, file=self.file)

        print(") ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;",
              file=self.file)

    @staticmethod
    def _get_primary_keys(formatted_columns):
        """Get columns that are primary key"""
        primary_keys = list()
        for column in formatted_columns:
            column_is_primary_key = column[3]
            if column_is_primary_key:
                column_name = column[0]
                primary_keys.append(column_name)
        return primary_keys

    @staticmethod
    def _get_index_keys(formatted_columns):
        """Get columns that are index key"""
        index_keys = list()
        for column in formatted_columns:
            column_name = column[0]
            column_is_primary_key = column[3]
            if not column_is_primary_key and column_name.lower().find("id", 0,
                                                                      2) != -1:
                index_keys.append(column_name)
        return index_keys

    def write_table_data(self, table_name, columns, data):
        """Write data of table"""
        print("--", file=self.file)
        print("-- Data for table `{}`".format(table_name), file=self.file)
        print("--", file=self.file)

        for row in data:
            insert_line = "INSERT INTO `{}` (".format(table_name)
            counter_row = 0
            for column in columns:
                column_name = column[3]
                insert_line += column_name
                if counter_row != (columns.__len__() - 1):
                    insert_line += ", "
                counter_row += 1
            insert_line += ") VALUES ("
            counter_value = 0
            for value in row:
                var_type = columns[counter_value][5]
                if isinstance(value, str) or var_type == "DATETIME":
                    insert_line += "'{}'".format(value)
                else:
                    if value is not None:
                        insert_line += "{}".format(value)
                    else:
                        insert_line += "'{}'".format("")
                if counter_value != (columns.__len__() - 1):
                    insert_line += ", "
                counter_value += 1
            insert_line += ");"
            print(insert_line, file=self.file)
