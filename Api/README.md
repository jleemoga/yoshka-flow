# Feature-Based Architecture API

This project demonstrates a feature-based architecture approach for building ASP.NET Core Web APIs with PostgreSQL.

## Project Structure

```
/Api
│
├── /Features
│   ├── /Database
│   │   └── /Extensions
│   │       └── DatabaseExtensions.cs
│   │
│   ├── /Health
│   │   ├── /Controllers
│   │   │   └── HealthController.cs
│   │   └── /Extensions
│   │       └── HealthFeatureExtensions.cs
│   │
│   └── /Users
│       ├── /Controllers
│       │   └── UserController.cs
│       ├── /Models
│       │   └── User.cs
│       ├── /Services
│       │   ├── IUserService.cs
│       │   └── UserService.cs
│       ├── /Repositories
│       │   ├── IUserRepository.cs
│       │   └── UserRepository.cs
│       └── /Extensions
│           └── UserFeatureExtensions.cs
│
├── /Shared
│   └── /Middleware
│       └── ExceptionMiddleware.cs
│
├── /Data
│   └── AppDbContext.cs
│
├── /Program.cs
└── /appsettings.json
```

## Architecture Overview

### Feature-Based Organization
Each feature is completely self-contained and includes all necessary components:
- **Controllers**: API endpoints
- **Models**: Data models and DTOs
- **Services**: Business logic
- **Repositories**: Data access logic
- **Extensions**: Feature-specific dependency injection setup

### Features
1. **Database**: Database context and configuration
   - PostgreSQL configuration
   - Entity Framework Core setup

2. **Health**: API health monitoring
   - Root endpoint (/) returning API status
   - Health check implementation

3. **Users**: User management
   - CRUD operations
   - User data persistence
   - Business logic implementation

### Shared Components
Contains only cross-cutting concerns:
- **Middleware**: Global exception handling

## Prerequisites

1. .NET 8.0 SDK
2. PostgreSQL 14 or later

## Getting Started

1. Install PostgreSQL and create a new database:
   ```sql
   CREATE DATABASE yoshka;
   ```

2. Update the connection string in `appsettings.json` if needed:
   ```json
   "DefaultConnection": "Host=localhost;Database=yoshka;Username=postgres;Password=postgres"
   ```

3. Install Entity Framework Core tools if not already installed:
   ```
   dotnet tool install --global dotnet-ef
   ```

4. Run Entity Framework migrations:
   ```
   dotnet ef database update
   ```

5. Run the application:
   ```
   dotnet run
   ```

## API Endpoints

### Health Check
- GET / - Get API status and health information

### Users
- GET /api/users - Get all users
- GET /api/users/{id} - Get user by ID
- POST /api/users - Create new user
- PUT /api/users/{id} - Update existing user
- DELETE /api/users/{id} - Delete user

## Dependencies
- Microsoft.AspNetCore.OpenApi (8.0.1)
- Microsoft.EntityFrameworkCore (8.0.1)
- Microsoft.EntityFrameworkCore.Design (8.0.1)
- Npgsql.EntityFrameworkCore.PostgreSQL (8.0.0)
- Swashbuckle.AspNetCore (6.5.0)
