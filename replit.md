# Website Screenshot Generator

## Overview

This project is a Flask-based web application that generates professional device mockups from website screenshots. Users can create projects by providing a website URL, then capture screenshots across different device types (mobile, tablet, desktop) and generate realistic device mockups. The application uses Playwright for browser automation and PIL for image processing to create high-quality mockups with device frames.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with Blueprint-based modular routing
- **Database**: SQLAlchemy ORM with support for both SQLite (development) and PostgreSQL (production via DATABASE_URL)
- **Models**: Two main entities - Project (stores website info) and Screenshot (stores device-specific captures)
- **Services**: Separated business logic into dedicated service classes
  - `ScreenshotService`: Handles browser automation and screenshot capture using Playwright
  - `MockupService`: Processes screenshots into device mockups using PIL image manipulation

### Frontend Architecture
- **Template Engine**: Jinja2 with server-side rendering
- **UI Framework**: Bootstrap with dark theme for responsive design
- **JavaScript**: Vanilla JS for API interactions and dynamic UI updates
- **Styling**: Custom CSS with hover effects and animations

### Data Storage
- **Primary Database**: SQLAlchemy with configurable backend (SQLite for dev, PostgreSQL for production)
- **File Storage**: Local filesystem for storing screenshot and mockup images
- **Database Schema**: 
  - Projects table with basic metadata and timestamps
  - Screenshots table with device info, file paths, and dimensions
  - One-to-many relationship with cascade delete

### Screenshot Generation
- **Browser Engine**: Playwright (Chromium) for cross-platform screenshot capture
- **Device Simulation**: Predefined device configurations with viewport dimensions and user agents
- **Image Processing**: PIL for creating device frames, shadows, and mockup effects
- **Supported Devices**: Mobile (iPhone, Samsung, Pixel), Tablet (iPad, Galaxy Tab), Desktop (various resolutions)

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework with SQLAlchemy extension for database operations
- **Werkzeug**: WSGI utilities including ProxyFix for deployment

### Browser Automation
- **Playwright**: Headless browser automation for screenshot capture
- **Chromium**: Browser engine bundled with Playwright

### Image Processing
- **Pillow (PIL)**: Image manipulation library for creating device mockups and frames

### Frontend Libraries
- **Bootstrap**: CSS framework with dark theme support
- **Font Awesome**: Icon library for UI elements

### Development Tools
- **Python Logging**: Built-in logging for debugging and monitoring
- **SQLAlchemy**: Database ORM with connection pooling and migrations support

The application is designed to be deployment-ready with environment variable configuration for database connections and session secrets, making it suitable for both development and production environments.