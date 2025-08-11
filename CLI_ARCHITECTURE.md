# CLI Architecture Documentation

## Overview

The CLI has been completely rewritten to support a scalable, hierarchical command structure with grouped commands and subcommands. The new architecture supports:

- **Command Groups**: Logical grouping of related commands
- **Nested Subcommands**: Unlimited depth of command nesting
- **Automatic Help**: Help text is automatically generated at each level
- **Scalable Design**: Easy to add new commands and command groups

## Command Structure

The CLI now follows this structure:

```
scs [command-group] [subcommand] [options]
```

### Examples

```bash
# Show help for all available command groups
scs

# Show help for project commands
scs project

# Show help for project configuration commands
scs project config

# Show help for project configuration rules commands
scs project config rules

# Execute specific commands
scs project init
scs project validate
scs project config show
scs project config rules list
scs standards list
scs tools format
```

## Architecture Components

### 1. CommandGroup (Base Class)

The `CommandGroup` class is the foundation for all command groups:

```python
from src.cli.base import CommandGroup

class MyCommandGroup(CommandGroup):
    def __init__(self):
        super().__init__(
            name="mygroup",
            help_text="Description of my command group"
        )
    
    def register_commands(self):
        """Register all commands for this group."""
        # Implementation here
```

### 2. NestedCommandGroup

For command groups that need to contain other command groups:

```python
from src.cli.base import NestedCommandGroup

class MyNestedGroup(NestedCommandGroup):
    def __init__(self):
        super().__init__(
            name="mynested",
            help_text="Description of my nested command group"
        )
    
    def register_commands(self):
        """Register commands and subgroups."""
        # Add direct commands
        self.add_command(func=my_function, name="mycommand", help_text="Help text")
        
        # Add subgroups
        self.add_subgroup(some_other_group)
```

### 3. CommandRegistry

The registry manages all command groups:

```python
from src.cli.base import CommandRegistry

registry = CommandRegistry()
registry.register_group(my_command_group)
```

## Adding New Commands

### Step 1: Create Command Functions

```python
# src/cli/commands/mygroup/commands.py
import typer

def my_command(
    path: str = typer.Argument(".", help="Path to process"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Description of what this command does."""
    typer.echo(f"Processing {path}")
    if verbose:
        typer.echo("Verbose mode enabled")
```

### Step 2: Create Command Group

```python
# src/cli/commands/mygroup/__init__.py
from ..base import CommandGroup
from .commands import my_command

class MyGroup(CommandGroup):
    def __init__(self):
        super().__init__(
            name="mygroup",
            help_text="Description of my command group"
        )
    
    def register_commands(self):
        self.app.command(
            name="command",
            help="Description of what this command does"
        )(my_command)

# Create instance
my_group = MyGroup()
```

### Step 3: Register with Main CLI

```python
# src/cli/__main__.py
from .commands import my_group

def create_main_app() -> typer.Typer:
    app = typer.Typer(...)
    
    registry = CommandRegistry()
    registry.register_group(my_group)
    # ... other groups
    
    return app
```

## Adding Nested Commands

### Step 1: Create Subgroup

```python
# src/cli/commands/mygroup/subgroup/__init__.py
from ...base import CommandGroup

class SubGroup(CommandGroup):
    def __init__(self):
        super().__init__(
            name="subgroup",
            help_text="Description of subgroup"
        )
    
    def register_commands(self):
        # Register subcommands
        pass

sub_group = SubGroup()
```

### Step 2: Add to Parent Group

```python
# src/cli/commands/mygroup/__init__.py
from ..base import NestedCommandGroup
from .subgroup import sub_group

class MyGroup(NestedCommandGroup):
    def register_commands(self):
        # Add direct commands
        self.add_command(func=my_command, name="command", help_text="Help")
        
        # Add subgroup
        self.add_subgroup(sub_group)
```

## Current Command Structure

### Project Commands

- `scs project init` - Initialize a new project
- `scs project validate` - Validate project against standards
- `scs project update` - Update project standards
- `scs project audit` - Audit project compliance
- `scs project config show` - Show project configuration
- `scs project config edit` - Edit project configuration
- `scs project config rules list` - List configuration rules
- `scs project config rules enable` - Enable a rule
- `scs project config rules disable` - Disable a rule

### Standards Commands

- `scs standards list` - List available standards
- `scs standards show` - Show standard details

### Tools Commands

- `scs tools format` - Format code
- `scs tools lint` - Lint code

## Benefits of the New Architecture

1. **Scalability**: Easy to add new commands and command groups
2. **Consistency**: All commands follow the same pattern
3. **Discoverability**: Help is available at every level
4. **Maintainability**: Clear separation of concerns
5. **Extensibility**: Support for unlimited nesting depth
6. **Reusability**: Command groups can be composed and reused

## Best Practices

1. **Use descriptive names**: Command and group names should be clear and intuitive
2. **Provide helpful descriptions**: Every command should have a clear help text
3. **Group logically**: Related commands should be grouped together
4. **Keep nesting reasonable**: Don't nest too deeply (3-4 levels max recommended)
5. **Use consistent patterns**: Follow the established patterns for adding commands

## Migration from Old System

The old flat command structure has been replaced with the new hierarchical system:

**Old**: `scs project-init`
**New**: `scs project init`

**Old**: `scs standards-list`
**New**: `scs standards list`

All existing functionality is preserved, just reorganized into a more logical structure.
