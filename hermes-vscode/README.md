 # ZSCE Agent VS Code Extension

A Visual Studio Code extension for the ZSCE (Zero-Shot Context Engineering) Agent - a multi-agent system for automated software development.

## Features

- 🚀 **Start Development Workflow**: Initiate AI-powered development tasks directly from VS Code
- 📊 **Real-time Workflow Status**: Monitor the progress of agent collaboration and debate
- 📜 **Project Constitution Viewer**: View and understand project rules and context
- 🔒 **Anti-Collusion System**: Uses different AI models for different agents to ensure independent thinking
- ⚡ **Integrated Experience**: Seamlessly integrated with your existing VS Code workflow

## Installation

1. Clone this repository
2. Install dependencies: `npm install`
3. Compile the extension: `npm run compile`
4. Press F5 to run the extension in a new Extension Development Host window

## Usage

### Starting a Development Workflow

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "ZSCE Agent: Start Development Workflow"
3. Enter your development task description
4. Watch the agents collaborate in real-time!

### Viewing Workflow Status

- Use the ZSCE Agent sidebar to monitor current workflows
- Check the status bar for real-time progress updates
- Use the command "ZSCE Agent: View Workflow Status" for detailed information

### Opening Project Constitution

- Use "ZSCE Agent: Open Project Constitution" to view project rules and context
- The constitution is automatically generated based on your project structure

## Configuration

The extension can be configured through VS Code settings:

- `zsweAgent.apiKey`: Your Google Gemini API Key
- `zsweAgent.maxDebateRounds`: Maximum number of debate rounds (default: 3)
- `zsweAgent.autoApprove`: Auto-approve agent decisions (default: false)

## Requirements

- Python 3.10+ with the ZSCE Agent package installed
- Google Gemini API Key
- VS Code 1.74.0 or higher

## Development

### Project Structure

```
src/
├── extension.ts          # Main extension entry point
├── workflowManager.ts    # Manages development workflows
├── zsceAgentProvider.ts  # VS Code tree view provider
└── constitutionViewer.ts # Constitution display component
```

### Building

```bash
npm install          # Install dependencies
npm run compile      # Compile TypeScript
npm run watch        # Watch for changes
npm run lint         # Run linter
npm run test         # Run tests
```

### Testing

Press F5 in VS Code to launch the Extension Development Host and test the extension.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This extension is part of the ZSCE Agent project and follows the same license terms.

## Support

For issues and questions:
- Check the [ZSCE Agent documentation](https://github.com/your-org/zswe-agent)
- Open an issue in this repository
- Join our community discussions
