# StoryGen

A Django + React application for AI-powered story generation.

## Project Structure

```
storygen/
├── backend/          # Django backend
│   ├── storygen_web/ # Django project
│   ├── main/         # Django app
│   │   └── pipelines/ # AI modules
│   └── media/        # File uploads
├── frontend/         # React frontend
└── README.md         # This file
```

## Features

- Django backend with AI story generation capabilities
- React frontend for user interface
- AI pipeline modules for story generation
- File upload support
- RESTful API architecture

## Getting Started

### Backend Setup
1. Navigate to `backend/`
2. Activate virtual environment: `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

### Frontend Setup
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Start development server: `npm start`

## Development

This project uses Django for the backend API and React for the frontend user interface. The AI story generation functionality is implemented in the `pipelines` module within the main Django app.
