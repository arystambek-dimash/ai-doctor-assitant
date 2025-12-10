# AI Doctor Assistant

An intelligent healthcare platform that connects patients with doctors and provides AI-powered medical consultations. Built with FastAPI, PostgreSQL, and OpenAI integration.

## Features

### For Patients
- 🔍 **Smart Doctor Search** - Find doctors by specialization, experience, and ratings
- 📅 **Appointment Booking** - Schedule appointments with available doctors
- 🤖 **AI Consultation** - Get preliminary medical advice through AI-powered chat
- 📋 **Medical Records** - Access and manage electronic medical records (EMR)
- 💬 **Real-time Chat** - WebSocket-based communication with AI assistant

### For Doctors
- 👨‍⚕️ **Profile Management** - Manage professional information and credentials
- 📆 **Schedule Management** - Set availability and manage appointments
- 📝 **Patient Records** - Access and update patient medical records
- 🔔 **Appointment Notifications** - Stay informed about bookings

### For Administrators
- 📊 **Dashboard Statistics** - Monitor system metrics and usage
- 👥 **User Management** - Full CRUD operations for users and patients
- 🏥 **Doctor Management** - Approve, reject, or suspend doctor registrations
- 📈 **Analytics** - Track appointments, consultations, and system health

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT
- **Authentication**: JWT (JSON Web Tokens)
- **Password Security**: bcrypt
- **Dependency Injection**: dependency-injector
- **Database Migrations**: Alembic
- **API Documentation**: Swagger/OpenAPI

## Architecture

The project follows **Clean Architecture** principles with clear separation of concerns:

```
src/
├── app/                    # Application entry point and configuration
├── domain/                 # Business entities and interfaces
│   ├── entities/          # Domain models
│   └── interfaces/        # Repository interfaces
├── infrastructure/         # External services and data access
│   ├── database/          # Database configuration and models
│   ├── repositories/      # Repository implementations
│   └── services/          # External service integrations
├── presentation/           # API layer
│   └── api/
│       ├── admin/         # Admin-only endpoints
│       ├── routers/       # Public/authenticated endpoints
│       └── schemas/       # Request/response models
└── use_cases/             # Business logic and application services
```

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Poetry (Python dependency management)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-doctor-assitant
```

2. **Install dependencies**
```bash
poetry install
```

3. **Set up environment variables**

Create a `.env` file in the root directory:

```env
# Database Configuration
POSTGRES_USER=your_user
POSTGRES_DB=doctor
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_PASSWORD=your_password

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# JWT Secrets
JWT_ACCESS_TOKEN_SECRET_KEY=your_access_token_secret
JWT_REFRESH_TOKEN_SECRET_KEY=your_refresh_token_secret
```

4. **Run database migrations**
```bash
poetry run alembic upgrade head
```

5. **Start the development server**
```bash
poetry run uvicorn src.app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - User login
- `POST /api/v1/users/refresh` - Refresh access token

### Doctors
- `GET /api/v1/doctors` - List all approved doctors
- `GET /api/v1/doctors/{id}` - Get doctor details
- `POST /api/v1/doctors/register` - Register as a doctor
- `PATCH /api/v1/doctors/profile` - Update doctor profile

### Appointments
- `GET /api/v1/appointments` - List user appointments
- `POST /api/v1/appointments` - Book an appointment
- `PATCH /api/v1/appointments/{id}` - Update appointment status

### AI Consultations
- `POST /api/v1/ai-consultations` - Start AI consultation
- `POST /api/v1/ai-consultations/{id}/messages` - Send message
- `GET /api/v1/ai-consultations/{id}/messages` - Get chat history
- `WS /api/v1/ws/chat/{consultation_id}` - WebSocket chat

### Admin Endpoints
- `GET /api/v1/admin/stats` - Dashboard statistics
- `GET /api/v1/admin/users` - Manage users
- `GET /api/v1/admin/doctors` - Manage doctors
- `PATCH /api/v1/admin/doctors/{id}/status` - Change doctor status

## Database Schema

Key entities:
- **Users** - Patient and admin accounts
- **Doctors** - Doctor profiles with credentials
- **Specializations** - Medical specialties
- **Schedules** - Doctor availability
- **Appointments** - Booking records
- **Medical Records** - Patient health records
- **AI Consultations** - AI chat sessions
- **Chat Messages** - Conversation history

## Development

### Running Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

Rollback migration:
```bash
poetry run alembic downgrade -1
```

### Code Structure

The project uses:
- **Unit of Work Pattern** for transaction management
- **Repository Pattern** for data access
- **Dependency Injection** for loose coupling
- **DTOs** for data transfer between layers
- **Clean separation** between domain, application, and infrastructure layers

## Features in Detail

### AI Consultation System
- Multi-turn conversation support
- Context-aware medical recommendations
- Specialization suggestions based on symptoms
- Streaming and non-streaming response modes
- Chat history persistence

### Doctor Management
- Multi-status workflow (pending → approved/rejected/suspended)
- Detailed profile with license verification
- Experience and specialization tracking
- Rating system

### Appointment System
- Real-time availability checking
- Status tracking (pending, confirmed, completed, cancelled)
- Notes and reason recording
- Patient and doctor views

## Security

- Password hashing with bcrypt
- JWT-based authentication
- Role-based access control (Patient, Doctor, Admin)
- Secure API endpoints with dependency injection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

Dimash Arystambekov - arystambekdimash005@gmail.com

---

**Note**: Make sure to never commit your `.env` file with actual credentials to version control.
