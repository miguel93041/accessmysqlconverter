[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen)](https://github.com/miguel93041/accessmysqlconverter)
[![License](https://img.shields.io/badge/license-GPL-blue.svg?style=flat)](https://github.com/miguel93041/accessmysqlconverter/blob/master/LICENSE)
[![paypal](https://www.paypalobjects.com/en_US/ES/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=N8EGU933CPFV8)

# AccessMySQLConverter
AccessMySQLConverter aims to provide a tool which converts MS Access database files (.mdb, .accdb) into a SQL file (compatible with PostgreSQL, MariaDB and MySQL) that can be run, generating It's structure (tables, ERM...) and if you select to, importing It's data

## Installation
To install it you must have Python 3.x installed and run in the command prompt

**`pip install --no-cache-dir --upgrade accessmysqlconverter`**

## Run it
For executing the program run in the command prompt the following instruction

**`python -m accessmysqlconverter.application`**

![Application Image](https://i.gyazo.com/12b7d363894abfd367e06c048710d4a2.png)

The tool is limited by the driver so after converting an Access Database you should look for:
* Nullability of columns and Default values
* Check ERM for missing 1:1, 1:N or N:N
* Collation, character set
* Foreign Keys ON DELETE actions
## License
See [LICENSE](LICENSE.gpl) for more information

## Donations
[![paypal](https://www.paypalobjects.com/en_US/ES/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=N8EGU933CPFV8)