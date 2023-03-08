# SQLFluff custom plugin

## How to start using SQLFluff with custom plugin

1. Install sqlfluff `pip install sqlfluff`
2. Install custom plugin `pip install git+https://github.com/ilhamsurya/sqlfluffy-plugin`
3. Check if plugin already active in `pip list`
4. After this to start using sqlfluff run these commands:

`sqlfluff lint path_to_file_or_folder` and `sqlfluff fix path_to_file_or_folder`

## How to update plugin content

1. Uninstall sqlfluff plugin `pip uninstall sqlfluff-plugin-ilham-plugin`
2. Install custom plugin again `pip install git+https://github.com/ilhamsurya/sqlfluffy-plugin`
