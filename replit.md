# Website Screenshot Generator

## Overview

This project is a Django-based web application that generates professional device mockups from website screenshots. Users can create projects by providing a website URL, then capture screenshots across different device types (mobile, tablet, desktop) and generate realistic device mockups. The application uses Playwright and Selenium for browser automation and PIL for image processing to create high-quality mockups with device frames.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Django with class-based views and modular app structure
- **Database**: Django ORM with support for both SQLite (development) and PostgreSQL (production via DATABASE_URL)
- **Models**: Two main entities - Project (stores website info) and Screenshot (stores device-specific captures)
- **Services**: Separated business logic into dedicated service classes
  - `ScreenshotService`: Handles browser automation and screenshot capture using Playwright/Selenium
  - `MockupService`: Processes screenshots into device mockups using PIL image manipulation

### Frontend Architecture
- **Template Engine**: Django Templates with inheritance and template tags
- **UI Framework**: Bootstrap with Replit dark theme for responsive design
- **JavaScript**: Vanilla JS for API interactions and dynamic UI updates
- **Styling**: Bootstrap classes with custom CSS for device mockup effects

### Data Storage
- **Primary Database**: Django ORM with configurable backend (SQLite for dev, PostgreSQL for production)
- **File Storage**: Local filesystem for storing screenshot and mockup images
- **Database Schema**: 
  - Projects table with basic metadata and timestamps
  - Screenshots table with device info, file paths, and dimensions
  - One-to-many relationship with cascade delete

### Screenshot Generation
- **Browser Engine**: Playwright (primary) and Selenium (fallback) for cross-platform screenshot capture
- **Device Simulation**: Predefined device configurations with viewport dimensions and user agents
- **Image Processing**: PIL for creating device frames, shadows, and mockup effects
- **Supported Devices**: Mobile (iPhone, Samsung, Pixel), Tablet (iPad, Galaxy Tab), Desktop (various resolutions)
- **Fallback System**: Placeholder generation when browser automation fails

### Admin Interface
- **Django Admin**: Full admin interface for managing projects and screenshots
- **User Management**: Django's built-in authentication system
- **Superuser Account**: Admin credentials for database management

## External Dependencies

### Core Framework Dependencies
- **Django**: Web framework with ORM, admin interface, and built-in features
- **Gunicorn**: WSGI HTTP server for production deployment

### Browser Automation
- **Playwright**: Primary headless browser automation for screenshot capture
- **Selenium**: Fallback browser automation with Chrome driver
- **Chromium**: Browser engine for headless screenshot capture

### Image Processing
- **Pillow (PIL)**: Image manipulation library for creating device mockups and frames

### Frontend Libraries
- **Bootstrap**: CSS framework with Replit dark theme support
- **Font Awesome**: Icon library for UI elements

### Development Tools
- **Python Logging**: Built-in logging for debugging and monitoring
- **Django Migrations**: Database schema versioning and management

## Recent Changes (August 2025)

### Migration to Django
- **Complete rebuild**: Migrated from Flask to Django framework
- **Django apps**: Organized code into `screenshots` app with proper Django structure
- **URL routing**: Django URLconf with app-level URL patterns
- **Template inheritance**: Base template with Bootstrap styling
- **Admin interface**: Full Django admin for project and screenshot management
- **API compatibility**: Maintained same API endpoints for seamless transition

### Enhanced Features
- **Admin dashboard**: Django admin interface for easy data management
- **Better error handling**: Improved error messages and user feedback
- **Template improvements**: Professional UI with Bootstrap dark theme
- **Service layer**: Clean separation of business logic from views
- **Fallback system**: Multiple browser automation options with placeholder fallback

The application is designed to be deployment-ready with environment variable configuration for database connections and session secrets, making it suitable for both development and production environments.