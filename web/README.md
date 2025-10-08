# DDCPTS Web Dashboard

React + TypeScript web application for dairy officers and managers to manage collections and view analytics.

## Features

- 📊 **Interactive Dashboard**: Real-time stats and quick actions
- 📦 **Delivery Management**: View and track milk deliveries
- 👥 **Farmer Management**: Manage farmer registrations
- 📈 **Reports & Analytics**: Daily reports with visualizations
- 🔐 **Role-Based Access**: Officer, Manager, and Admin roles
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Routing**: React Router v6

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running (see `../backend/README.md`)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Update API URL in .env
# VITE_API_URL=http://localhost:8000/api/v1
```

### Development

```bash
# Start development server
npm run dev

# Access at http://localhost:3000
```

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests (requires Playwright)
npm run test:e2e
```

## Project Structure

```
src/
├── components/        # Reusable UI components
│   └── Layout.tsx     # Main layout with navigation
├── pages/             # Page components
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── DeliveriesPage.tsx
│   ├── FarmersPage.tsx
│   └── ReportsPage.tsx
├── services/          # Business logic
│   ├── api.ts         # API client
│   └── AuthContext.tsx # Authentication state
├── types/             # TypeScript type definitions
├── utils/             # Helper functions
├── App.tsx            # Root component
├── main.tsx           # App entry point
└── index.css          # Global styles
```

## Demo Credentials

- **Officer**: officer@ddcpts.test / Officer@123
- **Manager**: manager@ddcpts.test / Manager@123
- **Admin**: admin@ddcpts.test / Admin@123

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run tests
- `npm run test:e2e` - Run end-to-end tests

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Deployment

### Static Hosting (Netlify, Vercel, etc.)

```bash
npm run build
# Upload dist/ folder to your hosting provider
```

### Docker

```bash
docker build -t ddcpts-web .
docker run -p 3000:80 ddcpts-web
```

### Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/ddcpts;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
    }
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

See main repository CONTRIBUTING.md for guidelines.

## License

See main repository LICENSE file.
