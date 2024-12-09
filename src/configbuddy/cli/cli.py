# Copyright (c) 2024 Harim Kang
# SPDX-License-Identifier: MIT

import argparse
from pathlib import Path

from rich.console import Console

from configbuddy import CONFIGBUDDY_LOGO, Config, __version__

from .help_formatter import CustomHelpFormatter


class CLI:
    def __init__(self, args: list[str] | None = None) -> None:
        self.console = Console()
        self.parser = self.init_parser()
        self.add_subcommands()
        self.args = self.parser.parse_args(args)
        self.execute()

    def init_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="ConfigBuddy: Configuration Management Tool",
            formatter_class=CustomHelpFormatter,
        )
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"%(prog)s {__version__}",
            help="Display configbuddy version number",
        )
        return parser

    def add_subcommands(self) -> None:
        subparsers = self.parser.add_subparsers(
            dest="command",
            required=True,
            title="commands",
            description="available commands",
        )

        # 1. visualize
        visualize_parser = subparsers.add_parser(
            "visualize",
            help="Visualize configuration in tree format",
            formatter_class=CustomHelpFormatter,
        )
        visualize_parser.add_argument("config", type=Path, help="Configuration file to visualize")

        # 2. diff
        diff_parser = subparsers.add_parser(
            "diff",
            help="Compare two configurations",
            formatter_class=CustomHelpFormatter,
        )
        diff_parser.add_argument("config", type=Path, help="Base configuration file")
        diff_parser.add_argument("--compare", type=Path, help="Other configuration file")

        # 3. merge
        merge_parser = subparsers.add_parser("merge", help="Merge configurations", formatter_class=CustomHelpFormatter)
        merge_parser.add_argument("configs", type=Path, nargs="+", help="Configuration files to merge")
        merge_parser.add_argument("--output", "-o", type=Path, help="Output file path")
        merge_parser.add_argument(
            "--strategy",
            choices=["deep", "shallow"],
            default="deep",
            help="Merge strategy (default: deep)",
        )

        # 4. validate
        validate_parser = subparsers.add_parser(
            "validate",
            help="Validate configuration",
            formatter_class=CustomHelpFormatter,
        )
        validate_parser.add_argument("config", type=Path, help="Configuration file to validate")
        validate_parser.add_argument("--schema", type=Path, help="JSON schema file")

        # 5. Generate Schema
        generate_schema_parser = subparsers.add_parser(
            "generate-schema",
            help="Generate schema from configuration",
            formatter_class=CustomHelpFormatter,
        )
        generate_schema_parser.add_argument("config", type=Path, help="Configuration file to generate schema")
        generate_schema_parser.add_argument("--output", "-o", type=Path, help="Output file path")

    def execute(self) -> None:
        self.console.print(CONFIGBUDDY_LOGO, style="blue")
        if self.args.command == "visualize":
            config = Config.from_file(self.args.config)
            config.visualize()
        elif self.args.command == "diff":
            config1 = Config.from_file(self.args.config)
            config2 = Config.from_file(self.args.compare)
            result = config1.diff_with(config2)
            result.visualize()
        elif self.args.command == "merge":
            configs = [Config.from_file(path) for path in self.args.configs]
            base_config = configs[0]
            for config in configs[1:]:
                merged_config, conflicts = base_config.merge_with(config)
                base_config = merged_config
                if conflicts:
                    self.console.print("[yellow]Merge conflicts detected:[/]")
                    for conflict in conflicts:
                        self.console.print(f"  - {conflict}")
            base_config.save(self.args.output)
            self.console.print(f"[green]Merged configuration saved to {self.args.output}[/]")
        elif self.args.command == "validate":
            config = Config.from_file(self.args.config)
            errors = config.validate(self.args.schema)

            if errors:
                self.console.print("[red]Validation errors:[/red]")
                for error in errors:
                    self.console.print(f"  - {error}", style="red")
            else:
                self.console.print("[green]Configuration is valid.[/green]")
        elif self.args.command == "generate-schema":
            from configbuddy.core.validator import ConfigValidator

            ConfigValidator.from_config(Config.from_file(self.args.config)).save_schema(self.args.output)
            self.console.print(f"[green]Schema generated and saved to {self.args.output}[/green]")
