# StoryGen - AI-Powered Story Generation Platform

A full-stack web application that generates creative stories, character images, and background images using AI models. Built with Django (backend) and React (frontend).

## 🚀 Features

- **Story Generation**: AI-powered story creation from user prompts
- **Character Image Generation**: Create character images based on story descriptions
- **Background Image Generation**: Generate setting images for stories
- **Image Merging**: Combine character and background images into final scenes
- **Real-time Progress**: Streaming updates during generation process
- **Audio Input**: Voice-to-text and audio file upload support
- **Download Options**: Export stories as text files and images as PNG

## 🏗️ Architecture

- **Backend**: Django REST API with AI pipelines
- **Frontend**: React.js with modern UI components
- **AI Models**: LangChain + HuggingFace transformers for text generation
- **Image Generation**: Stable Diffusion for character and background images
- **Image Processing**: OpenCV and rembg for image manipulation

## 🛠️ Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- LangChain
- Transformers (HuggingFace)
- Stable Diffusion
- OpenCV
- Pillow

### Frontend
- React 18
- Modern CSS with animations
- Fetch API with streaming support
- Responsive design

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/storygen.git
cd storygen
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Navigate to backend
cd backend

# Run migrations
python manage.py migrate

# Start Django server
python manage.py runserver
```

### 3. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 📁 Project Structure

```
storygen/
├── backend/                 # Django backend
│   ├── main/               # Main Django app
│   │   ├── pipelines/      # AI processing pipelines
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   └── urls.py         # URL routing
│   ├── storygen_web/       # Django project settings
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   └── pages/          # Page components
│   └── package.json        # Node.js dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### AI Model Configuration
The application automatically downloads required AI models on first run:
- GPT-2 for text generation
- Stable Diffusion for image generation

## 📖 API Endpoints

- `GET /api/health/` - Health check
- `POST /api/generate-story/` - Generate story content
- `POST /api/stream-generate-story/` - Streaming story generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- HuggingFace for AI models
- LangChain for AI pipeline orchestration
- Django and React communities for excellent frameworks

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Note**: This is a development version. For production use, ensure proper security configurations and environment setup.
