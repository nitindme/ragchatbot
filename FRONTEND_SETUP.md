# Frontend Setup Guide

## Admin UI (Port 3000)

### Installation

```bash
cd frontend/admin
npm install
```

### Configuration

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Run Development Server

```bash
npm run dev
```

Access at: http://localhost:3000

### Default Login

- Username: `admin`
- Password: `admin123`

### Build for Production

```bash
npm run build
npm start
```

---

## Chat UI (Port 3001)

### Installation

```bash
cd frontend/chat
npm install
```

### Configuration

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Run Development Server

```bash
npm run dev
```

Access at: http://localhost:3001

### Build for Production

```bash
npm run build
npm start
```

---

## Backend API (Port 8001)

Already configured via Docker Compose. See main README.md for details.

---

## Complete Setup (All Services)

### Terminal 1: Backend (Docker)
```bash
cd /path/to/delhipolicechatbot
./setup.sh
```

### Terminal 2: Admin UI
```bash
cd frontend/admin
npm install && npm run dev
```

### Terminal 3: Chat UI
```bash
cd frontend/chat
npm install && npm run dev
```

## Access Points

- **Backend API**: http://localhost:8001/docs
- **Admin Dashboard**: http://localhost:3000
- **Public Chat**: http://localhost:3001

## Features

### Admin UI
- Document upload (PDF, TXT, DOCX)
- Document listing
- Delete documents
- Duplicate detection (SHA256)
- JWT authentication

### Chat UI
- Start new conversations
- Send messages
- View chat history
- Real-time responses
- Auto-scroll
- Typing indicators

## Rate Limits

- Session creation: 10/minute
- Message sending: 20/minute
- History retrieval: 30/minute
- Session management: 10/minute

##Troubleshooting

### Admin UI won't start
```bash
cd frontend/admin
rm -rf node_modules .next
npm install
npm run dev
```

### Chat UI won't start
```bash
cd frontend/chat
rm -rf node_modules .next
npm install
npm run dev
```

### Backend API errors
```bash
docker-compose logs -f backend
docker-compose restart backend
```

### CORS errors
Check that `NEXT_PUBLIC_API_URL` in `.env.local` matches your backend URL.
