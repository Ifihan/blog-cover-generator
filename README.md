# Blog Cover Generator

AI-powered blog cover image generator using Google's Gemini 2.5 Flash Image model. Generate professional cover images for Hashnode, Dev.to, Medium, or custom dimensions.

## Features

- **AI Image Generation** - 6 visual styles (Creative, Cinematic, Minimalist, Professional, Abstract, and Tech)
- **Platform Presets** - Optimized dimensions for Hashnode (1600x840), Dev.to (1000x420), Medium (1500x750), and Custom sizes
- **Text Overlay** - Customizable fonts, colors, positions, and shadows
- **User Dashboard** - View and manage generation history

## Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **AI**: Google Gemini 2.5 Flash Image
- **Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Google Cloud project with Gemini API enabled
- GCS bucket for image storage

### Installation

```bash
git clone https://github.com/ifihan/blog-cover-generator.git
cd blog-cover-generator

# using uv - read about uv at https://docs.astral.sh/uv/

uv sync
```

### Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

### Run

```bash
python app.py

```

## API Endpoints

| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| POST   | `/api/generate`       | Generate cover images    |
| POST   | `/api/save-selection` | Save selected image      |
| POST   | `/api/download`       | Download with processing |
| GET    | `/api/styles`         | List available styles    |
| GET    | `/api/platforms`      | List platform dimensions |
| POST   | `/api/feedback`       | Submit feedback          |

## License

MIT License. See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open issues and submit pull requests for improvements or bug fixes. Refer to the [CONTRIBUTING](CONTRIBUTING.md) file for guidelines.
