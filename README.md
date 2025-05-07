# Blog Demo with FastAPI and Supabase

A simple blog application demonstrating various Supabase features using FastAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Supabase:

   ### Option A: Local Development (Recommended)
   1. Install Supabase CLI and Docker
   2. Start local Supabase instance:
      ```bash
      supabase init
      supabase start
      ```
   3. The app will automatically use the local instance

   ### Option B: Cloud Development
   1. Create a new project at https://supabase.com
   2. Copy your project URL and anon/public key
   3. Create a `.env` file in the project root with:
      ```
      SUPABASE_URL=your_supabase_project_url
      SUPABASE_KEY=your_supabase_anon_key
      ```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

The application will be available at http://localhost:8000

## Development

By default, the application will connect to a local Supabase instance. To use a cloud instance, set the appropriate environment variables in `.env`.