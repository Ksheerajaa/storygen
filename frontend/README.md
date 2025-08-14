# StoryGen React Frontend

A modern React application for the StoryGen AI-powered story generation platform.

## Features

- **Story Generation Form**: Input prompts to generate AI-powered stories
- **Real-time Display**: View generated stories, character descriptions, and background descriptions
- **Image Gallery**: Display AI-generated character, background, and merged images
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Modern UI**: Beautiful gradient design with smooth animations

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── StoryForm.js    # Story generation form
│   └── StoryDisplay.js # Story and image display
├── pages/              # Main application pages
│   └── HomePage.js     # Main application page
├── api.js              # API communication functions
├── App.js              # Main application component
└── App.css             # Custom styling
```

## Technologies Used

- **React 19**: Modern React with hooks
- **Bootstrap 5**: Responsive CSS framework
- **Bootstrap Icons**: Icon library
- **Axios**: HTTP client for API communication
- **CSS3**: Custom animations and styling

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Django backend running on localhost:8000

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Development Commands

- **Start development server**: `npm start`
- **Build for production**: `npm run build`
- **Run tests**: `npm test`
- **Eject from Create React App**: `npm run eject`

## API Integration

The frontend communicates with the Django backend through:

- **Base URL**: `http://localhost:8000` (configurable via proxy)
- **Main Endpoint**: `/api/generate-story/`
- **Request Format**: JSON with `prompt_text` field
- **Response**: Complete story data with images and metadata

## Configuration

### Proxy Setup

The frontend is configured to proxy API requests to the Django backend during development:

```json
{
  "proxy": "http://localhost:8000"
}
```

### Environment Variables

You can customize the API URL using environment variables:

```bash
REACT_APP_API_URL=http://your-backend-url.com
```

## Component Details

### StoryForm

- Handles user input for story prompts
- Manages form state and validation
- Shows loading states during generation
- Displays error messages for failed requests

### StoryDisplay

- Renders generated story content
- Displays character and background descriptions
- Shows generated images in a responsive grid
- Handles different processing statuses

### HomePage

- Main application container
- Combines form and display components
- Includes informational sections and tips
- Responsive layout for all screen sizes

## Styling

The application uses a custom gradient theme with:

- **Primary Colors**: Blue to purple gradient (#667eea to #764ba2)
- **Card Design**: Rounded corners with subtle shadows
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-first design approach

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure Django backend is running on port 8000
   - Check CORS configuration in Django
   - Verify proxy settings in package.json

2. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility
   - Clear npm cache: `npm cache clean --force`

3. **Styling Issues**
   - Ensure Bootstrap CSS is properly imported
   - Check for CSS conflicts in custom styles
   - Verify Bootstrap Icons are loaded

### Development Tips

- Use browser dev tools to inspect API requests
- Check console for JavaScript errors
- Monitor network tab for API communication
- Test responsive design on different screen sizes

## Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Maintain consistent code formatting
4. Test components thoroughly
5. Update documentation as needed

## License

This project is part of the StoryGen platform.
