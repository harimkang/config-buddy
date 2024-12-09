from rich.console import RenderableType
from rich.panel import Panel
from rich.theme import Theme
from rich_argparse import RichHelpFormatter


class CustomHelpFormatter(RichHelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=40, width=100)

    def format_help(self) -> str:
        """Format the help message for the current command and returns it as a string.

        The help message includes information about the command's arguments and options,
        as well as any additional information provided by the command's help guide.

        Returns:
            str: A string containing the formatted help message.
        """
        with self.console.use_theme(Theme(self.styles)), self.console.capture() as capture:
            section = self._root_section
            rendered_content: RenderableType = section
            if len(section.rich_items) > 1:
                rendered_content = Panel(section, border_style="dim", title="Arguments", title_align="left")
                self.console.print(rendered_content, highlight=True, soft_wrap=True)
        help_msg = capture.get()

        if help_msg:
            help_msg = self._long_break_matcher.sub("\n\n", help_msg).rstrip() + "\n"
        return help_msg
