# Claude 3.5 Sonnet Frontend

A modern React-based frontend interface for interacting with the Claude 3.5 Sonnet API.

## Features

- 🚀 Built with React 18, TypeScript, and Vite
- 🎨 Styled with TailwindCSS
- 🔍 Full TypeScript support
- 📱 Responsive design
- 🌙 Dark mode support
- ⚡ Real-time messaging
- 🎭 Code syntax highlighting
- 📊 Markdown support
- 🔧 Custom artifact rendering

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## Development

### Prerequisites

- Node.js 16.x or higher
- npm 7.x or higher

### Environment Setup

1. Copy `.env.example` to `.env`
2. Update environment variables as needed

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run lint` - Run linter
- `npm run type-check` - Run TypeScript type checking

### Project Structure

```
src/
├── api/          # API integration
├── components/   # React components
├── contexts/     # React contexts
├── hooks/        # Custom hooks
├── lib/          # Utilities
├── types/        # TypeScript types
└── utils/        # Helper functions
```

## Deployment

### Docker

```bash
# Build image
docker build -t claude-frontend .

# Run container
docker run -p 3000:80 claude-frontend
```

### Manual Deployment

1. Build the application: `npm run build`
2. Copy contents of `dist/` to your web server
3. Configure your web server to serve the application

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
