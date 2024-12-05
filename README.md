# 🛠️ ConfigBuddy

> Manage your configuration files with elegance! 🎨

[![PyPI version](https://badge.fury.io/py/configbuddy.svg)](https://badge.fury.io/py/configbuddy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/configbuddy.svg)](https://pypi.org/project/configbuddy/)

## ✨ Features

- 📝 Multiple format support (YAML, JSON, INI)
- 🔍 Smart configuration comparison and visualization
- 🔄 Intelligent configuration merging
- ✅ JSON Schema validation
- 🌳 Tree-style visualization

## 🚀 Getting Started

### Installation

```bash
pip install configbuddy
```

### Basic Usage

```python
from configbuddy import Config

# Load configuration files
config1 = Config.from_file('config1.yaml')
config2 = Config.from_file('config2.json')

# Visualize configuration
config1.visualize()

# Compare configurations
diff = config1.diff_with(config2)
diff.visualize()

# Merge configurations
merged, conflicts = config1.merge_with(config2)
if conflicts:
    print("Merge conflicts detected:", conflicts)
```

## 💡 Examples

### Loading and Saving

```python
# Load from YAML
config = Config.from_file('config.yaml')

# Save as JSON
config.save('config.json')
```

### Configuration Comparison

```python
# Compare two configs
diff = config1.diff_with(config2)

# Check differences
print("Added:", diff.added)
print("Removed:", diff.removed)
print("Modified:", diff.modified)
```

### Configuration Merging

```python
# Deep merge (default)
merged, conflicts = config1.merge_with(config2)

# Shallow merge
merged, conflicts = config1.merge_with(config2, strategy='shallow')
```

### Visualization Example

```
config.yaml
├── database
│   ├── host: "localhost"
│   ├── port: 5432
│   └── credentials
│       ├── username: "admin"
│       └── password: "******"
└── logging
    ├── level: "INFO"
    └── format: "%(asctime)s - %(message)s"
```

## 🎯 Use Cases

- 🔄 Manage dev/staging/prod configurations
- 🤝 Share and merge team configurations
- 🔍 Track configuration changes
- 📊 Version control experiment settings (ML/Data Science)

## 🛣️ Roadmap

- [ ] CLI interface
- [ ] Web dashboard (visualization/comparison)
- [ ] Git integration
- [ ] Comment preservation
- [ ] XML/TOML support

## 🤝 Contributing

Bug reports, feature suggestions, and pull requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=harimkang/configbuddy&type=Date)](https://star-history.com/#harimkang/configbuddy&Date)

---

Made with ❤️ by [Harim Kang](https://github.com/harimkang)
