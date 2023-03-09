"""An example of a custom rule implemented through the plugin system.

This uses the rules API supported from 0.4.0 onwards.
"""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import (
    BaseRule,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from typing import List, Type
import os.path
from sqlfluff.core.config import ConfigLoader
from sqlfluff.core.parser import WhitespaceSegment

@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules."""
    return [Rule_PolicyGroup_L001]


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_config_file(
        file_dir=os.path.dirname(__file__),
        file_name="plugin_default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict:
    """Get rule config validations and descriptions."""
    return {
        "forbidden_columns": {"definition": "A list of column to forbid"},
    }


# These two decorators allow plugins
# to be displayed in the sqlfluff docs
class Rule_PolicyGroup_L001(BaseRule):
    """ORDER BY on these columns is forbidden!

    **Anti-pattern**

    Using ``ORDER BY`` one some forbidden columns.

    .. code-block:: sql

        SELECT *
        FROM foo
        ORDER BY
            bar,
            baz

    **Best practice**

    Do not order by these columns.

    .. code-block:: sql

        SELECT *
        FROM foo
        ORDER BY bar
    """

    groups = ("all",)
    config_keywords = ["forbidden_columns"]
    crawl_behaviour = SegmentSeekerCrawler({"orderby_clause"})
    is_fix_compatible = True

    def __init__(self, *args, **kwargs):
        """Overwrite __init__ to set config."""
        super().__init__(*args, **kwargs)
        self.forbidden_columns = [
            col.strip() for col in self.forbidden_columns.split(",")
        ]

    def _eval(self, context: RuleContext):
        """We should not ORDER BY forbidden_columns."""
        for seg in context.segment.segments:
            col_name = seg.raw.lower()
            print(seg)
            if col_name in self.forbidden_columns:
                print(col_name)
                return LintResult(
                    anchor=seg,
                    description=f"Column `{col_name}` not allowed in ORDER BY.",
                )
            
class Rule_PolicyGroup_L002(BaseRule):
    config_keywords = ["data_type_checks"]
    has_configured_checks = False

    def __init__(self, *args, **kwargs):
        """Overwrite __init__ to set config."""
        super().__init__(*args, **kwargs)
        self.config_keywords = [
            check.strip() for check in self.config_keywords.split(",")
        ]

    def _eval(self, context: RuleContext):
        """Check if a column's data type matches certain criteria."""
        if not self.has_configured_checks:
            self.data_type_checks = self.get_config("data_type_checks")
            self.has_configured_checks = True
        for node in context.tree.traverse():
            if node.type == "column_definition":
                for segment in node.segments:
                    if segment.is_type(WhitespaceSegment):
                        continue
                    column_name = segment.raw.lower()
                    data_type = segment.next_raw.lower()
                    for check in self.data_type_checks:
                        if column_name in check["columns"] and data_type not in check["valid_data_types"]:
                            return LintResult(
                                anchor=segment,
                                description=f"Invalid data type '{data_type}' used for column '{column_name}'. {check['message']}"
                            )
        return None