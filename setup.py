"""Setup file for an example rules plugin."""
from setuptools import find_packages, setup

PLUGIN_LOGICAL_NAME = "mysql-schema-design"
PLUGIN_ROOT_MODULE = "mysql-schema-design"

setup(
    name=f"sqlfluff-plugin-{PLUGIN_LOGICAL_NAME}",
    version="1.0.0",
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires="sqlfluff>=0.4.0",
    entry_points={
        "sqlfluff": [f"sqlfluff_{PLUGIN_LOGICAL_NAME} = {PLUGIN_ROOT_MODULE}.rules"]
    },
)
