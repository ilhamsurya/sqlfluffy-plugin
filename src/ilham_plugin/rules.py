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
            if col_name in self.forbidden_columns:
                return LintResult(
                    anchor=seg,
                    description=f"Column `{col_name}` not allowed in ORDER BY.",
                )
            
class Rule_PolicyGroup_L002(BaseRule):
    config_keywords = ["valid_data_types"]
    has_configured_cols = False
    has_configured_data_types = False

    def __init__(self, *args, **kwargs):
        """Overwrite __init__ to set config."""
        super().__init__(*args, **kwargs)

    def _eval(self, context: RuleContext):
        """Check if a column's data type is valid."""
        if not self.has_configured_cols:
            self.columns = self.get_config("cols_to_check")
            self.has_configured_cols = True
        if not self.has_configured_data_types:
            self.valid_data_types = self.get_config("valid_data_types")
            self.has_configured_data_types = True
        for node in context.tree.traverse():
            if node.type == "column_definition":
                for segment in node.segments:
                    if segment.is_type(WhitespaceSegment):
                        continue
                    if segment.raw.lower() in self.columns:
                        if segment.next_raw.lower() not in self.valid_data_types:
                            return LintResult(
                                anchor=segment,
                                description=f"Invalid data type '{segment.next_raw}' used for column '{segment.raw}'."
                            )
        return None
    
    