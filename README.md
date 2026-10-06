# JENNA 2.0

A SaaS platform for managing QR/NFC interactions, restaurant reviews, staff activity, and operational analytics.

## Overview

JENNA 2.0 is a web-based platform designed for restaurants to centralize customer interaction data, staff activity, review information, and operational metrics.

The platform combines QR/NFC interaction tracking with review synchronization and attribution workflows, allowing businesses to analyze activity from a centralized dashboard.

## Features

- QR/NFC interaction tracking
- Waiter management
- NFC card management
- Review synchronization
- Review evidence management
- Review attribution workflows
- Automatic review attribution
- Name matching for review attribution
- Analytics and operational metrics
- Business and user management
- Authentication and session management
- Configurable review synchronization schedules
- Review synchronization health monitoring
- Dashboard for operational data

## Architecture

JENNA 2.0 is structured as a Flask API and a React frontend.

```text
Client
  |
  v
React + Vite
  |
  v
Flask API
  |
  +-- Authentication
  +-- Business Management
  +-- Waiters
  +-- Cards
  +-- Taps
  +-- Reviews
  +-- Review Attribution
  +-- Analytics
  |
  v
PostgreSQL
  |
  +-- External Google Services
```

## Tech Stack

### Backend

- Python
- Flask 3.1
- Gunicorn
- PostgreSQL
- psycopg
- python-dotenv

### Frontend

- React 19
- Vite 8
- React DOM
- Lucide React
- Motion
- ESLint

### External Integrations

- Google Places
- Google Translate

### Testing

- pytest

## Project Structure

```text
jenna-2.0/
├── app/
│   ├── routes/
│   ├── services/
│   ├── jobs/
│   └── database/
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
│
├── tests/
├── requirements.txt
└── run.py
```

## Core Modules

The backend is organized around business capabilities.

Key service areas include:

- Authentication and users
- Businesses and business users
- Waiters
- Cards and interactions
- Analytics
- Google Places integration
- Google review observation and synchronization
- Review evidence
- Review attribution
- Automatic attribution
- Review name matching
- Review snapshots
- Synchronization scheduling

## Review Attribution

A core part of JENNA is the separation between customer interactions and confirmed review attribution.

A QR/NFC interaction represents an interaction with the system. It is not automatically treated as proof that the interaction resulted in a review.

Review attribution uses additional evidence and matching workflows to identify cases where a review can be associated with a waiter.

This distinction keeps interaction metrics and review attribution as separate signals.

## Security

The application uses environment-based configuration for sensitive values.

Session cookies are configured with security-oriented attributes including:

- HttpOnly
- SameSite
- Configurable Secure flag

Secrets and environment-specific configuration are excluded from version control.

## Status

Active development.

JENNA 2.0 is also used as a software engineering portfolio project demonstrating backend development, API design, database-driven applications, external API integrations, automated processing, testing, and frontend development.