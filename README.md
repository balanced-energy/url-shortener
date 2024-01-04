# url-shortener

## Overview
The URL Shortener is a comprehensive system designed for creating, managing, and using short URLs. It offers a secure and user-friendly way to handle URL shortening and redirection.

## Live Application
The application is currently live and can be accessed at [camdensurlapp.com](http://camdensurlapp.com).

## Features
- **Short URL Generation:** Create short URLs from longer ones, with optional custom URLs.
- **User Authentication:** Secure login system with token-based user authentication.
- **Admin Functionality:** Administrative capabilities for managing URLs and users.
- **Error Handling:** Robust error handling for a smooth user experience.
- **URL Redirection:** Seamless redirection from short URLs to their original destinations.
- **User Management:** Features to create users, change passwords, and manage URL limits.
- **List URLs:** Endpoints to list all URLs or user-specific URLs.

## Technology Stack
- **Backend:** FastAPI for efficient and easy-to-use API development.
- **Database:** DynamoDB for scalable and reliable storage.
- **Authentication:** OAuth2 for secure user authentication.

## API Endpoints
The application provides several API endpoints, including:
- User authentication (`/token`)
- User creation (`/create_user`)
- Password change (`/change_password`)
- URL shortening (`/shorten_url`)
- Listing URLs (`/list_urls`, `/list_my_urls`)
- Updating URL limits (`/update_url_limit`)
- Redirecting short URLs (`/redirect/{short_url}`)

For more information, check out the full [Design Document](https://docs.google.com/document/d/15kf3xSnfBMEdwmWyDJH4nE8pdYRlgQV0vWAupNK8b40/edit#heading=h.j4kz88b8nsd7).
