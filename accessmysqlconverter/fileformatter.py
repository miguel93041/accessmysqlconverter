"""
This class handles the writing of the SQL File
"""


class Fileformatter:

    def __init__(self, file):
        self.file = file

    def write_header(self, database_name, is_other_database):
        """Writes the HEADER(SQL_Mode, time_zone, database name, CREATE and USE)"""
        if is_other_database:
            print("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';", file=self.file)
            print("SET time_zone = '+00:00';", file=self.file)
        print("", file=self.file)
        print("--", file=self.file)
        print("-- Database: `{}`".format(database_name), file=self.file)
        print("--", file=self.file)
        if is_other_database:
            print("CREATE DATABASE IF NOT EXISTS `{}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;".format(database_name), file=self.file)
            print("USE `{}`;".format(database_name), file=self.file)
        else:
            print("-- SELECT AND EXECUTE THE LINE BELOW FIRST!!!", file=self.file)
            print("CREATE DATABASE \"{}\" WITH OWNER \"postgres\" ENCODING \"UTF8\" LC_COLLATE=\"en_US.UTF-8\" LC_CTYPE=\"en_US.UTF-8\";".format(database_name), file=self.file)
            print("-- SELECT AND EXECUTE ALL THE LINES BELOW!!!", file=self.file)
            print("\connect \"{}\";".format(database_name), file=self.file)
        print("", file=self.file)

    def write_table(self, table_name, formatted_columns, is_other_database):
        """Writes table structure"""
        vars_with_no_size = ["double", "datetime", "longtext"]
        if not is_other_database:
            vars_with_no_size.append("int")
            vars_with_no_size.append("float")
            vars_with_no_size.append("timestamp")
            vars_with_no_size.append("text")
        primary_keys = self._get_primary_keys(formatted_columns)
        index_keys = self._get_index_keys(formatted_columns)

        print("--", file=self.file)
        print("-- Table structure for table `{}`".format(table_name), file=self.file)
        print("--", file=self.file)
        if is_other_database:
            print("CREATE TABLE `{}` (".format(table_name), file=self.file)
        else:
            print("CREATE TABLE \"{}\" (".format(table_name), file=self.file)

        counter_column = 0
        for column in formatted_columns:
            column_name, column_var_type, column_var_size, _, column_is_auto_increment = column

            if not is_other_database:
                if column_var_type == "datetime":
                    column_var_type = "timestamp"
                elif column_var_type == "longtext":
                    column_var_type = "text"

            line = ""
            if not (column_name in primary_keys and not is_other_database):
                if is_other_database:
                    line = "`{}` {}".format(column_name, column_var_type)
                else:
                    line = "\"{}\" {}".format(column_name, column_var_type)

                if column_var_type not in vars_with_no_size:
                    line += "({})".format(column_var_size)
                line += " NOT NULL"
                if column_is_auto_increment:
                    line += " AUTO_INCREMENT"
            else:
                if column_is_auto_increment:
                    line = "\"{}\" SERIAL PRIMARY KEY".format(column_name, column_var_type)
                else:
                    line = "\"{}\" {}".format(column_name, column_var_type)
                    if column_var_type not in vars_with_no_size:
                        line += "({})".format(column_var_size)
                    line += " NOT NULL PRIMARY KEY"

            if ((primary_keys.__len__() > 0 or index_keys.__len__() > 0) and is_other_database) or counter_column != (formatted_columns.__len__() - 1):
                line += ","
            counter_column += 1
            print(line, file=self.file)

        if primary_keys.__len__() > 0 and is_other_database:
            primary_line = "PRIMARY KEY ("
            counter_primary = 0
            for primary_key_name in primary_keys:
                if is_other_database:
                    primary_line += "`{}`".format(primary_key_name)
                else:
                    primary_line += "\"{}\"".format(primary_key_name)
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
                if is_other_database:
                    index_line = "KEY `{0}` (`{0}`)".format(index_key_name)
                else:
                    index_line = "KEY \"{0}\" (\"{0}\")".format(index_key_name)
                if counter_index != (index_keys.__len__() - 1):
                    index_line += ","
                counter_index += 1
                print(index_line, file=self.file)

        if is_other_database:
            print(") ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1;", file=self.file)
        else:
            print(");", file=self.file)

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
            if not column_is_primary_key and column_name.lower().find("id", 0, 2) != -1:
                index_keys.append(column_name)
        return index_keys

    def write_table_data(self, table_name, columns, data, is_other_database):
        """Write data of table"""
        if len(data) != 0:
            print("--", file=self.file)
            print("-- Data for table `{}`".format(table_name), file=self.file)
            print("--", file=self.file)
            self.write_table_insert_header(columns, table_name, is_other_database)
            self.write_table_insert_values(columns, data)

    def write_table_insert_header(self, columns, table_name, is_other_database):
        """Write insert table statement"""
        if is_other_database:
            insert_header = "INSERT INTO `{}` (".format(table_name)
        else:
            insert_header = "INSERT INTO \"{}\" (".format(table_name)
        for column in columns:
            column_name = column[3]
            if is_other_database:
                insert_header += "`{}`".format(column_name)
            else:
                insert_header += "\"{}\"".format(column_name)
            if column != columns[-1]:
                insert_header += ", "
        insert_header += ") VALUES"
        print(insert_header, file=self.file)

    def write_table_insert_values(self, columns, data):
        """Write insert table values"""
        for row in data:
            insert_value = self.get_table_insert_value(columns, row)
            if row != data[-1]:
                insert_value += ","
            else:
                insert_value += ";"
            print(insert_value, file=self.file)

    def get_table_insert_value(self, columns, row):
        """Get insert table row value"""
        insert_value = "("
        value_index = 0
        for value in row:
            var_type = columns[value_index][5]
            if var_type == "DATETIME":  # Transform DATETIME var into STRING
                value = "{}".format(value)
            if isinstance(value, str):
                # Check if char \ is in string
                index = value.find("\\")
                for _ in range(value.count("\\")):
                    value = value[:index] + '\\' + value[index:]
                    index = value.find("\\", index + 2)
                # Check if char ' is in string
                index = value.find("\'")
                for _ in range(value.count("\'")):
                    value = value[:index] + '\\' + value[index:]
                    index = value.find("\'", index + 2)
                index = value.find("\"")
                # Check if char " is in string
                for _ in range(value.count("\"")):
                    value = value[:index] + '\\' + value[index:]
                    index = value.find("\"", index + 2)
                insert_value += "'{}'".format(value)
            elif value is not None:
                insert_value += "{}".format(value)
            else:
                insert_value += "'{}'".format("")

            if value_index != (columns.__len__() - 1):
                insert_value += ", "
            value_index += 1
        insert_value += ")"
        return insert_value
