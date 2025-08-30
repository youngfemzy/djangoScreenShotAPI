# Website Screenshot Generator API

This Flask application provides a comprehensive API for generating website screenshots across multiple devices with professional mockups.

## Base URL
```
http://localhost:5000/api
```

## API Endpoints

### 1. Create Project
**POST** `/projects`

Create a new project for screenshot generation.

```json
{
    "name": "My Website Project",
    "website_url": "https://example.com"
}
```

**Response:**
```json
{
    "message": "Project created successfully",
    "project": {
        "id": 1,
        "name": "My Website Project",
        "website_url": "https://example.com",
        "created_at": "2025-08-30T22:00:00",
        "updated_at": "2025-08-30T22:00:00",
        "screenshot_count": 0
    }
}
```

### 2. List All Projects
**GET** `/projects`

**Response:**
```json
{
    "projects": [
        {
            "id": 1,
            "name": "My Website Project",
            "website_url": "https://example.com",
            "created_at": "2025-08-30T22:00:00",
            "updated_at": "2025-08-30T22:00:00",
            "screenshot_count": 3
        }
    ]
}
```

### 3. Get Project Details
**GET** `/projects/{project_id}`

**Response:**
```json
{
    "project": {
        "id": 1,
        "name": "My Website Project",
        "website_url": "https://example.com",
        "created_at": "2025-08-30T22:00:00",
        "updated_at": "2025-08-30T22:00:00",
        "screenshot_count": 3
    },
    "screenshots": [
        {
            "id": 1,
            "project_id": 1,
            "device_type": "mobile",
            "device_name": "iPhone 12",
            "original_path": "/users/user1/project_1/normal_screenshots/iphone_12_390x844.png",
            "mockup_path": "/users/user1/project_1/mockup_screenshots/mockup_iphone_12_390x844.png",
            "width": 390,
            "height": 844,
            "created_at": "2025-08-30T22:00:00"
        }
    ]
}
```

### 4. Generate Screenshots
**POST** `/projects/{project_id}/screenshots`

Generate screenshots for selected device types.

```json
{
    "devices": ["mobile", "tablet", "desktop"]
}
```

Available device types:
- `mobile`: iPhone 12, Samsung Galaxy S21, Google Pixel 5
- `tablet`: iPad Pro, Samsung Galaxy Tab, Surface Pro
- `desktop`: Desktop 1920x1080, Desktop 1366x768, MacBook Pro

**Response:**
```json
{
    "message": "Generated 3 screenshots",
    "screenshots": [
        {
            "id": 1,
            "project_id": 1,
            "device_type": "mobile",
            "device_name": "iPhone 12",
            "original_path": "/users/user1/project_1/normal_screenshots/iphone_12_390x844.png",
            "mockup_path": "/users/user1/project_1/mockup_screenshots/mockup_iphone_12_390x844.png",
            "width": 390,
            "height": 844,
            "created_at": "2025-08-30T22:00:00"
        }
    ]
}
```

### 5. List Project Screenshots
**GET** `/projects/{project_id}/screenshots`

**Response:**
```json
{
    "screenshots": [
        {
            "id": 1,
            "project_id": 1,
            "device_type": "mobile",
            "device_name": "iPhone 12",
            "original_path": "/users/user1/project_1/normal_screenshots/iphone_12_390x844.png",
            "mockup_path": "/users/user1/project_1/mockup_screenshots/mockup_iphone_12_390x844.png",
            "width": 390,
            "height": 844,
            "created_at": "2025-08-30T22:00:00"
        }
    ]
}
```

### 6. Delete Project
**DELETE** `/projects/{project_id}`

Deletes the project and all associated screenshots and files.

**Response:**
```json
{
    "message": "Project deleted successfully"
}
```

### 7. Serve Screenshot Files
**GET** `/screenshots/{file_path}`

Access screenshot files directly via URL.

Example: `http://localhost:5000/api/screenshots/user1/project_1/normal_screenshots/iphone_12_390x844.png`

## Folder Structure

The application creates an organized folder structure:

```
users/
└── user1/
    └── project_{project_id}/
        ├── normal_screenshots/
        │   ├── iphone_12_390x844.png
        │   ├── ipad_pro_1024x1366.png
        │   └── desktop_1920x1080_1920x1080.png
        └── mockup_screenshots/
            ├── mockup_iphone_12_390x844.png
            ├── mockup_ipad_pro_1024x1366.png
            └── mockup_desktop_1920x1080_1920x1080.png
```

## Device Mockups

Each screenshot gets processed into professional device mockups:
- **Mobile**: Realistic phone frame with home button and camera
- **Tablet**: Tablet frame with home button and rounded corners
- **Desktop**: Monitor with stand and shadow effects

## Usage Example with cURL

```bash
# Create a project
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Test Project", "website_url": "https://example.com"}'

# Generate screenshots for all devices
curl -X POST http://localhost:5000/api/projects/1/screenshots \
  -H "Content-Type: application/json" \
  -d '{"devices": ["mobile", "tablet", "desktop"]}'

# Get project details with screenshots
curl http://localhost:5000/api/projects/1

# Access a screenshot file
curl http://localhost:5000/api/screenshots/user1/project_1/normal_screenshots/iphone_12_390x844.png
```

## Database

The application uses SQLite by default, but can be configured to use PostgreSQL in production by setting the `DATABASE_URL` environment variable.

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

Error responses include descriptive messages:
```json
{
    "error": "Project not found"
}
```