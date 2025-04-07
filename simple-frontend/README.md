# Simple Frontend

A modern React frontend application built with TypeScript, Material-UI, and React Query.

## Features

- Modern React with TypeScript
- Material-UI components and theming
- React Query for data fetching
- React Router for navigation
- Authentication with protected routes
- Docker support for development and production
- Responsive design

## Prerequisites

- Node.js 20.x or later
- Docker and Docker Compose
- Git

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd simple-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:

   With Docker:
   ```bash
   docker-compose up --build
   ```

   Without Docker:
   ```bash
   npm start
   ```

The application will be available at http://localhost:3000.

## Project Structure

```
src/
  ├── components/     # Reusable components
  ├── contexts/       # React contexts (auth, etc.)
  ├── pages/          # Page components
  ├── theme.ts        # Material-UI theme configuration
  └── App.tsx         # Main application component
```

## Available Scripts

- `npm start` - Starts the development server
- `npm test` - Runs the test suite
- `npm run build` - Creates a production build
- `npm run eject` - Ejects from Create React App

## Docker Support

The project includes Docker support for both development and production environments:

- Development: `docker-compose up --build`
- Production: Build the production image using the Dockerfile

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 